# -*- coding: utf-8 -*-
import pickle, csv, os

K = pickle.load(open('final.pkl', 'rb'))
K.sort(key=lambda p: p['handle'])

COLS = ['Handle','Title','Body (HTML)','Vendor','Product Category','Type','Tags','Published',
        'Option1 Name','Option1 Value','Option2 Name','Option2 Value','Option3 Name','Option3 Value',
        'Variant SKU','Variant Grams','Variant Inventory Tracker','Variant Inventory Qty',
        'Variant Inventory Policy','Variant Fulfillment Service','Variant Price',
        'Variant Compare At Price','Variant Requires Shipping','Variant Taxable',
        'Gift Card','SEO Title','SEO Description','Status']

STOCK = 999

def opt_names(p):
    names = [o['name'] for o in sorted(p.get('options') or [], key=lambda o: o['position'])]
    return (names + ['', '', ''])[:3]

def opt_values(v, names):
    sel = {s['name']: s['value'] for s in (v.get('selectedOptions') or [])}
    return [sel.get(n, '') for n in names]

rows = []
for p in K:
    names = opt_names(p)
    variants = p['_variants']
    if not variants:
        continue
    for i, v in enumerate(variants):
        vals = opt_values(v, names)
        inv = v.get('inventoryItem') or {}
        r = {c: '' for c in COLS}
        r['Handle'] = p['handle']
        # option NAMES repeat on every row; product-level fields only on the first
        r['Option1 Name'], r['Option2 Name'], r['Option3 Name'] = names
        r['Option1 Value'], r['Option2 Value'], r['Option3 Value'] = vals
        if i == 0:
            r['Title']            = p['title']
            r['Body (HTML)']      = p['_new']
            r['Vendor']           = p.get('vendor') or 'Populars Clothes'
            r['Product Category'] = p.get('_cat') or ''
            r['Type']             = p.get('_type') or ''
            r['Tags']             = ', '.join(p.get('tags') or [])
            r['Published']        = 'TRUE'
            r['Gift Card']        = 'FALSE'
            r['SEO Title']        = (p['_seo'][0] or '')[:70]
            r['SEO Description']  = (p['_seo'][1] or '')[:320]
            r['Status']           = 'active'
        r['Variant SKU']                 = v.get('sku') or ''
        r['Variant Grams']               = '0'
        r['Variant Inventory Tracker']   = 'shopify'
        r['Variant Inventory Qty']       = STOCK
        r['Variant Inventory Policy']    = 'deny'
        r['Variant Fulfillment Service'] = 'manual'
        r['Variant Price']               = v.get('price') or ''
        r['Variant Compare At Price']    = v.get('compareAtPrice') or ''
        r['Variant Requires Shipping']   = 'TRUE' if inv.get('requiresShipping', True) else 'FALSE'
        r['Variant Taxable']             = 'TRUE' if v.get('taxable', True) else 'FALSE'
        rows.append(r)

out = 'populars_clothes_vestidos.csv'
with open(out, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=COLS)
    w.writeheader()
    w.writerows(rows)

size = os.path.getsize(out)
print('products:', len(K), '| rows:', len(rows), '| size: %.1f MB' % (size/1048576))

# Shopify caps CSV uploads at 15 MB — split if needed, always on product boundaries
LIMIT = 14 * 1024 * 1024
if size > LIMIT:
    parts, cur, cur_bytes, idx = [], [], 0, 1
    by_handle = {}
    for r in rows:
        by_handle.setdefault(r['Handle'], []).append(r)
    for h in sorted(by_handle):
        grp = by_handle[h]
        gb = sum(len(str(x)) for r in grp for x in r.values()) + 2 * len(grp)
        if cur and cur_bytes + gb > LIMIT:
            parts.append(cur); cur, cur_bytes = [], 0
        cur.extend(grp); cur_bytes += gb
    if cur: parts.append(cur)
    names = []
    for i, part in enumerate(parts, 1):
        fn = 'populars_clothes_vestidos_parte%d.csv' % i
        with open(fn, 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=COLS); w.writeheader(); w.writerows(part)
        names.append((fn, os.path.getsize(fn)/1048576, len({r['Handle'] for r in part}), len(part)))
    for fn, mb, ph, rr in names:
        print('  %-42s %5.1f MB  %5d productos  %6d filas' % (fn, mb, ph, rr))
