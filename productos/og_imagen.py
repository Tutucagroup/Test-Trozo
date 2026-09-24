"""Descarga la imagen principal (og:image / JSON-LD / VTEX / Shopify) de una página de producto.

Uso: python3 og_imagen.py <SKU> <URL_de_la_pagina>
Imprime: TITULO_PAGINA | URL_IMAGEN  y guarda imagenes/<SKU>.<ext>
"""
import html, json, re, sys
import buscar_imagenes as b

sku, url = sys.argv[1], sys.argv[2]
r = b.s.get(url, timeout=25)
r.raise_for_status()
t = r.text
titulo = html.unescape((re.search(r"<title[^>]*>(.*?)</title>", t, re.S | re.I) or [None, ""])[1].strip())
img = None
for pat in [r'<meta[^>]+property=["\']og:image(?::secure_url)?["\'][^>]+content=["\']([^"\']+)',
            r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image',
            r'"image"\s*:\s*\[?\s*"([^"]+)"']:
    m = re.search(pat, t, re.I)
    if m:
        img = html.unescape(m.group(1))
        break
if not img:
    sys.exit(f"SIN IMAGEN | {titulo}")
if img.startswith("//"):
    img = "https:" + img
ruta = b.descargar(img, sku)
print(f"{titulo} | {img} | {ruta}")
