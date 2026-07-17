"""
Parser de páginas de producto de Farmacias Chester (plataforma gSharp/batitienda).
Fuente principal: función JS getAccessedProductInfo() con JSON estructurado.
Complementos desde el HTML: PC-id de categoría, descripción e imágenes.

getAccessedProductInfo() -> {
  a: product_id, b: title, c: EAN, d: internal_id,
  e: list_price, f: sale_price, g: stock_qty,
  h: brand, i: category_leaf_name, j: url_path
}
"""
import re
import json
import html as htmllib

RELATED_MARKERS = ("Products_RelatedProducts", "detailsproducts-container")


def _clean(s):
    if s is None:
        return None
    s = htmllib.unescape(s)
    s = re.sub(r"[ \t\r\f\v]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip() or None


def _text(fragment):
    if fragment is None:
        return None
    t = re.sub(r"<[^>]+>", " ", fragment)
    return _clean(t)


def _desc_to_html(inner):
    """Convierte el contenido de #tab-description en HTML limpio de párrafos."""
    if not inner:
        return None
    # cortar el bloque de marca/categoría si quedó incluido
    cut = re.search(r'<div[^>]*class="[^"]*product_meta', inner)
    if cut:
        inner = inner[: cut.start()]
    # quitar scripts/estilos
    inner = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", inner, flags=re.S | re.I)
    # normalizar saltos a partir de <br>, <p>, <li>
    inner = re.sub(r"(?i)</p\s*>", "\n\n", inner)
    inner = re.sub(r"(?i)<br\s*/?>", "\n", inner)
    inner = re.sub(r"(?i)<li[^>]*>", "\n- ", inner)
    text = re.sub(r"<[^>]+>", "", inner)
    text = htmllib.unescape(text)
    text = re.sub(r"[ \t]+", " ", text)
    # armar párrafos separados por línea en blanco
    blocks = [b.strip() for b in re.split(r"\n\s*\n", text)]
    paras = []
    for b in blocks:
        lines = [ln.strip() for ln in b.split("\n") if ln.strip()]
        if lines:
            paras.append("<p>" + "<br>".join(lines) + "</p>")
    return "".join(paras) or None


def parse_product(url, html):
    d = {"url": url}

    # ---- JSON estructurado ----
    m = re.search(r"getAccessedProductInfo\(\)\s*\{\s*return\s*(\{.*?\});", html, re.S)
    info = json.loads(m.group(1)) if m else {}

    m = re.search(r"-WS(\d+)\b", url)
    d["ws_code"] = ("WS" + m.group(1)) if m else (("WS" + str(info["a"])) if info.get("a") else None)

    m = re.search(r"/shop/product/(.+?)-WS\d+", url)
    d["handle"] = m.group(1) if m else None

    d["title"] = _clean(info.get("b"))
    d["barcode"] = (str(info["c"]).strip() or None) if info.get("c") else None
    d["vendor"] = _clean(info.get("h"))
    d["category_name"] = _clean(info.get("i"))

    list_price = info.get("e")
    sale_price = info.get("f")
    d["price"] = round(sale_price, 2) if sale_price is not None else None
    # compare-at sólo si hay descuento real
    if list_price is not None and sale_price is not None and round(list_price, 2) > round(sale_price, 2):
        d["compare_at"] = round(list_price, 2)
    else:
        d["compare_at"] = None
    d["stock"] = int(info["g"]) if info.get("g") is not None else None

    # ---- categoría: PC-id + slug (para resolver el path completo) ----
    m = re.search(r'Categor\xEDa:\s*(?:<[^>]+>\s*)*<a[^>]*href="/shop/([a-z0-9-]+)-PC(\d+)"', html)
    if m:
        d["cat_slug"] = m.group(1)
        d["cat_pc"] = m.group(2)
    else:
        d["cat_slug"] = None
        d["cat_pc"] = None

    # ---- precio sin impuestos nacionales ----
    m = re.search(r"Precio sin impuestos nacionales:\s*</span>\s*<span[^>]*>\$\s*([\d.]+),(\d+)", html)
    if m:
        val = float(m.group(1).replace(".", "") + "." + m.group(2))
        d["precio_sin_imp_centavos"] = int(round(val * 100))
    else:
        d["precio_sin_imp_centavos"] = None

    # ---- descripción (Body HTML) ----
    m = re.search(r'id="tab-description">(.*?)</div>\s*</div>', html, re.S)
    if not m:
        m = re.search(r'id="tab-description">(.*)', html, re.S)
    d["body_html"] = _desc_to_html(m.group(1)) if m else None

    # ---- imágenes propias de la galería (anchors data-assetid, ordenados por #N) ----
    # La galería del producto usa <a data-assetid=...> ... product_picture ...; los
    # productos relacionados NO usan data-assetid, así que esto evita cualquier bleed.
    gallery = []
    for gm in re.finditer(
        r'data-assetid="\d+"(.*?)(?=data-assetid="\d+"|</div>\s*</div>\s*</div>|$)',
        html, re.S,
    ):
        block = gm.group(1)
        img = re.search(r"product_picture_([0-9a-f]{32})_(\d+)_0_[a-z]\.(?:jpg|jpeg|png|webp)", block)
        if not img:
            continue
        pos = re.search(r'#(\d+)\s*"', block)
        order_n = int(pos.group(1)) if pos else (len(gallery) + 1)
        gallery.append((order_n, img.group(1), img.group(2)))

    if not gallery:
        # fallback: og:image únicamente
        og = re.search(r'og:image"\s+content="[^"]*product_picture_([0-9a-f]{32})_(\d+)_0_[a-z]\.', html)
        if og:
            gallery.append((1, og.group(1), og.group(2)))

    gallery.sort(key=lambda x: x[0])
    seen, imgs = set(), []
    for _, h, n in gallery:
        if (h, n) in seen:
            continue
        seen.add((h, n))
        # _l = mayor tamaño accesible en el CDN; _f/_s devuelven 403
        imgs.append(f"https://cdn.batitienda.com/baticloud/images/product_picture_{h}_{n}_0_l.jpg")
    d["images"] = imgs
    return d


if __name__ == "__main__":
    import sys
    html = open(sys.argv[1], encoding="utf-8", errors="replace").read()
    print(json.dumps(parse_product(sys.argv[2], html), ensure_ascii=False, indent=2))
