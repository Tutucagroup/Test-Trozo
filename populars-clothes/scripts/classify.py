import pickle, re, json, collections
prods = pickle.load(open('prods.pkl','rb'))

DRESS_TYPES = {'Dresses', 'Maxi & Midi Dresses', 'Mini Dresses'}
dress_re = re.compile(r'\b(dress|dresses|gown)\b', re.I)
# One-piece garments / multi-piece items that are never a dress, even alongside the word "dress"
never_dress = re.compile(r'\b(romper|playsuit|jumpsuit|overall|cape|poncho|bikini|swimsuit|sets?)\b', re.I)
# Extra exclusions that only apply when the title has NO "dress" word
non_dress_noun = re.compile(r'\b(skirt|top|tee|shirt|blouse|pants?|trousers?|jeans?|shorts?|bodysuit|blazer|jacket|coat|cardigan|jumper|sweater|bag|clutch|tote|heels?|boots?|sandals?|flats?|necklace|bracelet|cuff|ring|earrings?|sunglasses|hat|scarf|belt|re-sizer|fee|gift card)\b', re.I)
silhouette = re.compile(r'\b(mini|midi|maxi|slip|frock|sundress)\b', re.I)

keep, delete = [], []
for p in prods.values():
    title = p.get('title','')
    ptype = p.get('productType') or ''
    has_dress = bool(dress_re.search(title))
    if never_dress.search(title):
        is_dress = False
    elif has_dress:
        is_dress = True                      # "Tie Skirt Mini Dress", "Shirt Dress", "Corset Dress" are dresses
    elif ptype in DRESS_TYPES:
        is_dress = bool(silhouette.search(title)) and not non_dress_noun.search(title)
    else:
        is_dress = False
    (keep if is_dress else delete).append(p)

print('KEEP  (dresses)    :', len(keep))
print('DELETE(non-dresses):', len(delete))
print('total              :', len(keep)+len(delete))
print()
for t, n in collections.Counter((p.get('productType') or '(none)') for p in delete).most_common():
    print('  %-22s %4d' % (t, n))
print('\n--- still deleting from dress-ish types (should be Set/Cape/Romper only) ---')
for p in delete:
    if p.get('productType') in DRESS_TYPES | {'Lingerie'}:
        print('  ', p.get('productType'), '|', p['title'])

json.dump([{'id':p['id'],'title':p['title'],'type':p.get('productType') or '','status':p['status']} for p in delete],
          open('to_delete.json','w'), indent=1)
json.dump([p['id'] for p in keep], open('keep_ids.json','w'))
