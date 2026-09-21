# Krika — Réplica VTEX (tema Shopify)

Tema Shopify Online Store 2.0 que replica la estructura y la identidad visual de
[krika.co](https://www.krika.co/) (tienda VTEX) y añade, al final del home, un
**carrusel UGC** de vídeos e imágenes de la comunidad.

Tienda: `piiv22-sv.myshopify.com` · Tema: **Krika — Réplica VTEX** (sin publicar)

## Estructura del home (`templates/index.json`)

| Orden | Sección | Archivo |
|---|---|---|
| 1 | Barra de anuncios rotativa (3 mensajes) | `sections/announcement-bar.liquid` |
| 2 | Cabecera fija + mega-menú de categorías | `sections/header.liquid` |
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

## Mega-menú

La barra de categorías lee el menú `main-menu` de *Contenido → Navegación* y
admite **tres niveles**: categoría → columna → subcategoría.

- **Escritorio**: al pasar el ratón sobre una categoría se despliega un panel a
  todo el ancho con una columna por subcategoría de segundo nivel y sus enlaces
  debajo, más un botón «Ver todo …». Funciona sin JavaScript (CSS `:hover` +
  `:focus-within`, accesible por teclado).
- **Móvil**: el mismo árbol se despliega en el cajón lateral con `<details>`
  anidados.

Para cambiar el menú basta editar `main-menu` en el admin; el tema no necesita
tocarse.

## Marcas

`sections/brand-carousel.liquid` tiene dos modos:

- **Automático** (el del home): recorre todas las marcas del catálogo publicado
  y cada tarjeta enlaza a *todos* los productos de esa marca
  (`/collections/vendors?q=<marca>`).
- **Manual**: bloques configurables con logo y enlace propios.

El logo se resuelve así, en orden: imagen del bloque → URL/nombre de archivo del
bloque → **`krika-marca-<handle-de-la-marca>.png` en Contenido → Archivos**. Si
no existe ninguno, la tarjeta muestra el nombre de la marca como logotipo
tipográfico. Para añadir un logo nuevo basta subir el archivo con ese nombre;
no hay que tocar código.

La página **/pages/marcas** (`sections/main-brands.liquid` +
`templates/page.marcas.json`) lista todas las marcas del catálogo.

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

**Colecciones automáticas** (162 en total, todas publicadas en Tienda online):

- Vitrinas del home (4): `15-dias-de-belleza`, `el-regalo-perfecto`,
  `dale-poder-a-tu-estilo`, `para-ellos`
- Categorías de primer nivel (9): `capilar`, `maquillaje`, `corporal`, `facial`,
  `manicure-pedicure`, `aseo-personal`, `electricos`, `fragancias`, `barberia`
- Subcategorías del mega-menú (149): 45 columnas de segundo nivel y 104 hojas de
  tercer nivel, replicando el árbol de categorías de krika.co. Casi todas usan la
  regla `Tipo de producto es igual a …` contra los 181 tipos del catálogo, de
  modo que se llenan solas; unas pocas (Metalizados, Esponjas, Maletas, Balacas,
  Cuchillas, Postsolar, Patilleras, Talcos, Anti Acné, Contorno de Ojos,
  Antiedad, Despigmentante) usan coincidencia por título.

El árbol completo y las reglas están en `docs/categorias.py` para poder
regenerarlas.

**Menús** (Contenido → Navegación): `main-menu` (árbol de 3 niveles con
DESCUENTOS destacado), `footer-categorias`, `footer-unete-krika`, `footer-tyc`.

**Páginas**: `Marcas` (`/pages/marcas`, plantilla `page.marcas`).

## Pendientes del catálogo (fuera del alcance del tema)

- Los **precios importados desde VTEX son `0,00 COP`** en todo el catálogo. El
  tema muestra «Precio a consultar» mientras el precio sea 0, pero hay que
  cargar los precios reales antes de vender.
- Solo **99 productos activos están publicados en el canal Online Store**
  (de 8.569 activos), así que las vitrinas se ven vacías o muy cortas hasta que
  se publique el catálogo.
- El inventario está en 0 en los productos muestreados.
- Las colecciones de primer nivel (Capilar, Maquillaje, …) usan coincidencia
  parcial sobre el tipo de producto y arrastran algún producto de más (p. ej.
  «POLVO» lleva polvos decolorantes a Maquillaje). Las subcategorías del
  mega-menú sí usan coincidencia exacta y son precisas.
- **Logos de marca**: krika.co solo publica 11 logos y ninguna de sus 403 marcas
  tiene imagen en su catálogo VTEX, así que las demás marcas se muestran con
  logotipo tipográfico. Para añadir un logo real basta subir el archivo a
  Contenido → Archivos con el nombre `krika-marca-<handle>.png`.

## Publicar el tema

El tema está **sin publicar** a propósito. Para revisarlo:
*Tienda online → Temas → «Krika — Réplica VTEX» → Vista previa*.
