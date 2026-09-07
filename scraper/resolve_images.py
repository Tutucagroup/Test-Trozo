"""
Resolver de imágenes (una sola pasada) -> data/images_final.json

Para cada imagen scrapeada (URL con sufijo _0_l.jpg que emite parse.py):
  1. Busca la mayor variante ACCESIBLE probando los 3 regímenes del CDN de
     batitienda: extensión .jpg/.jpeg/.png y sin extensión; tamaños l/m/t.
     (_f/_s dan 403; algunas imágenes sólo existen en cierto tamaño/extensión.)
  2. Mira el Content-Type de la variante elegida:
       - image/*          -> se usa la URL directa (Shopify la acepta)
       - octet-stream/otro -> se envuelve por images.weserv.nl, que la re-sirve
                              con Content-Type de imagen correcto (Shopify lo exige).
  3. Si ninguna variante responde 200 -> None (imagen muerta, se descarta).

Salida: { url_scrapeada: url_final_para_shopify | None }.  Resumible.
"""
import os
import re
import json
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRODUCTS = os.path.join(BASE, "data", "products.jsonl")
OUT = os.path.join(BASE, "data", "images_final.json")
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"

# candidatos de mayor a menor calidad, cubriendo los 3 regímenes de almacenamiento
CANDIDATE_SUFFIXES = [
    "_l.jpg", "_l.jpeg", "_l.png", "_l",
    "_m.jpg", "_m.jpeg", "_m.png", "_m",
    "_t.jpg", "_t.jpeg", "_t.png", "_t",
]


def variant(url, suffix):
    return re.sub(r"_0_[a-z](?:\.[a-z]+)?$", "_0" + suffix, url)


def weserv(url):
    return "https://images.weserv.nl/?url=ssl:" + re.sub(r"^https?://", "", url)


def probe(url):
    """GET 1 byte. Devuelve (status_ok, content_type) o (None, None) si transitorio."""
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Range": "bytes=0-0"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            ct = (r.headers.get("Content-Type") or "").split(";")[0].strip().lower()
            return (r.status in (200, 206), ct)
    except urllib.error.HTTPError as e:
        if e.code in (200, 206, 416):
            ct = (e.headers.get("Content-Type") or "").split(";")[0].strip().lower()
            return (True, ct)
        return (False, None)
    except Exception:
        return (None, None)


def resolve(scraped_url):
    for suf in CANDIDATE_SUFFIXES:
        v = variant(scraped_url, suf)
        ok, ct = probe(v)
        if ok is None:
            time.sleep(1.0)
            ok, ct = probe(v)
        if ok is True:
            # primera variante accesible (la de mayor calidad disponible)
            if ct and ct.startswith("image/"):
                return v
            return weserv(v)  # octet-stream u otro -> proxy corrige el content-type
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

    final = {}
    if os.path.exists(OUT):
        final = json.load(open(OUT, encoding="utf-8"))
    todo = [u for u in urls if u not in final]
    print(f"por resolver: {len(todo)}", flush=True)

    t0 = time.time()
    with ThreadPoolExecutor(max_workers=12) as ex:
        futs = {ex.submit(resolve, u): u for u in todo}
        n = 0
        for fut in as_completed(futs):
            final[futs[fut]] = fut.result()
            n += 1
            if n % 500 == 0 or n == len(todo):
                json.dump(final, open(OUT, "w", encoding="utf-8"))
                el = time.time() - t0
                dead = sum(1 for v in final.values() if not v)
                wsv = sum(1 for v in final.values() if v and "weserv" in v)
                print(f"{n}/{len(todo)} dead={dead} weserv={wsv} {n/el:.1f}/s "
                      f"eta={(len(todo)-n)/(n/el)/60:.1f}min", flush=True)
    json.dump(final, open(OUT, "w", encoding="utf-8"))
    dead = sum(1 for v in final.values() if not v)
    wsv = sum(1 for v in final.values() if v and "weserv" in v)
    print(f"DONE total={len(final)} directas={len(final)-dead-wsv} weserv={wsv} dead={dead}", flush=True)


if __name__ == "__main__":
    main()
