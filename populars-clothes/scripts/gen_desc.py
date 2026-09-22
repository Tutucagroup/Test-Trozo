# -*- coding: utf-8 -*-
"""Original Populars Clothes product copy, built from each garment's real specs."""
import re, html, hashlib

# ---------------------------------------------------------------- attributes
LENGTH = [('maxi', 'maxi'), ('midi', 'midi'), ('mini', 'mini')]
NECKLINES = [
    ('off shoulder', 'off-the-shoulder'), ('off-shoulder', 'off-the-shoulder'),
    ('one shoulder', 'one-shoulder'), ('one-shoulder', 'one-shoulder'),
    ('strapless', 'strapless'), ('halter', 'halter'), ('cowl', 'cowl'),
    ('sweetheart', 'sweetheart'), ('square neck', 'square'), ('scoop', 'scoop'),
    ('v-neck', 'V'), ('v neck', 'V'), ('plunge', 'plunging'),
    ('high neck', 'high'), ('boat neck', 'boat'), ('keyhole', 'keyhole'),
]
FABRICS = [
    ('sequin', 'sequin'), ('satin', 'satin'), ('mesh', 'mesh'), ('chiffon', 'chiffon'),
    ('lace', 'lace'), ('linen', 'linen'), ('denim', 'denim'), ('velvet', 'velvet'),
    ('crochet', 'crochet'), ('tulle', 'tulle'), ('organza', 'organza'),
    ('bandage', 'bandage'), ('knit', 'knit'), ('rib', 'ribbed'), ('shimmer', 'shimmer'),
    ('taffeta', 'taffeta'), ('poplin', 'poplin'), ('jersey', 'jersey'), ('tweed', 'tweed'),
]
PATTERNS = [
    ('floral', 'floral'), ('polka', 'polka dot'), ('stripe', 'striped'),
    ('check', 'checked'), ('paisley', 'paisley'), ('leopard', 'leopard'),
    ('animal', 'animal'), ('gingham', 'gingham'), ('tie dye', 'tie-dye'), ('plaid', 'plaid'),
]
SHAPES = [
    ('bodycon', 'body-skimming'), ('a-line', 'A-line'), ('a line', 'A-line'),
    ('slim fit', 'slim-fitting'), ('slim-fit', 'slim-fitting'), ('shift', 'shift'),
    ('wrap', 'wrap'), ('corset', 'corseted'), ('drop waist', 'drop-waist'),
    ('empire', 'empire-line'), ('flared', 'flared'), ('tiered', 'tiered'),
    ('babydoll', 'babydoll'), ('bubble hem', 'bubble-hem'), ('fit and flare', 'fit-and-flare'),
]
FEATURES = [
    ('ruch', 'ruching'), ('shirred', 'shirring'), ('pleat', 'pleating'),
    ('split', 'a leg split'), ('slit', 'a leg split'), ('cut-out', 'cut-out detail'),
    ('cut out', 'cut-out detail'), ('cutout', 'cut-out detail'),
    ('frill', 'frill trim'), ('ruffle', 'ruffle detail'), ('tie-back', 'a tie back'),
    ('tie back', 'a tie back'), ('open back', 'an open back'), ('low back', 'a low back'),
    ('backless', 'an open back'), ('twist', 'a twist detail'), ('knot', 'a knot detail'),
    ('bow', 'a bow detail'), ('lace up', 'lace-up detail'), ('lace-up', 'lace-up detail'),
    ('beaded', 'beading'), ('embellish', 'embellishment'), ('embroider', 'embroidery'),
    ('fringe', 'fringing'), ('feather', 'feather trim'), ('button', 'button detail'),
    ('pocket', 'pockets'), ('belt', 'a belt'), ('asymmetric', 'an asymmetric hem'),
]
OCCASION_TAGS = {
    'Wedding Guest Dresses': 'weddings and garden parties',
    'Cocktail Dresses': 'cocktail hour',
    'Formal Dresses': 'formal evenings',
    'Formal & Fancy Dresses': 'black-tie and formal evenings',
    'Homecoming Dresses': 'homecoming',
    'Party Dresses': 'parties',
    'Birthday Dresses': 'birthdays',
    'Date Night Dresses': 'date night',
    'Going Out Dresses': 'nights out',
    'Casual Dresses': 'easy everyday wear',
    'Basic Dresses': 'everyday wear',
    'Fall Dresses': 'cooler months',
}
COLOR_WORDS = ['black','white','red','blue','navy','green','pink','brown','beige','cream','yellow',
               'purple','lilac','lavender','orange','grey','gray','silver','gold','burgundy','wine',
               'mauve','sage','olive','teal','chocolate','latte','ivory','champagne','charcoal',
               'coral','peach','mint','rose','emerald','cherry','stone','denim','multi','aubergine']

def _kmatch(key, t):
    return re.search(r'(?<![a-z])' + re.escape(key) + r'(?![a-z])', t) is not None

def _find(text, table):
    t = text.lower()
    for key, val in table:
        if _kmatch(key, t):
            return val
    return None

def _find_all(text, table, limit=3):
    t, out = text.lower(), []
    for key, val in table:
        if _kmatch(key, t) and val not in out:
            out.append(val)
        if len(out) >= limit:
            break
    return out

def attrs(p):
    title = p['title']
    body = ' '.join(p['_rest'])
    both = title + ' ' + body
    a = {}
    a['length']   = _find(both, LENGTH) or ('midi' if 'Maxi & Midi' in (p.get('productType') or '') else 'mini')
    a['neckline'] = _find(both, NECKLINES)
    a['fabric']   = _find(both, FABRICS)
    a['pattern']  = _find(both, PATTERNS)
    a['shape']    = _find(both, SHAPES)
    a['features'] = _find_all(body, FEATURES, 3)
    # colour: prefer the Color option value, else trailing colour word in the title
    colour = None
    for o in (p.get('options') or []):
        if o['name'].lower() == 'color' and o.get('values'):
            colour = o['values'][0]
            break
    if not colour:
        for w in title.split():
            if w.lower().strip('/,') in COLOR_WORDS:
                colour = w.strip('/,')
    if colour:
        colour = re.sub(r'\s*/\s*', ' and ', colour.strip()).lower()
    a['colour'] = colour or None
    # size range line (Petite / Curve / Tall)
    a['range'] = None
    for r in ('Petite', 'Curve', 'Tall'):
        if re.search(r'\b%s\b' % r, title):
            a['range'] = r
    # occasions from tags
    occ = [OCCASION_TAGS[t] for t in (p.get('tags') or []) if t in OCCASION_TAGS]
    a['occasions'] = occ[:2]
    # lining / stretch
    fit = ' '.join(p['_fit']).lower()
    a['lined']   = 'fully lined' if 'fully lined' in fit else ('part-lined' if 'lined' in fit and 'unlined' not in fit else ('unlined' if 'unlined' in fit else None))
    a['stretch'] = ('good stretch' if 'good stretch' in fit else
                    'a little stretch' if 'stretch' in fit and 'non-stretch' not in fit else
                    'no stretch' if 'non-stretch' in fit else None)
    comp = ' '.join(p['_comp'])
    a['eco'] = bool(re.search(r'reclaimed|recycled', comp, re.I))
    comp = re.sub(r'(\d)%\s*(?=[A-Za-z])', r'\1% ', comp)
    comp = re.sub(r'\s*,\s*', ', ', comp)
    comp = re.sub(r'\s+', ' ', comp).strip().rstrip(',')
    comp = re.sub(r'(?i)\blining:', 'Lining:', comp)
    comp = re.sub(r'(?i)\bmain:', 'Main:', comp)
    a['comp'] = comp
    a['care'] = ' '.join(p['_care'])
    # the source's own silhouette sentence, cleaned of brand-replacement artefacts
    a['spec'] = [re.sub(r'Populars Clothes\s*(Lower Impact|Petite|Curve|Tall)?', '', x).strip(' ,-')
                 for x in p['_rest']]
    a['spec'] = [_fixtypos(x) for x in a['spec'] if x]
    return a

TYPOS = [(r'\bpleast\b', 'pleat'), (r'\bsilicon\b', 'silicone'),
         (r'\bsiliconee\b', 'silicone'), (r'\bfastning\b', 'fastening'),
         (r'\badjsutable\b', 'adjustable'), (r'\bneckine\b', 'neckline'),
         (r'\bdetailling\b', 'detailing'), (r'\bmaterail\b', 'material')]

def _fixtypos(s):
    for pat, rep in TYPOS:
        s = re.sub(pat, rep, s, flags=re.I)
    return s

# ---------------------------------------------------------------- copy
def _pick(options, seed, salt):
    h = int(hashlib.md5((seed + salt).encode()).hexdigest(), 16)
    return options[h % len(options)]

def name_of(title):
    """The style name: the leading words before the silhouette/colour words."""
    stop = re.compile(r'\b(mini|midi|maxi|dress|gown|strapless|halter|satin|sequin|lace|mesh|'
                      r'floral|petite|curve|tall|one|off|long|short|sleeve|neck|cowl|v|square|'
                      r'scoop|high|low|back|wrap|corset|bodycon|a-line|tiered|frill|linen|knit|'
                      r'chiffon|velvet|denim|shimmer|sheer|bubble|hem|drop|waist|cut|out|keyhole)\b', re.I)
    words = title.split()
    out = []
    for w in words:
        if stop.search(w) or w.lower().strip('/,') in COLOR_WORDS:
            break
        out.append(w)
    return ' '.join(out) if out else words[0]

def opener(p, a, seed):
    nm = name_of(p['title'])
    L = a['length']
    fab = a['fabric']
    pat = a['pattern']
    neck = a['neckline']
    col = a['colour']

    noun_bits = []
    if pat: noun_bits.append(pat)
    if fab: noun_bits.append(fab)
    noun = ' '.join(noun_bits + ['%s dress' % L]) if noun_bits else '%s dress' % L

    neck_clause = {
        None: '',
        'strapless': ' with a strapless neckline',
        'halter': ' with a halter neckline',
        'cowl': ' with a soft cowl neckline',
        'sweetheart': ' with a sweetheart neckline',
        'off-the-shoulder': ' with an off-the-shoulder neckline',
        'one-shoulder': ' with a one-shoulder neckline',
        'plunging': ' with a plunging neckline',
        'keyhole': ' with a keyhole front',
    }.get(neck, ' with a %s neckline' % neck if neck else '')

    colour_clause = ' in %s' % col if col else ''

    templates = [
        "The {nm} is a {noun}{neck}, cut{colour} to sit close through the bodice and move easily from there.",
        "Meet the {nm}: a {noun}{neck}, finished{colour} with the kind of detail that reads considered rather than fussy.",
        "The {nm} takes a {noun} and gives it a clean, confident line{neck}{colour}.",
        "A {noun}{neck}, the {nm} is built{colour} around an easy shape that flatters without pulling focus.",
        "The {nm} is our take on the {noun}{neck} — quietly striking{colour}, and comfortable enough to wear all evening.",
        "Cut as a {noun}{neck}, the {nm} balances a defined bodice{colour} with a skirt that moves.",
    ]
    s = _pick(templates, seed, 'open').format(nm=nm, noun=noun, neck=neck_clause, colour=colour_clause)
    return s[0].upper() + s[1:]

def second(p, a, seed):
    bits = []
    feats = a['features']
    shape = a['shape']
    if shape and feats:
        bits.append(_pick([
            "A {shape} cut is finished with {f}.",
            "The {shape} silhouette is detailed with {f}.",
            "Expect a {shape} shape, with {f}.",
        ], seed, 's1').format(shape=shape, f=_join(feats)))
    elif feats:
        bits.append(_pick([
            "Look closer for {f}.",
            "It's finished with {f}.",
            "Details include {f}.",
        ], seed, 's2').format(f=_join(feats)))
    elif shape:
        bits.append(_pick([
            "The cut is {shape} and deliberately simple.",
            "A {shape} shape keeps it clean.",
        ], seed, 's3').format(shape=shape))

    # fabric handle
    hand = []
    if a['stretch'] == 'good stretch':
        hand.append("The fabric has a generous stretch")
    elif a['stretch'] == 'a little stretch':
        hand.append("There's a little give in the fabric")
    elif a['stretch'] == 'no stretch':
        hand.append("The fabric holds its shape with no stretch")
    joiner = 'and ' if hand else ''
    if a['lined'] == 'fully lined':
        hand.append(joiner + ("it's fully lined" if joiner else "It's fully lined"))
    elif a['lined'] == 'part-lined':
        hand.append(joiner + ("the bodice is lined" if joiner else "The bodice is lined"))
    elif a['lined'] == 'unlined':
        hand.append(joiner + ("it's left unlined" if joiner else "It's left unlined"))
    if hand:
        bits.append(' '.join(hand) + '.')
    return ' '.join(bits)

def third(p, a, seed):
    out = []
    if a['occasions'] and _pick([1, 1, 1, 0], seed, 'occ-skip'):
        out.append(_pick([
            "One for {o}.",
            "We'd wear it for {o}.",
            "Made with {o} in mind.",
            "It earns its place at {o}.",
            "Filed under {o}.",
            "Built for {o}.",
            "Our pick for {o}.",
            "Pull it out for {o}.",
            "Keep it for {o}.",
            "Tailor-made for {o}.",
        ], seed, 'occ').format(o=_join(a['occasions'])))
    if a['eco']:
        out.append(_pick([
            "Made using reclaimed fibres.",
            "Cut from fabric woven with reclaimed fibres.",
            "Part of our ongoing move toward reclaimed and recycled fabrics.",
        ], seed, 'eco'))
    if a['range']:
        out.append({
            'Petite': "Cut to our Petite fit, shortened through the body and skirt.",
            'Curve':  "Cut to our Curve fit, graded for a fuller bust and hip.",
            'Tall':   "Cut to our Tall fit, lengthened through the body and skirt.",
        }[a['range']])
    return ' '.join(out)

def _join(items):
    items = list(items)
    if len(items) == 1: return items[0]
    if len(items) == 2: return '%s and %s' % tuple(items)
    return '%s and %s' % (', '.join(items[:-1]), items[-1])

def build_html(p):
    a = attrs(p)
    seed = p['handle']
    paras = [x for x in (opener(p, a, seed), second(p, a, seed), third(p, a, seed)) if x]
    body = ''.join('<p>%s</p>' % html.escape(x) for x in paras)

    details = []
    for s in a['spec']:
        details.append(s[0].upper() + s[1:])
    fitline = []
    if a['stretch']: fitline.append(a['stretch'].capitalize())
    if a['lined']:   fitline.append(a['lined'].capitalize())
    if fitline: details.append(', '.join(fitline))
    if a['comp']: details.append(a['comp'])
    if details:
        body += '<p><strong>Details</strong></p><ul>' + ''.join(
            '<li>%s</li>' % html.escape(d) for d in details) + '</ul>'

    extras = []
    extras.append('Model wears a US 4 / UK 8 unless stated. See the size guide for garment measurements.')
    if a['care']: extras.append('Care: %s.' % a['care'].rstrip('.'))
    body += '<p><strong>Fit &amp; care</strong></p><ul>' + ''.join(
        '<li>%s</li>' % html.escape(e) for e in extras) + '</ul>'
    return body

def build_seo(p):
    a = attrs(p)
    nm = name_of(p['title'])
    bits = [b for b in (a['colour'], a['fabric'], a['neckline']) if b]
    lead = ' '.join(bits[:2])
    d = "%s — %s %s dress by Populars Clothes." % (nm, lead.strip().capitalize() or 'A', a['length'])
    d = re.sub(r'\s+', ' ', d)
    tail = " Free US & UK shipping over $100. 30-day returns."
    return (p['title'][:70], (d + tail)[:320])
