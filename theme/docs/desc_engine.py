# -*- coding: utf-8 -*-
"""
Motor de descripciones de producto para Krika Cosmetics.

Lee el export JSONL del catalogo (bulk operation de Shopify) y genera para cada
producto una descripcion en HTML con: gancho, beneficios ("Pros"), modo de uso,
para quien es y un tip. La descripcion original del fabricante, si existe y es
util, se conserva al final bajo "Informacion del fabricante".

Uso:
    python3 desc_engine.py products.jsonl salida/
"""
import csv, html, json, os, re, sys, unicodedata

from desc_tipos import TIPOS, GENERICO

# --------------------------------------------------------------------------
# Utilidades de texto
# --------------------------------------------------------------------------

def sin_tildes(s):
    return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()

def plano(h):
    """HTML -> texto plano normalizado."""
    t = re.sub(r'<[^>]+>', ' ', h or '')
    t = html.unescape(t)
    return re.sub(r'\s+', ' ', t).strip()

SIGLAS = {'SPF', 'FPS', 'UV', 'UVA', 'UVB', 'LED', 'UVLED', 'BB', 'CC', 'HD', 'PH',
          'XL', 'XXL', 'ML', 'NT', '3D', 'AHA', 'BHA', 'PRO', 'USB', 'TV', 'DVD'}


def titulo_bonito(t):
    """'SHAMPOO ALFAPARFx500ml LISSE DESIGN' -> 'Shampoo Alfaparf 500 ml Lisse Design'."""
    t = re.sub(r'x(\d)', r' \1', t)
    t = re.sub(r'(\d)\s*(ml|gr|g|kg|cc|oz|mg|lt|l)\b', r'\1 \2', t, flags=re.I)
    t = re.sub(r'x\s*und\b', '', t, flags=re.I)
    t = re.sub(r'\s+', ' ', t).strip()
    palabras = []
    for w in t.split(' '):
        if re.fullmatch(r'[\d.,]+', w) or re.fullmatch(r'(ml|gr|g|kg|cc|oz|mg|lt|l)', w, re.I):
            palabras.append(w.lower() if w.isalpha() else w)
        elif w.upper() in SIGLAS:
            palabras.append(w.upper())
        elif not w.isalpha() and w.isupper():
            palabras.append(w)                      # codigos tipo 9NB, 1000ML
        else:
            palabras.append(w.capitalize())
    return ' '.join(palabras)

# --------------------------------------------------------------------------
# Parseo del titulo: TIPO + MARCAxTAMANO + VARIANTE
# --------------------------------------------------------------------------

UNIDADES = r'(?:ml|mls|gr|grs|g|kg|cc|oz|mg|lt|lts|l|und|unds|u|uds|pcs|pares|par)'
RE_TAM = re.compile(r'x\s*(\d+(?:[.,]\d+)?)?\s*(' + UNIDADES + r')\b', re.I)

def formatea_tamano(num, uni):
    if not num:
        return None
    uni = uni.lower()
    uni = {'mls': 'ml', 'grs': 'g', 'gr': 'g', 'lts': 'l', 'lt': 'l',
           'unds': 'und', 'uds': 'und', 'u': 'und'}.get(uni, uni)
    num = num.replace(',', '.')
    if num.endswith('.0'):
        num = num[:-2]
    if uni == 'und':
        return '%s unidades' % num if num not in ('1',) else '1 unidad'
    return '%s %s' % (num, uni)

def ml_equivalentes(num, uni):
    """Tamano aproximado en ml/g para decidir si es formato viaje o profesional."""
    if not num:
        return None
    try:
        v = float(num.replace(',', '.'))
    except ValueError:
        return None
    uni = uni.lower()
    if uni in ('l', 'lt', 'lts', 'kg'):
        return v * 1000
    if uni in ('ml', 'mls', 'g', 'gr', 'grs', 'cc'):
        return v
    if uni == 'oz':
        return v * 29.5
    return None

def parsea(titulo, marca):
    """Devuelve (tipo_texto, tamano, variante, ml_equiv)."""
    m = RE_TAM.search(titulo)
    tamano = variante = None
    ml = None
    if m:
        antes = titulo[:m.start()].strip()
        variante = titulo[m.end():].strip(' -–—·,')
        tamano = formatea_tamano(m.group(1), m.group(2))
        ml = ml_equivalentes(m.group(1), m.group(2))
    else:
        antes = titulo
        variante = ''
    # quitar la marca del tramo inicial para quedarnos con el tipo
    tipo_txt = antes
    if marca:
        tipo_txt = re.sub(re.escape(marca) + r'\s*$', '', antes, flags=re.I).strip()
        if not tipo_txt:
            tipo_txt = antes
    return tipo_txt.strip(), tamano, (variante or '').strip(), ml

# --------------------------------------------------------------------------
# Atributos detectados en el nombre -> beneficios extra
# --------------------------------------------------------------------------

ATRIBUTOS = [
    # (regex sobre el titulo sin tildes y en mayuscula, beneficio)
    (r'\bSPF\s*\d+|\bFPS\s*\d+',      'Incluye filtro solar, así que suma protección frente a la radiación UV en tu rutina diaria.'),
    (r'KERATIN|QUERATIN',             'Con queratina, la proteína que rellena la fibra capilar y devuelve resistencia al pelo castigado.'),
    (r'\bARGAN',                      'Con aceite de argán, uno de los mejores aliados para dar brillo y suavidad sin apelmazar.'),
    (r'\bCOCO\b',                     'Con coco, que nutre en profundidad y deja un aroma tropical difícil de resistir.'),
    (r'ALMENDRA',                     'Con aceite de almendras, suave incluso en pieles y cabellos sensibles.'),
    (r'\bOLIVA\b',                    'Con aceite de oliva, nutrición intensa para fibras secas y quebradizas.'),
    (r'ROMERO',                       'Con romero, tradicionalmente usado para estimular el cuero cabelludo.'),
    (r'CEBOLLA',                      'Con extracto de cebolla, uno de los ingredientes más buscados para fortalecer el cabello.'),
    (r'BIOTINA',                      'Con biotina, un clásico en las rutinas de fortalecimiento capilar.'),
    (r'COLAGENO',                     'Con colágeno, para un acabado más firme y con mejor textura.'),
    (r'HIALURONICO|HYALURON',         'Con ácido hialurónico, que retiene agua y deja la piel visiblemente más jugosa.'),
    (r'NIACINAMIDA|NIACINAMIDE',      'Con niacinamida, ideal para trabajar textura, poros y luminosidad.'),
    (r'RETINOL',                      'Con retinol, el activo de referencia para renovar la piel.'),
    (r'VITAMINA C|VIT C|\bVIT\.? ?C', 'Con vitamina C, que aporta luminosidad y ayuda a unificar el tono.'),
    (r'VITAMINA E|VIT E',             'Con vitamina E, antioxidante y muy agradecida en pieles secas.'),
    (r'\bALOE|SABILA',                'Con aloe vera, calmante y refrescante desde la primera aplicación.'),
    (r'CAFEINA|\bCAFE\b',             'Con cafeína, un activo habitual en rutinas reafirmantes.'),
    (r'CARBON|CHARCOAL',              'Con carbón activado, que arrastra impurezas y exceso de grasa.'),
    (r'ARCILLA|\bCLAY\b',             'Con arcilla, que purifica y matifica sin resecar.'),
    (r'\bAVENA\b',                    'Con avena, suave y calmante para pieles reactivas.'),
    (r'MANZANILLA',                   'Con manzanilla, que realza los reflejos claros y calma.'),
    (r'ORTIGA',                       'Con ortiga, tradicional en tratamientos para cuero cabelludo graso.'),
    (r'\bBIOTIN',                     'Con biotina para reforzar la fibra.'),
    (r'\bMIEL\b',                     'Con miel, humectante natural de acabado suave.'),
    (r'KARITE|SHEA',                  'Con manteca de karité, nutrición intensa de larga duración.'),
    (r'\bMATTE|MATE\b',               'Acabado mate, sin brillos y con ese aire sofisticado que no pasa de moda.'),
    (r'\bGLOSS|BRILLO\b',             'Acabado con brillo, para un efecto jugoso y luminoso.'),
    (r'METALIZAD|METALIC',            'Acabado metalizado, perfecto cuando querés que la mirada vaya directo ahí.'),
    (r'GLITTER|ESCARCHA',             'Con glitter, para los looks de noche y ocasiones especiales.'),
    (r'\bSATIN',                      'Acabado satinado: ni mate ni brillante, el punto medio más favorecedor.'),
    (r'VOLUMEN|VOLUME',               'Formulado para aportar volumen y cuerpo desde la raíz.'),
    (r'\bRIZO|\bCURL|CRESPO|ONDULAD', 'Pensado para cabello rizado y ondulado: define sin apelmazar.'),
    (r'\bLISO\b|LISS|SMOOTH|ALISA',   'Trabaja a favor del liso y ayuda a domar el frizz.'),
    (r'ANTICASPA|\bCASPA\b',          'Acción anticaspa para mantener el cuero cabelludo limpio y equilibrado.'),
    (r'ANTICAIDA|CAIDA|\bFALL\b',     'Formulado como apoyo en rutinas anticaída.'),
    (r'CRECIMIENT|CRECE|GROWTH',      'Pensado para acompañar rutinas de crecimiento capilar.'),
    (r'REPARA|REPAIR|RECONSTRU',      'Acción reparadora sobre fibras dañadas por calor, color o químicos.'),
    (r'NUTRITIV|NUTRICION|NOURISH',   'Nutrición profunda para cabellos secos y sin vida.'),
    (r'HIDRATA|HYDRA|MOIST',          'Hidratación real y sostenida, no solo sensación momentánea.'),
    (r'ANTIFRIZZ|ANTI-FRIZZ|FRIZZ',   'Control de frizz incluso en días húmedos.'),
    (r'TERMOPROTECT|HEAT PROTECT',    'Protege del calor de plancha y secador, clave si usás herramientas a diario.'),
    (r'SIN SULFAT|SULFATE FREE',      'Sin sulfatos: más amable con el color y con los cueros cabelludos sensibles.'),
    (r'VEGAN',                        'Fórmula vegana.'),
    (r'HIPOALERG',                    'Fórmula hipoalergénica, pensada para pieles delicadas.'),
    (r'OIL ?FREE|LIBRE DE ACEITE',    'Libre de aceites, ideal para pieles mixtas y grasas.'),
    (r'WATERPROOF|A PRUEBA DE AGUA',  'Resistente al agua: aguanta el calor, la humedad y alguna que otra lágrima.'),
    (r'LARGA DURACION|LONG ?LAST|24H|12H|8H', 'De larga duración: se queda donde lo pusiste durante horas.'),
    (r'\bMICELAR',                    'Tecnología micelar: arrastra impurezas sin frotar ni resecar.'),
    (r'\bPROFESIONAL|\bPRO\b|SALON',  'Calidad profesional, la misma que se usa en salón.'),
    (r'\bINFANTIL|\bBEBE|\bNINO|KIDS', 'Formulado para los más pequeños de la casa.'),
    (r'\bMEN\b|HOMBRE|MASCULINO',     'Pensado específicamente para el cuidado masculino.'),
]
ATRIBUTOS = [(re.compile(rx), txt) for rx, txt in ATRIBUTOS]

def beneficios_por_atributo(titulo, limite=3):
    t = sin_tildes(titulo).upper()
    out = []
    vistos = set()
    for rx, txt in ATRIBUTOS:
        if rx.search(t) and txt not in vistos:
            out.append(txt); vistos.add(txt)
            if len(out) >= limite:
                break
    return out

# --------------------------------------------------------------------------
# Composicion de la descripcion
# --------------------------------------------------------------------------

def bullets_formato(ml, tamano, cat):
    """Beneficio derivado del tamano del envase."""
    if ml is None:
        return None
    if ml >= 900:
        return 'Formato de %s: rinde muchísimo y baja el costo por uso, perfecto para salón o para quien ya sabe que lo va a repetir.' % tamano
    if ml >= 400:
        return 'Formato grande de %s, pensado para uso frecuente sin quedarte a mitad de camino.' % tamano
    if ml <= 60 and cat not in ('unas', 'maquillaje'):
        return 'Tamaño de %s: entra en cualquier neceser y viaja sin problema.' % tamano
    return None

def compone(tipo_cfg, datos):
    marca   = datos['marca']
    tamano  = datos['tamano']
    variante= datos['variante']
    titulo  = datos['titulo_bonito']
    extra   = datos['extra']

    det = tipo_cfg.get('det', 'Este')
    noun = tipo_cfg['noun']

    # --- gancho -----------------------------------------------------------
    linea = ''
    codigo = None
    if variante:
        v = titulo_bonito(variante)
        if len(v) > 45:
            v = v[:45].rsplit(' ', 1)[0]
        if re.fullmatch(r'[\d/.\-]+[A-Za-z]{0,3}', variante.strip()):
            codigo = variante.strip()          # tono o referencia, va en su propia linea
        else:
            linea = ' de la línea %s' % v
    marca_txt = ' de %s' % marca.title() if marca else ''
    medida = ' en presentación de %s' % tamano if tamano else ''

    gancho = '%s %s%s%s%s %s' % (det, noun, marca_txt, linea, medida, tipo_cfg['intro'])
    gancho = re.sub(r'\s+', ' ', gancho).strip()
    if not gancho.endswith('.'):
        gancho += '.'

    partes = ['<p><strong>%s</strong></p>' % html.escape(titulo),
              '<p>%s</p>' % html.escape(gancho)]

    if codigo:
        etiqueta = 'Tono' if tipo_cfg.get('cat') in ('color', 'unas', 'maquillaje') else 'Referencia'
        partes.append('<p><strong>%s:</strong> %s</p>' % (etiqueta, html.escape(codigo)))

    # --- pros -------------------------------------------------------------
    pros = list(tipo_cfg['pros'])
    pros = pros[:4] + extra
    fmt = bullets_formato(datos['ml'], tamano, tipo_cfg.get('cat', ''))
    if fmt:
        pros.append(fmt)
    partes.append('<p><strong>Por qué te va a gustar</strong></p><ul>%s</ul>'
                  % ''.join('<li>%s</li>' % html.escape(p) for p in pros))

    # --- modo de uso ------------------------------------------------------
    uso = tipo_cfg.get('uso')
    if uso:
        titulo_uso = tipo_cfg.get('titulo_uso', 'Modo de uso')
        partes.append('<p><strong>%s</strong></p><ol>%s</ol>'
                      % (titulo_uso, ''.join('<li>%s</li>' % html.escape(p) for p in uso)))

    # --- para quien -------------------------------------------------------
    if tipo_cfg.get('ideal'):
        partes.append('<p><strong>Ideal para:</strong> %s</p>' % html.escape(tipo_cfg['ideal']))
    if tipo_cfg.get('tip'):
        partes.append('<p><strong>Tip Krika:</strong> %s</p>' % html.escape(tipo_cfg['tip']))

    return ''.join(partes)

MIN_FABRICANTE = 120   # descripciones originales mas cortas que esto no aportan

def descripcion(prod):
    marca = (prod.get('vendor') or '').strip()
    titulo = (prod.get('title') or '').strip()
    tipo_txt, tamano, variante, ml = parsea(titulo, marca)

    cfg = TIPOS.get(prod.get('productType') or '', GENERICO)

    datos = {
        'marca': marca,
        'tamano': tamano,
        'variante': variante,
        'ml': ml,
        'titulo_bonito': titulo_bonito(titulo),
        'extra': beneficios_por_atributo(titulo, limite=3),
    }
    cuerpo = compone(cfg, datos)

    original = (prod.get('descriptionHtml') or '').strip()
    if len(plano(original)) >= MIN_FABRICANTE:
        cuerpo += '<p><strong>Información del fabricante</strong></p>' + original

    return cuerpo

# --------------------------------------------------------------------------
# Salida CSV para importar en Shopify
# --------------------------------------------------------------------------

COLUMNAS = ['Handle', 'Title', 'Body (HTML)']

def exporta(rows, destino, por_archivo=2000):
    os.makedirs(destino, exist_ok=True)
    archivos = []
    for i in range(0, len(rows), por_archivo):
        lote = rows[i:i + por_archivo]
        ruta = os.path.join(destino, 'krika-descripciones-%02d.csv' % (i // por_archivo + 1))
        with open(ruta, 'w', encoding='utf-8-sig', newline='') as f:
            w = csv.DictWriter(f, fieldnames=COLUMNAS)
            w.writeheader()
            for r in lote:
                w.writerow({'Handle': r['handle'], 'Title': r['title'], 'Body (HTML)': r['body']})
        archivos.append((ruta, len(lote), os.path.getsize(ruta)))
    return archivos

def main():
    origen = sys.argv[1] if len(sys.argv) > 1 else 'products.jsonl'
    destino = sys.argv[2] if len(sys.argv) > 2 else 'csv'
    solo_vacios = '--solo-vacios' in sys.argv

    prods = [json.loads(l) for l in open(origen, encoding='utf-8')]
    if solo_vacios:
        prods = [p for p in prods if len(plano(p.get('descriptionHtml'))) < MIN_FABRICANTE]

    faltantes = set()
    rows = []
    for p in prods:
        if (p.get('productType') or '') not in TIPOS:
            faltantes.add(p.get('productType') or '(sin tipo)')
        rows.append({'handle': p['handle'], 'title': p['title'], 'body': descripcion(p)})

    archivos = exporta(rows, destino)
    largos = sorted(len(plano(r['body'])) for r in rows)
    print('productos procesados: %d' % len(rows))
    print('largo del texto: min %d / mediana %d / max %d' %
          (largos[0], largos[len(largos) // 2], largos[-1]))
    if faltantes:
        print('tipos sin copy propio (usan el generico): %d -> %s'
              % (len(faltantes), sorted(faltantes)[:10]))
    for ruta, n, size in archivos:
        print('  %s  %d filas  %.1f MB' % (ruta, n, size / 1024 / 1024))

if __name__ == '__main__':
    main()
