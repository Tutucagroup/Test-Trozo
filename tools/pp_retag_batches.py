#!/usr/bin/env python3
"""
Parte el resultado de pp_retag.py en lotes de `tagsAdd` para enviar por la API.

Las mutaciones masivas están bloqueadas en este entorno, así que la alternativa
es agrupar varias llamadas con alias en un mismo documento GraphQL. Se usa
`tagsAdd` y no `productUpdate` a propósito: añade sin reemplazar, de modo que un
lote repetido o una edición hecha en el panel mientras tanto no borran nada.

Uso:
    python3 tools/pp_retag_batches.py catalogo.jsonl destino/ [--size 100]
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_retag():
    spec = importlib.util.spec_from_file_location("pp_retag", ROOT / "tools" / "pp_retag.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2

    retag = load_retag()
    source, dest = Path(sys.argv[1]), Path(sys.argv[2])
    size = int(sys.argv[sys.argv.index("--size") + 1]) if "--size" in sys.argv else 100
    dest.mkdir(parents=True, exist_ok=True)

    # El largo (mini/midi/maxi) se resuelve con reglas de colección, que lo
    # deducen del tipo y del título sin escribir en 1.657 fichas; con --sin-largo
    # esas etiquetas se omiten y sólo viaja lo que las reglas no pueden inferir
    # con precisión, que es el color y el corte.
    skip = {"Mini Dresses", "Midi Dresses", "Maxi Dresses"} if "--sin-largo" in sys.argv else set()

    changes = []
    for line in source.open():
        product = json.loads(line)
        tags = [t for t in retag.derive(product) if t not in skip]
        if tags:
            changes.append((product["id"], tags))

    for index in range(0, len(changes), size):
        chunk = changes[index : index + size]
        number = index // size + 1

        # Un alias por producto, con los valores en línea y sin espacios: el
        # documento tiene que viajar entero en cada llamada, y la variante con
        # variables lo duplicaba de tamaño sin aportar nada (no hay comillas ni
        # acentos en un gid ni en estos nombres de etiqueta).
        fields = "".join(
            f'a{n}:tagsAdd(id:"{pid}",tags:{json.dumps(tags, separators=(",", ":"))}){{...E}}'
            for n, (pid, tags) in enumerate(chunk)
        )
        # El fragmento evita repetir la selección de errores cien veces.
        query = f"mutation{{{fields}}}fragment E on TagsAddPayload{{userErrors{{message}}}}"

        (dest / f"lote-{number:02d}.txt").write_text(query)

    print(f"{len(changes)} productos -> {(len(changes) + size - 1) // size} lotes de {size} en {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
