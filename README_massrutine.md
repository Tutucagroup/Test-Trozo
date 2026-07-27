# Importador Massrutine (`massrutine_import.py`)

Trae los productos de las URLs de origen y los prepara para importar a la tienda
Shopify **Massrutine** como **marca propia** (private label — según la decisión
del usuario), rehosteando las imágenes en el CDN de Massrutine con nombre limpio.

## ⚠️ Requisitos para correrlo (hoy bloqueados)

1. **Acceso de red** a los dominios de origen (hoy dan 403 por política). Agregar
   en *Acceso a la red → Personalizado*:
   `medicube.us`, `*.medicube.us`, `www.ebay.com`, `i.ebayimg.com`,
   `poshmark.com`, `*.poshmark.com`, `lummia.com.co`, `www.lummia.com.co`,
   `cdn.shopify.com`. Luego **relanzar la sesión**.
2. **Conector Shopify activo en el chat** (o, para `--rehost`, las env
   `SHOPIFY_SHOP` + `SHOPIFY_ACCESS_TOKEN`).

## Qué hace

- **Scrape**: Shopify (`medicube.us`, `lummia.com.co`) vía `/products/<handle>.json`
  (limpio y completo); eBay/Poshmark vía JSON-LD.
- **Transform → Massrutine**: quita la marca de origen (Medicube/Anua/Lummia) del
  título y del handle, `Vendor = Massrutine`, limpia `subscr-`/tracking, entra
  como `draft` para revisar antes de publicar.
- **Rehost** (`--rehost`): sube cada imagen a Massrutine con
  `massrutine-{handle}-{posición}{ext}` (Shopify la ingiere desde el origen) y
  captura la URL del CDN nuevo.
- **Output**: `massrutine_products.json` (para importar por API/conector) +
  `massrutine_import.xlsx` (Matrixify, fallback).

## División de tareas (importante)

El script **no inventa descripciones**. Deja `body_raw` + `needs_rewrite=true`:
la **copy final original** (y la **traducción al inglés de Lummia**) la redacta
Claude producto por producto al importar, para que sea veraz y no una copia
textual de la web de origen. Así se evita misrepresentation y copyright.

## Uso

```bash
pip install openpyxl

# scrape + transform + genera json/xlsx (sin subir nada):
python massrutine_import.py --out-json massrutine_products.json --out-xlsx massrutine_import.xlsx

# además rehostea imágenes a Massrutine:
export SHOPIFY_SHOP=massrutine.myshopify.com
export SHOPIFY_ACCESS_TOKEN=shpat_xxx
python massrutine_import.py --rehost
```

## Fuentes (deduplicadas)

8 Medicube + 1 Lummia (Shopify) + Anua (Poshmark) + 1 ítem eBay. eBay y Poshmark
son listings de terceros (baja calidad); conviene revisarlos o reemplazarlos por
la fuente oficial de la marca.
