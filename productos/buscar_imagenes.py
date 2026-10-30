"""Busca y descarga la imagen de cada producto de productos_unicos.csv.

Orden de búsqueda por producto:
  1. Tiendas VTEX de Colombia, buscando por EAN exacto (resultado más confiable).
  2. Open Beauty Facts, por EAN.
  3. Esas mismas tiendas, buscando por nombre (revisar a mano).
  (buscar_bing queda disponible, pero Bing bloquea consultas automáticas desde servidores.)

Las imágenes quedan en imagenes/<SKU>.<ext> y el CSV se actualiza con la URL
y la fuente de cada una. El SKU y el EAN nunca se modifican.

Uso:  python3 buscar_imagenes.py
"""
import csv
import html
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor

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
    "www.farmaciaspasteur.com.co",
    "www.drogueriascolsubsidio.com",
    "www.bellapiel.com.co",
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


GENERICAS = {"X", "UND", "ML", "G", "GR", "DE", "LA", "EL", "CON", "Y", "PARA", "EN", "SEMI", "TONO"}


def palabras(texto):
    texto = re.sub(r"x(\d)", r" \1", texto.upper())
    return {w for w in re.findall(r"[A-Z0-9ÁÉÍÓÚÑ.]+", texto) if w not in GENERICAS and len(w) > 1}


def marcas_de(nombre, marca):
    """La columna Marca a veces está mal; la marca real suele ir pegada a la 'x' del tamaño."""
    m = re.search(r"([A-ZÁÉÍÓÚÑ ]+?)x[\d.]|([A-ZÁÉÍÓÚÑ ]+?)xund", nombre)
    cands = {marca.upper()} if marca else set()
    if m:
        frase = (m.group(1) or m.group(2)).split()
        cands.add(frase[-1])
        if len(frase) >= 2:
            cands.add(" ".join(frase[-2:]))
    return {c for c in cands if c}


def coincide(nuestro, marcas, encontrado):
    """True si el texto encontrado menciona la marca y al menos otra palabra clave."""
    enc = encontrado.upper()
    if not any(m in enc for m in marcas):
        return False
    resto = palabras(nuestro) - set(" ".join(marcas).split())
    return len(resto & palabras(encontrado)) >= 1


def buscar_vtex(ean, nombre, marcas):
    for host in VTEX_TIENDAS:
        url = f"https://{host}/api/catalog_system/pub/products/search?fq=alternateIds_Ean:{ean}"
        try:
            r = s.get(url, timeout=15)
            if r.status_code not in (200, 206):
                continue
            for prod in r.json():
                for item in prod.get("items", []):
                    if item.get("ean") != ean:
                        continue
                    imgs = item.get("images") or []
                    if not imgs:
                        continue
                    texto = f"{prod.get('brand', '')} {prod.get('productName', '')} {item.get('name', '')}"
                    fuente = host if coincide(nombre, marcas, texto) else f"{host} REVISAR (EAN coincide pero es: {prod.get('productName')})"
                    return imgs[0]["imageUrl"].split("?")[0], fuente
        except (requests.RequestException, ValueError):
            continue
    return None


def buscar_vtex_nombre(nombre, marcas):
    """Búsqueda por texto en las tiendas VTEX; exige marca + la mayoría de palabras clave."""
    claves = palabras(nombre) - set(" ".join(marcas).split())
    if not claves:
        return None
    consulta = " ".join(sorted(marcas, key=len)[:1] + [w for w in palabras(nombre) if w in claves][:4])
    mejor = None
    for host in VTEX_TIENDAS:
        url = f"https://{host}/api/catalog_system/pub/products/search"
        try:
            r = s.get(url, params={"ft": consulta, "_from": 0, "_to": 9}, timeout=15)
            if r.status_code not in (200, 206):
                continue
            for prod in r.json():
                for item in prod.get("items", []):
                    imgs = item.get("images") or []
                    texto = f"{prod.get('brand', '')} {prod.get('productName', '')} {item.get('name', '')}"
                    if not imgs or not any(m in texto.upper() for m in marcas):
                        continue
                    comunes = len(claves & palabras(texto))
                    if comunes >= max(2, round(len(claves) * 0.7)) and (not mejor or comunes > mejor[0]):
                        mejor = (comunes, imgs[0]["imageUrl"].split("?")[0], f"{host} REVISAR (por nombre: {prod.get('productName')})")
        except (requests.RequestException, ValueError):
            continue
    return mejor[1:] if mejor else None


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


def buscar_bing(nombre, marcas):
    consulta = re.sub(r"x(\d)", r" \1", nombre)  # "ALFAPARFx60ml" -> "ALFAPARF 60ml"
    consulta = consulta.replace("xund", "")
    try:
        r = s.get("https://www.bing.com/images/search", params={"q": consulta, "form": "HDRSC2"}, timeout=15)
        mejor = None
        for m in re.finditer(r'm="([^"]+)"', r.text):
            try:
                datos = json.loads(html.unescape(m.group(1)))
            except ValueError:
                continue
            if not isinstance(datos, dict):
                continue
            murl = datos.get("murl", "")
            if not re.search(r"\.(jpe?g|png|webp)", murl, re.I):
                continue
            texto = f"{datos.get('t', '')} {datos.get('purl', '')} {murl}".replace("-", " ").replace("_", " ")
            if coincide(nombre, marcas, texto):
                puntos = len(palabras(nombre) & palabras(texto))
                if not mejor or puntos > mejor[0]:
                    mejor = (puntos, murl)
        if mejor:
            return mejor[1], "bing REVISAR"
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


def procesar(fila):
    marcas = marcas_de(fila["Producto"], fila["Marca"])
    hallado = None
    for ean in eans_de(fila["EAN"]):
        hallado = buscar_vtex(ean, fila["Producto"], marcas) or buscar_openbeautyfacts(ean)
        if hallado:
            break
    if not hallado:
        hallado = buscar_vtex_nombre(fila["Producto"], marcas)
    if hallado:
        url, fuente = hallado
        try:
            descargar(url, fila["SKU"])
            fila["Imagen_URL"], fila["Fuente"] = url, fuente
        except (requests.RequestException, ValueError) as e:
            fila["Fuente"] = f"error descarga: {e}"
    else:
        fila["Fuente"] = "no encontrada"
    return fila


def guardar(filas):
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=filas[0].keys())
        w.writeheader()
        w.writerows(filas)


def main():
    os.makedirs(IMG_DIR, exist_ok=True)
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        filas = list(csv.DictReader(f))
    pendientes = [f for f in filas if not f["Imagen_URL"]]

    # Varias búsquedas en paralelo; se guarda el avance cada 10 productos para poder reanudar.
    with ThreadPoolExecutor(max_workers=12) as ex:
        for i, fila in enumerate(ex.map(procesar, pendientes), 1):
            print(f"[{i}/{len(pendientes)}] {fila['SKU']} {fila['Producto'][:50]} -> {fila['Fuente']}", flush=True)
            if i % 10 == 0:
                guardar(filas)
    guardar(filas)


if __name__ == "__main__":
    sys.exit(main())
