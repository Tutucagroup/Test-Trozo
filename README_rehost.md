# Rehost de imágenes — The Moon Toys

Rehostea las imágenes del catálogo en el CDN de **tu** tienda Shopify actual,
cortando la dependencia del CDN de la tienda vieja
(`cdn.shopify.com/s/files/1/0793/9457/0452/...`) y sacando el token `popmart`
(y el id de la tienda vieja) de los nombres de archivo.

## Qué hace

Por cada imagen del CSV (`Image Src` y `Variant Image`):

1. La sube a tu tienda actual vía **Shopify Admin GraphQL API** (`fileCreate`),
   ingiriéndola directamente desde la URL vieja (no hace falta descargar/re-subir
   a mano) y forzando un nombre nuevo **limpio y determinístico**:

   ```
   themoontoys-{Handle}-{Image Position}{extensión original}
   ```
   p. ej. `themoontoys-the-monsters-have-a-seat-vinyl-plush-blind-box-1.jpg`

   El nombre **nunca** contiene `popmart` ni el id de la tienda vieja (el script
   aborta si eso pasara).

2. Espera a que Shopify procese el archivo (`fileStatus = READY`) y captura la
   URL nueva del CDN.

3. Reescribe `Image Src` y `Variant Image` en el CSV apuntando a esas URLs
   nuevas, dejando el resto del archivo idéntico al CLEAN.

## Por qué hacen falta credenciales (y por qué no se puede generar el FINAL "en seco")

La URL final del CDN nuevo la asigna Shopify al subir
(`https://cdn.shopify.com/s/files/1/<TU_SHOP_ID>/files/<nombre>?v=<version>`).
El `shop id` y el `?v=` **no son derivables del CSV** — sólo se conocen después
de subir. Por eso hay que ejecutar la subida real contra tu tienda.

## Credenciales (sólo por variables de entorno, nunca hardcodeadas)

| Variable               | Ejemplo                        | Para qué |
|------------------------|--------------------------------|----------|
| `SHOPIFY_SHOP`         | `mi-dominio.myshopify.com`     | dominio de tu tienda |
| `SHOPIFY_ACCESS_TOKEN` | `shpat_xxxxxxxxxxxxxxxxxxxxxxx` | Admin API token con scopes `write_files`, `read_files` |

El token sale de **Settings → Apps and sales channels → Develop apps → (tu app)
→ API credentials → Admin API access token**.

## Uso

### 1) Sólo el mapa de renombres (determinístico, sin credenciales ni red)

```bash
python rehost_images.py \
  --in the_moon_toys_products_CLEAN.csv \
  --map rename_map.csv \
  --make-map-only
```

Genera `rename_map.csv` con `old_url, new_filename, new_url, file_id, status`.
Sirve para revisar los nombres nuevos antes de tocar la tienda.

### 2) Rehost completo (sube imágenes y escribe el FINAL)

```bash
export SHOPIFY_SHOP=mi-dominio.myshopify.com
export SHOPIFY_ACCESS_TOKEN=shpat_xxx

python rehost_images.py \
  --in the_moon_toys_products_CLEAN.csv \
  --out the_moon_toys_products_FINAL.csv \
  --map rename_map.csv
```

## Detalles de robustez

- **Idempotente / reanudable**: `rename_map.csv` funciona como caché. Si el
  proceso se corta, al re-ejecutar saltea las imágenes que ya tienen `new_url`.
- **Sin duplicados**: usa `duplicateResolutionMode: REPLACE`, así re-correr
  reemplaza el archivo del mismo nombre en vez de crear copias `_1`, `_2`.
- **Determinístico**: en este export, `Handle` + `Image Position` no tiene
  colisiones (118 imágenes únicas) y las 16 `Variant Image` coinciden con una
  `Image Src`, así que un solo mapa cubre ambas columnas.
- **Verificación final**: el script aborta si alguna URL reescrita todavía
  contiene `popmart` o el id de la tienda vieja.
- Sólo dependencias de la stdlib de Python 3 (no requiere `pip install`).
