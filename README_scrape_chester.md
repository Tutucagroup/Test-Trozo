# Scraper Farmacias Chester → template Matrixify

Recorre `https://www.farmaciaschester.com.ar/`, extrae **todos** los productos y
escribe un `.xlsx` idéntico en columnas al template de importación de Matrixify.

## ⚠️ Bloqueo de red en esta sesión

El entorno de Claude Code on the web tiene el dominio `farmaciaschester.com.ar`
(y `cdn.batitienda.com`) **bloqueado por la política de egress** — el proxy
responde `403` al CONNECT. Por eso el scraper **no se puede correr desde esta
sesión todavía**. Dos formas de destrabarlo:

1. **Habilitar el dominio** en la allowlist de red del entorno y **reabrir la
   sesión** (los cambios de política aplican al crear el entorno nuevo). Ahí
   corro el scraper contra el sitio vivo y te dejo el xlsx.
   Docs: https://code.claude.com/docs/en/claude-code-on-the-web
2. **Correrlo local**, en una máquina con acceso al sitio (ver Uso).

## Qué extrae y cómo

Prioriza **datos estructurados** (robusto y agnóstico de plataforma):

1. **JSON-LD** `schema.org/Product` (nombre, descripción, marca, SKU,
   `offers.price` / `highPrice`, `availability`, imágenes, breadcrumb).
2. **OpenGraph** / `<meta description>` como fallback.
3. **Selectores HTML** configurables (`SELECTORS` en el script) como último recurso.

Mapea cada producto a las **32 columnas** del template, con `Command = MERGE`,
`Option1 = Title / Default Title`, e imágenes 2..N como **filas extra** (sólo
`Handle` + `Image Src` + `Image Position`), tal como pide la hoja
*Instrucciones*.

### Tags y Type

`chester_tags_map.json` (generado del template, hoja *Tags por categoría*, 160
entradas L1/L2/L3) se usa para mapear el breadcrumb/categoría del producto a los
tags y al Type sugerido. El match prioriza la subcategoría más específica.
Conviene revisar los tags después de la primera corrida.

### Metafields

Los 8 `Metafield: custom.*` (tipo_piel, funcion, formulacion, rutina, fps,
consumo_consciente, promo_vigencia, precio_sin_impuestos_nac) son taxonomía
propia de Chester y **no** son deducibles de forma fiable del HTML; se dejan
vacíos para que los completes (el theme calcula `precio_sin_impuestos_nac` solo
si queda vacío). Si en la ficha viva aparecen como specs, se puede extender
`extract()` para poblarlos.

## Uso

```bash
pip install openpyxl

# 1) Corrida completa (descubre URLs por sitemap.xml):
python scrape_chester.py \
  --tags-map chester_tags_map.json \
  --out chester_productos_FINAL.xlsx \
  --delay 1.0

# 2) Prueba corta (primeros 10 productos):
python scrape_chester.py --limit 10 --out _test.xlsx

# 3) Si ya tenés las URLs de producto en un .txt (una por línea):
python scrape_chester.py --urls-file urls.txt --out chester_productos_FINAL.xlsx
```

## Notas de robustez

- Sólo `openpyxl` como dependencia; el resto es stdlib.
- Reintentos con backoff, `--delay` para no golpear el sitio, User-Agent propio.
- Descubrimiento por `sitemap.xml` / `sitemap_index.xml` (recursivo, soporta
  `.gz`), con fallback a filtrar URLs de producto.
- Confía en el CA del proxy (`/root/.ccr/ca-bundle.crt`) si está presente.
- **Calibración**: los `SELECTORS` de fallback son genéricos; una vez que se ve
  el DOM real conviene ajustarlos. Con JSON-LD presente, casi no se usan.
