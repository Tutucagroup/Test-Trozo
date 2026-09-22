import pickle, re, html, json, collections
prods = pickle.load(open('prods.pkl','rb'))
keep = set(json.load(open('keep_ids.json')))
K = [p for p in prods.values() if p['id'] in keep]

def lis(h):
    if not h: return []
    items = re.findall(r'<li[^>]*>(.*?)</li>', h, re.S|re.I)
    if not items:
        items = [x for x in re.split(r'<br\s*/?>|</p>', h) if x.strip()]
    out = []
    for i in items:
        t = html.unescape(re.sub(r'<[^>]+>', ' ', i))
        t = re.sub(r'\s+', ' ', t).strip().strip('.,;')
        if t: out.append(t)
    return out

stats = collections.Counter()
sample_unparsed = []
for p in K:
    L = lis(p.get('descriptionHtml'))
    comp = [x for x in L if '%' in x]
    care = [x for x in L if re.search(r'\b(wash|dry clean|hand wash|do not)\b', x, re.I) and '%' not in x]
    # a fit line is SHORT and only about stretch/lining — long lines are feature lists
    fit  = [x for x in L if re.search(r'\b(stretch|lined|unlined)\b', x, re.I) and '%' not in x
            and x not in care and len(x.split()) <= 6]
    rest = [x for x in L if x not in comp and x not in care and x not in fit]
    p['_L'] = L; p['_comp'] = comp; p['_care'] = care; p['_fit'] = fit; p['_rest'] = rest
    stats['has_comp' if comp else 'NO_comp'] += 1
    stats['has_care' if care else 'NO_care'] += 1
    stats['has_fit'  if fit  else 'NO_fit']  += 1
    stats['has_rest' if rest else 'NO_rest'] += 1
    if not rest and len(sample_unparsed) < 5: sample_unparsed.append((p['title'], L))

print('parsed', len(K), 'dresses')
for k in sorted(stats): print('  %-10s %5d' % (k, stats[k]))
print('\n--- products with no silhouette/detail line ---')
for t, L in sample_unparsed: print(' *', t, '=>', L)
pickle.dump(K, open('keep_parsed.pkl','wb'))
