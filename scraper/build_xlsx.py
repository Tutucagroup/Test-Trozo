"""
Genera el xlsx Matrixify de productos a partir de:
- data/products.jsonl (scrape)
- data/categories.json (path completo por PC-id)
- árbol de tags del usuario (TreeMatcher)

Parte del template original (conserva hojas Instrucciones y Tags por categoría),
limpia las filas de ejemplo y escribe todos los productos.
"""
import os
import re
import sys
import json
import openpyxl

# caracteres de control no permitidos en XML/openpyxl
_ILLEGAL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def sanitize(v):
    if isinstance(v, str):
        return _ILLEGAL.sub("", v)
    return v

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "scraper"))
from tree import TreeMatcher

PRODUCTS = os.path.join(BASE, "data", "products.jsonl")
CATEGORIES = os.path.join(BASE, "data", "categories.json")
# mapa único: url scrapeada -> url final para Shopify (directa, weserv, o None si muerta)
IMAGES_FINAL = os.path.join(BASE, "data", "images_final.json")
TEMPLATE = os.path.join(BASE, "plantilla_nuevo_producto.xlsx")
OUT = os.path.join(BASE, "chester_productos_matrixify.xlsx")

SHEET = "Products (Matrixify)"


def load_products():
    """Dedup por WS (id único). Handles se hacen únicos: cuando un slug se repite
    entre productos distintos (variantes de color/talle que el sitio publica por
    separado), se le agrega el número de WS para no pisarse con MERGE en Shopify."""
    prods, seen_ws = [], set()
    for line in open(PRODUCTS, encoding="utf-8"):
        try:
            rec = json.loads(line)
        except Exception:
            continue
        if not rec.get("ok"):
            continue
        ws = rec.get("ws_code")
        if not ws or ws in seen_ws:
            continue
        seen_ws.add(ws)
        prods.append(rec)

    # contar slugs para detectar colisiones
    from collections import Counter
    counts = Counter(p.get("handle") for p in prods)
    used = set()
    for p in prods:
        h = p.get("handle") or (p.get("ws_code") or "").lower()
        if counts[h] > 1 or h in used:
            num = re.sub(r"\D", "", p.get("ws_code") or "")
            h = f"{h}-{num}"
        used.add(h)
        p["handle"] = h
    return prods


def col_index(ws):
    return {ws.cell(1, c).value: c for c in range(1, ws.max_column + 1)}


def main():
    cats = json.load(open(CATEGORIES, encoding="utf-8"))
    # mapa único: url scrapeada -> url final para Shopify (o None si muerta)
    img_final = json.load(open(IMAGES_FINAL, encoding="utf-8")) if os.path.exists(IMAGES_FINAL) else {}
    tm = TreeMatcher()
    prods = load_products()
    prods.sort(key=lambda r: (r.get("vendor") or "", r.get("title") or ""))
    print(f"productos: {len(prods)}")

    wb = openpyxl.load_workbook(TEMPLATE)
    ws = wb[SHEET]
    ci = col_index(ws)
    # limpiar filas de ejemplo (2..max)
    if ws.max_row > 1:
        ws.delete_rows(2, ws.max_row - 1)

    def put(row, colname, val):
        if colname in ci and val is not None and val != "":
            ws.cell(row, ci[colname], sanitize(val))

    r = 2
    stats = {"con_tags": 0, "sin_tags": 0, "con_oferta": 0, "sin_stock": 0, "imgs": 0}
    for p in prods:
        title = p.get("title") or ""
        vendor = p.get("vendor") or ""
        # resolver tags/type via path de categoría
        node = None
        cat = cats.get(str(p.get("cat_pc")) or "")
        if cat and cat.get("path"):
            node = tm.match_path(cat["path"])
        tags = node["tags"] if node else None
        cat_name = p.get("category_name")
        if cat_name and cat_name.strip().lower() == "sin categoría":
            cat_name = None  # el sitio no lo categorizó -> no forzar Type
        ptype = node["type"] if node else cat_name
        if tags:
            stats["con_tags"] += 1
        else:
            stats["sin_tags"] += 1

        stock = p.get("stock")
        if stock == 0:
            stats["sin_stock"] += 1
        if p.get("compare_at"):
            stats["con_oferta"] += 1

        put(r, "Handle", p.get("handle"))
        put(r, "Command", "MERGE")
        put(r, "Title", title)
        put(r, "Body HTML", p.get("body_html"))
        put(r, "Vendor", vendor)
        put(r, "Type", ptype)
        put(r, "Tags", tags)
        put(r, "Published", "TRUE")
        put(r, "Status", "active")
        put(r, "Option1 Name", "Title")
        put(r, "Option1 Value", "Default Title")
        put(r, "Variant SKU", p.get("ws_code"))
        put(r, "Variant Price", p.get("price"))
        put(r, "Variant Compare At Price", p.get("compare_at"))
        put(r, "Variant Inventory Qty", stock if stock is not None else 0)
        put(r, "Variant Inventory Policy", "deny")
        put(r, "Variant Inventory Tracker", "shopify")
        put(r, "Variant Requires Shipping", "TRUE")
        put(r, "Variant Taxable", "TRUE")
        # mapear cada imagen scrapeada a su URL final (directa/weserv); descartar muertas
        imgs = []
        for im in (p.get("images") or []):
            final_url = img_final.get(im, im)
            if final_url:
                imgs.append(final_url)
        if imgs:
            put(r, "Image Src", imgs[0])
            put(r, "Image Position", 1)
            put(r, "Image Alt Text", title)
        put(r, "SEO Title", f"{title} | Farmacias Chester" if title else None)
        put(r, "SEO Description",
            f"Comprá {title} online en Farmacias Chester. Envío a todo el país y cuotas sin interés."
            if title else None)
        put(r, "Metafield: custom.precio_sin_impuestos_nac [number_integer]",
            p.get("precio_sin_imp_centavos"))
        r += 1
        stats["imgs"] += len(imgs)

        # imágenes adicionales: filas nuevas sólo con Handle + Image Src + Position
        for i, img in enumerate(imgs[1:], start=2):
            put(r, "Handle", p.get("handle"))
            put(r, "Image Src", img)
            put(r, "Image Position", i)
            put(r, "Image Alt Text", f"{title} #{i}" if title else None)
            r += 1

    wb.save(OUT)
    print("guardado:", OUT)
    print("filas totales:", r - 1)
    print("stats:", stats)


if __name__ == "__main__":
    main()
