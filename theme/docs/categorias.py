# -*- coding: utf-8 -*-
# Arbol de categorias replicado de krika.co.
# ("Titulo", "handle", reglas, [hijos])
# reglas: {"any": [tipos...]}  |  {"anyTitle": [textos...]}  |  {"all": [(col,rel,cond)...]}
# handle None  => el item enlaza a otra coleccion existente (campo "ref")

T = lambda *t: {"any": list(t)}
TT = lambda *t: {"anyTitle": list(t)}
def ALL(*rules): return {"all": list(rules)}

TREE = [
 ("Capilar", "capilar", None, [
   ("Cuidado capilar", "capilar-cuidado", T("SHAMPOO CAPILAR","ACONDICIONADOR/BALSAMO CAPILAR","TRATAMIENTOS/MASCARILLAS","ACEITE/SERUM CAPILAR","AMPOLLETAS CAPILARES","TONICOS CAPILARES","CREMAS PARA PEINAR","KIT CAPILARES","CUIDADO CAPILAR","CERAS/GEL CAPILAR"), [
      ("Shampoo Capilar","capilar-shampoo", T("SHAMPOO CAPILAR")),
      ("Acondicionador capilar","capilar-acondicionador", T("ACONDICIONADOR/BALSAMO CAPILAR")),
      ("Tratamientos capilares","capilar-tratamientos", T("TRATAMIENTOS/MASCARILLAS")),
      ("Aceites capilares","capilar-aceites", T("ACEITE/SERUM CAPILAR")),
      ("Ampolletas","capilar-ampolletas", T("AMPOLLETAS CAPILARES")),
      ("Tónicos capilares","capilar-tonicos", T("TONICOS CAPILARES")),
      ("Crema de peinar","capilar-crema-peinar", T("CREMAS PARA PEINAR")),
      ("Kit","capilar-kit", T("KIT CAPILARES")),
      ("Ceras capilares","capilar-ceras", T("CERAS/GEL CAPILAR")),
   ]),
   ("Coloración", "capilar-coloracion", T("TINTES TEMPORALES","TINTES PERMANENTES","DECOLORANTES","MATIZANTES","ACCESORIOS COLORACION","HENNAS"), [
      ("Temporal","coloracion-temporal", T("TINTES TEMPORALES","HENNAS")),
      ("Permanente","coloracion-permanente", T("TINTES PERMANENTES")),
      ("Decolorantes","coloracion-decolorantes", T("DECOLORANTES")),
      ("Matizantes","coloracion-matizantes", T("MATIZANTES")),
      ("Accesorios Coloración","coloracion-accesorios", T("ACCESORIOS COLORACION")),
   ]),
   ("Styling capilar", "capilar-styling", T("ALIZADORAS","ESPUMAS CAPILARES","LACAS","CEPILLOS CAPILARES","COMPLEMENTOS PARA PEINADO","PEINETAS/PEINES","GORROS BANO/SATIN"), [
      ("Alisadoras","styling-alisadoras", T("ALIZADORAS")),
      ("Espumas","styling-espumas", T("ESPUMAS CAPILARES")),
      ("Laca","styling-laca", T("LACAS")),
      ("Cepillos","styling-cepillos", T("CEPILLOS CAPILARES")),
      ("Accesorios Styling","styling-accesorios", T("COMPLEMENTOS PARA PEINADO","PEINETAS/PEINES","GORROS BANO/SATIN")),
   ]),
   ("Accesorios", "capilar-accesorios", T("ACCESORIOS CAPILARES","TIJERAS","COMPLEMENTOS ESTILISTA"), [
      ("Tijeras","capilar-tijeras", T("TIJERAS")),
   ]),
 ]),

 ("Maquillaje", "maquillaje", None, [
   ("Rostro", "maquillaje-rostro", T("BASES & PRIMER","CORRECTORES","POLVOS","RUBOR & ILUMINADOR","FIJADORES MAQUILLAJE","CONTORNO & BRONCEADOR"), [
      ("Bases & Primer","rostro-bases-primer", T("BASES & PRIMER")),
      ("Correctores","rostro-correctores", T("CORRECTORES")),
      ("Polvos","rostro-polvos", T("POLVOS")),
      ("Rubor & Iluminador","rostro-rubor-iluminador", T("RUBOR & ILUMINADOR")),
      ("Fijador Maquillaje","rostro-fijador", T("FIJADORES MAQUILLAJE")),
      ("Contorno & Bronceador","rostro-contorno-bronceador", T("CONTORNO & BRONCEADOR")),
   ]),
   ("Ojos y Cejas", "maquillaje-ojos-cejas", T("SOMBRAS","PESTANINA","PESTANAS DESECHABLES","PEGANTES PESTANAS","TRATAMIENTOS CEJAS/PESTANAS","MAQUILLAJE CEJAS","LAPIZ OJOS","LAPIZ CEJAS","PERFILADORES & DEPILADORES","DELINEADORES OJOS/CEJAS","ENCRESPADOR PESTANAS","ESTILIZADORES CEJAS","COMPLEMENTOS CEJAS/PESTANAS","REPUESTOS ENCRESPADOR"), [
      ("Sombras","ojos-sombras", T("SOMBRAS")),
      ("Pestañina","ojos-pestanina", T("PESTANINA")),
      ("Pestañas & Pegantes","ojos-pestanas-pegantes", T("PESTANAS DESECHABLES","PEGANTES PESTANAS","ENCRESPADOR PESTANAS","REPUESTOS ENCRESPADOR")),
      ("Tratamientos para Cejas/Pestañas","ojos-tratamientos-cejas", T("TRATAMIENTOS CEJAS/PESTANAS","COMPLEMENTOS CEJAS/PESTANAS")),
      ("Maquillaje Cejas","ojos-maquillaje-cejas", T("MAQUILLAJE CEJAS","ESTILIZADORES CEJAS")),
      ("Lápiz Ojos","ojos-lapiz-ojos", T("LAPIZ OJOS","DELINEADORES OJOS/CEJAS")),
      ("Lápiz Cejas","ojos-lapiz-cejas", T("LAPIZ CEJAS")),
      ("Perfiladores & Depiladores","ojos-perfiladores", T("PERFILADORES & DEPILADORES")),
   ]),
   ("Labios", "maquillaje-labios", T("BRILLOS LABIALES","CREMOSOS/HUMECTANTES","LABIALES MATTE","LAPICES/DELINEADORES LABIALES","PROTECTORES/BALSAMOS LABIALES","TINTA PARA LABIOS","EXFOLIANTES/MASCARILLAS LABIOS"), [
      ("Brillos Labiales","labios-brillos", T("BRILLOS LABIALES")),
      ("Cremoso & Humectantes","labios-cremosos", T("CREMOSOS/HUMECTANTES")),
      ("Matte","labios-matte", T("LABIALES MATTE")),
      ("Lápices Labiales","labios-lapices", T("LAPICES/DELINEADORES LABIALES")),
      ("Protector","labios-protector", T("PROTECTORES/BALSAMOS LABIALES","EXFOLIANTES/MASCARILLAS LABIOS")),
      ("Metalizados","labios-metalizados", TT("METALIZADO","METALIC")),
      ("Tinta para labios","labios-tinta", T("TINTA PARA LABIOS")),
   ]),
   ("Brochas", "maquillaje-brochas", T("BROCHAS","BROCHAS/PINCELES","LIMPIEZA BROCHAS/ESPONJAS"), [
      ("Brochas & Pinceles","brochas-pinceles", T("BROCHAS/PINCELES","BROCHAS")),
      ("Set Brochas","brochas-set", TT("SET BROCHA","SET DE BROCHA","KIT BROCHA")),
   ]),
   ("Accesorios Maquillaje", "maquillaje-accesorios", T("ACCESORIOS MAQUILLAJE","COMPLEMENTOS MAQUILLAJE","POMOS/BORLAS/ESPONJAS","ESPEJOS","COSMETIQUERAS/NECESER","DILUSORES MAQUILLAJE","KIT MAQUILLAJE","MAQUILLAJE ARTISTICO","LIMPIEZA BROCHAS/ESPONJAS"), [
      ("Pomos Maquillaje","accmaq-pomos", T("POMOS/BORLAS/ESPONJAS")),
      ("Esponjas Maquillaje","accmaq-esponjas", TT("ESPONJA")),
      ("Espejos Maquillaje","accmaq-espejos", T("ESPEJOS")),
      ("Cosmetiqueras Maquillaje","accmaq-cosmetiqueras", T("COSMETIQUERAS/NECESER")),
      ("Maletas Maquillaje","accmaq-maletas", TT("MALETA")),
      ("Balacas Maquillaje","accmaq-balacas", TT("BALACA","DIADEMA")),
   ]),
 ]),

 ("Corporal", "corporal", None, [
   ("Hidratación Corporal","corporal-hidratacion", T("CREMAS CORPORALES","LECHES/BALSAMOS CORPORALES","MANTEQUILLAS CORPORALES"), [
      ("Cremas corporales","corporal-cremas", T("CREMAS CORPORALES","MANTEQUILLAS CORPORALES")),
      ("Leches","corporal-leches", T("LECHES/BALSAMOS CORPORALES")),
   ]),
   ("Aceites Corporales","corporal-aceites", T("ACEITES CORPORALES"), []),
   ("Geles","corporal-geles", T("GELES CORPORALES","GELES/CREMAS REDUCTORAS"), []),
   ("Solar","corporal-solar", T("ACELERADORES","BRONCEADORES","AUTOBRONCEADORES","BLOQUEADORES CORPORALES","BLOQUEADORES FACIALES"), [
      ("Aceleradores","solar-aceleradores", T("ACELERADORES")),
      ("Bronceadores","solar-bronceadores", T("BRONCEADORES")),
      ("Auto bronceadores","solar-autobronceadores", T("AUTOBRONCEADORES")),
      ("Bloqueadores","solar-bloqueadores", T("BLOQUEADORES CORPORALES","BLOQUEADORES FACIALES")),
      ("Postsolar","solar-postsolar", TT("POST SOLAR","POSTSOLAR","AFTER SUN","POST-SOLAR")),
   ]),
   ("Depilación","corporal-depilacion", T("CERAS CALIENTES","BANDAS DEPILATORIAS","CREMAS DEPILATORIAS","COMPLEMENTOS DEPILACION","CALENTADORES CERA","ACLARADORES BELLOS CORPORALES","DECOLORANTES CORPORALES"), [
      ("Ceras Calientes","depilacion-ceras-calientes", T("CERAS CALIENTES")),
      ("Ceras Frías","depilacion-ceras-frias", T("BANDAS DEPILATORIAS")),
      ("Cremas Depilatorias","depilacion-cremas", T("CREMAS DEPILATORIAS")),
      ("Cuchillas","depilacion-cuchillas", TT("CUCHILLA","RASURADORA","PRESTOBARBA")),
      ("Accesorios Depilación","depilacion-accesorios", T("COMPLEMENTOS DEPILACION","CALENTADORES CERA","ACLARADORES BELLOS CORPORALES","DECOLORANTES CORPORALES")),
   ]),
   ("Aseo Corporal","corporal-aseo", T("JABONES CORPORALES","EXFOLIANTES/MASCARILLAS CORPORALES","ANTITRANSPIRANTES","JABONES/GELES INTIMOS","CUIDADO CORPORAL","TONICOS CORPORALES"), [
      ("Jabones Corporales","aseo-jabones", T("JABONES CORPORALES")),
      ("Exfoliantes Corporales","aseo-exfoliantes", T("EXFOLIANTES/MASCARILLAS CORPORALES")),
      ("Desodorantes Women","aseo-desodorantes-women", T("ANTITRANSPIRANTES")),
   ]),
   ("Accesorios Corporales","corporal-accesorios", T("ACCESORIOS CORPORALES","ACCESORIOS PEZONES","MADEROTERAPIA","KIT CORPORALES"), [
      ("Película Osmótica","corporal-pelicula-osmotica", TT("OSMOTIC","PELICULA")),
      ("Toallas","corporal-toallas", TT("TOALLA")),
   ]),
   ("Men","corporal-men", TT("FOR MEN","HOMBRE","MASCULINO","MEN'S"), [
      ("Cremas Corporales","men-cremas", ALL(("TYPE","EQUALS","CREMAS CORPORALES"),("TITLE","CONTAINS","MEN"))),
      ("Exfoliantes Corporales","men-exfoliantes", ALL(("TYPE","EQUALS","EXFOLIANTES/MASCARILLAS CORPORALES"),("TITLE","CONTAINS","MEN"))),
      ("Jabones Corporales","men-jabones", ALL(("TYPE","EQUALS","JABONES CORPORALES"),("TITLE","CONTAINS","MEN"))),
      ("Desodorantes","men-desodorantes", ALL(("TYPE","EQUALS","ANTITRANSPIRANTES"),("TITLE","CONTAINS","MEN"))),
   ]),
 ]),

 ("Facial", "facial", None, [
   ("Limpieza Facial","facial-limpieza", T("LIMPIEZA FACIAL","AGUAS FACIALES","JABONES FACIALES","DESMAQUILLANTES & BIFASICOS","TOALLITAS DESMAQUILLANTES","EXFOLIANTES FACIALES","ESPUMAS FACIALES","GELES FACIALES","MASCARILLAS FACIALES","VELOS FACIALES","ACCESORIOS DE LIMPIEZA FACIAL","BANDAS FACIALES","MASAJEADORES FACIALES"), [
      ("Agua Micelar","limpieza-agua-micelar", T("AGUAS FACIALES")),
      ("Jabón","limpieza-jabon", T("JABONES FACIALES")),
      ("Desmaquillantes & Bifásicos","limpieza-desmaquillantes", T("DESMAQUILLANTES & BIFASICOS","TOALLITAS DESMAQUILLANTES")),
      ("Exfoliantes Faciales","limpieza-exfoliantes", T("EXFOLIANTES FACIALES")),
      ("Gel Limpiador","limpieza-gel", T("GELES FACIALES","ESPUMAS FACIALES","LIMPIEZA FACIAL")),
      ("Mascarillas","limpieza-mascarillas", T("MASCARILLAS FACIALES")),
      ("Velos","limpieza-velos", T("VELOS FACIALES","BANDAS FACIALES")),
      ("Accesorios Limpieza Facial","limpieza-accesorios", T("ACCESORIOS DE LIMPIEZA FACIAL","MASAJEADORES FACIALES")),
   ]),
   ("Cuidado Facial","facial-cuidado", T("CREMAS FACIALES","SERUM FACIALES","AMPOLLETAS/BALSAMOS FACIALES","TONICOS FACIALES","LECHES/ACEITES FACIALES","BRUMAS FACIALES","FACIAL","KIT FACIALES"), [
      ("Anti Acné","cuidado-anti-acne", TT("ACNE","ANTIACNE","ANTI-ACNE")),
      ("Contorno de Ojos","cuidado-contorno-ojos", ALL(("TITLE","CONTAINS","CONTORNO"),("TYPE","NOT_EQUALS","CONTORNO & BRONCEADOR"))),
      ("Antiedad & Antiarrugas","cuidado-antiedad", TT("ANTIEDAD","ANTI EDAD","ARRUGA","LIFTING","ANTI-AGE","RETINOL")),
      ("Hidratación Facial","cuidado-hidratacion", T("CREMAS FACIALES","AMPOLLETAS/BALSAMOS FACIALES","BRUMAS FACIALES","LECHES/ACEITES FACIALES")),
      ("Despigmentante","cuidado-despigmentante", TT("DESPIGMENT","MANCHA","ACLARANTE","BLANQUEADOR")),
      ("Tónicos Faciales","cuidado-tonicos", T("TONICOS FACIALES")),
      ("Sérums Faciales","cuidado-serums", T("SERUM FACIALES")),
   ]),
 ]),

 ("Manicure & pedicure", "manicure-pedicure", None, [
   ("Herramientas Uñas","manicure-herramientas", T("CORTAUNAS/GUILLOTINAS","CORTACUTICULA","LIMAS","BLOQUES UNAS","ESPATULAS/PINZAS UNAS","PALAS/ESMERILES","PULIDORES/DRILL UNAS","FRESAS/BROCAS UNAS","PATECABRAS","REMOVEDORES CALLOS"), [
      ("Cortauñas","herr-cortaunas", T("CORTAUNAS/GUILLOTINAS")),
      ("Cortacutícula","herr-cortacuticula", T("CORTACUTICULA")),
      ("Limas","herr-limas", T("LIMAS")),
      ("Bloques","herr-bloques", T("BLOQUES UNAS")),
      ("Separadores","herr-separadores", T("ESPATULAS/PINZAS UNAS")),
      ("Removedores","herr-removedores", T("REMOVEDORES CALLOS","REMOVEDORES/ACEITES CUTICULA")),
      ("Pala","herr-pala", T("PALAS/ESMERILES","PATECABRAS")),
   ]),
   ("Bases y Tratamientos","manicure-bases-tratamientos", T("BASES/TRATAMIENTOS UNAS","HIGIENE/CUIDADO UNAS","SECANTES","ANTIHONGOS"), []),
   ("Removedores","manicure-removedores", T("REMOVEDORES ESMALTE","REMOVEDORES/ACEITES CUTICULA","DILUSORES ESMALTE","LIMPIADORES UNAS"), []),
   ("Maquillaje Uñas","manicure-maquillaje-unas", T("ESMALTE TRADICIONAL","ESMALTE SEMIPERMANENTE","ESMALTE EFECTO GEL","BRILLO UNAS","APLIQUES/STICKERS","PINTURA ACRILICA UNAS","MAQUILLAJE UNAS","ACRILICOS/PAINTING GEL","UNAS POSTIZAS","MONOMEROS"), [
      ("Esmaltes","unas-esmaltes", T("ESMALTE TRADICIONAL")),
      ("Semipermanentes","unas-semipermanentes", T("ESMALTE SEMIPERMANENTE")),
      ("Efecto Gel","unas-efecto-gel", T("ESMALTE EFECTO GEL")),
      ("Brillo Uñas","unas-brillo", T("BRILLO UNAS")),
      ("Decoración","unas-decoracion", T("APLIQUES/STICKERS","PINTURA ACRILICA UNAS","UNAS POSTIZAS","ACRILICOS/PAINTING GEL","MONOMEROS")),
   ]),
   ("Accesorios Uñas","manicure-accesorios", T("COMPLEMENTOS MANICURE/PEDICURE","PINCELES MANICURE","LAMPARAS UNAS","MALETAS UNAS","KIT MANICURE/PEDICURE","MANICURE & PEDICURE","LIMPIADORES CEPILLOS","PULIDORES/DRILL UNAS","FRESAS/BROCAS UNAS"), []),
 ]),

 ("Aseo personal", "aseo-personal", None, [
   ("Aseo Personal","aseo-personal-general", T("ANTITRANSPIRANTES","ANTIBACTERIALES/DESINFECTANTES","PANITOS HUMEDOS","PANITOS INTIMOS","JABONES/GELES INTIMOS","COPITOS","ALGODÓN","REPELENTES","CAPSULAS DURAS"), [
      ("Talcos y Desodorantes Pies","aseo-talcos", TT("TALCO","DESODORANTE PIES","PIE")),
      ("Desodorantes Antitranspirante","aseo-antitranspirantes", T("ANTITRANSPIRANTES")),
      ("Cuidado Personal","aseo-cuidado-personal", T("PANITOS HUMEDOS","PANITOS INTIMOS","JABONES/GELES INTIMOS","COPITOS","ALGODÓN")),
      ("Antibacteriales","aseo-antibacteriales", T("ANTIBACTERIALES/DESINFECTANTES")),
   ]),
   ("Botiquín Alcohol","aseo-botiquin", T("ALCOHOL","ANTIHONGOS","REPELENTES","BIENESTAR TERAPEUTICO","CAPSULAS DURAS"), []),
 ]),

 ("Eléctricos", "electricos", None, [
   ("Cepillos Electrónicos","electricos-cepillos", T("CEPILLOS ELECTRICOS"), []),
   ("Rizadoras","electricos-rizadoras", T("RIZADORAS"), []),
   ("Pinzas","electricos-pinzas", T("PINZAS ELECTRICAS"), []),
   ("Planchas","electricos-planchas", T("PLANCHAS"), []),
   ("Secadores","electricos-secadores", T("SECADORES/DIFUSORES"), []),
   ("Maquinillas","electricos-maquinillas", T("MAQUINAS/AFEITADORAS"), []),
   ("Trimmer","electricos-trimmer", T("TRIMMER/DEPILADORAS"), []),
   ("Accesorios Eléctricos","electricos-accesorios", T("ACCESORIOS/REPUESTOS/LUBRICANTES ELECTRI","ELECTROMENORES"), []),
 ]),

 ("Fragancias", "fragancias", None, [
   ("Fragancias Capilares","fragancias-capilares", T("FRAGANCIAS CAPILARES"), []),
   ("Fragancias Corporales Women","fragancias-women", T("AGUAS PERFUMES","SPLASH","COLONIAS","KITS DE PERFUMERIA"), []),
   ("Aromatizadores","fragancias-aromatizadores", T("AROMATERAPIA","KITS AROMATERAPIA"), []),
   ("Fragancias Corporales Men","fragancias-men", TT("FOR MEN","HOMBRE","MASCULINO","MEN'S","CABALLERO"), []),
 ]),

 ("Barbería", "barberia", None, [
   ("Cuidado Capilar Barbería","barberia-cuidado-capilar", TT("BARBER"), [
      ("Shampoo Barbería","barberia-shampoo", ALL(("TYPE","EQUALS","SHAMPOO CAPILAR"),("TITLE","CONTAINS","BARBER"))),
      ("Acondicionador Barbería","barberia-acondicionador", ALL(("TYPE","EQUALS","ACONDICIONADOR/BALSAMO CAPILAR"),("TITLE","CONTAINS","BARBER"))),
   ]),
   ("Styling Barbería","barberia-styling", T("CERAS/GEL CAPILAR","LACAS"), []),
   ("Tintes","barberia-tintes", T("TINTES PERMANENTES","TINTES TEMPORALES"), []),
   ("Corte de Cabello","barberia-corte", T("MAQUINAS/AFEITADORAS","TRIMMER/DEPILADORAS","TIJERAS","COMPLEMENTOS/ACCESORIOS BARBERIA"), [
      ("Trimmer","barberia-trimmer", {"ref": "electricos-trimmer"}),
      ("Maquinas","barberia-maquinas", {"ref": "electricos-maquinillas"}),
      ("Patilleras","barberia-patilleras", TT("PATILLERA")),
   ]),
   ("Corporal Barbería","barberia-corporal", T("CREMAS CORPORALES","EXFOLIANTES/MASCARILLAS CORPORALES","JABONES CORPORALES","ANTITRANSPIRANTES"), [
      ("Cremas","barberia-cremas", {"ref": "corporal-cremas"}),
      ("Exfoliantes","barberia-exfoliantes", {"ref": "aseo-exfoliantes"}),
      ("Jabones","barberia-jabones", {"ref": "aseo-jabones"}),
      ("Fragancias","barberia-fragancias", {"ref": "fragancias-men"}),
      ("Desodorantes","barberia-desodorantes", {"ref": "aseo-antitranspirantes"}),
   ]),
   ("Tónicos & Aceites","barberia-tonicos", T("TONICOS CAPILARES","ACEITE/SERUM CAPILAR"), []),
   ("Afeitada","barberia-afeitada", T("AFEITADO"), []),
 ]),
]
