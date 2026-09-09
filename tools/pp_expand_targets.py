#!/usr/bin/env python3
"""
Reconstruye el JSON completo de `stagedUploadsCreate` a partir de la forma
compacta de tools/pp_staged_compact.json.

La respuesta de Shopify repite en cada destino la misma credencial, fecha y
algoritmo, y su `policy` es sólo el base64 de un JSON derivable de la clave; lo
único irrepetible por destino es el UUID y la firma. Guardar sólo eso mantiene
el fichero legible y evita arrastrar 16 bloques idénticos.
"""
from __future__ import annotations

import base64
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "tools" / "pp_staged_compact.json"
DEST = ROOT / "tools" / "pp_staged_targets.json"
BUCKET = "https://shopify-staged-uploads.storage.googleapis.com/"


def policy_for(key: str, date: str, credential: str, expiration: str) -> str:
    conditions = [
        {"Content-Type": "text/plain"},
        {"success_action_status": "201"},
        {"acl": "private"},
        ["content-length-range", 1, 104857600],
        {"bucket": "shopify-staged-uploads"},
        {"key": key},
        {"x-goog-date": date},
        {"x-goog-credential": credential},
        {"x-goog-algorithm": "GOOG4-RSA-SHA256"},
    ]
    # Shopify serializa con las barras escapadas y sin espacios; la firma cubre
    # este base64 exacto, así que cualquier variación lo invalidaría.
    raw = json.dumps({"conditions": conditions, "expiration": expiration}, separators=(",", ":"))
    raw = raw.replace("/", r"\/")
    return base64.b64encode(raw.encode()).decode()


def main() -> None:
    cfg = json.loads(SRC.read_text())
    targets = []
    for filename, uuid, signature in cfg["files"]:
        key = f"{cfg['prefix']}/{uuid}/{filename}"
        targets.append(
            {
                "url": BUCKET,
                "resourceUrl": BUCKET,
                "parameters": [
                    {"name": "Content-Type", "value": "text/plain"},
                    {"name": "success_action_status", "value": "201"},
                    {"name": "acl", "value": "private"},
                    {"name": "key", "value": key},
                    {"name": "x-goog-date", "value": cfg["date"]},
                    {"name": "x-goog-credential", "value": cfg["credential"]},
                    {"name": "x-goog-algorithm", "value": "GOOG4-RSA-SHA256"},
                    {"name": "x-goog-signature", "value": signature},
                    {"name": "policy", "value": policy_for(key, cfg["date"], cfg["credential"], cfg["expiration"])},
                ],
            }
        )
    DEST.write_text(json.dumps(targets, indent=2))
    print(f"{len(targets)} destinos -> {DEST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
