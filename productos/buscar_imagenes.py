"""Busca y descarga la imagen de cada producto de productos_unicos.csv.

Orden de búsqueda por producto:
  1. Tiendas VTEX de Colombia, buscando por EAN exacto (resultado más confiable).
  2. Open Beauty Facts, por EAN.
  3. Bing Imágenes, por "marca + nombre del producto" (revisar a mano).

Las imágenes quedan en imagenes/<SKU>.<ext> y el CSV se actualiza con la URL
y la fuente de cada una. El SKU y el EAN nunca se modifican.

Uso:  python3 buscar_imagenes.py
"""
import csv
import html
import os
import re
import sys
import time

import requests

AQUI = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(AQUI, "productos_unicos.csv")
IMG_DIR = os.path.join(AQUI, "imagenes")

VTEX_TIENDAS = [
    "www.krika.co",
    "www.locatelcolombia.com",
    "www.exito.com",
    "www.olimpica.com",
    "www.larebajavirtual.com",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36",
    "Accept-Language": "es-CO,es;q=0.9",
}
s = requests.Session()
s.headers.update(HEADERS)


def eans_de(valor):
    return [e for e in re.split(r"[,\s]+", valor) if re.fullmatch(r"\d{8,14}", e)]


def buscar_vtex(ean):
    for host in VTEX_TIENDAS:
        url = f"https://{host}/api/catalog_system/pub/products/search?fq=alternateIds_Ean:{ean}"
        try:
            r = s.get(url, timeout=15)
            if r.status_code not in (200, 206):
                continue
            for prod in r.json():
                for item in prod.get("items", []):
                    if item.get("ean") and item["ean"] != ean:
                        continue
                    imgs = item.get("images") or []
                    if imgs:
                        return imgs[0]["imageUrl"].split("?")[0], host
        except (requests.RequestException, ValueError):
            continue
    return None


def buscar_openbeautyfacts(ean):
    try:
        r = s.get(f"https://world.openbeautyfacts.org/api/v2/product/{ean}.json", timeout=15)
        prod = r.json().get("product") or {}
        url = prod.get("image_front_url") or prod.get("image_url")
        if url:
            return url, "openbeautyfacts"
    except (requests.RequestException, ValueError):
        pass
    return None


def buscar_bing(nombre, marca):
    consulta = re.sub(r"x(\d)", r" \1", nombre)  # "ALFAPARFx60ml" -> "ALFAPARF 60ml"
    if marca and marca.lower() not in consulta.lower():
        consulta = f"{marca} {consulta}"
    try:
        r = s.get("https://www.bing.com/images/search", params={"q": consulta, "form": "HDRSC2"}, timeout=15)
        for m in re.finditer(r'm="([^"]+)"', r.text):
            murl = re.search(r'"murl":"([^"]+)"', html.unescape(m.group(1)))
            if murl and re.search(r"\.(jpe?g|png|webp)", murl.group(1), re.I):
                return murl.group(1), "bing (revisar)"
    except requests.RequestException:
        pass
    return None


def descargar(url, sku):
    r = s.get(url, timeout=30)
    r.raise_for_status()
    tipo = r.headers.get("Content-Type", "")
    if not tipo.startswith("image/"):
        raise ValueError(f"no es imagen: {tipo}")
    ext = {"image/png": "png", "image/webp": "webp"}.get(tipo.split(";")[0], "jpg")
    ruta = os.path.join(IMG_DIR, f"{sku}.{ext}")
    with open(ruta, "wb") as f:
        f.write(r.content)
    return ruta


def main():
    os.makedirs(IMG_DIR, exist_ok=True)
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        filas = list(csv.DictReader(f))

    for i, fila in enumerate(filas, 1):
        if fila["Imagen_URL"]:
            continue
        hallado = None
        for ean in eans_de(fila["EAN"]):
            hallado = buscar_vtex(ean) or buscar_openbeautyfacts(ean)
            if hallado:
                break
        hallado = hallado or buscar_bing(fila["Producto"], fila["Marca"])
        if hallado:
            url, fuente = hallado
            try:
                descargar(url, fila["SKU"])
                fila["Imagen_URL"], fila["Fuente"] = url, fuente
            except (requests.RequestException, ValueError) as e:
                fila["Fuente"] = f"error descarga: {e}"
        else:
            fila["Fuente"] = "no encontrada"
        print(f"[{i}/{len(filas)}] {fila['SKU']} {fila['Producto'][:50]} -> {fila['Fuente']}", flush=True)

        # Guardar avance cada 10 productos para poder reanudar.
        if i % 10 == 0 or i == len(filas):
            with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=filas[0].keys())
                w.writeheader()
                w.writerows(filas)
        time.sleep(0.5)


if __name__ == "__main__":
    sys.exit(main())
