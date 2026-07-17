"""
Resuelve cada imagen al tamaño más grande DISPONIBLE en el CDN (_l -> _m),
porque _f/_s devuelven 403 (no accesibles -> Shopify no puede descargarlas).
Descarta imágenes muertas (403 en todos los tamaños).

Salida: data/images_resolved.json  { url_original(_f): url_ok | null }
Resumible.
"""
import os
import re
import json
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRODUCTS = os.path.join(BASE, "data", "products.jsonl")
OUT = os.path.join(BASE, "data", "images_resolved.json")
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
# El CDN tiene tres regímenes de almacenamiento por imagen:
#   - jpg con extensión: _l.jpg / _m.jpg            -> image/jpeg
#   - png con extensión: _l.png / _m.png            -> image/png
#   - sin extensión:     _m / _t (no hay _l)        -> octet-stream
# Candidatos de mayor a menor calidad, cubriendo los tres.
CANDIDATE_SUFFIXES = [
    "_l.jpg", "_l.jpeg", "_l.png", "_l",
    "_m.jpg", "_m.jpeg", "_m.png", "_m",
    "_t.jpg", "_t.jpeg", "_t.png", "_t",
]


def variant(url, suffix):
    return re.sub(r"_0_[a-z](?:\.jpg)?$", f"_0{suffix}", url)


def available(url):
    """GET con Range 1 byte; True si 200/206, False si 403/404, None si transitorio."""
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Range": "bytes=0-0"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.status in (200, 206)
    except urllib.error.HTTPError as e:
        if e.code in (200, 206, 416):
            return True
        return False
    except Exception:
        return None


def resolve(url):
    for suf in CANDIDATE_SUFFIXES:
        v = variant(url, suf)
        ok = available(v)
        if ok is None:
            time.sleep(1.0)
            ok = available(v)
        if ok is True:
            return v
    return None


def main():
    urls = set()
    for line in open(PRODUCTS, encoding="utf-8"):
        try:
            rec = json.loads(line)
        except Exception:
            continue
        for im in rec.get("images") or []:
            urls.add(im)
    urls = sorted(urls)
    print(f"imágenes únicas: {len(urls)}", flush=True)

    resolved = {}
    if os.path.exists(OUT):
        resolved = json.load(open(OUT, encoding="utf-8"))
    # reprocesar las no resueltas y las marcadas como muertas (null)
    todo = [u for u in urls if not resolved.get(u)]
    print(f"por resolver (incluye reintentos de muertas): {len(todo)}", flush=True)

    t0 = time.time()
    with ThreadPoolExecutor(max_workers=12) as ex:
        futs = {ex.submit(resolve, u): u for u in todo}
        n = 0
        for fut in as_completed(futs):
            u = futs[fut]
            resolved[u] = fut.result()
            n += 1
            if n % 500 == 0 or n == len(todo):
                json.dump(resolved, open(OUT, "w", encoding="utf-8"))
                el = time.time() - t0
                dead = sum(1 for v in resolved.values() if not v)
                print(f"{n}/{len(todo)} dead={dead} {n/el:.1f}/s eta={(len(todo)-n)/(n/el)/60:.1f}min", flush=True)
    json.dump(resolved, open(OUT, "w", encoding="utf-8"))
    dead = sum(1 for v in resolved.values() if not v)
    up = sum(1 for v in resolved.values() if v and v.endswith("_l.jpg"))
    print(f"DONE total={len(resolved)} _l={up} dead={dead}", flush=True)


if __name__ == "__main__":
    main()
