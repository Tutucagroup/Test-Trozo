#!/usr/bin/env python3
"""
Sube los archivos del tema a los destinos temporales (staged uploads) de Shopify.

Se usa junto con la mutación `stagedUploadsCreate`: guardá su respuesta en
tools/staged_targets.json y ejecutá este script. Luego, `themeFilesUpsert` puede
apuntar a cada `resourceUrl` con `body: { type: URL }`, evitando reescribir a mano
cientos de KB de Liquid (y los errores de transcripción que eso implicaría).

Uso:
    python3 tools/push_staged.py            # sube todo
    python3 tools/push_staged.py --dry-run  # sólo muestra el plan
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGETS = ROOT / "tools" / "staged_targets.json"
THEME = ROOT / "theme"


def theme_path_for(staged_filename: str) -> Path:
    """`sections__valca-hero.liquid.txt` -> `theme/sections/valca-hero.liquid`."""
    name = staged_filename[:-4] if staged_filename.endswith(".txt") else staged_filename
    return THEME / name.replace("__", "/")


def main() -> int:
    dry = "--dry-run" in sys.argv
    targets = json.loads(TARGETS.read_text())
    if isinstance(targets, dict):
        targets = targets.get("stagedTargets", targets.get("data", {}).get("stagedUploadsCreate", {}).get("stagedTargets", []))

    ok, failed = 0, []
    for target in targets:
        params = {p["name"]: p["value"] for p in target["parameters"]}
        staged_name = params["key"].rsplit("/", 1)[-1]
        src = theme_path_for(staged_name)

        if not src.exists():
            failed.append((staged_name, "archivo local inexistente"))
            print(f"  FALTA  {staged_name} -> {src}")
            continue

        print(f"  {'(dry) ' if dry else ''}{src.relative_to(ROOT)}  ({src.stat().st_size} B)")
        if dry:
            ok += 1
            continue

        cmd = ["curl", "-sS", "-m", "120", "-o", "/dev/null", "-w", "%{http_code}", "-X", "POST", target["url"]]
        for name, value in params.items():
            cmd += ["-F", f"{name}={value}"]
        cmd += ["-F", f"file=@{src};type=text/plain"]

        res = subprocess.run(cmd, capture_output=True, text=True)
        code = res.stdout.strip()
        if code == "201":
            ok += 1
        else:
            failed.append((staged_name, f"HTTP {code} {res.stderr.strip()[:100]}"))
            print(f"    ERROR HTTP {code}")

    print(f"\n{ok}/{len(targets)} subidos")
    if failed:
        print("fallaron:")
        for name, why in failed:
            print(f"  - {name}: {why}")
        return 1

    # Deja listo el input de themeFilesUpsert para no tener que rearmarlo a mano.
    files = []
    for target in targets:
        params = {p["name"]: p["value"] for p in target["parameters"]}
        staged_name = params["key"].rsplit("/", 1)[-1]
        theme_rel = str(theme_path_for(staged_name).relative_to(THEME))
        files.append({"filename": theme_rel, "body": {"type": "URL", "value": target["resourceUrl"]}})
    out = ROOT / "tools" / "upsert_input.json"
    out.write_text(json.dumps(files, indent=1, ensure_ascii=False))
    print(f"input de themeFilesUpsert -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
