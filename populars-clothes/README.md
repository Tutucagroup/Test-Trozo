# Populars Clothes — limpieza de catálogo y auditoría Merchant Center

Trabajo sobre la tienda Shopify **popularsclothes.com** (22 sep 2026).

## Entregables

| Archivo | Qué es |
|---|---|
| `populars_clothes_vestidos.csv` | CSV de importación Shopify. 4.347 productos / 29.976 filas de variante. Descripciones nuevas + stock 999. |
| `auditoria-merchant-center.html` | Informe de auditoría de la web contra las políticas de Merchant Center. |
| `backup-246-productos-eliminados.json` | Respaldo completo (con variantes e imágenes) de los 246 productos borrados. |
| `scripts/` | Los scripts usados, para poder rehacer o auditar el proceso. |

## Cómo subir el CSV

Shopify Admin → Productos → Importar → tildar
**"Overwrite any current products that have the same handle"**.

El CSV **no incluye columnas de imagen** a propósito, así que las fotos actuales
de cada producto quedan intactas. La clave de coincidencia es el `Handle`, y cada
variante se ubica por `Option1 Value` / `Option2 Value` más el `Variant SKU`.

### Qué cambia el CSV

- `Body (HTML)` — descripción nueva en las 4.347 fichas.
- `Variant Inventory Qty` → `999` en las 29.976 variantes.
- `Variant Inventory Tracker` → `shopify` (antes 29.037 variantes no tenían seguimiento).
- `Variant Inventory Policy` → `deny`.
- `Type` y `Product Category` corregidos en 4 vestidos mal clasificados.
- `SEO Title` / `SEO Description` regenerados.

> **Ojo con el inventario.** Hoy casi todas las variantes tienen el seguimiento
> apagado, así que Shopify las trata como stock infinito. Al activarlo con 999,
> el stock empieza a descontarse con cada venta y llega a cero alguna vez. Si
> preferís que nunca se agoten, cambiá `Variant Inventory Policy` a `continue`
> antes de subir.

## Qué se hizo en la tienda

Se eliminaron **246 productos que no eran vestidos** (79 monos/enteritos, 78 tops,
23 shorts, 5 jeans, calzado, bolsos, gafas y bijouterie). Quedaron 4.347 vestidos.

La clasificación fue por tipo de producto **y** por título, porque 4 vestidos
estaban mal tipificados (3 como *Lingerie*, 1 sin tipo) y se habrían borrado por
error. También se preservaron compuestos como *"Tie Skirt Mini Dress"*, que son
vestidos aunque el título mencione otra prenda.

## Sobre las descripciones

4.325 productos tenían fichas técnicas copiadas de otro retailer. 1.168 contenían
`Populars Clothes Lower Impact` y otras `Populars Clothes Petite/Curve/Tall`:
restos de un "buscar y reemplazar" del nombre de la marca original.

Se reescribieron 4.340 con voz propia, conservando los datos reales de cada
prenda (composición, forro, elasticidad, cierres, cuidado). Las 7 que ya tenían
copy propio de la marca quedaron sin tocar.

Verificado: 4.347 descripciones **únicas**, sin duplicados y sin artefactos de
marca. Largo mediano 559 caracteres.
