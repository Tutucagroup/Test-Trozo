#!/usr/bin/env python3
"""
Deriva las etiquetas que alimentan las colecciones automáticas de la tienda a
partir de datos que ya están en cada producto (tipo y título), y escribe el
JSONL de variables para `bulkOperationRunMutation` con `productUpdate`.

Por qué hace falta: las colecciones son inteligentes y filtran por etiqueta,
pero el catálogo llegó con el tipo de producto bien puesto y las etiquetas a
medias (2.521 productos de tipo «mini dresses» y sólo 984 con la etiqueta), así
que media tienda no aparecía en su categoría.

Sólo se deducen atributos que el propio producto declara: largo, color, tejido y
corte. Las etiquetas de decisión comercial —«Best Seller», «Sale Dresses»,
«Back In Stock»— no se tocan: inventarlas sería afirmar algo que la tienda no
dice en ninguna parte.

Uso:
    python3 tools/pp_retag.py catalogo.jsonl            # informe, no escribe
    python3 tools/pp_retag.py catalogo.jsonl --write salida.jsonl
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter

# --- Diccionarios de derivación ------------------------------------------- #

# Familias de color: cada colección existe en la tienda, así que sólo se mapean
# los términos que caen sin discusión en una de ellas. Gris, morado, naranja y
# los estampados (multi, leopardo, rayas) se dejan fuera porque no hay colección
# donde ponerlos y una etiqueta sin colección no sirve a nadie.
COLORS = {
    "Black Dresses": ["black", "onyx"],
    "White Dresses": ["white", "ivory", "cream"],
    "Red Dresses": ["red", "burgundy", "wine", "cherry", "crimson", "maroon", "scarlet"],
    "Pink Dresses": ["pink", "blush", "fuchsia", "fuschia", "magenta"],
    "Blue Dresses": ["blue", "navy", "aqua", "teal", "cobalt", "periwinkle"],
    "Green Dresses": ["green", "sage", "olive", "mint", "emerald", "khaki"],
    "Brown Dresses": ["brown", "chocolate", "tan", "camel", "mocha", "taupe", "beige"],
    "Yellow Dresses": ["yellow", "lemon", "butter", "mustard", "gold", "champagne"],
}

# Tejido y corte: la palabra aparece literal en el título del producto.
STYLES = {
    "Floral Dresses": [r"floral"],
    "Polka Dot Dresses": [r"polka\s*dot", r"\bpolka\b"],
    "Satin Dresses": [r"satin"],
    "Strapless Dresses": [r"strapless"],
    "Halter Dresses": [r"halter"],
    "Bodycon Dresses": [r"bodycon"],
    "Corset Dresses": [r"corset"],
    "Bandage Dresses": [r"bandage"],
    "Long Sleeve Dresses": [r"long\s*sleeve"],
    "Curve Dresses": [r"\bcurve\b"],
}

BASE_TAG = "Dresses"
CATALOG_TAG = "New Dresses"


def is_dress(product: dict) -> bool:
    kind = product.get("productType", "").upper()
    title = product["title"].lower()
    if "DRESS" in kind:
        return True
    # El tipo viene vacío en un puñado de fichas; el título lo resuelve.
    if not kind.strip() and "dress" in title:
        return True
    return False


def length_tag(product: dict) -> str | None:
    title = product["title"].lower()
    kind = product.get("productType", "").upper()
    # El título manda sobre el tipo: el tipo «MAXI & MIDI DRESSES» agrupa dos
    # largos distintos y sólo el título distingue cuál es.
    if re.search(r"\bmidi\b", title):
        return "Midi Dresses"
    if re.search(r"\bmaxi\b", title):
        return "Maxi Dresses"
    if re.search(r"\bmini\b", title):
        return "Mini Dresses"
    if "MINI" in kind:
        return "Mini Dresses"
    if "MAXI" in kind:
        return "Maxi Dresses"
    if "MIDI" in kind:
        return "Midi Dresses"
    return None


def color_segment(title: str) -> str:
    """Parte del título donde vive el color.

    Las fichas siguen el patrón «<nombre> <corte> Dress <color>», así que el
    color va después de la última aparición de «dress». Buscarlo en el título
    entero confundía nombres propios con colores: «River Rose ... Green Stripe»
    es un vestido verde, no rosa.
    """
    lowered = title.lower()
    matches = list(re.finditer(r"\bdress(es)?\b", lowered))
    return lowered[matches[-1].end():] if matches else lowered


def color_tags(product: dict) -> list[str]:
    segment = color_segment(product["title"])
    found = []
    for tag, words in COLORS.items():
        if any(re.search(rf"\b{w}\b", segment) for w in words):
            found.append(tag)
    return found


def style_tags(product: dict) -> list[str]:
    title = product["title"].lower()
    return [tag for tag, pats in STYLES.items() if any(re.search(p, title) for p in pats)]


def derive(product: dict) -> list[str]:
    """Etiquetas que le faltan al producto, en orden estable."""
    if not is_dress(product):
        return []

    current = set(product.get("tags", []))
    wanted = {BASE_TAG, CATALOG_TAG}

    length = length_tag(product)
    if length:
        wanted.add(length)
    wanted.update(color_tags(product))
    wanted.update(style_tags(product))

    return sorted(wanted - current)


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2

    rows = [json.loads(line) for line in open(sys.argv[1])]
    added = Counter()
    changes = []
    for product in rows:
        new_tags = derive(product)
        if not new_tags:
            continue
        added.update(new_tags)
        changes.append((product, new_tags))

    dresses = sum(1 for p in rows if is_dress(p))
    print(f"productos activos:      {len(rows)}")
    print(f"  reconocidos vestido:  {dresses}")
    print(f"  otros (no se tocan):  {len(rows) - dresses}")
    print(f"  con etiquetas nuevas: {len(changes)}\n")
    print("etiquetas a añadir:")
    for tag, count in added.most_common():
        print(f"  +{count:5d}  {tag}")

    if "--write" in sys.argv:
        dest = sys.argv[sys.argv.index("--write") + 1]
        with open(dest, "w") as handle:
            for product, new_tags in changes:
                # productUpdate reemplaza la lista entera, así que se envía la
                # unión: mandar sólo las nuevas borraría las que ya tenía.
                merged = sorted(set(product.get("tags", [])) | set(new_tags))
                handle.write(json.dumps({"input": {"id": product["id"], "tags": merged}}) + "\n")
        print(f"\n{len(changes)} líneas -> {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
