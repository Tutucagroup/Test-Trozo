#!/usr/bin/env python3
"""
Rehost The Moon Toys product images onto the *current* store's Shopify CDN.

Why: the export (the_moon_toys_products_CLEAN.csv) still points Image Src /
Variant Image at the OLD store's CDN
(cdn.shopify.com/s/files/1/0793/9457/0452/...) and many file names carry the
"popmart" token plus the old store id. This script re-uploads every image to
the current store with a clean, deterministic name and rewrites the CSV.

Naming convention (deterministic from the CSV, never contains "popmart" nor the
old store id):

    themoontoys-{Handle}-{Image Position}{original extension}

    e.g. themoontoys-the-monsters-have-a-seat-vinyl-plush-blind-box-1.jpg

Credentials are read from the environment ONLY (never hardcoded):

    SHOPIFY_SHOP          e.g. mi-dominio.myshopify.com
    SHOPIFY_ACCESS_TOKEN  Admin API access token (shpat_...) with write_files /
                          read_files scopes.

Usage
-----
1) Build just the deterministic rename map (no credentials, no network):

    python rehost_images.py \
        --in the_moon_toys_products_CLEAN.csv \
        --map rename_map.csv \
        --make-map-only

2) Full rehost (uploads to the current store, then writes the FINAL csv).
   The map file is used as a resumable cache: rows already carrying a new_url
   are skipped on re-runs.

    export SHOPIFY_SHOP=mi-dominio.myshopify.com
    export SHOPIFY_ACCESS_TOKEN=shpat_xxx
    python rehost_images.py \
        --in the_moon_toys_products_CLEAN.csv \
        --out the_moon_toys_products_FINAL.csv \
        --map rename_map.csv
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request
from collections import OrderedDict

# --- columns we touch -------------------------------------------------------
IMAGE_SRC_COL = "Image Src"
IMAGE_POS_COL = "Image Position"
IMAGE_ALT_COL = "Image Alt Text"
VARIANT_IMG_COL = "Variant Image"
HANDLE_COL = "Handle"

NAME_PREFIX = "themoontoys"
OLD_STORE_ID = "0793/9457/0452"          # must never appear in a new name
FORBIDDEN_TOKENS = ("popmart", "0793", "9457", "0452")

API_VERSION = "2024-10"                   # fileCreate supports `filename` since 2024-04
POLL_TRIES = 30
POLL_SLEEP = 2.0                          # seconds between status polls
UPLOAD_BATCH = 10                         # files per fileCreate call

MAP_FIELDS = ["old_url", "new_filename", "new_url", "file_id", "status"]


# --------------------------------------------------------------------------- #
# Deterministic naming
# --------------------------------------------------------------------------- #
def ext_of(url: str) -> str:
    """Return the lower-case extension (incl. dot) of an image URL, '.jpg' default."""
    path = url.split("?", 1)[0]
    dot = path.rfind(".")
    slash = path.rfind("/")
    if dot > slash:
        ext = path[dot:].lower()
        if 2 <= len(ext) <= 6:
            return ext
    return ".jpg"


def new_filename(handle: str, position: str, url: str) -> str:
    handle = handle.strip()
    position = (position or "").strip() or "1"
    name = f"{NAME_PREFIX}-{handle}-{position}{ext_of(url)}"
    low = name.lower()
    for bad in FORBIDDEN_TOKENS:
        if bad in low:
            raise ValueError(f"refusing to emit name containing '{bad}': {name}")
    return name


def build_url_map(rows: list[dict]) -> "OrderedDict[str, str]":
    """
    old_url -> new_filename.

    Names are derived from the Image Src rows (which carry Handle + Image
    Position). Every Variant Image URL in this export also appears as an Image
    Src, so a single map covers both columns; any stray Variant-only URL falls
    back to the variant row's own Handle/Position.
    """
    url_to_name: "OrderedDict[str, str]" = OrderedDict()
    for r in rows:
        src = r.get(IMAGE_SRC_COL, "").strip()
        if src and src not in url_to_name:
            url_to_name[src] = new_filename(r[HANDLE_COL], r.get(IMAGE_POS_COL, ""), src)
    for r in rows:
        vi = r.get(VARIANT_IMG_COL, "").strip()
        if vi and vi not in url_to_name:
            url_to_name[vi] = new_filename(r[HANDLE_COL], r.get(IMAGE_POS_COL, ""), vi)
    return url_to_name


def alt_for_url(rows: list[dict], url: str) -> str:
    for r in rows:
        if r.get(IMAGE_SRC_COL, "").strip() == url:
            return r.get(IMAGE_ALT_COL, "").strip()
    return ""


# --------------------------------------------------------------------------- #
# Resumable map file (cache)
# --------------------------------------------------------------------------- #
def load_map(path: str) -> "OrderedDict[str, dict]":
    cache: "OrderedDict[str, dict]" = OrderedDict()
    if path and os.path.exists(path):
        with open(path, newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                cache[row["old_url"]] = row
    return cache


def save_map(path: str, cache: "OrderedDict[str, dict]") -> None:
    if not path:
        return
    tmp = path + ".tmp"
    with open(tmp, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=MAP_FIELDS)
        w.writeheader()
        for rec in cache.values():
            w.writerow({k: rec.get(k, "") for k in MAP_FIELDS})
    os.replace(tmp, path)


# --------------------------------------------------------------------------- #
# Shopify Admin GraphQL
# --------------------------------------------------------------------------- #
class Shopify:
    def __init__(self, shop: str, token: str):
        self.endpoint = f"https://{shop}/admin/api/{API_VERSION}/graphql.json"
        self.token = token

    def _call(self, query: str, variables: dict) -> dict:
        body = json.dumps({"query": query, "variables": variables}).encode("utf-8")
        req = urllib.request.Request(
            self.endpoint,
            data=body,
            headers={
                "Content-Type": "application/json",
                "X-Shopify-Access-Token": self.token,
                "Accept": "application/json",
            },
            method="POST",
        )
        for attempt in range(5):
            try:
                with urllib.request.urlopen(req, timeout=60) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                break
            except urllib.error.HTTPError as e:
                if e.code in (429, 502, 503) and attempt < 4:
                    time.sleep(2 ** attempt)
                    continue
                raise RuntimeError(f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')}")
            except urllib.error.URLError:
                if attempt < 4:
                    time.sleep(2 ** attempt)
                    continue
                raise
        if "errors" in data and data["errors"]:
            # throttle -> back off and retry once more
            if any("Throttled" in str(err) for err in data["errors"]):
                time.sleep(3)
                return self._call(query, variables)
            raise RuntimeError(f"GraphQL errors: {json.dumps(data['errors'])}")
        return data["data"]

    FILE_CREATE = """
    mutation fileCreate($files: [FileCreateInput!]!) {
      fileCreate(files: $files) {
        files {
          id
          fileStatus
          alt
          ... on MediaImage { image { url } }
          ... on GenericFile { url }
        }
        userErrors { field message code }
      }
    }"""

    NODE_STATUS = """
    query node($id: ID!) {
      node(id: $id) {
        ... on MediaImage { fileStatus image { url } }
        ... on GenericFile { fileStatus url }
      }
    }"""

    def create_files(self, items: list[dict]) -> list[dict]:
        """items: [{originalSource, filename, alt}] -> created file nodes."""
        files = [
            {
                "originalSource": it["originalSource"],
                "filename": it["filename"],
                "alt": it.get("alt") or "",
                "contentType": "IMAGE",
                "duplicateResolutionMode": "REPLACE",
            }
            for it in items
        ]
        data = self._call(self.FILE_CREATE, {"files": files})
        res = data["fileCreate"]
        if res["userErrors"]:
            raise RuntimeError(f"fileCreate userErrors: {json.dumps(res['userErrors'])}")
        return res["files"]

    def wait_ready(self, file_id: str) -> str:
        for _ in range(POLL_TRIES):
            data = self._call(self.NODE_STATUS, {"id": file_id})
            node = data.get("node") or {}
            status = node.get("fileStatus")
            url = (node.get("image") or {}).get("url") or node.get("url")
            if status == "READY" and url:
                return url
            if status == "FAILED":
                raise RuntimeError(f"file {file_id} processing FAILED")
            time.sleep(POLL_SLEEP)
        raise RuntimeError(f"file {file_id} not READY after {POLL_TRIES} polls")


# --------------------------------------------------------------------------- #
# Pipeline
# --------------------------------------------------------------------------- #
def read_csv(path: str) -> tuple[list[str], list[dict]]:
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
        return reader.fieldnames, rows


def write_csv(path: str, fieldnames: list[str], rows: list[dict]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def do_upload(url_to_name, rows, cache, shop: Shopify, map_path: str) -> None:
    pending = [(u, n) for u, n in url_to_name.items()
               if not (cache.get(u, {}).get("new_url"))]
    print(f"{len(url_to_name)} unique images, {len(pending)} to upload "
          f"({len(url_to_name) - len(pending)} cached).")

    for i in range(0, len(pending), UPLOAD_BATCH):
        batch = pending[i:i + UPLOAD_BATCH]
        items = [{"originalSource": u, "filename": n, "alt": alt_for_url(rows, u)}
                 for u, n in batch]
        created = shop.create_files(items)
        # fileCreate preserves input order
        for (old_url, name), node in zip(batch, created):
            cache[old_url] = {
                "old_url": old_url, "new_filename": name,
                "new_url": "", "file_id": node["id"], "status": node["fileStatus"],
            }
        save_map(map_path, cache)
        for (old_url, name), node in zip(batch, created):
            new_url = shop.wait_ready(node["id"])
            cache[old_url].update(new_url=new_url, status="READY")
            print(f"  ok {name}")
        save_map(map_path, cache)


def rewrite_rows(rows, cache) -> int:
    changed = 0
    for r in rows:
        for col in (IMAGE_SRC_COL, VARIANT_IMG_COL):
            v = r.get(col, "").strip()
            if v and v in cache and cache[v].get("new_url"):
                if r[col] != cache[v]["new_url"]:
                    r[col] = cache[v]["new_url"]
                    changed += 1
    return changed


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in", dest="inp", required=True, help="input CLEAN csv")
    ap.add_argument("--out", dest="out", help="output FINAL csv")
    ap.add_argument("--map", dest="map", required=True, help="rename map csv (cache)")
    ap.add_argument("--make-map-only", action="store_true",
                    help="only emit the deterministic old_url->new_filename map")
    args = ap.parse_args()

    fieldnames, rows = read_csv(args.inp)
    url_to_name = build_url_map(rows)

    cache = load_map(args.map)
    # seed cache with deterministic names (preserve any existing new_url)
    for old_url, name in url_to_name.items():
        rec = cache.get(old_url, {})
        rec.setdefault("old_url", old_url)
        rec["new_filename"] = name
        rec.setdefault("new_url", rec.get("new_url", ""))
        rec.setdefault("file_id", rec.get("file_id", ""))
        rec.setdefault("status", rec.get("status", "PENDING"))
        cache[old_url] = rec
    save_map(args.map, cache)

    if args.make_map_only:
        print(f"Wrote deterministic rename map for {len(url_to_name)} images -> {args.map}")
        return 0

    shop = os.environ.get("SHOPIFY_SHOP", "").strip()
    token = os.environ.get("SHOPIFY_ACCESS_TOKEN", "").strip()
    if not shop or not token:
        sys.stderr.write(
            "ERROR: set SHOPIFY_SHOP and SHOPIFY_ACCESS_TOKEN in the environment.\n"
            "  export SHOPIFY_SHOP=mi-dominio.myshopify.com\n"
            "  export SHOPIFY_ACCESS_TOKEN=shpat_xxx\n")
        return 2
    if not args.out:
        sys.stderr.write("ERROR: --out is required for the full rehost.\n")
        return 2

    do_upload(url_to_name, rows, cache, Shopify(shop, token), args.map)

    missing = [u for u in url_to_name if not cache.get(u, {}).get("new_url")]
    if missing:
        sys.stderr.write(f"ERROR: {len(missing)} images never got a new URL; aborting.\n")
        return 1

    changed = rewrite_rows(rows, cache)
    write_csv(args.out, fieldnames, rows)

    # safety: no forbidden token survived in the rewritten image columns
    leaks = []
    for r in rows:
        for col in (IMAGE_SRC_COL, VARIANT_IMG_COL):
            v = r.get(col, "")
            if OLD_STORE_ID in v or "popmart" in v.lower():
                leaks.append(v)
    if leaks:
        sys.stderr.write(f"ERROR: {len(leaks)} image URLs still reference the old store/token.\n")
        return 1

    print(f"Rewrote {changed} image references -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
