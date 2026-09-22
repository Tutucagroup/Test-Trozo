# Ronda 2 — correcciones aplicadas en vivo

Todo lo de abajo ya está aplicado en la tienda vía Admin API. Verificado con
exportación masiva posterior: 4.347 productos / 29.976 variantes.

| Ítem | Antes | Ahora |
|---|---|---|
| Títulos duplicados | 18 | **0** |
| URLs que contradecían el color | 77 | **0** |
| Variantes sin SKU | 103 | **0** |
| SKUs duplicados | 0 | **0** |
| Colección de la portada | 1 producto | **114**, automática |
| About Us | mencionaba tops, skirts, accesorios | solo vestidos |

## Detalle

**About Us** reescrita: describe únicamente vestidos y mantiene las tarifas de
envío ya corregidas ($8 Standard, $18 Priority US, $14 Priority UK, gratis
desde $100), que ahora sí coinciden con el checkout.

**Portada**: la colección `frontpage` era manual con 1 producto. Se convirtió en
colección automática con la regla `tag = Best Seller OR Best Selling Dresses`,
así se mantiene sola. Pasó a 114 productos.

**76 handles corregidos** con `redirectNewHandle: true`, así que Shopify creó el
301 de la URL vieja a la nueva y no se rompe ningún enlace ni ranking. El color
del título se tomó como verdad porque coincide con la opción Color de la variante
en 76 de 77 casos.

**1 título corregido al revés**: `carys-maxi-dress-cream` decía "Carys Maxi Dress
White" pero su opción Color es Cream. Ahí el equivocado era el título.

**19 títulos** diferenciados. 15 pares eran el mismo vestido en versión normal y
en versión reciclada: se verificó la composición de cada uno antes de agregarles
el sufijo "Recycled". Los otros 4 se diferenciaron por un atributo real de la
prenda (flared vs slim, stretch vs no stretch, viscosa vs rayón).

**103 SKUs** generados con formato `PC-<id de variante>`, únicos y estables.

## Pendiente

- **Inventario**: importar `populars_clothes_inventario_900.csv` por
  Productos → Inventario → Importar. El CSV de productos no carga cantidades en
  productos existentes, por eso quedó en 0 tras la primera importación.
- **Descripción de la tienda**: no existe mutation en la Admin API. Va a mano en
  Tienda online → Preferencias.
- **Colección "Sale Dresses"**: 717 productos etiquetados sin descuento real.
  Sigue abierto y es el principal riesgo de *misrepresentation* que queda.
