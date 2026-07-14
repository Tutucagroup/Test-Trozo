"""
Construye el catálogo de categorías: PC-id -> path completo (top-down).
Toma los (cat_pc, cat_slug) únicos que aparecen en data/products.jsonl,
descarga cada página de categoría una vez y lee el path del <title>.
"""
import os
import re
import sys
import json
import time
import html as H
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRODUCTS = os.path.join(BASE, "data", "products.jsonl")
OUT = os.path.join(BASE, "data", "categories.json")
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"


def fetch_path(pc, slug, tries=3):
    url = f"https://www.farmaciaschester.com.ar/shop/{slug}-PC{pc}"
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=45) as r:
                # sólo necesitamos el <head>; leemos un chunk
                data = r.read(60000).decode("utf-8", "replace")
            m = re.search(r"<title>(.*?)</title>", data, re.S)
            if not m:
                return None
            t = H.unescape(m.group(1)).strip()
            t = re.sub(r"\s*-\s*Farmacias Chester\s*$", "", t)
            parts = [p.strip() for p in t.split(",") if p.strip()]
            return list(reversed(parts))  # top-down: [dept, cat, subcat, ...]
        except Exception as e:
            last = e
            time.sleep(1.5 * (i + 1))
    print("caterr", pc, slug, last, flush=True)
    return None


def main():
    pairs = {}
    for line in open(PRODUCTS, encoding="utf-8"):
        try:
            rec = json.loads(line)
        except Exception:
            continue
        pc = rec.get("cat_pc")
        if pc and pc not in pairs:
            pairs[pc] = rec.get("cat_slug") or "c"
    print(f"unique categories: {len(pairs)}", flush=True)

    cat = {}
    if os.path.exists(OUT):
        cat = json.load(open(OUT, encoding="utf-8"))
    todo = {pc: s for pc, s in pairs.items() if pc not in cat}
    print(f"to fetch: {len(todo)}", flush=True)

    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(fetch_path, pc, slug): (pc, slug) for pc, slug in todo.items()}
        n = 0
        for fut in as_completed(futs):
            pc, slug = futs[fut]
            path = fut.result()
            cat[pc] = {"slug": slug, "path": path}
            n += 1
            if n % 25 == 0 or n == len(todo):
                print(f"{n}/{len(todo)}", flush=True)
    json.dump(cat, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    miss = [pc for pc, v in cat.items() if not v.get("path")]
    print(f"saved {len(cat)} categories; without path: {len(miss)}", flush=True)


if __name__ == "__main__":
    main()
