"""
Scraper principal de productos de Farmacias Chester.
- Lee scraper/product_urls.txt
- Descarga cada página, extrae con parse_product
- Escribe data/products.jsonl (append, resumible)
- Concurrente y con reintentos
"""
import os
import sys
import json
import time
import threading
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(__file__))
from parse import parse_product

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URLS = os.path.join(BASE, "scraper", "product_urls.txt")
OUT = os.path.join(BASE, "data", "products.jsonl")
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"

lock = threading.Lock()
counter = {"ok": 0, "err": 0}


def fetch(url, tries=3):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "es-AR,es"})
            with urllib.request.urlopen(req, timeout=45) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:
            last = e
            time.sleep(1.5 * (i + 1))
    raise last


def worker(url):
    try:
        html = fetch(url)
        d = parse_product(url, html)
        d["ok"] = bool(d.get("title") and d.get("price") is not None)
        return d
    except Exception as e:
        return {"url": url, "ok": False, "error": str(e)}


def main():
    urls = [u.strip() for u in open(URLS) if u.strip()]
    done = set()
    if os.path.exists(OUT):
        for line in open(OUT, encoding="utf-8"):
            try:
                rec = json.loads(line)
                if rec.get("ok"):
                    done.add(rec["url"])
            except Exception:
                pass
    todo = [u for u in urls if u not in done]
    print(f"total={len(urls)} done={len(done)} todo={len(todo)}", flush=True)

    fout = open(OUT, "a", encoding="utf-8")
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=12) as ex:
        futs = {ex.submit(worker, u): u for u in todo}
        n = 0
        for fut in as_completed(futs):
            rec = fut.result()
            with lock:
                fout.write(json.dumps(rec, ensure_ascii=False) + "\n")
                fout.flush()
                n += 1
                if rec.get("ok"):
                    counter["ok"] += 1
                else:
                    counter["err"] += 1
                if n % 100 == 0 or n == len(todo):
                    el = time.time() - t0
                    rate = n / el if el else 0
                    eta = (len(todo) - n) / rate if rate else 0
                    print(f"{n}/{len(todo)} ok={counter['ok']} err={counter['err']} "
                          f"{rate:.1f}/s eta={eta/60:.1f}min", flush=True)
    fout.close()
    print("DONE", counter, flush=True)


if __name__ == "__main__":
    main()
