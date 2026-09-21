# Krika — Réplica VTEX (tema Shopify)

Tema Shopify Online Store 2.0 que replica la estructura y la identidad visual de
[krika.co](https://www.krika.co/) (tienda VTEX) y añade, al final del home, un
**carrusel UGC** de vídeos e imágenes de la comunidad.

Tienda: `piiv22-sv.myshopify.com` · Tema: **Krika — Réplica VTEX** (sin publicar)

## Estructura del home (`templates/index.json`)

| Orden | Sección | Archivo |
|---|---|---|
| 1 | Barra de anuncios rotativa (3 mensajes) | `sections/announcement-bar.liquid` |
| 2 | Cabecera fija + menú de categorías | `sections/header.liquid` |
| 3 | Carrusel principal (7 diapositivas, 3 por vista en escritorio) | `sections/hero-carousel.liquid` |
| 4 | Vitrina «15 Días de Belleza. 💄» | `sections/product-shelf.liquid` |
| 5 | Fila de 3 banners promocionales | `sections/banner-grid.liquid` |
| 6 | Vitrina «El regalo perfecto 🎁» | `sections/product-shelf.liquid` |
| 7 | Vitrina «Dale poder a tu estilo ✨» | `sections/product-shelf.liquid` |
| 8 | Vitrina «Para ellos 🧔» | `sections/product-shelf.liquid` |
| 9 | Carrusel de marcas (7 logos) | `sections/brand-carousel.liquid` |
| 10 | **Carrusel UGC** | `sections/ugc-carousel.liquid` |
| 11 | Pie de página (4 columnas + medios de pago) | `sections/footer.liquid` |

Cabecera y pie se montan como *section groups*: `sections/header-group.json` y
`sections/footer-group.json`.

## Carrusel UGC

Sección con bloques repetibles. Cada publicación admite, por orden de prioridad:

1. **Vídeo de YouTube o Vimeo** (`Vídeo de YouTube o Vimeo`)
2. **Vídeo subido a Shopify** (`Vídeo subido a Shopify`)
3. **URL de un vídeo MP4** — acepta una URL completa o el nombre de un archivo
   subido a *Contenido → Archivos* (se resuelve con `file_url`)
4. **Imagen** (selector o nombre de archivo)

Cada tarjeta lleva formato vertical 9:16, autor, descripción, etiqueta y un botón
«Comprar el look» que apunta al producto asociado o a un enlace propio.
Los vídeos arrancan al pulsar sobre la tarjeta; solo se reproduce uno a la vez.

## Identidad visual

Extraída de los logos originales de Krika:

- Magenta principal `#EB0284`
- Acento `#FF167D`
- Texto `#252628`

Configurable en *Personalizar → Configuración del tema* (ajustes con prefijo `k_`).

## Recursos en Shopify

**Archivos** (Contenido → Archivos), referenciados desde Liquid con `file_url`:

`krika-logo-header.png`, `krika-logo-footer.png`, `krika-favicon.png`,
`krika-medios-pago.png`, `krika-hero-1-desk.png`, `krika-hero-1-mob.png`,
`krika-hero-2-desk.gif` … `krika-hero-7-desk.png`,
`krika-banner-{moco,anyeluz,pili}.png`,
`krika-marca-{recamier,kura,pili,schwarzkopf,masglo,lmar,loreal}.png`

**Colecciones automáticas** (regla `Tipo de producto contiene …`):

- Vitrinas del home: `15-dias-de-belleza`, `el-regalo-perfecto`,
  `dale-poder-a-tu-estilo`, `para-ellos`
- Categorías del menú: `capilar`, `maquillaje`, `corporal`, `facial`,
  `manicure-pedicure`, `aseo-personal`, `electricos`, `fragancias`, `barberia`

**Menús** (Contenido → Navegación): `main-menu` (categorías, con DESCUENTOS
destacado), `footer-categorias`, `footer-unete-krika`, `footer-tyc`.

## Pendientes del catálogo (fuera del alcance del tema)

- Los **precios importados desde VTEX son `0,00 COP`** en todo el catálogo. El
  tema muestra «Precio a consultar» mientras el precio sea 0, pero hay que
  cargar los precios reales antes de vender.
- Solo **99 productos activos están publicados en el canal Online Store**
  (de 8.569 activos), así que las vitrinas se ven vacías o muy cortas hasta que
  se publique el catálogo.
- El inventario está en 0 en los productos muestreados.
- Las reglas de las colecciones de categoría usan coincidencias por texto sobre
  el tipo de producto; conviene afinarlas en el admin (p. ej. «POLVO» arrastra
  productos capilares hacia Maquillaje).

## Publicar el tema

El tema está **sin publicar** a propósito. Para revisarlo:
*Tienda online → Temas → «Krika — Réplica VTEX» → Vista previa*.
