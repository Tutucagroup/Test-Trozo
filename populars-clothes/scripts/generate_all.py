import pickle, sys, re, collections, json
sys.path.insert(0,'.')
import gen_desc

K = pickle.load(open('keep_parsed.pkl','rb'))
SPEC_TYPES = {'Mini Dresses', 'Maxi & Midi Dresses'}

rewritten = kept = 0
for p in K:
    # products whose copy is a clean spec list (the scraped bulk) get fully rewritten;
    # the handful already written in house prose is left alone
    is_spec = len(p['_L']) >= 3 and all(len(x) < 220 for x in p['_L'])
    if is_spec:
        p['_new'] = gen_desc.build_html(p)
        p['_seo'] = gen_desc.build_seo(p)
        rewritten += 1
    else:
        p['_new'] = p.get('descriptionHtml') or ''
        seo = p.get('seo') or {}
        p['_seo'] = (seo.get('title') or p['title'], seo.get('description') or '')
        kept += 1

# four dresses were filed under the wrong product type / category — correct them
TYPE_FIX = {
    'Sleep Schedule Sleep Mini Dress Pink Polka': 'Mini Dresses',
    'Ambition Activewear Mini Dress Cherry':      'Mini Dresses',
    'Challengers Active Halter Mini Dress Black': 'Mini Dresses',
    'Black Poppy Sophie Dress':                   'Maxi & Midi Dresses',
}
DRESS_CAT = 'Apparel & Accessories > Clothing > Dresses'
fixed = 0
for p in K:
    p['_type'] = p.get('productType') or ''
    cat = (p.get('category') or {}).get('fullName') or ''
    p['_cat'] = cat
    if p['title'] in TYPE_FIX:
        p['_type'] = TYPE_FIX[p['title']]
        p['_cat'] = DRESS_CAT
        fixed += 1
print('rewritten:', rewritten, '| kept house copy:', kept, '| type/category corrected:', fixed)

# ---- QA ----
def txt(h):
    import html as H
    return re.sub(r'\s+',' ', H.unescape(re.sub(r'<[^>]+>',' ', h or ''))).strip()

bad = [p['title'] for p in K if re.search(r'Populars Clothes (Lower Impact|Petite|Curve|Tall)', txt(p['_new']))]
print('brand find/replace artefacts left:', len(bad))

news = [txt(p['_new']) for p in K]
dup = collections.Counter(news)
worst = [(n,d[:90]) for d,n in dup.most_common(5) if n>1]
print('unique descriptions:', len(dup), '/', len(news))
print('most repeated:', worst if worst else 'none')

lens=[len(n) for n in news]
print('desc length  min/median/max:', min(lens), sorted(lens)[len(lens)//2], max(lens))
short=[p['title'] for p in K if len(txt(p['_new']))<180]
print('under 180 chars:', len(short), short[:5])

# opener variety
op = collections.Counter(n.split('.')[0][:40] for n in news)
print('distinct opening shapes:', len(op))
pickle.dump(K, open('final.pkl','wb'))
