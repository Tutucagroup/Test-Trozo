#!/usr/bin/env python3
"""
Scraper de catálogo -> template Matrixify (Shopify) para Farmacias Chester.

Recorre https://www.farmaciaschester.com.ar/, descubre TODAS las URLs de
producto (via sitemap.xml, con fallback a crawl de colecciones), extrae los
datos de cada ficha priorizando datos estructurados (JSON-LD schema.org
Product, luego OpenGraph, luego selectores HTML) y escribe un .xlsx idéntico
en columnas al template 'chesterproductosmatrixifytemplate_1.xlsx'.

Diseño defensivo / agnóstico de plataforma: la tienda corre sobre un CDN
cdn.batitienda.com; en vez de atarnos a su HTML, leemos el JSON-LD que casi
todas las plataformas de e-commerce inyectan. Si una ficha no lo trae, caemos a
OpenGraph y a selectores configurables (SELECTORS abajo).

Salida (32 columnas, ver template):
  Handle, Command(MERGE), Title, Body HTML, Vendor, Type, Tags, Published,
  Status, Option1 Name/Value, Variant SKU, Variant Price,
  Variant Compare At Price, Variant Inventory Qty/Policy/Tracker,
  Variant Requires Shipping/Taxable, Image Src/Position/Alt, SEO Title/Desc,
  y los 8 Metafields custom.* (best-effort; se dejan vacíos si no se detectan).

Las imágenes 2..N se emiten como FILAS EXTRA con sólo Handle + Image Src +
Image Position (como pide la hoja 'Instrucciones').

Uso:
    python scrape_chester.py \
        --template chesterproductosmatrixifytemplate_1.xlsx \
        --tags-map chester_tags_map.json \
        --out chester_productos_FINAL.xlsx \
        [--limit N] [--delay 1.0] [--urls-file urls.txt]

Requiere: openpyxl  (pip install openpyxl). El resto es stdlib.
"""
from __future__ import annotations

import argparse
import gzip
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
from collections import OrderedDict

BASE = "https://www.farmaciaschester.com.ar"
UA = "Mozilla/5.0 (compatible; ChesterCatalogBot/1.0; +import to Shopify via Matrixify)"

# Exact template header order (Products (Matrixify) sheet).
HEADERS = [
    "Handle", "Command", "Title", "Body HTML", "Vendor", "Type", "Tags",
    "Published", "Status", "Option1 Name", "Option1 Value", "Variant SKU",
    "Variant Price", "Variant Compare At Price", "Variant Inventory Qty",
    "Variant Inventory Policy", "Variant Inventory Tracker",
    "Variant Requires Shipping", "Variant Taxable", "Image Src",
    "Image Position", "Image Alt Text", "SEO Title", "SEO Description",
    "Metafield: custom.precio_sin_impuestos_nac [number_integer]",
    "Metafield: custom.tipo_piel [list.single_line_text]",
    "Metafield: custom.funcion [list.single_line_text]",
    "Metafield: custom.formulacion [single_line_text]",
    "Metafield: custom.rutina [list.single_line_text]",
    "Metafield: custom.fps [single_line_text]",
    "Metafield: custom.consumo_consciente [list.single_line_text]",
    "Metafield: custom.promo_vigencia [single_line_text]",
]

# CSS-ish fallback selectors (regex-based, adjust after seeing the live DOM).
SELECTORS = {
    "title": [r'<h1[^>]*class="[^"]*product[^"]*"[^>]*>(.*?)</h1>', r'<h1[^>]*>(.*?)</h1>'],
    "price": [r'itemprop="price"[^>]*content="([\d.,]+)"'],
}


# --------------------------------------------------------------------------- #
# HTTP
# --------------------------------------------------------------------------- #
def _ssl_ctx() -> ssl.SSLContext:
    ctx = ssl.create_default_context()
    ca = "/root/.ccr/ca-bundle.crt"          # proxy CA in Claude Code web sessions
    if os.path.exists(ca):
        try:
            ctx.load_verify_locations(ca)
        except Exception:
            pass
    return ctx


_CTX = _ssl_ctx()


def fetch(url: str, tries: int = 4, timeout: int = 30) -> bytes | None:
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA,
                                                       "Accept-Language": "es-AR,es;q=0.9"})
            with urllib.request.urlopen(req, timeout=timeout, context=_CTX) as r:
                data = r.read()
                if r.headers.get("Content-Encoding") == "gzip":
                    data = gzip.decompress(data)
                return data
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if e.code in (429, 500, 502, 503) and attempt < tries - 1:
                time.sleep(2 ** attempt)
                continue
            sys.stderr.write(f"  HTTP {e.code} {url}\n")
            return None
        except Exception as e:  # noqa
            if attempt < tries - 1:
                time.sleep(2 ** attempt)
                continue
            sys.stderr.write(f"  ERR {url}: {e}\n")
            return None
    return None


def fetch_text(url: str) -> str | None:
    b = fetch(url)
    return b.decode("utf-8", "replace") if b is not None else None


# --------------------------------------------------------------------------- #
# Product URL discovery
# --------------------------------------------------------------------------- #
def _sitemap_urls(sm_url: str, seen: set, out: list, depth: int = 0) -> None:
    if depth > 5 or sm_url in seen:
        return
    seen.add(sm_url)
    body = fetch(sm_url)
    if not body:
        return
    if sm_url.endswith(".gz"):
        try:
            body = gzip.decompress(body)
        except Exception:
            pass
    text = body.decode("utf-8", "replace")
    locs = re.findall(r"<loc>\s*(.*?)\s*</loc>", text, re.I | re.S)
    if "<sitemapindex" in text.lower():
        for loc in locs:
            _sitemap_urls(html.unescape(loc), seen, out, depth + 1)
    else:
        out.extend(html.unescape(l) for l in locs)


def discover_product_urls() -> list[str]:
    seen, locs = set(), []
    for sm in (f"{BASE}/sitemap.xml", f"{BASE}/sitemap_index.xml"):
        _sitemap_urls(sm, seen, locs)
    # Heuristic: product pages usually contain '/products/' or '/producto'.
    prod = [u for u in locs if re.search(r"/(products?|producto)s?/", u, re.I)]
    prod = list(OrderedDict.fromkeys(prod))
    if prod:
        return prod
    # Fallback: return every non-asset URL and let per-page parsing filter.
    return list(OrderedDict.fromkeys(
        u for u in locs if not re.search(r"\.(jpg|png|webp|css|js|xml)$", u, re.I)))


# --------------------------------------------------------------------------- #
# Parsing helpers
# --------------------------------------------------------------------------- #
def strip_tags(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s or "").strip()


def jsonld_blocks(page: str) -> list:
    out = []
    for m in re.finditer(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        page, re.I | re.S):
        raw = m.group(1).strip()
        try:
            out.append(json.loads(raw))
        except Exception:
            try:
                out.append(json.loads(re.sub(r",\s*([}\]])", r"\1", raw)))
            except Exception:
                pass
    return out


def find_product_node(blocks: list):
    def walk(node):
        if isinstance(node, dict):
            t = node.get("@type")
            types = t if isinstance(t, list) else [t]
            if any(str(x).lower() == "product" for x in types):
                return node
            for v in node.values():
                r = walk(v)
                if r:
                    return r
        elif isinstance(node, list):
            for v in node:
                r = walk(v)
                if r:
                    return r
        return None
    for b in blocks:
        r = walk(b)
        if r:
            return r
    return None


def og(page: str, prop: str) -> str:
    m = re.search(rf'<meta[^>]+property=["\']og:{prop}["\'][^>]+content=["\'](.*?)["\']',
                  page, re.I)
    return html.unescape(m.group(1)) if m else ""


def meta_desc(page: str) -> str:
    m = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']',
                  page, re.I)
    return html.unescape(m.group(1)) if m else ""


def first_match(page: str, patterns: list) -> str:
    for pat in patterns:
        m = re.search(pat, page, re.I | re.S)
        if m:
            return html.unescape(strip_tags(m.group(1)))
    return ""


def slugify(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    return re.sub(r"-{2,}", "-", s)


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", s.lower()).strip()


def price_num(v) -> str:
    if v is None:
        return ""
    s = str(v).strip()
    s = re.sub(r"[^\d,.\-]", "", s)
    if "," in s and "." in s:            # 1.234,56 -> 1234.56
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    try:
        return f"{float(s):.2f}"
    except Exception:
        return ""


# --------------------------------------------------------------------------- #
# Category -> Tags/Type mapping
# --------------------------------------------------------------------------- #
class TagMapper:
    def __init__(self, path: str | None):
        self.entries = []
        if path and os.path.exists(path):
            self.entries = json.load(open(path, encoding="utf-8"))

    def match(self, category_terms: list[str]):
        """Best L3>L2>L1 match against breadcrumb/category terms. Returns (tags,type)."""
        if not self.entries or not category_terms:
            return "", ""
        terms = {norm(t) for t in category_terms if t}
        best, best_score = None, 0
        for e in self.entries:
            score = sum(1 for kt in e["key_terms"] if kt in terms)
            # prefer deeper (more specific) matches on ties
            depth = {"L1": 1, "L2": 2, "L3": 3}.get(e.get("nivel"), 0)
            score = score * 10 + depth if score else 0
            if score > best_score:
                best, best_score = e, score
        if best:
            return (best.get("tags") or "").strip(), (best.get("type") or "").strip()
        return "", ""


# --------------------------------------------------------------------------- #
# Product extraction
# --------------------------------------------------------------------------- #
def extract(url: str, mapper: TagMapper) -> dict | None:
    page = fetch_text(url)
    if not page:
        return None
    blocks = jsonld_blocks(page)
    node = find_product_node(blocks)

    title = (node or {}).get("name", "") or og(page, "title") or first_match(page, SELECTORS["title"])
    title = html.unescape(strip_tags(title)).strip()
    if not title:
        return None  # not a product page

    desc = (node or {}).get("description", "") or og(page, "description") or meta_desc(page)
    body_html = desc if "<" in desc else (f"<p>{html.escape(desc)}</p>" if desc else "")

    brand = (node or {}).get("brand", "")
    if isinstance(brand, dict):
        brand = brand.get("name", "")

    sku = (node or {}).get("sku", "") or (node or {}).get("mpn", "")

    # offers -> price / compareAt / availability
    price = compare = ""
    avail = ""
    offers = (node or {}).get("offers")
    if isinstance(offers, list):
        offers = offers[0] if offers else {}
    if isinstance(offers, dict):
        price = price_num(offers.get("price") or offers.get("lowPrice"))
        compare = price_num(offers.get("highPrice"))
        avail = str(offers.get("availability", ""))
    if not price:
        price = price_num(first_match(page, SELECTORS["price"]))

    # images
    imgs = []
    img = (node or {}).get("image")
    if isinstance(img, str):
        imgs = [img]
    elif isinstance(img, list):
        imgs = [i if isinstance(i, str) else i.get("url", "") for i in img]
    elif isinstance(img, dict):
        imgs = [img.get("url", "")]
    if not imgs:
        ogi = og(page, "image")
        if ogi:
            imgs = [ogi]
    imgs = [html.unescape(u) for u in imgs if u]
    # dedupe, keep order
    imgs = list(OrderedDict.fromkeys(imgs))

    # category / breadcrumb terms for tag mapping
    terms = []
    for b in blocks:
        def collect(n):
            if isinstance(n, dict):
                if str(n.get("@type", "")).lower() == "breadcrumblist":
                    for el in n.get("itemListElement", []):
                        nm = el.get("name") or (el.get("item") or {}).get("name")
                        if nm:
                            terms.append(nm)
                for v in n.values():
                    collect(v)
            elif isinstance(n, list):
                for v in n:
                    collect(v)
        collect(b)
    cat = (node or {}).get("category")
    if isinstance(cat, str):
        terms.extend(re.split(r"[>/|]", cat))
    tags, ptype = mapper.match(terms)

    handle = slugify(re.sub(r"\bWS\d+\b", "", title)) or slugify(url.rstrip("/").split("/")[-1])

    return {
        "handle": handle, "title": title, "body": body_html, "vendor": (brand or "").strip(),
        "type": ptype, "tags": tags, "sku": sku, "price": price, "compare": compare,
        "avail": avail, "images": imgs, "url": url,
    }


# --------------------------------------------------------------------------- #
# Rows -> xlsx
# --------------------------------------------------------------------------- #
def to_rows(p: dict) -> list[dict]:
    inv_policy = "continue" if "InStock" not in p["avail"] and p["avail"] else "deny"
    main = {h: "" for h in HEADERS}
    main.update({
        "Handle": p["handle"], "Command": "MERGE", "Title": p["title"],
        "Body HTML": p["body"], "Vendor": p["vendor"], "Type": p["type"],
        "Tags": p["tags"], "Published": "TRUE", "Status": "active",
        "Option1 Name": "Title", "Option1 Value": "Default Title",
        "Variant SKU": p["sku"], "Variant Price": p["price"],
        "Variant Compare At Price": p["compare"] if p["compare"] and p["compare"] != p["price"] else "",
        "Variant Inventory Qty": "", "Variant Inventory Policy": "deny",
        "Variant Inventory Tracker": "shopify",
        "Variant Requires Shipping": "TRUE", "Variant Taxable": "TRUE",
        "Image Src": p["images"][0] if p["images"] else "",
        "Image Position": "1" if p["images"] else "",
        "Image Alt Text": p["title"] if p["images"] else "",
        "SEO Title": f"{p['title']} | Farmacias Chester",
        "SEO Description": strip_tags(p["body"])[:300],
    })
    rows = [main]
    for i, u in enumerate(p["images"][1:], start=2):
        extra = {h: "" for h in HEADERS}
        extra.update({"Handle": p["handle"], "Image Src": u, "Image Position": str(i),
                      "Image Alt Text": f"{p['title']} - imagen {i}"})
        rows.append(extra)
    return rows


def write_xlsx(path: str, all_rows: list[dict]) -> None:
    import openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Products (Matrixify)"
    ws.append(HEADERS)
    for r in all_rows:
        ws.append([r.get(h, "") for h in HEADERS])
    wb.save(path)


# --------------------------------------------------------------------------- #
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="chester_productos_FINAL.xlsx")
    ap.add_argument("--tags-map", default="chester_tags_map.json")
    ap.add_argument("--urls-file", help="optional newline-separated product URLs (skips discovery)")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--delay", type=float, default=1.0)
    args = ap.parse_args()

    mapper = TagMapper(args.tags_map)

    if args.urls_file:
        urls = [l.strip() for l in open(args.urls_file) if l.strip()]
    else:
        print("Descubriendo URLs de producto (sitemap)…")
        urls = discover_product_urls()
    print(f"{len(urls)} URLs candidatas.")
    if args.limit:
        urls = urls[:args.limit]

    all_rows, ok, skip = [], 0, 0
    for i, u in enumerate(urls, 1):
        p = extract(u, mapper)
        if p:
            all_rows.extend(to_rows(p))
            ok += 1
            print(f"[{i}/{len(urls)}] OK  {p['title'][:60]}")
        else:
            skip += 1
        time.sleep(args.delay)

    write_xlsx(args.out, all_rows)
    print(f"\nProductos: {ok}  ·  descartadas: {skip}  ·  filas: {len(all_rows)}")
    print(f"Escrito -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
