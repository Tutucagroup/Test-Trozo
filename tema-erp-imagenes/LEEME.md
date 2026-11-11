# Imagen del producto en cada línea del pedido (para el ERP)

Copia del tema: "Krika — imágenes en pedido (ERP)" (190308515914). El tema publicado no se modificó.

Cada producto que se agrega a la bolsa guarda la propiedad oculta `_imagen_url` (URL pública de la foto de la variante o, si no tiene, la del producto).
Llega en el webhook `orders/create` en `line_items[].properties`. Por empezar con `_`, Shopify no la muestra en el checkout ni en los correos.

Archivos:
- snippets/kn-img-url.liquid (nuevo): calcula la URL.
- snippets/kn-card.liquid, snippets/kn-upsell-card.liquid, sections/kn-main-product.liquid: agregan `data-img` al formulario y a cada variante.
- assets/kn.js: el envío a /cart/add.js incluye `properties._imagen_url`; si un formulario no la trae, la completa con la imagen de la bolsa.

Entrega: se toma de `shipping_lines[0].title` (Local Delivery = domicilio Cali; empieza con "Krika Cosmetics" = retiro en esa tienda; el resto = envío a domicilio).
