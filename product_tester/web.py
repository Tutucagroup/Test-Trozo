"""
Interfaz web local: python -m product_tester web

Sirve una página en http://127.0.0.1:<puerto> para armar el brief con formularios,
subir el export de Kalodata y los videos, ver la estructura y los anuncios, y lanzar.
Solo escucha en tu computadora: las credenciales siguen en el .env.
"""

import dataclasses
import json
import mimetypes
import os
import re
import threading
import uuid
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, urlparse

import yaml

from .config import ConfigError, MetaSettings, ShopifySettings, normalize_brief
from .copywriting import build_copy
from .kalodata import VIDEO_EXTS
from .launcher import LaunchError, launch, prepare
from .structures import total_daily_budget

INDEX = Path(__file__).parent / "web" / "index.html"
USER_ERRORS = (ConfigError, LaunchError)
USER_ERROR_NAMES = {"MetaAPIError", "ShopifyError", "MediaError"}
LOCAL_HOSTS = {"127.0.0.1", "localhost"}


def _safe_name(name):
    name = Path(name or "").name
    name = re.sub(r"[^\w.\- ]+", "_", name).strip(" .")
    return name or "archivo"


def _strip_empty(value):
    """Saca claves vacías para que el YAML exportado quede limpio."""
    if isinstance(value, dict):
        out = {k: _strip_empty(v) for k, v in value.items() if not k.startswith("_")}
        return {k: v for k, v in out.items() if v not in (None, "", [], {})}
    if isinstance(value, list):
        return [_strip_empty(v) for v in value]
    return value


def ads_manager_url(account_id, campaign_id):
    act = (account_id or "").replace("act_", "")
    return (f"https://adsmanager.facebook.com/adsmanager/manage/campaigns"
            f"?act={act}&selected_campaign_ids={campaign_id}")


class App:
    def __init__(self, workspace="workspace", runs_dir="runs"):
        self.workspace = Path(workspace).resolve()
        self.uploads = self.workspace / "uploads"
        self.uploads.mkdir(parents=True, exist_ok=True)
        self.runs_dir = Path(runs_dir)
        self.jobs = {}
        self.allowed_media = set()
        self._lock = threading.Lock()
        self._launching = False

    # -------------------------------------------------------------- estado
    def status(self):
        from .meta_ads import MetaAdsClient
        from .shopify import ShopifyClient

        out = {}
        try:
            settings = MetaSettings.from_env()
            acc = MetaAdsClient(settings).account_info()
            out["meta"] = {"ok": True, "name": acc.get("name"), "currency": acc.get("currency"),
                           "account_id": settings.ad_account_id}
        except ConfigError as e:
            out["meta"] = {"ok": False, "configured": False, "error": str(e)}
        except Exception as e:
            out["meta"] = {"ok": False, "configured": True, "error": str(e)}
        try:
            shop = ShopifyClient(ShopifySettings.from_env()).shop_info()
            out["shopify"] = {"ok": True, "name": shop["name"], "domain": shop["primaryDomain"]["host"]}
        except ConfigError as e:
            out["shopify"] = {"ok": False, "configured": False, "error": str(e)}
        except Exception as e:
            out["shopify"] = {"ok": False, "configured": True, "error": str(e)}
        return out

    # -------------------------------------------------------------- subidas
    def save_upload(self, name, subdir, stream, length):
        folder = self.uploads / _safe_name(subdir) if subdir else self.uploads
        folder.mkdir(parents=True, exist_ok=True)
        dest = folder / _safe_name(name)
        remaining = length
        with open(dest, "wb") as f:
            while remaining > 0:
                chunk = stream.read(min(1 << 20, remaining))
                if not chunk:
                    break
                f.write(chunk)
                remaining -= len(chunk)
        return {"path": str(dest.relative_to(self.workspace)), "name": dest.name,
                "size": dest.stat().st_size}

    # ----------------------------------------------------------------- plan
    def _creative_json(self, creative, copy):
        primary, headline, description = copy
        media_url = None
        if creative.path:
            self.allowed_media.add(str(Path(creative.path).resolve()))
            media_url = "/media?path=" + quote(str(Path(creative.path).resolve()))
        elif Path(urlparse(creative.url).path).suffix.lower() in VIDEO_EXTS:
            media_url = creative.url
        return {
            "label": creative.label, "source": creative.source,
            "kind": "file" if creative.path else "url", "url": creative.url,
            "media_url": media_url, "caption": creative.caption, "creator": creative.creator,
            "metrics": creative.metrics, "primary_text": primary, "headline": headline,
            "description": description,
        }

    def plan(self, raw):
        brief = normalize_brief(raw, self.workspace)
        creatives, plan = prepare(brief)
        return {
            "creatives": [self._creative_json(c, build_copy(brief, c, i))
                          for i, c in enumerate(creatives)],
            "plan": dataclasses.asdict(plan),
            "total_daily_budget": total_daily_budget(plan),
        }

    # -------------------------------------------------------------- shopify
    def shopify_product(self, handle):
        from .shopify import ShopifyClient
        client = ShopifyClient(ShopifySettings.from_env())
        product = client.get_product(handle)
        product["url"] = client.product_url(product)
        return product

    # ---------------------------------------------------------------- brief
    def brief_yaml(self, raw):
        return {"yaml": yaml.safe_dump(_strip_empty(raw), allow_unicode=True, sort_keys=False)}

    def parse_brief(self, text):
        data = yaml.safe_load(text or "") or {}
        if not isinstance(data, dict):
            raise ConfigError("El archivo no es un brief válido")
        return data

    # --------------------------------------------------------------- launch
    def start_launch(self, raw, activate=False, force=False):
        from .meta_ads import MetaAdsClient
        from .shopify import ShopifyClient

        with self._lock:
            if self._launching:
                raise LaunchError("Ya hay un lanzamiento en curso")
            self._launching = True
        try:
            brief = normalize_brief(raw, self.workspace)
            meta = MetaAdsClient(MetaSettings.from_env())
            try:
                shopify = ShopifyClient(ShopifySettings.from_env())
            except ConfigError:
                shopify = None
        except Exception:
            self._launching = False
            raise

        job = {"id": uuid.uuid4().hex[:10], "status": "running", "logs": [],
               "result": None, "error": None, "activate": activate}
        self.jobs[job["id"]] = job

        def run():
            try:
                result = launch(brief, meta, shopify, activate=activate, force=force,
                                runs_dir=self.runs_dir, media_dir=self.workspace / "media",
                                log=job["logs"].append)
                job["result"] = result
                job["ads_manager_url"] = ads_manager_url(meta.s.ad_account_id, result.get("campaign_id"))
                job["status"] = "done"
            except Exception as e:
                job["error"] = str(e)
                job["status"] = "failed"
            finally:
                self._launching = False

        threading.Thread(target=run, daemon=True).start()
        return {"job_id": job["id"]}

    def runs(self, limit=20):
        if not self.runs_dir.exists():
            return []
        account = os.environ.get("META_AD_ACCOUNT_ID", "")
        out = []
        files = sorted((p for p in self.runs_dir.glob("*.json") if p.name != "video_cache.json"),
                       reverse=True)[:limit]
        for p in files:
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
            except ValueError:
                continue
            cid = data.get("campaign_id")
            out.append({
                "file": p.name, "started_at": data.get("started_at"), "product": data.get("product"),
                "status": data.get("status"), "campaign_id": cid,
                "campaign_name": data.get("campaign_name"), "ads": len(data.get("ads", [])),
                "error": data.get("error"),
                "ads_manager_url": ads_manager_url(account, cid) if cid and account else None,
            })
        return out


def make_handler(app):
    class Handler(BaseHTTPRequestHandler):
        server_version = "ProductTester"

        def log_message(self, *args):
            pass

        # ------------------------------------------------------- helpers
        def _host_ok(self):
            host = (self.headers.get("Host") or "").rsplit(":", 1)[0].strip("[]")
            return host in LOCAL_HOSTS

        def _json(self, code, data):
            body = json.dumps(data, ensure_ascii=False, default=str).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _body_json(self):
            length = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(length) if length else b"{}"
            return json.loads(raw.decode("utf-8") or "{}")

        def _error(self, e):
            if isinstance(e, USER_ERRORS) or type(e).__name__ in USER_ERROR_NAMES:
                self._json(400, {"error": str(e)})
            else:
                self._json(500, {"error": f"{type(e).__name__}: {e}"})

        def _send_index(self):
            body = INDEX.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _send_media(self, raw_path):
            path = Path(raw_path).resolve() if raw_path else None
            if not path or str(path) not in app.allowed_media or not path.is_file():
                return self._json(404, {"error": "video no encontrado"})
            size = path.stat().st_size
            start, end = 0, size - 1
            rng = self.headers.get("Range", "")
            if rng.startswith("bytes="):
                first, _, last = rng[6:].split(",")[0].partition("-")
                if first:
                    start = int(first)
                    end = min(int(last), size - 1) if last else size - 1
                elif last:
                    start = max(0, size - int(last))
                self.send_response(206)
                self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
            else:
                self.send_response(200)
            self.send_header("Content-Type", mimetypes.guess_type(path.name)[0] or "video/mp4")
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Content-Length", str(end - start + 1))
            self.end_headers()
            try:
                with open(path, "rb") as f:
                    f.seek(start)
                    remaining = end - start + 1
                    while remaining > 0:
                        chunk = f.read(min(1 << 16, remaining))
                        if not chunk:
                            break
                        self.wfile.write(chunk)
                        remaining -= len(chunk)
            except (BrokenPipeError, ConnectionResetError):
                pass  # el navegador cortó (p. ej. al adelantar el video)

        # ------------------------------------------------------- routes
        def do_GET(self):
            if not self._host_ok():
                return self._json(403, {"error": "solo acceso local"})
            url = urlparse(self.path)
            query = parse_qs(url.query)
            try:
                if url.path in ("/", "/index.html"):
                    self._send_index()
                elif url.path == "/api/status":
                    self._json(200, app.status())
                elif url.path == "/api/runs":
                    self._json(200, {"runs": app.runs()})
                elif url.path.startswith("/api/jobs/"):
                    job = app.jobs.get(url.path.rsplit("/", 1)[1])
                    self._json(200, job) if job else self._json(404, {"error": "no existe"})
                elif url.path == "/media":
                    self._send_media(query.get("path", [""])[0])
                else:
                    self._json(404, {"error": "no encontrado"})
            except Exception as e:
                self._error(e)

        def do_POST(self):
            if not self._host_ok():
                return self._json(403, {"error": "solo acceso local"})
            url = urlparse(self.path)
            query = parse_qs(url.query)
            try:
                if url.path == "/api/upload":
                    length = int(self.headers.get("Content-Length") or 0)
                    self._json(200, app.save_upload(query.get("name", [""])[0],
                                                    query.get("dir", [""])[0], self.rfile, length))
                    return
                body = self._body_json()
                if url.path == "/api/plan":
                    self._json(200, app.plan(body))
                elif url.path == "/api/shopify/product":
                    self._json(200, app.shopify_product(body.get("handle", "")))
                elif url.path == "/api/brief/yaml":
                    self._json(200, app.brief_yaml(body))
                elif url.path == "/api/brief/parse":
                    self._json(200, app.parse_brief(body.get("text", "")))
                elif url.path == "/api/launch":
                    self._json(200, app.start_launch(body.get("brief") or {},
                                                     activate=bool(body.get("activate")),
                                                     force=bool(body.get("force"))))
                else:
                    self._json(404, {"error": "no encontrado"})
            except Exception as e:
                self._error(e)

    return Handler


def serve(port=8765, open_browser=True, workspace="workspace", runs_dir="runs"):
    app = App(workspace=workspace, runs_dir=runs_dir)
    server = ThreadingHTTPServer(("127.0.0.1", port), make_handler(app))
    url = f"http://127.0.0.1:{server.server_address[1]}"
    print(f"Product Tester abierto en {url}  (Ctrl+C para cerrar)")
    if open_browser:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nCerrado.")
    finally:
        server.server_close()
