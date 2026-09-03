#!/usr/bin/env python3
"""
Renderiza localmente las secciones del tema VALCA con python-liquid y datos reales
de Latinologia, para poder revisar el resultado visualmente antes de subirlo a Shopify.

No sustituye a Shopify: aproxima los objetos globales (shop, collections, product,
linklists, routes) y omite `{% schema %}`, igual que hace el motor real al renderizar.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from liquid import Environment, FileSystemLoader

ROOT = Path(__file__).resolve().parent.parent
THEME = ROOT / "theme"
DATA = json.loads((ROOT / "tools" / "data.json").read_text())
OUT = ROOT / "out"

MONEY_FORMAT = DATA["shop"]["money_format"]


# --------------------------------------------------------------------------- #
# Filtros al estilo Shopify
# --------------------------------------------------------------------------- #
def f_image_url(value, *, width=None, height=None, crop=None, **_):
    """Aproxima el filtro image_url de Shopify sobre una URL del CDN."""
    if not value:
        return ""
    url = value.get("src") if isinstance(value, dict) else str(value)
    if not url:
        return ""
    base = url.split("&width=")[0]
    sep = "&" if "?" in base else "?"
    parts = []
    if width:
        parts.append(f"width={int(width)}")
    if height:
        parts.append(f"height={int(height)}")
    if crop:
        parts.append(f"crop={crop}")
    return base + (sep + "&".join(parts) if parts else "")


def _group_thousands(number: str, sep: str) -> str:
    return re.sub(r"(\d)(?=(\d{3})+$)", r"\1" + sep, number)


def f_money(value, *_a, **_k):
    """Formatea centavos con el money_format de la tienda."""
    if value in (None, "", False):
        return ""
    try:
        cents = int(round(float(value)))
    except (TypeError, ValueError):
        return ""

    def repl(match):
        token = match.group(1)
        if token in ("amount", "amount_with_comma_separator"):
            whole, frac = divmod(cents, 100)
            dec_sep, th_sep = (",", ".") if "comma" in token else (".", ",")
            return f"{_group_thousands(str(whole), th_sep)}{dec_sep}{frac:02d}"
        whole = int(round(cents / 100))
        th_sep = "." if "comma" in token else ","
        return _group_thousands(str(whole), th_sep)

    return re.sub(r"\{\{\s*(\w+)\s*\}\}", repl, MONEY_FORMAT)


def f_at_most(value, arg, *_a, **_k):
    try:
        return min(float(value), float(arg)) if isinstance(value, float) else min(int(value), int(arg))
    except (TypeError, ValueError):
        return value


def f_at_least(value, arg, *_a, **_k):
    try:
        return max(float(value), float(arg)) if isinstance(value, float) else max(int(value), int(arg))
    except (TypeError, ValueError):
        return value


def f_default_errors(value, *_a, **_k):
    if not value:
        return ""
    return "<br>".join(value) if isinstance(value, (list, tuple)) else str(value)


def f_payment_type_svg_tag(value, *_a, **_k):
    return ""


def f_json(value, *_a, **_k):
    return json.dumps(value)


def f_handleize(value, *_a, **_k):
    return re.sub(r"[^a-z0-9]+", "-", str(value).lower()).strip("-")


# --------------------------------------------------------------------------- #
# Objetos globales
# --------------------------------------------------------------------------- #
def build_image(url: str) -> dict:
    return {"src": url, "url": url, "alt": "", "width": 1000, "height": 1000}


def build_product(raw: dict) -> dict:
    images = [build_image(u) for u in raw["images"]]
    return {
        "handle": raw["handle"],
        "title": raw["title"],
        "url": f"/products/{raw['handle']}",
        "tags": raw.get("tags", []),
        "price": raw["price"],
        "compare_at_price": raw.get("compare_at_price"),
        "available": raw.get("available", True),
        "images": images,
        "featured_image": images[0] if images else None,
        "metafields": {"custom": {}},
    }


PRODUCTS = {h: build_product(p) for h, p in DATA["products"].items()}

COLLECTIONS = {}
for handle, coll in DATA["collections"].items():
    prods = [PRODUCTS[h] for h in coll["products"] if h in PRODUCTS]
    COLLECTIONS[handle] = {
        "handle": handle,
        "title": coll["title"],
        "url": f"/collections/{handle}",
        "products": prods,
        "image": "",  # Shopify entrega nil; "" es lo que python-liquid trata como blank
        "all_products_count": len(prods),
    }

LINKLISTS = {}
for handle, menu in DATA["menus"].items():
    LINKLISTS[handle] = {
        "handle": handle,
        "title": menu["title"],
        "links": [
            {
                "title": item["title"],
                "url": item["url"],
                "active": False,
                "child_active": False,
                "links": [
                    {"title": c["title"], "url": c["url"], "active": False, "links": []}
                    for c in item.get("items", [])
                ],
            }
            for item in menu["items"]
        ],
    }

FILE_MAP = DATA["files"]

GLOBALS = {
    "shop": {
        "name": DATA["shop"]["name"],
        "url": DATA["shop"]["url"],
        "customer_accounts_enabled": True,
        "enabled_payment_types": [],
        "money_format": MONEY_FORMAT,
    },
    "cart": {"item_count": 0, "items": [], "total_price": 0},
    "customer": None,
    "collections": COLLECTIONS,
    "linklists": LINKLISTS,
    "routes": {
        "root_url": "/",
        "cart_url": "/cart",
        "search_url": "/search",
        "account_url": "/account",
        "account_login_url": "/account/login",
        "all_products_collection_url": "/collections/all",
    },
    "request": {"design_mode": False, "page_type": "index"},
    "form": {"posted_successfully": False, "errors": None, "email": ""},
    "settings": {},
}


# --------------------------------------------------------------------------- #
# Resolución de referencias shopify://
# --------------------------------------------------------------------------- #
def resolve(value):
    """Convierte referencias shopify:// en objetos/URLs utilizables."""
    if not isinstance(value, str) or not value.startswith("shopify://"):
        return value

    if value.startswith("shopify://shop_images/"):
        name = value[len("shopify://shop_images/"):]
        url = FILE_MAP.get(name)
        if not url:
            print(f"  [aviso] imagen sin mapear: {name}", file=sys.stderr)
            return None
        return build_image(url)

    for prefix, path in (
        ("shopify://collections/", "/collections/"),
        ("shopify://pages/", "/pages/"),
        ("shopify://products/", "/products/"),
    ):
        if value.startswith(prefix):
            return path + value[len(prefix):]
    return value


class BlankDict(dict):
    """Los ajustes sin valor deben comportarse como `blank`, igual que en Shopify.

    python-liquid considera `nil != blank` verdadero, mientras que Shopify lo
    considera falso; devolver "" para las claves ausentes replica el motor real.
    """

    def __missing__(self, key):  # noqa: D105
        return ""


def resolve_settings(settings: dict, section_type: str) -> dict:
    out = BlankDict()
    for key, val in settings.items():
        if key == "collection" and isinstance(val, str) and val:
            out[key] = val  # el Liquid hace collections[handle]
        elif key == "product" and isinstance(val, str) and val:
            out[key] = PRODUCTS.get(val)
        elif key == "menu" and isinstance(val, str):
            out[key] = val
        else:
            out[key] = resolve(val)
    return BlankDict({k: ("" if v is None else v) for k, v in out.items()})


# --------------------------------------------------------------------------- #
# Motor
# --------------------------------------------------------------------------- #
SCHEMA_RE = re.compile(r"\{%-?\s*schema\s*-?%\}.*?\{%-?\s*endschema\s*-?%\}", re.DOTALL)
FORM_OPEN_RE = re.compile(r"\{%-?\s*form\s+'customer'(?:\s*,\s*class:\s*'([^']*)')?\s*-?%\}")
FORM_CLOSE_RE = re.compile(r"\{%-?\s*endform\s*-?%\}")


def preprocess(src: str) -> str:
    """Quita {% schema %} y traduce {% form %} a HTML, como hace el motor real."""
    src = SCHEMA_RE.sub("", src)
    src = FORM_OPEN_RE.sub(
        lambda m: (
            '<form method="post" action="/contact#contact_form" id="contact_form" '
            f'accept-charset="UTF-8" class="{m.group(1) or ""}">'
        ),
        src,
    )
    src = FORM_CLOSE_RE.sub("</form>", src)
    src = src.replace("form.posted_successfully?", "form.posted_successfully")
    return src


def make_env() -> Environment:
    env = Environment(loader=FileSystemLoader(str(THEME / "snippets"), ext=".liquid"))
    env.filters.update(
        {
            "image_url": f_image_url,
            "img_url": f_image_url,
            "money": f_money,
            "money_without_trailing_zeros": f_money,
            "money_with_currency": f_money,
            "at_most": f_at_most,
            "at_least": f_at_least,
            "default_errors": f_default_errors,
            "payment_type_svg_tag": f_payment_type_svg_tag,
            "json": f_json,
            "handleize": f_handleize,
            "handle": f_handleize,
        }
    )
    return env


def render_section(env: Environment, key: str, conf: dict) -> str:
    stype = conf["type"]
    path = THEME / "sections" / f"{stype}.liquid"
    if not path.exists():
        raise FileNotFoundError(f"sección inexistente: {stype}")

    blocks = []
    for bid in conf.get("block_order", []):
        braw = conf.get("blocks", {}).get(bid, {})
        blocks.append(
            {
                "id": f"{key}-{bid}",
                "type": braw.get("type", ""),
                "settings": resolve_settings(braw.get("settings", {}), stype),
                "shopify_attributes": "",
            }
        )

    section = {
        "id": key,
        "settings": resolve_settings(conf.get("settings", {}), stype),
        "blocks": blocks,
        "index": 1,
        "location": "template",
    }

    template = env.from_string(preprocess(path.read_text()), globals=GLOBALS)
    return template.render(section=section)


def load_group(name: str):
    raw = (THEME / "sections" / f"{name}.json").read_text()
    raw = re.sub(r"/\*.*?\*/", "", raw, flags=re.DOTALL)
    data = json.loads(raw)
    return [(k, data["sections"][k]) for k in data["order"]]


def main() -> int:
    env = make_env()
    OUT.mkdir(exist_ok=True)

    index = json.loads((THEME / "templates" / "index.json").read_text())
    pipeline = (
        load_group("header-group")
        + [(k, index["sections"][k]) for k in index["order"]]
        + load_group("footer-group")
    )

    chunks, failures = [], []
    for key, conf in pipeline:
        try:
            html = render_section(env, key, conf)
            chunks.append(f"<!-- section: {key} ({conf['type']}) -->\n{html}")
            print(f"  ok   {key:16s} {conf['type']}")
        except Exception as exc:  # noqa: BLE001 - queremos ver todos los fallos
            failures.append((key, conf["type"], exc))
            print(f"  FAIL {key:16s} {conf['type']}: {exc}")

    page = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Vista previa · Réplica VALCA para Latinologia</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; }}
  html {{ -webkit-text-size-adjust: 100%; }}
  body {{ margin: 0; font-family: 'Manrope', system-ui, sans-serif; background: #fff; }}
  img {{ max-width: 100%; }}
  button {{ font-family: inherit; }}
</style>
</head>
<body>
{chr(10).join(chunks)}
</body>
</html>
"""
    (OUT / "preview.html").write_text(page)
    print(f"\nEscrito {OUT / 'preview.html'} ({len(page)} bytes)")

    if failures:
        print(f"\n{len(failures)} sección(es) con error:")
        for key, stype, exc in failures:
            print(f"  - {key} ({stype}): {type(exc).__name__}: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
