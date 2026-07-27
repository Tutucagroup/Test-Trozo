#!/usr/bin/env python3
"""
Massrutine — importador de catálogo desde URLs de origen hacia Shopify.

Pipeline (por producto):
  1. SCRAPE    -> extrae data de la URL de origen.
                 - Shopify (medicube.us, lummia.com.co): endpoint limpio
                   /products/<handle>.json  (título, body_html, variantes,
                   precios, imágenes, opciones).
                 - eBay / Poshmark: parseo de JSON-LD schema.org/Product.
  2. TRANSFORM -> marca propia Massrutine (según decisión del usuario):
                 - saca la marca de origen (Medicube/Anua/Lummia/…) del título
                   y del body (STRIP_BRANDS),
                 - Vendor = "Massrutine",
                 - handle limpio sin marca ni códigos,
                 - deja el body de origen en `body_raw` y marca `needs_rewrite`:
                   la copy FINAL (original, y traducida al inglés para Lummia)
                   la redacta Claude en el momento de importar — el script NO
                   inventa descripciones para no degradar calidad ni veracidad.
  3. REHOST    -> (opcional, con credenciales) sube cada imagen a TU Shopify vía
                 Admin GraphQL fileCreate ingiriéndola desde el origen, con
                 nombre nuevo:  massrutine-{handle}-{posición}{ext}
                 y captura la URL del CDN de Massrutine.
  4. OUTPUT    -> massrutine_products.json  (normalizado, para importar por API/
                 conector Shopify)  +  massrutine_import.xlsx (Matrixify, fallback).

Credenciales (solo por env, nunca hardcodeadas) — necesarias sólo para --rehost:
    SHOPIFY_SHOP          massrutine.myshopify.com
    SHOPIFY_ACCESS_TOKEN  shpat_...  (scopes write_files, read_files, write_products)

Uso:
    # Scrape + transform + genera json/xlsx (sin subir nada):
    python massrutine_import.py --out-json massrutine_products.json \
        --out-xlsx massrutine_import.xlsx

    # Además rehostea imágenes a Massrutine y completa las URLs nuevas:
    export SHOPIFY_SHOP=massrutine.myshopify.com
    export SHOPIFY_ACCESS_TOKEN=shpat_xxx
    python massrutine_import.py --rehost --out-json massrutine_products.json

Requiere: openpyxl (solo para el xlsx). El resto es stdlib.
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import ssl
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

VENDOR = "Massrutine"
NAME_PREFIX = "massrutine"
API_VERSION = "2024-10"

# Marcas / tokens de origen a remover de títulos y handles (modo marca propia).
STRIP_BRANDS = ["medicube", "anua", "lummia"]
# Tokens de tienda/tracking a limpiar de los handles.
STRIP_HANDLE_TOKENS = ["subscr", "subscription"]

# Lista de origen deduplicada (params de tracking y duplicados ya sacados).
SOURCES = [
    # Medicube (Shopify)
    "https://medicube.us/products/collagen-night-wrapping-mask",
    "https://medicube.us/products/kojic-acid-turmeric-overnight-wrapping-mask",
    "https://medicube.us/products/collagen-swirl-duo",
    "https://medicube.us/products/deep-glow-set-1",
    "https://medicube.us/products/pdrn-caffeine-collagen-eye-patch",
    "https://medicube.us/products/age-r-booster-pro",
    "https://medicube.us/products/age-r-spotless-radiance-set",
    "https://medicube.us/products/pdrn-pink-glow-home-aesthetic-full-set",
    # Lummia (Shopify, es-CO -> traducir en el rewrite)
    "https://www.lummia.com.co/products/lummimask",
    # Marketplaces (data de terceros, baja calidad — revisar)
    "https://poshmark.com/listing/10-Niacinamide-Serum-by-Anua-699e17a50015428a2bbcf780",
    "https://www.ebay.com/itm/277959643978",
]

UA = ("Mozilla/5.0 (compatible; MassrutineImporter/1.0)")


# --------------------------------------------------------------------------- #
# HTTP
# --------------------------------------------------------------------------- #
def _ctx() -> ssl.SSLContext:
    c = ssl.create_default_context()
    ca = "/root/.ccr/ca-bundle.crt"
    if os.path.exists(ca):
        try:
            c.load_verify_locations(ca)
        except Exception:
            pass
    return c


_CTX = _ctx()


def fetch(url: str, tries: int = 4, timeout: int = 30) -> bytes | None:
    for a in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA,
                                                       "Accept-Language": "en;q=0.9,es;q=0.8"})
            with urllib.request.urlopen(req, timeout=timeout, context=_CTX) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if e.code in (429, 500, 502, 503) and a < tries - 1:
                time.sleep(2 ** a); continue
            sys.stderr.write(f"  HTTP {e.code} {url}\n"); return None
        except Exception as e:  # noqa
            if a < tries - 1:
                time.sleep(2 ** a); continue
            sys.stderr.write(f"  ERR {url}: {e}\n"); return None
    return None


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def slugify(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    return re.sub(r"-{2,}", "-", s)


def strip_tags(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s or "").strip()


def price_num(v) -> str:
    if v is None:
        return ""
    s = re.sub(r"[^\d,.\-]", "", str(v))
    if "," in s and "." in s:
        s = s.replace(",", "") if s.rfind(",") < s.rfind(".") else s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    try:
        return f"{float(s):.2f}"
    except Exception:
        return ""


def debrand(text: str) -> str:
    out = text or ""
    for b in STRIP_BRANDS:
        out = re.sub(rf"\b{re.escape(b)}\b", "", out, flags=re.I)
    return re.sub(r"\s{2,}", " ", out).strip(" -–—|")


def ext_of(url: str) -> str:
    path = url.split("?", 1)[0]
    m = re.search(r"\.(jpg|jpeg|png|webp|gif)$", path, re.I)
    return "." + m.group(1).lower() if m else ".jpg"


def jsonld_products(page: str) -> list:
    out = []
    for m in re.finditer(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>',
                         page, re.I | re.S):
        try:
            data = json.loads(m.group(1).strip())
        except Exception:
            continue
        stack = [data]
        while stack:
            n = stack.pop()
            if isinstance(n, dict):
                t = n.get("@type")
                t = t if isinstance(t, list) else [t]
                if any(str(x).lower() == "product" for x in t):
                    out.append(n)
                stack.extend(n.values())
            elif isinstance(n, list):
                stack.extend(n)
    return out


# --------------------------------------------------------------------------- #
# Scrapers per source
# --------------------------------------------------------------------------- #
def scrape_shopify(url: str) -> dict | None:
    base = url.split("?", 1)[0].rstrip("/")
    raw = fetch(base + ".json")
    if not raw:
        return None
    try:
        prod = json.loads(raw).get("product", {})
    except Exception:
        return None
    if not prod:
        return None
    variants = [{
        "sku": v.get("sku", ""),
        "price": price_num(v.get("price")),
        "compare_at": price_num(v.get("compare_at_price")),
        "title": v.get("title", ""),
        "grams": v.get("grams"),
    } for v in prod.get("variants", [])]
    imgs = [i.get("src", "") for i in prod.get("images", []) if i.get("src")]
    return {
        "source": "shopify", "source_url": url,
        "source_brand": (prod.get("vendor") or "").strip(),
        "title_raw": prod.get("title", ""),
        "body_raw": prod.get("body_html", ""),
        "product_type": prod.get("product_type", ""),
        "variants": variants, "images": imgs,
        "price": variants[0]["price"] if variants else "",
        "compare_at": variants[0]["compare_at"] if variants else "",
    }


def scrape_jsonld(url: str, brand_hint: str = "") -> dict | None:
    raw = fetch(url)
    if not raw:
        return None
    page = raw.decode("utf-8", "replace")
    prods = jsonld_products(page)
    node = prods[0] if prods else {}
    offers = node.get("offers")
    if isinstance(offers, list):
        offers = offers[0] if offers else {}
    offers = offers or {}
    img = node.get("image")
    if isinstance(img, str):
        imgs = [img]
    elif isinstance(img, list):
        imgs = [i if isinstance(i, str) else i.get("url", "") for i in img]
    elif isinstance(img, dict):
        imgs = [img.get("url", "")]
    else:
        imgs = []
    brand = node.get("brand")
    if isinstance(brand, dict):
        brand = brand.get("name", "")
    return {
        "source": "marketplace", "source_url": url,
        "source_brand": (brand or brand_hint or "").strip(),
        "title_raw": html.unescape(strip_tags(node.get("name", ""))),
        "body_raw": node.get("description", ""),
        "product_type": "",
        "variants": [{"sku": node.get("sku", ""), "price": price_num(offers.get("price")),
                      "compare_at": "", "title": "Default Title", "grams": None}],
        "images": [html.unescape(u) for u in imgs if u],
        "price": price_num(offers.get("price")), "compare_at": "",
    }


def scrape(url: str) -> dict | None:
    host = urllib.parse.urlparse(url).hostname or ""
    if "medicube.us" in host or "lummia.com.co" in host:
        return scrape_shopify(url)
    if "ebay." in host:
        return scrape_jsonld(url)
    if "poshmark." in host:
        return scrape_jsonld(url, brand_hint="Anua")
    # default: try shopify json, then jsonld
    return scrape_shopify(url) or scrape_jsonld(url)


# --------------------------------------------------------------------------- #
# Transform -> Massrutine (private label)
# --------------------------------------------------------------------------- #
def transform(p: dict) -> dict:
    title = debrand(p["title_raw"]) or p["title_raw"]
    handle = slugify(title)
    for tok in STRIP_HANDLE_TOKENS:
        handle = re.sub(rf"\b{tok}\b-?", "", handle)
    handle = re.sub(r"-{2,}", "-", handle).strip("-")
    images = []
    for i, src in enumerate(dict.fromkeys(p["images"]), start=1):
        images.append({
            "position": i, "source_src": src,
            "new_filename": f"{NAME_PREFIX}-{handle}-{i}{ext_of(src)}",
            "new_src": "",  # se completa en --rehost
            "alt": title,
        })
    return {
        "handle": handle,
        "title": title,
        "vendor": VENDOR,
        "product_type": debrand(p.get("product_type", "")),
        "source_url": p["source_url"],
        "source_brand": p["source_brand"],
        "body_raw": p["body_raw"],
        "needs_rewrite": True,        # Claude redacta la copy final (orig./EN)
        "translate_to_en": "lummia.com.co" in p["source_url"],
        "price": p["price"],
        "compare_at": p["compare_at"],
        "variants": p["variants"],
        "images": images,
        "status": "draft",           # entra como borrador para revisar antes de publicar
    }


# --------------------------------------------------------------------------- #
# Rehost (opcional) — Shopify Admin GraphQL fileCreate
# --------------------------------------------------------------------------- #
def gql(shop: str, token: str, query: str, variables: dict) -> dict:
    body = json.dumps({"query": query, "variables": variables}).encode()
    req = urllib.request.Request(
        f"https://{shop}/admin/api/{API_VERSION}/graphql.json", data=body,
        headers={"Content-Type": "application/json", "X-Shopify-Access-Token": token},
        method="POST")
    with urllib.request.urlopen(req, timeout=60, context=_CTX) as r:
        data = json.loads(r.read())
    if data.get("errors"):
        raise RuntimeError(json.dumps(data["errors"]))
    return data["data"]


FILE_CREATE = """
mutation($files:[FileCreateInput!]!){ fileCreate(files:$files){
  files{ id fileStatus ... on MediaImage{ image{ url } } }
  userErrors{ field message } } }"""
NODE = """query($id:ID!){ node(id:$id){ ... on MediaImage{ fileStatus image{ url } } } }"""


def rehost_all(products: list, shop: str, token: str) -> None:
    for p in products:
        for im in p["images"]:
            if im["new_src"]:
                continue
            data = gql(shop, token, FILE_CREATE, {"files": [{
                "originalSource": im["source_src"], "filename": im["new_filename"],
                "alt": im["alt"], "contentType": "IMAGE",
                "duplicateResolutionMode": "REPLACE"}]})
            res = data["fileCreate"]
            if res["userErrors"]:
                sys.stderr.write(f"  fileCreate err {im['new_filename']}: {res['userErrors']}\n")
                continue
            fid = res["files"][0]["id"]
            for _ in range(30):
                nd = gql(shop, token, NODE, {"id": fid}).get("node") or {}
                url = (nd.get("image") or {}).get("url")
                if nd.get("fileStatus") == "READY" and url:
                    im["new_src"] = url
                    break
                time.sleep(2)
            print(f"  rehosted {im['new_filename']} -> {im['new_src'][:60]}")


# --------------------------------------------------------------------------- #
# Output
# --------------------------------------------------------------------------- #
MATRIXIFY_HEADERS = [
    "Handle", "Command", "Title", "Body HTML", "Vendor", "Type", "Tags",
    "Published", "Status", "Option1 Name", "Option1 Value", "Variant SKU",
    "Variant Price", "Variant Compare At Price", "Variant Inventory Policy",
    "Variant Inventory Tracker", "Image Src", "Image Position", "Image Alt Text",
]


def write_xlsx(path: str, products: list) -> None:
    import openpyxl
    wb = openpyxl.Workbook(); ws = wb.active; ws.title = "Products (Matrixify)"
    ws.append(MATRIXIFY_HEADERS)
    for p in products:
        v0 = p["variants"][0] if p["variants"] else {}
        imgs = p["images"]
        first = imgs[0] if imgs else {}
        body = p["body_raw"] if not p["needs_rewrite"] else \
            "<!-- PENDIENTE: descripción original redactada por Claude -->"
        ws.append([
            p["handle"], "MERGE", p["title"], body, p["vendor"], p["product_type"], "",
            "FALSE", p["status"], "Title", "Default Title", v0.get("sku", ""),
            p["price"], p["compare_at"], "deny", "shopify",
            first.get("new_src") or first.get("source_src", ""),
            first.get("position", 1) if imgs else "", first.get("alt", ""),
        ])
        for im in imgs[1:]:
            row = [""] * len(MATRIXIFY_HEADERS)
            row[0] = p["handle"]
            row[16] = im.get("new_src") or im["source_src"]
            row[17] = im["position"]; row[18] = im["alt"]
            ws.append(row)
    wb.save(path)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out-json", default="massrutine_products.json")
    ap.add_argument("--out-xlsx", default="massrutine_import.xlsx")
    ap.add_argument("--rehost", action="store_true")
    ap.add_argument("--delay", type=float, default=1.0)
    args = ap.parse_args()

    products = []
    for url in SOURCES:
        raw = scrape(url)
        if not raw:
            sys.stderr.write(f"SKIP (no data): {url}\n"); continue
        p = transform(raw)
        products.append(p)
        print(f"OK  {p['title'][:55]:55}  imgs={len(p['images'])}")
        time.sleep(args.delay)

    if args.rehost:
        shop = os.environ.get("SHOPIFY_SHOP", "").strip()
        token = os.environ.get("SHOPIFY_ACCESS_TOKEN", "").strip()
        if not (shop and token):
            sys.stderr.write("ERROR: --rehost necesita SHOPIFY_SHOP y SHOPIFY_ACCESS_TOKEN.\n")
            return 2
        rehost_all(products, shop, token)

    json.dump(products, open(args.out_json, "w"), ensure_ascii=False, indent=1)
    write_xlsx(args.out_xlsx, products)
    print(f"\n{len(products)} productos -> {args.out_json} / {args.out_xlsx}")
    print("NOTA: las descripciones finales (originales, y traducción EN de Lummia) "
          "las redacta Claude al importar; el JSON trae body_raw + needs_rewrite.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
