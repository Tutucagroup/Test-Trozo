# Descripciones de producto — Krika Cosmetics

CSV listos para importar en Shopify y sobrescribir la descripción de los
productos. Generados el 21/09/2026 a partir del catálogo real de la tienda
(11.063 productos, 181 tipos de producto).

## Qué hay acá

| Carpeta / archivo | Productos | Para qué |
|---|---|---|
| `PRUEBA-20-productos.csv` | 20 | **Importá este primero.** 20 productos de 20 categorías distintas para revisar el resultado antes de tocar el catálogo entero. |
| `completo/` (6 archivos) | 11.063 | Todos los productos del catálogo. |
| `solo-sin-descripcion/` (3 archivos) | 5.362 | Solo los productos que no tenían descripción o la tenían demasiado corta (menos de 120 caracteres). |

Elegí **una** de las dos carpetas, no las dos.

## Cómo importar

1. **Hacé un respaldo primero**: *Productos → Exportar → Todos los productos → CSV*.
   Si algo no te gusta, con ese archivo volvés atrás.
2. Importá `PRUEBA-20-productos.csv` y revisá esos 20 productos en la tienda.
3. Si te convence, importá los archivos de la carpeta que elijas, **de a uno y
   en orden** (01, 02, 03…).

En cada importación: *Productos → Importar → Agregar archivo → marcar
**«Sobrescribir cualquier producto actual que tenga el mismo identificador
(handle)»** → Cargar y continuar*.

El CSV solo trae tres columnas: `Handle`, `Title` y `Body (HTML)`. Shopify deja
intacto todo lo demás (precios, variantes, imágenes, colecciones, inventario),
porque esas columnas no están en el archivo.

## Qué contiene cada descripción

1. **Gancho**: qué es el producto, de qué marca, de qué línea o tono y en qué
   presentación.
2. **Por qué te va a gustar**: 4 a 7 beneficios concretos, sin promesas vacías.
3. **Modo de uso** (o **Cómo usarlo** en herramientas): los pasos reales, con
   los detalles que la gente suele hacer mal.
4. **Ideal para**: a quién le sirve.
5. **Tip Krika**: un consejo corto que aporta valor y da confianza.
6. **Información del fabricante**: si el producto ya tenía una descripción útil,
   se conserva íntegra al final. No se pierde nada.

Largo: entre 433 y 2.937 caracteres, mediana de 1.093. Todo el HTML fue
validado con un parser: 0 documentos mal formados.

## Cómo se generaron

- `theme/docs/desc_tipos.py` — la biblioteca de copy: beneficios, modo de uso,
  público y tip escritos uno por uno para **los 181 tipos de producto** del
  catálogo.
- `theme/docs/desc_engine.py` — parsea cada título (tipo, marca, tamaño, línea,
  tono), detecta activos y características mencionadas en el nombre (SPF,
  queratina, argán, matte, waterproof, sin sulfatos, volumen, rizos…) y suma
  beneficios específicos, ajusta el mensaje según el formato del envase y arma
  el HTML final.

Para regenerar todo:

```bash
cd theme/docs
python3 desc_engine.py products.jsonl salida/            # todos
python3 desc_engine.py products.jsonl salida/ --solo-vacios   # solo los vacíos
```

`products.jsonl` sale de una *bulk operation* de la Admin API con
`{ products { edges { node { id handle title vendor productType status descriptionHtml } } } }`.

## Sobre el alcance

Las descripciones se construyen a partir de lo que el catálogo afirma: la
categoría del producto y lo que dice su propio nombre. No se inventan
ingredientes, porcentajes ni resultados clínicos que no estén declarados, y no
se hacen afirmaciones de salud. Donde el producto lo pedía (antihongos,
suplementos, bienestar) el texto remite a consultar con un profesional.
