import json, collections, re, pickle

prods = {}
variants = collections.defaultdict(list)
images = collections.defaultdict(list)

with open('products.jsonl') as f:
    for line in f:
        o = json.loads(line)
        gid = o.get('id', '')
        if '__parentId' not in o and gid.startswith('gid://shopify/Product/'):
            prods[gid] = o
        elif gid.startswith('gid://shopify/ProductVariant/'):
            variants[o['__parentId']].append(o)
        elif 'image' in o:
            images[o['__parentId']].append(o)

for gid, p in prods.items():
    p['_variants'] = variants.get(gid, [])
    p['_images'] = [i['image'] for i in images.get(gid, []) if i.get('image')]

pickle.dump(prods, open('prods.pkl','wb'))
print('products:', len(prods))
print('variants:', sum(len(p['_variants']) for p in prods.values()))
print('images:', sum(len(p['_images']) for p in prods.values()))

DRESS_TYPES = {'Dresses', 'Maxi & Midi Dresses', 'Mini Dresses'}
dress_re = re.compile(r'\b(dress|gown)\b', re.I)

xtab = collections.Counter()
for p in prods.values():
    t = p.get('productType') or '(none)'
    has = bool(dress_re.search(p.get('title','')))
    xtab[(t, has)] += 1

print('\n%-24s %8s %8s' % ('TYPE', 'dress-ttl', 'no-dress-ttl'))
for t in sorted({k[0] for k in xtab}):
    print('%-24s %8d %8d %s' % (t, xtab[(t,True)], xtab[(t,False)], '<-- DRESS TYPE' if t in DRESS_TYPES else ''))
