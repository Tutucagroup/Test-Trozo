#!/bin/bash
# Doble clic para abrir Product Tester en el navegador (Mac).
cd "$(dirname "$0")" || exit 1

if ! command -v python3 >/dev/null 2>&1; then
  echo "No encontré Python. Instalalo desde https://www.python.org/downloads/ y volvé a abrir este archivo."
  read -r -p "Presioná Enter para cerrar..."
  exit 1
fi

if [ ! -d .venv ]; then
  echo "Primera vez: instalando lo necesario (tarda un minuto)..."
  python3 -m venv .venv || { read -r -p "Error creando el entorno. Enter para cerrar..."; exit 1; }
  .venv/bin/pip install -q --upgrade pip
fi
.venv/bin/pip install -q -r requirements.txt || { read -r -p "Error instalando dependencias. Enter para cerrar..."; exit 1; }

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Creé el archivo .env: completalo con tus claves de Meta y Shopify cuando las tengas."
fi

echo "Abriendo Product Tester... (dejá esta ventana abierta; cerrala para apagarlo)"
.venv/bin/python -m product_tester web "$@"
