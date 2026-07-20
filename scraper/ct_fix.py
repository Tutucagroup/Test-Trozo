"""
Shopify rechaza imágenes servidas como application/octet-stream
("unsupported file type ... is not a recognized format"), aunque los bytes
sean un JPEG/PNG válido.

Este script chequea el Content-Type real de cada imagen resuelta:
  - image/*            -> se deja la URL directa
  - octet-stream/otro  -> se envuelve por images.weserv.nl, que la re-sirve
                          con Content-Type de imagen correcto.

Salida: data/images_final.json  { url_resuelta: url_final_para_shopify }
Resumible.
"""
import os
import re
import json
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESOLVED = os.path.join(BASE, "data", "images_resolved.json")
OUT = os.path.join(BASE, "data", "images_final.json")
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"


def weserv(url):
    # weserv acepta la fuente sin esquema con prefijo ssl: para https
    src = re.sub(r"^https?://", "", url)
    return "https://images.weserv.nl/?url=ssl:" + src


def content_type(url):
    """Devuelve el Content-Type (o None si error transitorio)."""
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Range": "bytes=0-0"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return (r.headers.get("Content-Type") or "").split(";")[0].strip().lower()
    except urllib.error.HTTPError as e:
        return "ERR%d" % e.code
    except Exception:
        return None


def decide(url):
    ct = content_type(url)
    if ct is None:
        time.sleep(1.0)
        ct = content_type(url)
    if ct and ct.startswith("image/"):
        return url  # directa, Shopify la acepta
    # octet-stream u otro -> proxy que corrige el content-type
    return weserv(url)


def main():
    resolved = json.load(open(RESOLVED, encoding="utf-8"))
    urls = sorted(set(v for v in resolved.values() if v))
    print(f"imágenes resueltas: {len(urls)}", flush=True)

    final = {}
    if os.path.exists(OUT):
        final = json.load(open(OUT, encoding="utf-8"))
    todo = [u for u in urls if u not in final]
    print(f"por chequear: {len(todo)}", flush=True)

    t0 = time.time()
    with ThreadPoolExecutor(max_workers=12) as ex:
        futs = {ex.submit(decide, u): u for u in todo}
        n = 0
        for fut in as_completed(futs):
            u = futs[fut]
            final[u] = fut.result()
            n += 1
            if n % 500 == 0 or n == len(todo):
                json.dump(final, open(OUT, "w", encoding="utf-8"))
                el = time.time() - t0
                wrapped = sum(1 for k, v in final.items() if v != k)
                print(f"{n}/{len(todo)} wrapped={wrapped} {n/el:.1f}/s "
                      f"eta={(len(todo)-n)/(n/el)/60:.1f}min", flush=True)
    json.dump(final, open(OUT, "w", encoding="utf-8"))
    wrapped = sum(1 for k, v in final.items() if v != k)
    print(f"DONE total={len(final)} directas={len(final)-wrapped} wrapped(weserv)={wrapped}", flush=True)


if __name__ == "__main__":
    main()
