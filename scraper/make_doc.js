const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  Table, TableRow, TableCell, WidthType, BorderStyle, ShadingType,
  LevelFormat, PageBreak,
} = require("docx");

const BRAND = "2C6E63";      // verde
const ACCENT = "EC7C29";     // naranja Chester
const LIGHT = "F2F7F5";
const GREY = "6B7280";

const H = (t, level) => new Paragraph({ heading: level, spacing: { before: 260, after: 120 }, children: [new TextRun({ text: t, color: level === HeadingLevel.HEADING_1 ? BRAND : "1F2937" })] });
const P = (runs, opts = {}) => new Paragraph({ spacing: { after: 120, line: 276 }, ...opts, children: Array.isArray(runs) ? runs : [new TextRun(runs)] });
const T = (t, o = {}) => new TextRun({ text: t, ...o });
const bullet = (runs) => new Paragraph({ numbering: { reference: "bul", level: 0 }, spacing: { after: 80, line: 276 }, children: Array.isArray(runs) ? runs : [new TextRun(runs)] });
const num = (runs, ref = "steps") => new Paragraph({ numbering: { reference: ref, level: 0 }, spacing: { after: 100, line: 276 }, children: Array.isArray(runs) ? runs : [new TextRun(runs)] });
const code = (t) => new Paragraph({ spacing: { before: 60, after: 120 }, shading: { type: ShadingType.CLEAR, fill: "F3F4F6" }, border: { top: { style: BorderStyle.SINGLE, size: 2, color: "E5E7EB" }, bottom: { style: BorderStyle.SINGLE, size: 2, color: "E5E7EB" }, left: { style: BorderStyle.SINGLE, size: 2, color: "E5E7EB" }, right: { style: BorderStyle.SINGLE, size: 2, color: "E5E7EB" } }, children: [new TextRun({ text: t, font: "Consolas", size: 20, color: "B91C1C" })] });

function cell(text, { w, header = false, bold = false, fill } = {}) {
  return new TableCell({
    width: { size: w, type: WidthType.DXA },
    shading: fill ? { type: ShadingType.CLEAR, fill } : undefined,
    margins: { top: 60, bottom: 60, left: 110, right: 110 },
    children: [new Paragraph({ children: [new TextRun({ text, bold: header || bold, color: header ? "FFFFFF" : "1F2937", size: 20 })] })],
  });
}
function table(rows, widths, { headerFill = BRAND } = {}) {
  return new Table({
    columnWidths: widths,
    width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA },
    rows: rows.map((r, i) =>
      new TableRow({
        tableHeader: i === 0,
        children: r.map((c, j) => cell(c, { w: widths[j], header: i === 0, fill: i === 0 ? headerFill : (i % 2 === 0 ? LIGHT : undefined) })),
      })
    ),
  });
}

const deps = JSON.parse(fs.readFileSync("/tmp/deps.json", "utf8"));

const doc = new Document({
  numbering: {
    config: [
      { reference: "steps", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.START, style: { paragraph: { indent: { left: 420, hanging: 260 } } } }] },
      { reference: "steps2", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.START, style: { paragraph: { indent: { left: 420, hanging: 260 } } } }] },
      { reference: "bul", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.START, style: { paragraph: { indent: { left: 420, hanging: 260 } } } }] },
    ],
  },
  styles: { default: { document: { run: { font: "Calibri", size: 22, color: "1F2937" } } } },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1100, bottom: 1100, left: 1200, right: 1200 } } },
    children: [
      // Portada / título
      new Paragraph({ spacing: { after: 40 }, children: [new TextRun({ text: "Farmacias Chester · Shopify", color: ACCENT, bold: true, size: 24 })] }),
      new Paragraph({ spacing: { after: 60 }, border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: ACCENT } }, children: [new TextRun({ text: "Cómo agregar un producto nuevo", bold: true, size: 44, color: BRAND })] }),
      P([T("Guía práctica para dar de alta productos manteniendo el formato del catálogo y el vínculo automático con las colecciones inteligentes (smart collections).", { italics: true, color: GREY })]),

      // Idea clave
      H("Lo más importante: los Tags", HeadingLevel.HEADING_1),
      P([T("Tus colecciones son ", {}), T("inteligentes (automáticas)", { bold: true }), T(": se llenan solas con los productos que tengan el ", {}), T("tag", { bold: true }), T(" correspondiente. La regla de cada colección es ", {}), T("«Tag = nombre de la colección»", { italics: true }), T(".", {})]),
      P([T("➜ Si al producto nuevo le ponés los tags correctos, ", {}), T("aparece solo", { bold: true, color: BRAND }), T(" en su colección. Si no le ponés tags, queda sin colección (huérfano).", {})]),

      // Camino A
      H("Camino A — 1 o 2 productos sueltos (directo en Shopify)", HeadingLevel.HEADING_1),
      P([T("Es lo más rápido cuando son pocos.", { color: GREY })]),
      num("Entrá a Shopify → Productos → Agregar producto."),
      num("Cargá título, descripción, precio, imágenes y stock como siempre."),
      num([T("Paso clave — campo «Etiquetas» (Tags): ", { bold: true }), T("poné los tags de la ruta del producto, separados por coma. Ejemplo para un sérum facial:", {})]),
      code("dermocosmetica, skin-care, serum"),
      num([T("Completá también ", {}), T("Proveedor", { bold: true }), T(" (la marca, sirve de filtro) y ", {}), T("Tipo de producto", { bold: true }), T(" (la subcategoría).", {})]),
      num([T("Guardá. En cuanto queda con esos tags, el producto aparece automáticamente en las colecciones ", {}), T("dermocosmetica", { font: "Consolas", size: 20 }), T(", ", {}), T("skin-care", { font: "Consolas", size: 20 }), T(" y ", {}), T("serum", { font: "Consolas", size: 20 }), T(".", {})]),
      P([T("¿Qué tags poner? ", { bold: true }), T("Mirá la hoja ", {}), T("«Tags por categoría»", { italics: true }), T(" de la plantilla: buscás la subcategoría más específica del producto y copiás la última columna.", {})]),

      // Camino B
      H("Camino B — Varios productos (plantilla + Matrixify)", HeadingLevel.HEADING_1),
      P([T("Para cargar una tanda de una sola vez, usá el archivo ", {}), T("plantilla_nuevo_producto.xlsx", { bold: true, font: "Consolas", size: 20 }), T(".", {})]),
      num([T("Completá ", {}), T("una fila por producto", { bold: true }), T(" (viene 1 fila de ejemplo como guía y la hoja «Instrucciones» con qué va en cada columna).", {})], "steps2"),
      num([T("Campos mínimos: ", {}), T("Handle", { bold: true }), T(" (único), ", {}), T("Command = MERGE", { bold: true }), T(", Title, Vendor, Type, ", {}), T("Tags", { bold: true }), T(", Variant Price, Variant Inventory Qty, Image Src, y Option1 Name/Value = ", {}), T("Title / Default Title", { font: "Consolas", size: 20 }), T(".", {})], "steps2"),
      num([T("En Shopify → app ", {}), T("Matrixify → Import → Add file", { bold: true }), T(", subí la plantilla y confirmá.", {})], "steps2"),
      P([T("Como el comando es ", {}), T("MERGE", { bold: true }), T(", Matrixify ", {}), T("crea los nuevos y no toca los existentes", { bold: true }), T(" (no duplica).", {})]),

      new Paragraph({ children: [new PageBreak()] }),

      // Imágenes caveat
      H("⚠ Importante sobre las imágenes", HeadingLevel.HEADING_1),
      P([T("Si tomás la imagen del sitio viejo (", {}), T("cdn.batitienda.com", { font: "Consolas", size: 20 }), T("), Shopify puede rechazarla por un problema de formato (", {}), T("«unsupported file type – application/octet-stream»", { italics: true }), T("). Dos soluciones:", {})]),
      bullet([T("Lo más simple: ", { bold: true }), T("subí la imagen directo al producto en Shopify (arrastrando el archivo), en vez de pegar una URL del CDN.", {})]),
      bullet([T("Si usás URL del CDN y falla, ", {}), T("envolvela con el proxy de imágenes", { bold: true }), T(" (así se corrige el formato):", {})]),
      code("https://images.weserv.nl/?url=ssl:cdn.batitienda.com/baticloud/images/...."),

      // Referencia de tags
      H("Referencia rápida — Departamentos (tag base)", HeadingLevel.HEADING_1),
      P([T("Cada producto lleva el tag de su departamento + categoría + subcategoría (rollup). Estos son los 9 departamentos; el detalle completo con subcategorías está en la hoja ", {}), T("«Tags por categoría»", { italics: true }), T(".", {})]),
      table(
        [["Departamento", "Tag base"], ...deps.map(([h]) => [
          ({ "bebe-maternidad": "Bebé & Maternidad", "cuidado-salud": "Cuidado de la Salud", "cuidado-personal": "Cuidado Personal", "dermocosmetica": "Dermocosmética", "electro": "Electro", "infantiles": "Infantiles", "maquillaje": "Maquillaje", "nutricion-deporte": "Nutrición y Deporte", "perfumes-fragancias": "Perfumes & Fragancias" })[h], h])],
        [4400, 4400]
      ),
      P([T("Ejemplo de ruta completa: un protector solar facial lleva ", { color: GREY }), T("dermocosmetica, proteccion-solar, solar-rostro", { font: "Consolas", size: 20, color: GREY }), T(".", { color: GREY })]),

      // Resumen
      H("Resumen", HeadingLevel.HEADING_1),
      table(
        [
          ["¿Cuántos?", "Cómo", "No olvidar"],
          ["1 – 2", "Directo en Shopify (Agregar producto)", "Poner los Tags de la colección"],
          ["Varios", "Plantilla + Matrixify (Import, MERGE)", "Tags + Handle único"],
        ],
        [1900, 4100, 2800]
      ),
      P([T("Mientras el producto tenga los tags correctos, se vincula solo a las colecciones. No hay que asignarlo a mano.", { bold: true, color: BRAND })], { spacing: { before: 160 } }),
    ],
  }],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync("Guia_agregar_producto.docx", buf);
  console.log("OK Guia_agregar_producto.docx", buf.length, "bytes");
});
