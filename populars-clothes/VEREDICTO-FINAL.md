# Veredicto final — 23 sep 2026

**La tienda está lista para pedir la revisión de Merchant Center.**

Segunda auditoría completa sobre exportación masiva en vivo: 4.347 productos,
29.976 variantes, 31.691 imágenes. No sobre una muestra.

## Las trece verificaciones

| Verificación | Antes | Ahora |
|---|---|---|
| Productos que no son vestidos | 246 | **0** |
| Descripciones copiadas de otro comercio | 4.325 | **0** |
| Artefactos "Populars Clothes Lower Impact" | 1.168 | **0** |
| Descripciones duplicadas entre sí | — | **0 de 4.347** |
| Títulos duplicados | 18 | **0** |
| URLs que contradecían el color | 77 | **0** |
| Variantes sin stock | 29.037 | **0** |
| Variantes sin SKU | 103 | **0** |
| SKUs duplicados | — | **0** |
| Productos sin imagen | 0 | **0** |
| Productos sin SEO title/description | 1 | **0** |
| Descuentos inválidos | — | **0** |
| Enlaces rotos en la navegación | 1 | **0** |

## Corregido en esta pasada

**Un 404 en el pie de todas las páginas.** Al borrar la colección Sale quedó
huérfano el enlace `/collections/sale-dresses` en el menú del footer. Como el
footer se renderiza en todo el sitio, era un enlace roto en cada página.
Reemplazado por la colección Curve.

**75 productos sin stock.** Error de secuencia: el CSV de inventario se generó
antes de renombrar los 76 handles, y el import de inventario matchea por handle.
Cargados por API. Verificado: los 4.347 productos tienen 900 unidades.

**Páginas de confianza sin enlazar.** About Us, FAQ y Size Guide existían pero
no aparecían en ningún menú. Agregadas al footer.

## Pendiente

1. **Obligatorio** — declarar `identifier_exists = no` en Merchant Center. Es
   marca propia sin GTIN; Google acepta marca + MPN, que ya está cubierto porque
   las 29.976 variantes tienen SKU. No se generaron códigos de barras a
   propósito: un GTIN inventado es causa de suspensión directa.
2. **Opcional** — descripción de la tienda. No existe mutation en la Admin API;
   va a mano en Tienda online → Preferencias.
3. **Opcional** — 717 etiquetas "Sale Dresses" huérfanas. Metadato inerte: la
   colección ya no existe y ningún menú la enlaza.

## Alcance

Este veredicto dice que la tienda cumple las políticas de Merchant Center según
todo lo verificable desde la Admin API de Shopify. No incluye los motivos de
rechazo que informa Google: la cuenta de Merchant Center de Populars Clothes no
está conectada a esta sesión. Una cuenta ya suspendida por tergiversación suele
necesitar que se pida la re-revisión de forma explícita.
