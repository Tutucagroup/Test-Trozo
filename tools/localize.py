#!/usr/bin/env python3
"""
Descarga a disco los recursos remotos de out/preview.html (imágenes del CDN de
Shopify y las fuentes de Google) y reescribe las URLs a rutas locales, para que
las capturas de pantalla se rendericen sin depender de la red del navegador.
"""
from __future__ import annotations

import hashlib
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
ASSETS = OUT / "assets"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36"


def fetch(url: str, dest: Path) -> bool:
    if dest.exists() and dest.stat().st_size > 0:
        return True
    dest.parent.mkdir(parents=True, exist_ok=True)
    res = subprocess.run(
        ["curl", "-sS", "-L", "--max-time", "90", "-A", UA, "-o", str(dest), url],
        capture_output=True,
        text=True,
    )
    if res.returncode != 0 or not dest.exists() or dest.stat().st_size == 0:
        print(f"  [fallo] {url[:100]} :: {res.stderr.strip()[:80]}")
        dest.unlink(missing_ok=True)
        return False
    return True


def ext_for(url: str, default: str) -> str:
    stem = url.split("?")[0]
    for cand in (".webp", ".png", ".jpg", ".jpeg", ".svg", ".mp4", ".woff2", ".woff", ".css"):
        if stem.lower().endswith(cand):
            return cand
    return default


def local_name(url: str, default_ext: str) -> str:
    digest = hashlib.sha1(url.encode()).hexdigest()[:12]
    return f"{digest}{ext_for(url, default_ext)}"


def main() -> None:
    html = (OUT / "preview.html").read_text()
    ASSETS.mkdir(parents=True, exist_ok=True)

    # 1) Fuentes de Google: descargar la hoja de estilos y sus woff2.
    for css_url in set(re.findall(r'href="(https://fonts\.googleapis\.com/[^"]+)"', html)):
        css_file = ASSETS / local_name(css_url, ".css")
        if not fetch(css_url, css_file):
            continue
        css = css_file.read_text()
        for font_url in set(re.findall(r"url\((https://fonts\.gstatic\.com/[^)]+)\)", css)):
            font_file = ASSETS / local_name(font_url, ".woff2")
            if fetch(font_url, font_file):
                css = css.replace(font_url, font_file.name)
        css_file.write_text(css)
        html = html.replace(css_url, f"assets/{css_file.name}")

    # 2) Recursos del CDN de Shopify (imágenes y videos).
    cdn = set(re.findall(r'https://cdn\.shopify\.com/[^\s"\')]+', html))
    ok = 0
    for url in sorted(cdn):
        default = ".mp4" if "/videos/" in url else ".png"
        dest = ASSETS / local_name(url, default)
        if fetch(url, dest):
            html = html.replace(url, f"assets/{dest.name}")
            ok += 1

    # 3) Quitar los preconnect: ya no hacen falta y bloquean el evento load.
    html = re.sub(r'\s*<link rel="preconnect"[^>]*>', "", html)

    (OUT / "preview.local.html").write_text(html)
    print(f"recursos del CDN: {ok}/{len(cdn)} descargados")
    print(f"escrito {OUT / 'preview.local.html'}")
    leftovers = re.findall(r"https://(?:cdn\.shopify\.com|fonts\.g)[^\s\"')]+", html)
    if leftovers:
        print(f"quedan {len(leftovers)} URL(s) remotas, p. ej. {leftovers[0][:90]}")


if __name__ == "__main__":
    main()
