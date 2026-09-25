"""
Tarea 1 — Recategorización multi-colección.

Analiza título + descripción de cada producto y AGREGA (nunca quita) los tags
de las colecciones adicionales donde también encaja. Determinístico y auditable:
las reglas son (colección destino, patrones, guard de contexto).

Se agrega el rollup completo de cada colección detectada (consistente con el
sistema de tags existente). Entrada: scratchpad/products_all.jsonl.
Salida: scratchpad/recat.jsonl  {handle, old_tags, new_tags, added:[handles]}.
"""
import os
import re
import json
import unicodedata

SC = "/tmp/claude-0/-home-user-Test-Trozo/f4677800-7e33-5d4e-ab81-cb54e5e95596/scratchpad"
ROLLUP = json.load(open("/tmp/handle_rollup.json", encoding="utf-8"))


def norm(s):
    s = unicodedata.normalize("NFD", (s or "").lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", s)


def rx(*words):
    return re.compile("|".join(words))


# ---- guards de contexto (reciben ctx) ----
def facial(ctx):
    return bool(re.search(r"\bfacial|\brostro|\bcara\b|contorno de ojo|piel del rostro", ctx["t"])) or \
        bool(ctx["tags"] & {"skin-care", "cuidado-piel-faciales", "serum-y-boosters",
                            "cuidado-piel-contorno-ojos", "combos-faciales"})


def corporal(ctx):
    return bool(re.search(r"corporal|\bcuerpo\b|\bpiernas?\b|\bmanos?\b|\bpies?\b|\btalon", ctx["t"])) or \
        bool(ctx["tags"] & {"cuidado-piel-corporales", "corporal-dermo", "combos-corporales"})


def capilar(ctx):
    return bool(re.search(r"cabello|capilar|\bpelo\b|cuero cabelludo|shampoo|acondicionador", ctx["t"])) or \
        bool(ctx["tags"] & {"shampoo", "cuidado-capilar", "capilares-dermo", "acondicionador",
                            "shampoo-dermo", "tinturas-coloracion", "reparacion-nutricion"})


def piel(ctx):   # cualquier producto para la piel
    return facial(ctx) or corporal(ctx) or bool(
        ctx["tags"] & {"cuidado-de-la-piel", "dermocosmetica", "skin-care"})


def is_makeup(ctx):
    return "maquillaje" in ctx["tags"] or bool(
        re.search(r"labial|mascara de pestan|\bbase de maquillaje\b|corrector|\brubor|"
                  r"sombra|delineador|esmalte|iluminador|\bprimer\b|maquillaje",
                  ctx["title"] + " " + ctx.get("type", "")))


def is_nutri(ctx):
    # sólo productos de nutrición: por tag de depto o por tipo suplemento
    return bool(ctx["tags"] & {"nutricion-deporte", "suplemento-deportivo", "suplemento-dietario",
                               "suplemento-nutricional"}) or "suplemento" in ctx.get("type", "")


def is_diabetes(ctx):
    # sólo si es un producto para diabéticos (título/tipo/ya categorizado), no una mención suelta
    return ("diabetes" in ctx["tags"]) or ("diabet" in ctx.get("type", "")) or \
        bool(re.search(r"diabet|glucos|glucemi", ctx["title"]))


def always(ctx):
    return True


# guards compuestos: piel real (no maquillaje)
def facial_skin(ctx):
    return facial(ctx) and not is_makeup(ctx)


def corporal_skin(ctx):
    return corporal(ctx) and not is_makeup(ctx)


def piel_skin(ctx):
    return piel(ctx) and not is_makeup(ctx)


def serum_guard(ctx):
    # sólo si el producto ES un sérum/booster (título o tipo), no si sólo lo menciona la desc
    return facial(ctx) and not is_makeup(ctx) and bool(
        re.search(r"\bserum\b|\bbooster\b", ctx["title"]) or "serum" in ctx.get("type", ""))


# ---- reglas: (handle destino, patrones, guard) ----
RULES = [
    ("anti-edad", rx(r"antiage", r"anti-age", r"anti edad", r"antiedad", r"antiarrugas",
                     r"anti-arrugas", r"\barrugas?\b", r"lineas de expresion", r"reafirm",
                     r"\bfirmeza\b", r"colageno", r"rejuvenec", r"efecto lifting", r"antienvejecim"), facial_skin),
    ("anti-manchas", rx(r"antimanchas", r"anti-manchas", r"despigment",
                        r"unifica(r)? el tono", r"tono desparejo", r"hiperpigment", r"aclarant",
                        r"manchas (solares|oscuras|del rostro|en la piel)"), facial_skin),
    ("anti-acne", rx(r"\bacne\b", r"antiacne", r"anti-acne", r"puntos negros", r"espinilla",
                     r"comedon", r"imperfeccion", r"piel grasa"), facial_skin),
    ("aguas-termales-anti-rojeces", rx(r"agua termal", r"\brojeces\b", r"\brojez\b", r"enrojecim",
                                       r"antirojeces", r"rosacea", r"couperosis"), facial_skin),
    ("contorno-de-ojos", rx(r"contorno de ojo", r"\bojeras?\b", r"\bparpados?\b",
                            r"bolsas de los ojos", r"bolsas en los ojos"), facial_skin),
    ("serum", rx(r"."), serum_guard),
    ("skincare-hidratacion", rx(r"hidratant", r"\bhidrata\b", r"hidratacion", r"humectant",
                                r"acido hialuronico"), facial_skin),
    ("anti-caspa", rx(r"\bcaspa\b", r"anticaspa", r"anti-caspa", r"descamacion del cuero"), capilar),
    ("anti-caida", rx(r"\bcaida\b", r"caida del cabello", r"anticaida", r"anti-caida", r"crecimiento capilar",
                      r"estimula el crecimiento", r"fortalece el cabello"), capilar),
    ("manos-y-pies", rx(r"manos y pies", r"pies y manos", r"para (los )?pies", r"crema (de|para) pies",
                        r"\btalon", r"pies resecos", r"pies agrietados", r"manos agrietadas",
                        r"para (las )?manos"), corporal_skin),
    ("cicatrizantes", rx(r"cicatriz", r"regenera(dora)? la piel", r"agrietad", r"\bheridas\b",
                         r"quemaduras", r"escaras", r"piel dañada"), piel_skin),
    ("corporal-hidratacion", rx(r"hidratant", r"\bhidrata\b", r"emolient", r"nutre la piel",
                                r"humectant"), corporal_skin),
    ("celulitis", rx(r"celulitis", r"anticelulit", r"reductor", r"reafirmante corporal"), corporal_skin),
    ("post-solar", rx(r"post ?solar", r"after ?sun", r"despues del sol", r"reparador solar"), always),
    ("autobronceante", rx(r"autobronceant", r"self ?tan", r"bronceado sin sol"), always),
    ("diabetes", rx(r"diabet", r"\bglucosa\b", r"glucemi", r"hipoglucem", r"apto para diabetic"), is_diabetes),
    ("cuidado-del-adulto", rx(r"incontinencia", r"panal(es)? para adulto", r"adulto mayor",
                              r"tercera edad", r"ropa interior absorbente"), always),
    ("suplemento-nutricional", rx(r"multivitamin", r"vitaminas y minerales", r"nutricion completa",
                                  r"suplemento nutricional", r"polivitamin"), is_nutri),
    ("suplemento-deportivo", rx(r"proteina", r"creatina", r"aminoacido", r"\bbcaa\b", r"pre-?entreno",
                                r"masa muscular", r"\bwhey\b"), is_nutri),
    ("depilacion", rx(r"depila", r"cera depilatoria", r"bandas depilatorias", r"crema depilatoria"), always),
    ("desodorantes-antitranspirante", rx(r"desodorante", r"antitranspirante", r"antiperspir"), always),
]

# solar: ruteo por contexto
# nota: se quitan "uva"/"uvb" (colisión con "extracto de uva") y "rayos uv" (muy débil)
SOLAR_PAT = rx(r"\bfps\s*\d", r"\bspf\s*\d", r"protector solar", r"proteccion solar", r"filtro solar",
               r"pantalla solar", r"anthelios", r"fotoprotec")


def solar_handles(ctx):
    if is_makeup(ctx):
        return None
    t = ctx["t"]
    if re.search(r"\blabial|\blabios?\b", t):
        return "solar-labios"
    if re.search(r"\bninos?\b|\binfantil|\bpediatr|\bkids\b|\bbaby\b", ctx["title"]):
        return "solar-ninos"
    if facial(ctx) or re.search(r"\bfacial|\brostro\b", t):
        return "solar-rostro"
    if corporal(ctx) or re.search(r"corporal|\bcuerpo\b", t):
        return "solar-cuerpo"
    return "proteccion-solar"


def add_rollup(tagset, handle):
    roll = ROLLUP.get(handle)
    if roll and roll.get("tags"):
        for t in [x.strip() for x in roll["tags"].split(",")]:
            tagset.add(t)


def main():
    out = open(os.path.join(SC, "recat.jsonl"), "w", encoding="utf-8")
    from collections import Counter
    added_counter = Counter()
    n = changed = 0
    for line in open(os.path.join(SC, "products_all.jsonl"), encoding="utf-8"):
        p = json.loads(line)
        n += 1
        old_tags = [x.strip() for x in (p["tags"] or "").split(",") if x.strip()]
        tagset = set(old_tags)
        ctx = {"t": norm(p["title"] + " . " + p["desc"]),
               "title": norm(p["title"]), "type": norm(p.get("type", "")), "tags": set(old_tags)}
        added = []
        for handle, pat, guard in RULES:
            if pat.search(ctx["t"]) and guard(ctx):
                before = set(tagset)
                add_rollup(tagset, handle)
                if tagset != before:
                    added.append(handle)
        if SOLAR_PAT.search(ctx["t"]):
            h = solar_handles(ctx)
            if h:
                before = set(tagset)
                add_rollup(tagset, h)
                if tagset != before:
                    added.append(h)
        # nuevos tags = viejos (en orden) + agregados nuevos
        new_tags = old_tags + [t for t in tagset if t not in old_tags]
        if added:
            changed += 1
            for h in added:
                added_counter[h] += 1
        out.write(json.dumps({"handle": p["handle"], "sku": p["sku"], "title": p["title"],
                              "old_tags": ", ".join(old_tags), "new_tags": ", ".join(new_tags),
                              "added": added}, ensure_ascii=False) + "\n")
    out.close()
    print(f"productos: {n} | con colecciones agregadas: {changed}")
    print("top colecciones agregadas:")
    for h, c in added_counter.most_common(25):
        print(f"  {c:5}  {h}")


if __name__ == "__main__":
    main()
