# Descripciones de producto — Krika Cosmetics

CSV listos para importar en Shopify. Generados a partir del catálogo real
(11.063 productos, 181 tipos de producto, 1 variante por producto).

## Elegí UN archivo

| Archivo | Productos | Tamaño | Qué hace |
|---|---|---|---|
| `PRUEBA-20-productos.csv` | 20 | 32 KB | **Importá este primero.** 20 productos de 20 categorías distintas para revisar antes de tocar el catálogo. |
| `krika-descripciones-TODO-EN-1.csv` | 11.063 | 13,1 MB | **Todo en un solo archivo**, como pediste. Reemplaza la descripción de todos los productos. |
| `krika-descripciones-SOLO-SIN-DESCRIPCION.csv` | 5.362 | 6,1 MB | Solo los que no tenían descripción o la tenían inservible. No toca los que ya tenían texto del fabricante. |
| `krika-descripciones-COMPLETO-01/02.csv` | 11.063 | 7,6 + 8,0 MB | Los 11.063 **conservando** el texto original del fabricante al final de cada descripción. Son 2 archivos porque juntos pesan 15,6 MB y Shopify acepta 15 MB por archivo. |

**Por qué el "todo en 1" pesa menos que el completo en 2**: para que entrara en
un archivo saqué el bloque «Información del fabricante», que reproducía el texto
original del producto. Si ese texto te importa, usá los dos archivos
`COMPLETO`. Si no, con `TODO-EN-1` alcanza (y siempre lo podés recuperar del
respaldo que exportes antes de importar).

## Cómo importar

1. **Respaldo primero**: *Productos → Exportar → Todos los productos → CSV*.
2. Importá `PRUEBA-20-productos.csv` y revisá esos 20 productos en la tienda.
3. Si te convence, importá el archivo que elegiste.

En *Productos → Importar → Agregar archivo*, marcá
**«Sobrescribir cualquier producto actual que tenga el mismo identificador (handle)»**.

## Columnas del CSV

`Handle`, `Title`, `Body (HTML)`, `Option1 Name`, `Option1 Value`

Las dos últimas son obligatorias: sin ellas Shopify rechaza la importación con
*"Product options input is required when updating variants"*. Todos los productos
del catálogo tienen una sola variante con la opción `Title` = `Default Title`,
así que esas columnas van con ese valor y no modifican nada.

Todo lo que no está en el archivo (precios, variantes, imágenes, colecciones,
inventario, proveedor, etiquetas) queda intacto.

## Qué contiene cada descripción

1. **Gancho**: qué es, de qué marca, de qué línea y en qué presentación.
2. **Tono / Referencia**: cuando el nombre del producto trae un código.
3. **Por qué te va a gustar**: 4 a 7 beneficios concretos.
4. **Modo de uso** (o **Cómo usarlo** en herramientas): los pasos reales.
5. **Ideal para**: a quién le sirve.
6. **Tip Krika**: un consejo corto que aporta valor.
7. **Información del fabricante**: solo en los archivos `COMPLETO`.

## Cómo se generaron

- `theme/docs/desc_tipos.py` — biblioteca de copy escrita a mano para **los 181
  tipos de producto** del catálogo: beneficios, modo de uso, público y tip.
- `theme/docs/desc_engine.py` — parsea cada título (tipo, marca, tamaño, línea,
  tono), detecta más de 40 activos y características declaradas en el nombre
  (SPF, queratina, argán, matte, waterproof, sin sulfatos, volumen, rizos…),
  ajusta el mensaje según el formato del envase y arma el HTML.

```bash
cd theme/docs
# todos, conservando el texto del fabricante (se parte solo si supera 15 MB)
python3 desc_engine.py products.jsonl salida/ variants.jsonl

# todos en un archivo, sin el bloque del fabricante
python3 desc_engine.py products.jsonl salida/ variants.jsonl --sin-fabricante

# solo los que no tenían descripción útil
python3 desc_engine.py products.jsonl salida/ variants.jsonl --solo-vacios
```

`products.jsonl` y `variants.jsonl` salen de dos *bulk operations* de la Admin API:

```graphql
{ products { edges { node { id handle title vendor productType status descriptionHtml } } } }
{ products { edges { node { id handle options { name position }
    variants { edges { node { id sku selectedOptions { name value } } } } } } } }
```

## Sobre el alcance

Las descripciones se construyen con lo que el catálogo afirma: la categoría del
producto y lo que dice su propio nombre. No se inventan ingredientes,
porcentajes ni resultados clínicos, y no se hacen afirmaciones de salud. Donde
el producto lo pedía (antihongos, suplementos, bienestar) el texto remite a
consultar con un profesional.
