# -*- coding: utf-8 -*-
"""
Biblioteca de copy por tipo de producto (los 181 tipos del catalogo de Krika).

Cada entrada define:
  noun       sustantivo que encabeza el gancho ("Este <noun> de <marca> ...")
  det        determinante concordado ("Este" / "Esta" / "Estos" / "Estas")
  intro      continuacion del gancho, en 3a persona
  pros       beneficios concretos (se muestran los 4 primeros + los detectados
             en el nombre del producto)
  uso        pasos del modo de uso (omitir cuando el producto no lo requiere)
  ideal      a quien le sirve
  tip        consejo corto de venta
  cat        familia, usada para decidir mensajes de formato
"""

def T(noun, intro, pros, uso=None, ideal=None, tip=None, det='Este', cat='', titulo_uso=None):
    d = {'noun': noun, 'det': det, 'intro': intro, 'pros': pros, 'cat': cat}
    if uso: d['uso'] = uso
    if ideal: d['ideal'] = ideal
    if tip: d['tip'] = tip
    if titulo_uso: d['titulo_uso'] = titulo_uso
    return d

GENERICO = T(
    'producto', 'suma a tu rutina de belleza la calidad que esperás de una marca seria',
    ['Producto original, con la garantía de Krika Cosmetics.',
     'Rendimiento probado: cunde más de lo que parece.',
     'Fácil de integrar en la rutina que ya tenés.',
     'Presentación pensada para el uso diario.'],
    uso=['Seguí siempre las indicaciones del envase.',
         'Ante la duda, escribinos por WhatsApp y te ayudamos a elegir.'],
    ideal='quien busca calidad real sin pagar de más.',
    tip='Si es tu primera vez con el producto, empezá por la presentación más pequeña.')

TIPOS = {}

# ==========================================================================
# CAPILAR — limpieza y tratamiento
# ==========================================================================
TIPOS['SHAMPOO CAPILAR'] = T(
    'shampoo', 'limpia a fondo sin dejar el pelo áspero ni el cuero cabelludo tirante',
    ['Arrastra grasa, residuo de producto y contaminación sin llevarse la hidratación que el pelo necesita.',
     'Espuma abundante y fácil de enjuagar: no quedan restos que apaguen el brillo.',
     'Deja el cabello manejable desde el lavado, así el peinado después cuesta menos.',
     'Apto para uso frecuente dentro de una rutina completa de lavado y acondicionado.'],
    uso=['Mojá el cabello con agua tibia, nunca muy caliente.',
         'Aplicá una porción del tamaño de una moneda y masajeá el cuero cabelludo con las yemas, no con las uñas.',
         'Dejá actuar 1 o 2 minutos y enjuagá hasta que el agua salga limpia.',
         'Repetí solo si el cabello estaba muy cargado de producto.'],
    ideal='rutina de lavado de cualquier tipo de cabello, ajustando la frecuencia a tu cuero cabelludo.',
    tip='Terminá el último enjuague con agua fría: sella la cutícula y el brillo se nota al instante.',
    cat='capilar')

TIPOS['ACONDICIONADOR/BALSAMO CAPILAR'] = T(
    'acondicionador', 'cierra la cutícula después del shampoo y devuelve suavidad y brillo en minutos',
    ['Desenreda de verdad: el peine pasa sin tirones y se rompe mucho menos pelo.',
     'Sella la fibra tras el lavado, que es cuando el cabello está más vulnerable.',
     'Aporta suavidad sin apelmazar ni engrasar las raíces.',
     'Facilita el secado y el peinado posterior, incluso en melenas largas.'],
    uso=['Después del shampoo, escurrí bien el exceso de agua.',
         'Aplicá de medios a puntas, evitando la raíz.',
         'Dejá actuar de 2 a 3 minutos.',
         'Enjuagá con agua tibia o fría.'],
    ideal='todo tipo de cabello, especialmente el largo, teñido o con tendencia al enredo.',
    tip='Si tenés raíz grasa y puntas secas, usá acondicionador solo de las orejas hacia abajo.',
    cat='capilar')

TIPOS['TRATAMIENTOS/MASCARILLAS'] = T(
    'tratamiento capilar', 'trabaja en profundidad sobre la fibra para devolverle cuerpo, suavidad y brillo',
    ['Tratamiento intensivo: actúa donde el acondicionador diario no llega.',
     'Recupera cabello castigado por plancha, secador, color o decoloración.',
     'Mejora la textura de forma acumulativa: cada aplicación suma.',
     'Deja la melena más pesada, brillante y fácil de manejar.'],
    uso=['Lavá con shampoo y escurrí muy bien el exceso de agua.',
         'Aplicá de medios a puntas y distribuí con un peine de dientes anchos.',
         'Dejá actuar entre 5 y 20 minutos según lo dañado que esté el cabello.',
         'Enjuagá abundantemente. Repetí una o dos veces por semana.'],
    ideal='cabello seco, poroso, teñido o con daño por calor.',
    tip='Envolvé la cabeza en una toalla tibia mientras actúa: el calor abre la cutícula y el tratamiento penetra mejor.',
    cat='capilar')

TIPOS['AMPOLLETAS CAPILARES'] = T(
    'ampolleta capilar', 'concentra en una sola dosis el activo que tu cabello necesita en este momento',
    ['Dosis única y concentrada: la potencia de un tratamiento de salón en casa.',
     'Resultado visible desde la primera aplicación en cabello muy castigado.',
     'Formato individual, sin desperdicio ni producto que se oxide en el frasco.',
     'Se puede sumar puntualmente a la rutina sin cambiar el resto de productos.'],
    uso=['Lavá el cabello y escurrí el exceso de agua.',
         'Aplicá el contenido de la ampolleta de medios a puntas o en el cuero cabelludo, según indique el envase.',
         'Masajeá y dejá actuar el tiempo indicado.',
         'Enjuagá o dejá sin enjuagar según el tipo de ampolleta.'],
    det='Esta',
    ideal='cabello muy dañado o como refuerzo semanal de la rutina.',
    tip='Una ampolleta por semana durante un mes rinde más que aplicarlas todas seguidas.',
    cat='capilar')

TIPOS['ACEITE/SERUM CAPILAR'] = T(
    'aceite capilar', 'sella las puntas, controla el frizz y devuelve ese brillo de pelo sano',
    ['Unas gotas alcanzan: rinde muchísimo y no deja sensación grasosa si se dosifica bien.',
     'Disciplina el frizz y los pelitos rebeldes sin acartonar.',
     'Protege las puntas del roce, que es donde empieza la mayoría de la rotura.',
     'Se puede usar sobre cabello húmedo o seco, antes o después del peinado.'],
    uso=['Poné 2 o 3 gotas en la palma y frotá las manos.',
         'Repartí de medios a puntas, nunca en la raíz.',
         'Peiná para distribuir de forma pareja.',
         'Si lo usás sobre cabello húmedo, secá normalmente después.'],
    ideal='puntas secas, cabello con frizz o melenas largas que pierden brillo.',
    tip='Menos es más: si te pasás de cantidad, el pelo se ve grasoso. Empezá con dos gotas.',
    cat='capilar')

TIPOS['TONICOS CAPILARES'] = T(
    'tónico capilar', 'se aplica directo en el cuero cabelludo para acompañar rutinas de fortalecimiento',
    ['Va donde importa: directo al cuero cabelludo, sin quedarse en el largo.',
     'Textura ligera que no engrasa ni deja el pelo pesado.',
     'Sin enjuague, así que se integra a la rutina diaria sin sumar pasos al baño.',
     'Pensado para usarse de forma constante, que es cuando este tipo de producto rinde.'],
    uso=['Aplicá sobre cuero cabelludo limpio, con el cabello húmedo o seco.',
         'Repartí por secciones para cubrir toda la zona.',
         'Masajeá con las yemas 1 o 2 minutos para activar la circulación.',
         'No enjuagues. Usalo a diario o según indique el envase.'],
    ideal='rutinas de fortalecimiento y cuidado del cuero cabelludo.',
    tip='La constancia es todo: los resultados de un tónico se ven a partir de la cuarta o sexta semana.',
    cat='capilar')

TIPOS['CREMAS PARA PEINAR'] = T(
    'crema para peinar', 'desenreda, define y controla el frizz sin necesidad de enjuagar',
    ['Sin enjuague: desenreda al momento y sigue trabajando todo el día.',
     'Define la forma natural del cabello sin dejarlo duro ni acartonado.',
     'Reduce la rotura al peinar, sobre todo en cabello mojado.',
     'Sirve como base antes del secador o para refrescar el peinado al día siguiente.'],
    uso=['Sobre cabello húmedo y escurrido, tomá una porción según el largo.',
         'Repartí de medios a puntas con las manos.',
         'Desenredá con peine de dientes anchos.',
         'Dejá secar al aire o secá con difusor.'],
    ideal='cabello rizado, ondulado o con tendencia al frizz.',
    tip='Aplicala con el pelo bien mojado y "amasando" los rizos: así se definen mucho mejor.',
    det='Esta', cat='capilar')

TIPOS['KIT CAPILARES'] = T(
    'kit capilar', 'reúne los pasos de una rutina completa en un solo combo, ya coordinados entre sí',
    ['Los productos están formulados para trabajar juntos: el resultado se nota más que comprándolos sueltos.',
     'Sale más a cuenta que llevar cada producto por separado.',
     'Ideal para regalar o para probar una línea completa sin invertir de más.',
     'Rutina resuelta: no tenés que adivinar qué combina con qué.'],
    uso=['Seguí el orden indicado en el kit, normalmente shampoo, acondicionador y tratamiento.',
         'Respetá los tiempos de exposición de cada paso.',
         'Usá la rutina completa al menos durante un mes para ver el resultado real.'],
    ideal='quien quiere cambiar de rutina capilar completa o busca un regalo seguro.',
    tip='Si es tu primera vez con la línea, arrancá con el kit antes de comprar los tamaños grandes.',
    cat='capilar')

TIPOS['CUIDADO CAPILAR'] = T(
    'producto de cuidado capilar', 'suma un paso más de cuidado a la rutina del cabello',
    ['Pensado para integrarse con el resto de tu rutina capilar.',
     'Calidad de marca reconocida, con respaldo de Krika.',
     'Resultado acumulativo: mejora a medida que lo usás.',
     'Presentación práctica para el día a día.'],
    uso=['Seguí las indicaciones del envase.',
         'Usalo de forma constante para notar el cambio.'],
    ideal='sumar cuidado extra a tu rutina capilar.',
    cat='capilar')

TIPOS['ESPUMAS CAPILARES'] = T(
    'espuma de peinado', 'da cuerpo y fijación ligera sin el efecto cartón de los fijadores fuertes',
    ['Volumen real desde la raíz, que es donde hace falta.',
     'Fijación flexible: el peinado se mueve, no se queda tieso.',
     'No deja residuo blanco ni sensación pegajosa.',
     'Funciona igual de bien con secador que al aire.'],
    uso=['Agitá el envase antes de usar.',
         'Aplicá una porción del tamaño de un huevo sobre cabello húmedo.',
         'Repartí desde la raíz hacia las puntas.',
         'Secá con secador y cepillo, o dejá secar al aire.'],
    ideal='cabello fino o sin volumen y peinados con movimiento.',
    tip='Aplicala con la cabeza boca abajo: el volumen en la raíz sube otro nivel.',
    det='Esta', cat='capilar')

TIPOS['CERAS/GEL CAPILAR'] = T(
    'producto de styling', 'define, fija y da textura al peinado con el nivel de control que elijas',
    ['Define la forma y la mantiene durante horas.',
     'Se puede reactivar con los dedos para retocar sin volver a aplicar.',
     'Da textura visible, ideal para cortes con capas o peinados desordenados a propósito.',
     'Se retira fácil con el lavado habitual.'],
    uso=['Tomá una cantidad pequeña y calentala entre las palmas.',
         'Aplicá sobre cabello seco o apenas húmedo, empezando por la nuca.',
         'Modelá con los dedos hasta conseguir la forma.',
         'Sumá producto de a poco si necesitás más fijación.'],
    ideal='peinados definidos, cortes masculinos y texturizados.',
    tip='Menos producto y bien repartido fija mejor que mucho producto en un solo punto.',
    cat='capilar')

TIPOS['LACAS'] = T(
    'laca', 'fija el peinado terminado y lo mantiene en su sitio hasta el final del día',
    ['Fijación que aguanta humedad, viento y horas de uso.',
     'Secado rápido, sin dejar el pelo pegajoso.',
     'Se cepilla sin dejar escamas blancas.',
     'Sirve tanto para fijar el peinado completo como para retocar zonas puntuales.'],
    uso=['Agitá el envase.',
         'Pulverizá a unos 25 o 30 cm de distancia.',
         'Aplicá en capas finas, dejando secar unos segundos entre una y otra.',
         'Para volumen, levantá mechones y rociá directamente en la raíz.'],
    ideal='peinados de evento, recogidos y cualquier look que tenga que durar.',
    tip='Rociá primero el cepillo y después peiná: fijás los pelitos sueltos sin cargar el peinado.',
    det='Esta', cat='capilar')

TIPOS['ALIZADORAS'] = T(
    'producto alisador', 'ayuda a conseguir un liso más duradero y con mejor acabado',
    ['Reduce el volumen y el frizz de forma notoria.',
     'Facilita muchísimo el planchado posterior: menos pasadas, menos daño.',
     'Deja el cabello más brillante y ordenado.',
     'El efecto se mantiene varios lavados según el tipo de cabello.'],
    uso=['Leé con atención las instrucciones del fabricante antes de empezar.',
         'Hacé siempre una prueba de mecha en una zona poco visible.',
         'Aplicá por secciones sobre cabello limpio y seco, respetando el tiempo indicado.',
         'Enjuagá y completá el proceso según indique el envase.'],
    ideal='cabello con mucho volumen o frizz que busca un liso duradero.',
    tip='Si nunca hiciste un alisado, hacelo con un profesional la primera vez y mantenelo en casa después.',
    cat='capilar')

TIPOS['ACCESORIOS CAPILARES'] = T(
    'accesorio capilar', 'resuelve ese detalle del peinado que marca la diferencia',
    ['Práctico y resistente para el uso diario.',
     'Sujeta sin marcar ni tironear el cabello.',
     'Liviano y cómodo de llevar durante horas.',
     'Se guarda en cualquier neceser o cartera.'],
    titulo_uso='Cómo usarlo',
    uso=['Usalo sobre cabello seco o húmedo según el peinado que busques.',
         'Evitá apretar de más para no marcar la fibra.',
         'Guardalo limpio y seco para que dure más.'],
    ideal='el día a día y los peinados rápidos.',
    cat='capilar')

TIPOS['CEPILLOS CAPILARES'] = T(
    'cepillo', 'desenreda, da forma y reparte el brillo natural del cabello de raíz a puntas',
    ['Desenreda con menos tirones y menos rotura que un peine común.',
     'Reparte la grasa natural del cuero cabelludo hacia las puntas: más brillo sin producto.',
     'Mango ergonómico, cómodo incluso en sesiones largas de brushing.',
     'Fácil de limpiar y pensado para durar.'],
    titulo_uso='Cómo usarlo',
    uso=['Empezá siempre por las puntas y subí de a poco hacia la raíz.',
         'Sujetá el mechón por encima de donde cepillás para no tironear.',
         'Para brushing, trabajá con el secador siguiendo el cepillo.',
         'Limpiá el cepillo una vez por semana quitando el pelo acumulado.'],
    ideal='desenredado diario, brushing y cuidado general del cabello.',
    tip='Nunca cepilles el pelo empapado sin producto: es cuando más se rompe.',
    cat='capilar')

TIPOS['PEINETAS/PEINES'] = T(
    'peine', 'ordena el cabello con precisión, tanto para desenredar como para trabajar por secciones',
    ['Dientes bien pulidos: pasan sin engancharse ni rayar la fibra.',
     'Imprescindible para dividir en secciones al teñir, planchar o peinar.',
     'Resistente y fácil de desinfectar.',
     'Tamaño manejable, entra en el neceser.'],
    titulo_uso='Cómo usarlo',
    uso=['Usá los dientes anchos para desenredar en húmedo.',
         'Usá los dientes finos para alisar y definir la raya.',
         'Lavalo con agua y jabón cada tanto para quitar el residuo de producto.'],
    ideal='desenredado, secciones de color y peinado de precisión.',
    cat='capilar')

TIPOS['GORROS BANO/SATIN'] = T(
    'gorro', 'protege el peinado y la hidratación del cabello mientras dormís o te bañás',
    ['Evita el frizz que genera el roce con la almohada.',
     'Mantiene el peinado y el tratamiento en su sitio durante la noche.',
     'Elástico cómodo que no deja marca en la frente.',
     'Lavable y reutilizable.'],
    titulo_uso='Cómo usarlo',
    uso=['Recogé el cabello sin apretar.',
         'Colocá el gorro cubriendo todo el largo.',
         'Para tratamientos, ponelo encima del producto para aprovechar el calor.'],
    ideal='cabello rizado, alisados y quien quiere estirar el peinado un día más.',
    tip='Dormir con gorro de satín es el truco más barato que existe para reducir frizz.',
    cat='capilar')

TIPOS['COMPLEMENTOS PARA PEINADO'] = T(
    'complemento de peinado', 'da esa ayuda extra para que el peinado quede como lo tenías en la cabeza',
    ['Facilita peinados que solos cuestan bastante más.',
     'Discreto: cumple su función sin verse.',
     'Resistente y reutilizable.',
     'Práctico para el día a día y para eventos.'],
    titulo_uso='Cómo usarlo',
    uso=['Colocalo sobre cabello seco y peinado.',
         'Fijá con horquillas si el peinado lo requiere.',
         'Retiralo con cuidado al final del día.'],
    ideal='recogidos, moños y peinados de ocasión.',
    cat='capilar')

TIPOS['COMPLEMENTOS ESTILISTA'] = T(
    'complemento de estilista', 'es de esas herramientas que en el salón no pueden faltar',
    ['Pensado para uso profesional intensivo.',
     'Materiales que aguantan el trabajo del día a día.',
     'Agiliza el servicio y mejora el acabado.',
     'Fácil de higienizar entre cliente y cliente.'],
    titulo_uso='Cómo usarlo',
    uso=['Usalo según el servicio que estés realizando.',
         'Desinfectalo entre usos.'],
    ideal='estilistas y salones de belleza.',
    cat='capilar')

TIPOS['TIJERAS'] = T(
    'tijera', 'corta limpio y parejo, que es lo único que evita las puntas abiertas después',
    ['Filo preciso: corta el pelo en lugar de aplastarlo, y así la punta no se abre.',
     'Acero resistente que mantiene el filo con el uso.',
     'Tornillo ajustable para regular la tensión a tu gusto.',
     'Diseño cómodo para trabajar largos ratos sin cansar la mano.'],
    titulo_uso='Cómo usarla',
    uso=['Trabajá siempre sobre cabello limpio y bien peinado.',
         'Cortá por secciones pequeñas, nunca todo el mechón de una.',
         'Limpiá y secá la tijera después de cada uso.',
         'Guardala en su estuche para proteger el filo.'],
    ideal='estilistas, barberos y cortes de mantenimiento en casa.',
    tip='Nunca uses tijeras de peluquería para cortar otra cosa: el filo se arruina enseguida.',
    det='Esta', cat='capilar')

# ==========================================================================
# CAPILAR — coloracion
# ==========================================================================
TIPOS['TINTES PERMANENTES'] = T(
    'tinte permanente', 'cubre el color anterior y las canas de raíz a puntas con un resultado uniforme y duradero',
    ['Cobertura total de canas cuando se respeta la proporción y el tiempo de exposición.',
     'Color parejo de la raíz a las puntas, sin ese efecto de dos tonos.',
     'Resultado duradero: se mantiene hasta el crecimiento de la raíz.',
     'Permite subir o bajar de tono dentro del rango del producto.'],
    uso=['Hacé la prueba de sensibilidad 48 horas antes, en el pliegue del codo. No te la saltes.',
         'Mezclá el tinte con el oxidante en la proporción que indica el envase, en un bol no metálico.',
         'Aplicá con pincel sobre cabello seco y sin lavar, empezando por la raíz y dividiendo en cuatro secciones.',
         'Dejá actuar el tiempo indicado, enjuagá hasta que el agua salga clara y terminá con acondicionador o el post-color del kit.'],
    ideal='cobertura de canas y cambios de color duraderos.',
    tip='El cabello sin lavar tiñe mejor: la grasa natural protege el cuero cabelludo del oxidante.',
    cat='color')

TIPOS['TINTES TEMPORALES'] = T(
    'tinte temporal', 'aporta color sin compromiso: se va lavado a lavado y no genera raíz marcada',
    ['Sin amoníaco ni oxidante en la mayoría de los casos: mucho más amable con la fibra.',
     'Perfecto para probar un color antes de decidirte por algo permanente.',
     'Se desvanece de forma progresiva, sin dejar una línea de crecimiento visible.',
     'Ideal para fantasía, reflejos o refrescar el color entre tintes.'],
    uso=['Aplicá sobre cabello limpio y seco o húmedo, según indique el envase.',
         'Repartí de forma pareja con guantes o pincel.',
         'Dejá actuar el tiempo indicado; a más tiempo, más intensidad.',
         'Enjuagá con agua fría y sin shampoo para que dure más.'],
    ideal='colores de fantasía, pruebas de tono y refrescar el color entre aplicaciones.',
    tip='Sobre base clara el color rinde muchísimo más. Si tenés el pelo oscuro, el resultado será sutil.',
    cat='color')

TIPOS['DECOLORANTES'] = T(
    'decolorante', 'aclara la base del cabello para preparar el tono que querés conseguir después',
    ['Aclara de forma controlada cuando se respeta el volumen de oxidante y el tiempo.',
     'Base imprescindible para colores de fantasía y rubios fríos.',
     'Mezcla homogénea, fácil de aplicar con pincel.',
     'Permite trabajar por niveles según cuánto necesites subir.'],
    uso=['Prueba de mecha obligatoria: te dice cuánto aclara y en cuánto tiempo en TU cabello.',
         'Mezclá con el oxidante en la proporción indicada, en bol no metálico.',
         'Aplicá con pincel empezando por medios y puntas; la raíz va al final porque el calor del cuero cabelludo acelera el proceso.',
         'Controlá visualmente cada 5 minutos y enjuagá apenas llegues al nivel buscado. Nunca superes el tiempo máximo del envase.'],
    ideal='aclarados, mechas y preparación de base para color.',
    tip='Después de decolorar, un tratamiento reconstructor no es opcional: es lo que evita que el pelo se quiebre.',
    cat='color')

TIPOS['MATIZANTES'] = T(
    'matizante', 'neutraliza los tonos amarillos o anaranjados y devuelve el rubio al punto que querías',
    ['Corrige el amarillento sin necesidad de volver a decolorar.',
     'Refresca el color entre visitas al salón.',
     'Actúa en pocos minutos: es de los productos más agradecidos que existen.',
     'Se puede usar de forma regular como mantenimiento.'],
    uso=['Aplicá sobre cabello lavado y escurrido.',
         'Repartí de forma pareja con guantes.',
         'Controlá el tiempo de cerca: de 2 a 5 minutos suele alcanzar, más puede dejar el pelo violáceo.',
         'Enjuagá y aplicá acondicionador.'],
    ideal='rubios, canas y cabello decolorado con tendencia al amarillo.',
    tip='Si es tu primera vez, mezclalo con un poco de acondicionador: matiza más suave y es más difícil pasarse.',
    cat='color')

TIPOS['HENNAS'] = T(
    'henna', 'colorea y da cuerpo a la fibra con un enfoque más natural que un tinte convencional',
    ['Alternativa vegetal a la coloración química tradicional.',
     'Aporta cuerpo y brillo además de color.',
     'El resultado es cálido y se funde de forma natural con tu base.',
     'Se puede repetir para intensificar el tono de forma gradual.'],
    uso=['Mezclá con agua tibia hasta formar una pasta, siguiendo las indicaciones del envase.',
         'Aplicá con guantes sobre cabello limpio y seco, por secciones.',
         'Cubrí con gorro y dejá actuar entre 1 y 3 horas según la intensidad buscada.',
         'Enjuagá con agua abundante, sin shampoo el primer día.'],
    det='Esta',
    ideal='quien busca color con un enfoque más natural.',
    tip='La henna no se lleva bien con decoloraciones posteriores. Si pensás aclararte, avisá en el salón.',
    cat='color')

TIPOS['ACCESORIOS COLORACION'] = T(
    'accesorio de coloración', 'hace que aplicar color en casa sea tan ordenado como en el salón',
    ['Aplicación precisa: menos manchas y menos producto desperdiciado.',
     'Fácil de limpiar para reutilizar en la próxima coloración.',
     'Resistente a los productos químicos del tinte y el decolorante.',
     'Imprescindible si te teñís en casa con frecuencia.'],
    titulo_uso='Cómo usarlo',
    uso=['Preparalo antes de mezclar el color, para no perder tiempo con la mezcla ya activada.',
         'Usá siempre bol y utensilios no metálicos con decolorantes.',
         'Lavá inmediatamente después de usar, antes de que el producto seque.'],
    ideal='coloración en casa y trabajo de salón.',
    cat='color')

# ==========================================================================
# MAQUILLAJE — rostro
# ==========================================================================
TIPOS['BASES & PRIMER'] = T(
    'base de maquillaje', 'unifica el tono de la piel y deja una superficie pareja sobre la que construir todo el maquillaje',
    ['Cobertura graduable: una capa fina para el día, dos para la noche.',
     'Se funde con la piel en lugar de quedar como una máscara.',
     'No se cuartea ni marca las líneas de expresión si la piel está bien hidratada.',
     'Base sólida para que el rubor, el contorno y el iluminador se difuminen bien.'],
    uso=['Empezá con la piel limpia e hidratada; esperá un par de minutos a que la crema absorba.',
         'Aplicá primer si querés más duración y mejor acabado.',
         'Poné pequeñas cantidades en frente, mejillas, nariz y mentón.',
         'Difuminá con esponja húmeda o brocha, siempre desde el centro hacia afuera.'],
    det='Esta',
    ideal='maquillaje diario y de ocasión, en todo tipo de piel.',
    tip='Probá el tono en la mandíbula, no en la mano: es la única forma de que no se note el corte con el cuello.',
    cat='maquillaje')

TIPOS['POLVOS'] = T(
    'polvo', 'sella el maquillaje, controla los brillos y deja la piel con acabado uniforme',
    ['Fija la base y hace que el maquillaje aguante muchas más horas.',
     'Controla el brillo de la zona T sin resecar el resto del rostro.',
     'Se puede retocar durante el día sin que el maquillaje se acumule.',
     'Textura fina que no marca poros ni líneas.'],
    uso=['Aplicá después de la base y el corrector.',
         'Cargá la brocha, sacudí el exceso y presioná suavemente sobre la piel.',
         'Insistí en la zona T, que es donde primero aparece el brillo.',
         'Para retocar durante el día, usá papel matificante antes de sumar más polvo.'],
    ideal='pieles mixtas y grasas, y cualquier maquillaje que tenga que durar.',
    tip='Presioná el polvo en lugar de barrerlo: así no arrastrás la base que pusiste debajo.',
    cat='maquillaje')

TIPOS['CORRECTORES'] = T(
    'corrector', 'tapa ojeras, rojeces y marquitas justo donde hace falta, sin cargar el resto del rostro',
    ['Alta cobertura en poco producto: corrige sin apelmazar.',
     'Ilumina la zona de la ojera y levanta la mirada al instante.',
     'Se difumina fácil y se funde con la base sin dejar bordes.',
     'Sirve también para perfilar y limpiar el contorno de labios y cejas.'],
    uso=['Aplicá después de la base.',
         'Para ojeras, dibujá un triángulo invertido bajo el ojo con la punta hacia la mejilla.',
         'Difuminá con esponja húmeda dando pequeños toques, sin arrastrar.',
         'Sellá con un poco de polvo suelto para que no se marque.'],
    ideal='ojeras, imperfecciones puntuales y correcciones de tono.',
    tip='Un corrector un tono más claro que tu base ilumina; del mismo tono, corrige. No es lo mismo.',
    cat='maquillaje')

TIPOS['RUBOR & ILUMINADOR'] = T(
    'rubor', 'devuelve color y dimensión al rostro para que el maquillaje no se vea plano',
    ['Pigmentación buena y construible: empezás suave y subís a gusto.',
     'Se difumina sin esfuerzo y no deja manchones.',
     'Da ese aspecto de buena cara que ninguna base consigue sola.',
     'Combina bien con acabados mate y satinados.'],
    uso=['Aplicá después de la base y el polvo.',
         'Sonreí y aplicá sobre la parte alta de la mejilla.',
         'Difuminá hacia la sien con movimientos suaves.',
         'Si usás iluminador, ponelo sobre el pómulo, el arco de cupido y el lagrimal.'],
    ideal='maquillaje diario y looks de fiesta.',
    tip='Subir el rubor hacia la sien estira ópticamente el rostro. Bajarlo lo redondea.',
    cat='maquillaje')

TIPOS['CONTORNO & BRONCEADOR'] = T(
    'producto de contorno', 'da profundidad y estructura al rostro con un efecto que se ve natural',
    ['Define pómulos, mandíbula y nariz sin que se note el truco.',
     'Tono pensado para generar sombra real, no una línea marrón.',
     'Textura que se difumina fácil, que es todo en contorno.',
     'Sirve también como bronceador para un efecto de piel con sol.'],
    uso=['Aplicá después de la base.',
         'Marcá bajo el pómulo, en las sienes y en la línea de la mandíbula.',
         'Difuminá muchísimo con brocha limpia hasta que no queden bordes.',
         'Terminá con rubor e iluminador para equilibrar.'],
    ideal='looks definidos, fotografía y eventos.',
    tip='Para contorno elegí un tono frío (gris-marrón); los tonos cálidos sirven para bronceador, no para sombra.',
    cat='maquillaje')

TIPOS['FIJADORES MAQUILLAJE'] = T(
    'fijador de maquillaje', 'sella el trabajo terminado y le suma horas de duración',
    ['El maquillaje aguanta calor, humedad y jornada larga.',
     'Quita el efecto polvoriento y devuelve un acabado de piel real.',
     'Funde las capas de producto entre sí, así no se ven separadas.',
     'Refresca el rostro en cualquier momento del día.'],
    uso=['Agitá el envase antes de usar.',
         'Cerrá los ojos y pulverizá a unos 20 o 30 cm en forma de X y de T.',
         'Dejá secar al aire, sin tocar ni secar con las manos.',
         'También podés rociar la esponja antes de difuminar para un acabado más jugoso.'],
    ideal='eventos, climas cálidos y maquillajes de larga duración.',
    tip='Rociar la brocha con fijador antes de aplicar sombras intensifica muchísimo el pigmento.',
    cat='maquillaje')

TIPOS['MAQUILLAJE'] = T(
    'producto de maquillaje', 'suma a tu neceser una opción versátil para el día a día',
    ['Pigmentación pareja y fácil de trabajar.',
     'Se integra bien con el resto de productos de tu rutina.',
     'Formato práctico para llevar encima.',
     'Buena relación entre lo que cuesta y lo que rinde.'],
    uso=['Aplicá sobre piel limpia o sobre la base, según el producto.',
         'Difuminá los bordes para que no queden marcas.',
         'Sellá con polvo o fijador si querés más duración.'],
    ideal='maquillaje diario.',
    cat='maquillaje')

TIPOS['MAQUILLAJE ARTISTICO'] = T(
    'maquillaje artístico', 'permite crear personajes, caracterizaciones y looks que no se hacen con maquillaje común',
    ['Pigmentación muy alta: los colores se ven exactamente como en el envase.',
     'Pensado para trabajo de caracterización, teatro, fotografía y disfraces.',
     'Se puede mezclar entre tonos para conseguir el color exacto.',
     'Larga duración bajo luces y calor.'],
    uso=['Preparalo según indique el envase (algunos se activan con agua).',
         'Aplicá con pincel, esponja o aerógrafo según la técnica.',
         'Construí en capas finas y dejá secar entre una y otra.',
         'Retirá con desmaquillante bifásico o aceite.'],
    ideal='caracterización, Halloween, teatro y producciones de foto.',
    cat='maquillaje')

TIPOS['RETOCADORES'] = T(
    'retocador', 'resuelve el retoque sobre la marcha, sin tener que rehacer el maquillaje',
    ['Corrige al instante y sin herramientas extra.',
     'Formato de bolsillo, siempre a mano.',
     'Preciso: retoca solo donde hace falta.',
     'Rinde muchísimo porque se usa en cantidades mínimas.'],
    titulo_uso='Cómo usarlo',
    uso=['Aplicá directamente sobre la zona a corregir.',
         'Difuminá con el dedo o con una esponja pequeña.',
         'Sellá con polvo si el retoque es sobre base.'],
    ideal='retoques durante el día y viajes.',
    cat='maquillaje')

TIPOS['DILUSORES MAQUILLAJE'] = T(
    'diluyente de maquillaje', 'devuelve la textura original al producto que empezó a secarse',
    ['Recupera productos que darías por perdidos: pura economía.',
     'Ajusta la fluidez para trabajar con aerógrafo o pincel fino.',
     'Unas gotas alcanzan.',
     'No altera el color del producto.'],
    uso=['Agregá 2 o 3 gotas al producto.',
         'Mezclá bien y esperá unos segundos.',
         'Sumá más gotas solo si hace falta.'],
    ideal='maquilladores profesionales y productos muy usados.',
    cat='maquillaje')

# ==========================================================================
# MAQUILLAJE — ojos y cejas
# ==========================================================================
TIPOS['SOMBRAS'] = T(
    'sombra de ojos', 'aporta color, profundidad y luz a la mirada con la intensidad que vos decidas',
    ['Pigmento que se ve desde la primera pasada, sin tener que insistir.',
     'Se difumina sin cortes, que es lo que separa un buen maquillaje de ojos de uno regular.',
     'Se puede trabajar en seco para un efecto suave o en húmedo para máxima intensidad.',
     'Los tonos combinan entre sí para armar looks de día y de noche.'],
    uso=['Aplicá primer o corrector en el párpado y sellá con polvo.',
         'Poné el tono medio en toda la cuenca como base.',
         'Sumá el tono oscuro en el pliegue y el ángulo externo, difuminando en forma de V.',
         'Iluminá el lagrimal y bajo la ceja con el tono más claro.'],
    det='Esta',
    ideal='maquillaje de ojos de día, noche y eventos.',
    tip='Difuminá siempre con una brocha limpia y sin producto: es el truco para que no queden bordes duros.',
    cat='maquillaje')

TIPOS['PESTANINA'] = T(
    'pestañina', 'abre la mirada al instante: es el producto que más cambia la cara con menos esfuerzo',
    ['Aporta volumen y longitud desde la primera capa.',
     'Cepillo diseñado para separar y peinar sin dejar grumos.',
     'Fórmula que no se cuartea ni cae bajo el ojo durante el día.',
     'Si solo pudieras usar un producto de maquillaje, sería este.'],
    uso=['Encrespá las pestañas antes de aplicar, nunca después.',
         'Limpiá el exceso de producto del cepillo en el borde del envase.',
         'Apoyá el cepillo en la raíz y movelo en zigzag hacia las puntas.',
         'Aplicá una segunda capa antes de que seque la primera si querés más volumen.'],
    det='Esta',
    ideal='maquillaje diario y cualquier look, por mínimo que sea.',
    tip='Nunca bombees el cepillo dentro del tubo: metés aire y la pestañina se seca antes de tiempo.',
    cat='maquillaje')

TIPOS['DELINEADORES OJOS/CEJAS'] = T(
    'delineador', 'define la mirada con el trazo justo, del más discreto al más gráfico',
    ['Trazo preciso y de color intenso desde la primera pasada.',
     'Buena duración: no se corre ni se transfiere al párpado móvil.',
     'Permite desde una línea fina hasta un delineado gráfico.',
     'Se retira fácil con desmaquillante bifásico.'],
    uso=['Apoyá el codo en una superficie firme para no temblar.',
         'Trazá pequeños guiones pegados a la línea de las pestañas y después unilos.',
         'Para el rabito, seguí la prolongación imaginaria de la línea inferior del ojo.',
         'Corregí el borde con un hisopo y un poco de desmaquillante.'],
    ideal='delineado diario, cat eye y maquillajes de noche.',
    tip='Si te tiembla el pulso, delineá con el ojo abierto y mirando al frente en el espejo.',
    cat='maquillaje')

TIPOS['LAPIZ OJOS'] = T(
    'lápiz de ojos', 'define la mirada con un trazo fácil de controlar y de difuminar',
    ['Textura que se desliza sin tirar del párpado.',
     'Se puede difuminar apenas aplicado para un efecto ahumado.',
     'Sirve para línea de agua, línea superior e inferior.',
     'Más fácil de manejar que un delineador líquido si estás empezando.'],
    uso=['Afilá el lápiz antes de usar para un trazo limpio.',
         'Trazá pegado a la raíz de las pestañas.',
         'Difuminá con un pincel o el dedo dentro de los primeros segundos.',
         'Sellá con una sombra del mismo tono para que dure más.'],
    ideal='delineados suaves, ahumados y uso diario.',
    tip='Guardá el lápiz unos minutos en la heladera antes de afilarlo: la punta sale perfecta.',
    cat='maquillaje')

TIPOS['LAPIZ CEJAS'] = T(
    'lápiz de cejas', 'rellena los huecos y define la forma sin que se note que hay producto',
    ['Trazo fino que imita el pelo real en lugar de pintar un bloque.',
     'Color que se funde con el vello natural.',
     'Buena fijación: la ceja se mantiene todo el día.',
     'Muchos incluyen cepillo para peinar y difuminar.'],
    uso=['Peiná la ceja hacia arriba con el cepillo.',
         'Marcá la forma con trazos cortos siguiendo la dirección del pelo.',
         'Rellená los huecos empezando por la parte media, no por el nacimiento.',
         'Difuminá con el cepillo para suavizar el resultado.'],
    ideal='cejas con poco vello o poco definidas.',
    tip='Elegí un tono igual o un poco más claro que tu cabello: el más oscuro casi siempre endurece la cara.',
    cat='maquillaje')

TIPOS['MAQUILLAJE CEJAS'] = T(
    'producto para cejas', 'da forma, color y fijación a la ceja con un acabado natural',
    ['Define la ceja sin el efecto marcador.',
     'Fija el vello en su sitio durante todo el día.',
     'Construible: aplicás poco y sumás si hace falta.',
     'Combina bien con lápiz para un resultado más completo.'],
    uso=['Peiná la ceja hacia arriba y afuera.',
         'Aplicá el producto siguiendo la forma natural.',
         'Difuminá los bordes para que no queden marcas.',
         'Fijá con gel transparente si querés que aguante más.'],
    ideal='cejas de todo tipo, en maquillaje diario y de evento.',
    cat='maquillaje')

TIPOS['ESTILIZADORES CEJAS'] = T(
    'estilizador de cejas', 'peina, fija y mantiene la ceja en su lugar todo el día',
    ['Fija el vello rebelde sin dejarlo acartonado ni brillante.',
     'Da ese efecto de ceja peinada que se ve prolijo sin parecer maquillado.',
     'Transparente o con color, se adapta a lo que necesites.',
     'Aguanta humedad y jornadas largas.'],
    uso=['Peiná la ceja hacia arriba con el cepillo del producto.',
         'Aplicá desde el nacimiento hacia la cola.',
         'Dejá secar unos segundos sin tocar.',
         'Si usaste lápiz o sombra, aplicá el gel al final.'],
    ideal='cejas con vello rebelde y looks de ceja peinada.',
    cat='maquillaje')

TIPOS['TRATAMIENTOS CEJAS/PESTANAS'] = T(
    'tratamiento para cejas y pestañas', 'acompaña el cuidado del vello para que se vea más fuerte y poblado',
    ['Se aplica en segundos y se integra a la rutina de noche sin esfuerzo.',
     'Formato con aplicador de precisión para llegar justo a la raíz.',
     'Pensado para uso continuado, que es cuando este tipo de producto rinde.',
     'Se puede usar bajo el maquillaje o solo por la noche.'],
    uso=['Desmaquillá muy bien la zona antes de aplicar.',
         'Pasá el aplicador por la línea de nacimiento de las pestañas y por las cejas.',
         'Usalo todas las noches sin saltarte días.',
         'Dale entre 6 y 8 semanas antes de evaluar el resultado.'],
    ideal='pestañas y cejas debilitadas por el uso de extensiones o maquillaje.',
    tip='La constancia importa más que la cantidad: una pasada cada noche, todas las noches.',
    cat='maquillaje')

TIPOS['PESTANAS DESECHABLES'] = T(
    'pestaña postiza', 'multiplica el volumen de la mirada en minutos y sin compromiso',
    ['Efecto inmediato que ninguna pestañina consigue sola.',
     'Banda flexible que se adapta a la forma del párpado.',
     'Reutilizables varias veces si las limpiás con cuidado.',
     'Desde el efecto natural hasta el más dramático, según el modelo.'],
    uso=['Medí la banda contra tu ojo y recortá el sobrante por el extremo externo.',
         'Aplicá una línea fina de pegante y esperá 30 segundos a que se ponga pegajoso.',
         'Colocá la banda pegada a la raíz de tus pestañas, empezando por el centro.',
         'Presioná los extremos y, si querés, delineá por encima para disimular la banda.'],
    det='Esta',
    ideal='eventos, fotografía y maquillajes de noche.',
    tip='Esperar a que el pegante se ponje pegajoso (no líquido) es la diferencia entre que peguen o no.',
    cat='maquillaje')

TIPOS['PEGANTES PESTANAS'] = T(
    'pegante para pestañas', 'sujeta las postizas todo el día sin despegarse en el peor momento',
    ['Agarre firme que aguanta calor y humedad.',
     'Secado transparente o negro según el producto: no se ve.',
     'Aplicador de precisión para no pasarse de cantidad.',
     'Se retira sin arrastrar las pestañas naturales.'],
    uso=['Agitá el envase antes de usar.',
         'Aplicá una línea muy fina sobre la banda de la pestaña postiza.',
         'Esperá 30 segundos hasta que el pegante esté pegajoso.',
         'Colocá la pestaña y presioná unos segundos.'],
    ideal='uso con pestañas postizas de banda.',
    cat='maquillaje')

TIPOS['ENCRESPADOR PESTANAS'] = T(
    'encrespador de pestañas', 'levanta la pestaña desde la raíz y abre la mirada antes de aplicar nada',
    ['Abre la mirada al instante, incluso sin maquillaje.',
     'Hace que la pestañina se vea mucho mejor: el rizo sostiene el producto.',
     'Almohadilla de silicona que no quiebra el pelo.',
     'Dura años si lo cuidás y cambiás la almohadilla.'],
    titulo_uso='Cómo usarlo',
    uso=['Usalo siempre ANTES de la pestañina, nunca después.',
         'Colocalo en la raíz, cerrá suave y mantené 5 segundos.',
         'Repetí a la mitad y en la punta para un rizo progresivo.',
         'Cambiá la almohadilla cada 3 meses aproximadamente.'],
    ideal='pestañas lacias o que caen.',
    tip='Calentá el encrespador unos segundos con el secador (que quede tibio, no caliente) y el rizo dura el doble.',
    cat='maquillaje')

TIPOS['REPUESTOS ENCRESPADOR'] = T(
    'repuesto de encrespador', 'devuelve al encrespador el agarre suave que tenía cuando era nuevo',
    ['Evita que tengas que cambiar el encrespador entero.',
     'Almohadilla blanda que protege la pestaña de quebrarse.',
     'Cambio en segundos, sin herramientas.',
     'Varias unidades por paquete.'],
    titulo_uso='Cómo usarlo',
    uso=['Retirá la almohadilla vieja con la uña o una pinza.',
         'Encajá la nueva en la ranura.',
         'Verificá que quede pareja antes de usar.'],
    ideal='mantenimiento del encrespador.',
    cat='maquillaje')

TIPOS['COMPLEMENTOS CEJAS/PESTANAS'] = T(
    'complemento para cejas y pestañas', 'completa el trabajo de la mirada con la herramienta correcta',
    ['Precisión en una zona donde el error se nota mucho.',
     'Fácil de manejar incluso si estás empezando.',
     'Resistente y reutilizable.',
     'Se higieniza sin problema entre usos.'],
    titulo_uso='Cómo usarlo',
    uso=['Trabajá siempre con buena luz y sobre la piel limpia.',
         'Desinfectá la herramienta antes y después de usarla.'],
    ideal='trabajo de cejas y pestañas en casa o en cabina.',
    cat='maquillaje')

TIPOS['PERFILADORES & DEPILADORES'] = T(
    'perfilador', 'define el contorno del vello con precisión y sin complicaciones',
    ['Trazo o corte limpio justo donde lo necesitás.',
     'Manejable y seguro incluso en zonas delicadas como la ceja.',
     'Resultado inmediato, sin esperas ni preparación.',
     'Compacto para llevar en el neceser.'],
    titulo_uso='Cómo usarlo',
    uso=['Trabajá con buena luz y la piel limpia y seca.',
         'Seguí la forma natural del vello, sin quitar de más.',
         'Avanzá de a poco: siempre podés sacar más, nunca devolver.',
         'Desinfectá la herramienta después de usarla.'],
    ideal='mantenimiento de cejas y perfilado en casa.',
    tip='Depilá siempre después de la ducha: el poro está abierto y duele bastante menos.',
    cat='maquillaje')

# ==========================================================================
# MAQUILLAJE — labios
# ==========================================================================
TIPOS['CREMOSOS/HUMECTANTES'] = T(
    'labial cremoso', 'aporta color intenso y sensación cómoda, sin ese tirantez del mate puro',
    ['Textura cremosa que se desliza y no marca las líneas del labio.',
     'Color cubriente en una sola pasada.',
     'Sensación humectante durante el uso, no solo al aplicarlo.',
     'Acabado luminoso que rejuvenece el rostro.'],
    uso=['Exfoliá los labios suavemente si están resecos.',
         'Aplicá bálsamo y esperá un minuto.',
         'Perfilá el contorno con lápiz si querés más definición y duración.',
         'Aplicá el labial desde el centro hacia las comisuras.'],
    ideal='uso diario y para quien no soporta la sensación de los mate.',
    tip='Si el labial se corre, perfilá primero con lápiz del mismo tono: hace de barrera.',
    cat='maquillaje')

TIPOS['LABIALES MATTE'] = T(
    'labial mate', 'da color intenso con acabado aterciopelado y una duración que no tienen los cremosos',
    ['Color muy pigmentado desde la primera capa.',
     'Acabado mate moderno, sin brillos.',
     'Larga duración: aguanta charla, café y buena parte del día.',
     'No transfiere tanto como un labial cremoso.'],
    uso=['Exfoliá e hidratá los labios un rato antes, esto es clave con los mate.',
         'Secá el exceso de bálsamo con un pañuelo.',
         'Perfilá con lápiz y rellená desde el centro.',
         'Dejá secar sin apretar los labios entre sí.'],
    ideal='eventos, jornadas largas y quien busca máxima duración.',
    tip='Los mate resaltan la resequedad. La exfoliación previa no es un extra, es parte del proceso.',
    cat='maquillaje')

TIPOS['BRILLOS LABIALES'] = T(
    'brillo labial', 'suma luz y volumen óptico al labio con el efecto jugoso que nunca pasa de moda',
    ['Efecto labio lleno sin necesidad de nada más.',
     'Se puede usar solo o encima de un labial para cambiar el acabado.',
     'Texturas que ya no se sienten pegajosas como las de antes.',
     'Aplicador que reparte el producto de forma pareja.'],
    uso=['Aplicá sobre labios limpios o sobre un labial mate.',
         'Poné más producto en el centro del labio inferior para maximizar el efecto volumen.',
         'Evitá frotar los labios: se lleva el brillo.',
         'Retocá cada 2 o 3 horas.'],
    ideal='looks frescos, maquillaje de día y adolescentes.',
    tip='Un toque de brillo en el centro del labio sobre un mate da un efecto tridimensional buenísimo.',
    cat='maquillaje')

TIPOS['LAPICES/DELINEADORES LABIALES'] = T(
    'delineador labial', 'define el contorno, evita que el color se corra y hace que el labial dure mucho más',
    ['Define la forma del labio y corrige asimetrías.',
     'Funciona como barrera: el labial deja de migrar hacia las arruguitas.',
     'Relleno completo del labio como base de color para máxima duración.',
     'Trazo firme pero cómodo, sin tironear.'],
    uso=['Perfilá siguiendo tu línea natural, empezando por el arco de cupido.',
         'Uní las líneas hacia las comisuras.',
         'Rellená todo el labio con el lápiz, no solo el borde.',
         'Aplicá el labial encima.'],
    ideal='maquillaje de labios duradero y corrección de forma.',
    tip='Rellenar el labio entero con el lápiz antes del labial duplica la duración del color.',
    cat='maquillaje')

TIPOS['TINTA PARA LABIOS'] = T(
    'tinta para labios', 'deja color que aguanta horas con ese efecto de labio mordido que se ve natural',
    ['Duración larguísima: el color queda aunque comas o tomes algo.',
     'Acabado ligero, sin sensación de tener producto encima.',
     'Efecto degradé muy fácil de conseguir.',
     'Se puede intensificar aplicando capas.'],
    det='Esta',
    uso=['Aplicá sobre labios limpios y secos.',
         'Difuminá hacia afuera con el dedo para el efecto degradé.',
         'Dejá secar unos segundos antes de sumar otra capa.',
         'Terminá con bálsamo para dar comodidad.'],
    ideal='looks naturales, clima cálido y días largos.',
    tip='Aplicá bálsamo por encima al final: la tinta sola puede resecar.',
    cat='maquillaje')

TIPOS['PROTECTORES/BALSAMOS LABIALES'] = T(
    'bálsamo labial', 'repara y protege el labio, que es piel fina y sin glándulas sebáceas propias',
    ['Alivia la resequedad y la descamación desde la primera aplicación.',
     'Protege del sol, el frío y el viento.',
     'Base imprescindible antes de cualquier labial mate.',
     'Formato de bolsillo para tener siempre a mano.'],
    uso=['Aplicá las veces que haga falta durante el día.',
         'Usalo siempre antes de un labial mate y esperá un minuto.',
         'Por la noche, aplicá una capa generosa antes de dormir.'],
    ideal='labios resecos, clima frío y uso diario todo el año.',
    tip='Si te lamés los labios constantemente, el bálsamo no va a alcanzar. Ese es el hábito a cortar primero.',
    cat='maquillaje')

TIPOS['EXFOLIANTES/MASCARILLAS LABIOS'] = T(
    'exfoliante labial', 'elimina la piel muerta del labio y lo deja liso para que el labial se vea parejo',
    ['Quita la descamación que arruina cualquier labial mate.',
     'Deja el labio suave al instante.',
     'Textura suave, pensada para una zona delicada.',
     'Uso rápido: un minuto y listo.'],
    uso=['Aplicá una pequeña cantidad sobre el labio.',
         'Masajeá con movimientos circulares durante 30 segundos, sin frotar fuerte.',
         'Retirá con un paño húmedo.',
         'Terminá siempre con bálsamo. Usalo una o dos veces por semana.'],
    ideal='labios resecos y como paso previo a labiales mate.',
    tip='No exfolies todos los días: el labio se irrita y terminás peor que al principio.',
    cat='maquillaje')

# ==========================================================================
# UNAS
# ==========================================================================
TIPOS['ESMALTE TRADICIONAL'] = T(
    'esmalte', 'da color parejo y brillante a la uña con la comodidad de quitarlo cuando quieras',
    ['Cubre en dos capas sin rayas ni zonas más claras.',
     'Secado rápido que no te obliga a quedarte quieta media hora.',
     'Pincel que se adapta a la curva de la uña y facilita el borde limpio.',
     'Se retira con removedor común, sin lámpara ni limado.'],
    uso=['Limá y dale forma a la uña seca, siempre en una sola dirección.',
         'Aplicá una base protectora y dejá secar.',
         'Pintá en tres pasadas: centro primero, después los laterales.',
         'Dejá secar y sellá con top coat brillante. Repetí el top coat cada dos días para estirar la manicura.'],
    ideal='manicura en casa y cambios de color frecuentes.',
    tip='Pasá el pincel con esmalte por el borde libre de la uña: es lo que evita que se descascare por la punta.',
    cat='unas')

TIPOS['ESMALTE SEMIPERMANENTE'] = T(
    'esmalte semipermanente', 'mantiene color y brillo de salón durante semanas, sin descascarados a los dos días',
    ['Dura entre 2 y 3 semanas con brillo de primer día.',
     'Se seca en lámpara al instante: no hay riesgo de arruinarla buscando las llaves.',
     'Color intenso y parejo, con acabado de gel.',
     'Suma resistencia a la uña natural mientras lo llevás puesto.'],
    uso=['Preparación: empujá cutícula, limá el brillo de la superficie y deshidratá la uña.',
         'Aplicá base y curá en lámpara UV/LED el tiempo que indique el fabricante.',
         'Aplicá dos capas finas de color, curando entre cada una.',
         'Sellá con top coat, curá y retirá la capa pegajosa con limpiador si el producto lo requiere.'],
    ideal='manicura de larga duración y trabajo profesional.',
    tip='Capas finas siempre: una capa gruesa no cura bien por dentro y se levanta a los pocos días.',
    cat='unas')

TIPOS['ESMALTE EFECTO GEL'] = T(
    'esmalte efecto gel', 'consigue el brillo y el cuerpo del gel sin necesidad de lámpara',
    ['Acabado tipo gel, con ese volumen y brillo que el esmalte común no da.',
     'Sin lámpara ni curado: seca al aire.',
     'Dura más que un esmalte tradicional.',
     'Se retira con removedor normal, sin limar.'],
    uso=['Prepará la uña y aplicá base.',
         'Pintá dos capas finas de color, dejando secar entre una y otra.',
         'Sellá con el top coat efecto gel del sistema.',
         'Evitá el agua caliente las primeras dos horas.'],
    ideal='quien quiere duración sin comprometerse con el semipermanente.',
    cat='unas')

TIPOS['MAQUILLAJE UNAS'] = T(
    'producto para uñas', 'suma color y acabado a la manicura con la textura que estés buscando',
    ['Pigmentación pareja y fácil de aplicar.',
     'Compatible con el resto de tu sistema de manicura.',
     'Acabado prolijo con poco esfuerzo.',
     'Rinde bastante más de lo que parece por el tamaño del frasco.'],
    uso=['Prepará la uña: limá, empujá cutícula y limpiá.',
         'Aplicá el producto en capas finas.',
         'Dejá secar o curá según corresponda.',
         'Sellá con top coat.'],
    ideal='manicura en casa y en cabina.',
    cat='unas')

TIPOS['ACRILICOS/PAINTING GEL'] = T(
    'producto de acrílico y gel', 'permite construir, esculpir y decorar uñas con acabado profesional',
    ['Permite alargar y corregir la forma de la uña, no solo pintarla.',
     'Buena adherencia y resistencia al uso diario.',
     'Se trabaja con el tiempo suficiente antes de endurecer.',
     'Se lima y pule hasta dejar el acabado exacto que buscás.'],
    uso=['Prepará la uña natural: empujá cutícula, limá el brillo y deshidratá.',
         'Colocá tip o molde según la técnica.',
         'Construí en capas finas respetando la arquitectura de la uña.',
         'Curá si corresponde, limá, pulí y sellá con top coat.'],
    ideal='manicuristas y uñas esculpidas.',
    tip='La preparación de la uña natural decide si el trabajo dura tres semanas o tres días.',
    cat='unas')

TIPOS['PINTURA ACRILICA UNAS'] = T(
    'pintura acrílica para uñas', 'permite dibujar decoraciones finas con el detalle de un pincel de artista',
    ['Colores muy pigmentados para trazos finos y nítidos.',
     'Se mezclan entre sí para conseguir cualquier tono.',
     'Se diluyen con agua: se corrige mientras está fresca.',
     'Rinde muchísimo, se usa en cantidades mínimas.'],
    uso=['Poné una gota sobre una paleta.',
         'Cargá el pincel fino y dibujá sobre la uña ya coloreada.',
         'Dejá secar al aire unos minutos.',
         'Sellá con top coat para proteger el diseño.'],
    det='Esta',
    ideal='nail art y decoración de uñas.',
    cat='unas')

TIPOS['BASES/TRATAMIENTOS UNAS'] = T(
    'base para uñas', 'protege la uña natural del pigmento y mejora el agarre del esmalte',
    ['Evita que los esmaltes oscuros manchen la uña de amarillo.',
     'El esmalte agarra mejor y la manicura dura más días.',
     'Muchas fórmulas suman activos fortalecedores.',
     'Rellena las irregularidades de la superficie para un acabado más liso.'],
    uso=['Aplicá sobre la uña limpia, seca y sin restos de grasa.',
         'Una sola capa fina alcanza.',
         'Dejá secar antes de aplicar el color.',
         'Usala siempre, también cuando pintás con colores claros.'],
    det='Esta',
    ideal='toda manicura, en casa o en cabina.',
    tip='Saltarse la base es la razón número uno por la que una manicura se descascara a los dos días.',
    cat='unas')

TIPOS['BRILLO UNAS'] = T(
    'top coat', 'sella el color y le da ese brillo de manicura recién hecha',
    ['Brillo espejo que dura días.',
     'Protege el color de golpes y roces.',
     'Alarga la manicura varios días si lo reaplicás.',
     'Secado rápido, no deja huellas.'],
    uso=['Aplicá sobre el color ya seco.',
         'Pasá el pincel también por el borde libre de la uña.',
         'Dejá secar sin tocar nada durante unos minutos.',
         'Reaplicá cada dos o tres días para renovar el brillo.'],
    ideal='cualquier manicura con esmalte.',
    cat='unas')

TIPOS['SECANTES'] = T(
    'secante de esmalte', 'acelera el secado para que puedas volver a usar las manos sin arruinar la manicura',
    ['Reduce el tiempo de secado de forma notoria.',
     'Evita las marcas que aparecen cuando el esmalte parecía seco y no lo estaba.',
     'Suma brillo además de secar.',
     'Unas gotas por uña alcanzan.'],
    uso=['Esperá 2 minutos después de la última capa de color.',
         'Aplicá una gota sobre cada uña o pulverizá según el formato.',
         'No toques nada durante un par de minutos.'],
    ideal='manicura en casa cuando andás con el tiempo justo.',
    cat='unas')

TIPOS['REMOVEDORES ESMALTE'] = T(
    'removedor de esmalte', 'quita el color sin tener que frotar durante diez minutos',
    ['Disuelve el esmalte rápido, incluso los colores oscuros.',
     'Menos frotado significa menos daño en la uña y la cutícula.',
     'Muchas fórmulas incluyen activos que compensan la resequedad.',
     'Rinde bastante: se usa poca cantidad por uña.'],
    uso=['Empapá un algodón y apoyalo sobre la uña 10 segundos antes de arrastrar.',
         'Arrastrá en una sola dirección, hacia la punta.',
         'Repetí con algodón limpio si queda pigmento en los bordes.',
         'Lavá las manos y aplicá aceite de cutícula al terminar.'],
    ideal='retirar esmalte tradicional y efecto gel.',
    tip='Apoyar el algodón unos segundos antes de frotar cambia por completo el resultado.',
    cat='unas')

TIPOS['DILUSORES ESMALTE'] = T(
    'diluyente de esmalte', 'devuelve la fluidez al esmalte que se volvió espeso en el frasco',
    ['Recupera esmaltes que ibas a tirar.',
     'Mantiene el color y el acabado originales, cosa que el removedor no hace.',
     'Unas pocas gotas por frasco alcanzan.',
     'Un frasco de diluyente salva decenas de esmaltes.'],
    uso=['Agregá 2 o 3 gotas dentro del frasco de esmalte.',
         'Cerrá y rodá el frasco entre las palmas, no lo agites.',
         'Dejá reposar unos minutos y probá la textura.',
         'Sumá gotas de a una si sigue espeso.'],
    ideal='esmaltes usados que empezaron a espesar.',
    tip='Nunca uses removedor para diluir esmalte: arruina la fórmula y el color queda opaco.',
    cat='unas')

TIPOS['REMOVEDORES/ACEITES CUTICULA'] = T(
    'producto para cutícula', 'ablanda y cuida la cutícula para que el contorno de la uña se vea prolijo',
    ['Ablanda la cutícula y hace que empujarla sea indoloro.',
     'Los aceites nutren el contorno y evitan los padrastros.',
     'Mejora el aspecto de la manicura incluso sin esmalte.',
     'Uso rápido y agradable, se convierte en hábito fácil.'],
    uso=['Aplicá en el contorno de cada uña.',
         'Esperá el tiempo indicado si es removedor (suele ser 1 minuto).',
         'Empujá suavemente con palito de naranjo o empujador.',
         'Si es aceite, masajeá y dejá absorber. Usalo todas las noches.'],
    ideal='manicura prolija y cuidado diario de la cutícula.',
    tip='Nunca cortes la cutícula si podés empujarla: es la barrera natural que protege la matriz de la uña.',
    cat='unas')

TIPOS['CORTACUTICULA'] = T(
    'cortacutícula', 'recorta con precisión el excedente de piel alrededor de la uña',
    ['Corte limpio que no desgarra ni deja padrastros.',
     'Filo de acero que mantiene la precisión con el uso.',
     'Tamaño de cabeza pensado para trabajar en un espacio muy pequeño.',
     'Cómodo de manejar incluso si no sos profesional.'],
    titulo_uso='Cómo usarlo',
    uso=['Ablandá la cutícula con removedor o agua tibia.',
         'Empujá con palito de naranjo.',
         'Cortá solo la piel suelta, nunca la cutícula viva.',
         'Desinfectá la herramienta antes y después de cada uso.'],
    ideal='manicura y pedicura en casa o en cabina.',
    tip='Si sangra, cortaste de más. Trabajá solo sobre la piel que ya está separada.',
    cat='unas')

TIPOS['CORTAUNAS/GUILLOTINAS'] = T(
    'cortaúñas', 'corta parejo y sin astillar, que es más de lo que se puede decir de cualquier cortaúñas',
    ['Corte limpio, sin dejar la uña quebrada ni con bordes filosos.',
     'Acero resistente que no se desafila a los tres usos.',
     'Buen agarre, no se resbala.',
     'Sirve para manos y pies según el modelo.'],
    titulo_uso='Cómo usarlo',
    uso=['Cortá con la uña seca, nunca recién salida del agua.',
         'Hacé varios cortes pequeños en lugar de uno solo.',
         'En los pies, cortá recto para evitar uñas encarnadas.',
         'Limá el borde después de cortar.'],
    ideal='cuidado básico de manos y pies.',
    cat='unas')

TIPOS['LIMAS'] = T(
    'lima', 'da forma al borde de la uña y deja el filo suave sin quebrar la lámina',
    ['Grano que desgasta sin astillar la uña.',
     'Da forma precisa: cuadrada, almendrada, redonda o lo que busques.',
     'Liviana y fácil de manejar.',
     'Larga vida útil si la limpiás después de usar.'],
    titulo_uso='Cómo usarla',
    uso=['Limá siempre con la uña seca.',
         'Trabajá en una sola dirección, de afuera hacia el centro.',
         'No hagas movimientos de vaivén: eso es lo que abre capas en la uña.',
         'Terminá suavizando el borde libre.'],
    det='Esta',
    ideal='manicura y pedicura en casa o profesional.',
    tip='Limar de ida y vuelta es el error más común y el que más uñas quiebra.',
    cat='unas')

TIPOS['BLOQUES UNAS'] = T(
    'bloque pulidor', 'alisa y da brillo natural a la superficie de la uña sin necesidad de esmalte',
    ['Deja la uña lisa y con brillo natural en un minuto.',
     'Empareja las crestas y las irregularidades de la lámina.',
     'Varias caras con distinto grano en una sola pieza.',
     'Ideal si no querés usar color pero querés uñas prolijas.'],
    titulo_uso='Cómo usarlo',
    uso=['Usá las caras en el orden indicado, del grano más grueso al más fino.',
         'Pasá suave, sin presionar.',
         'No lo uses más de una vez cada dos semanas: adelgaza la uña.',
         'Terminá con aceite de cutícula.'],
    ideal='uñas naturales y acabados sin esmalte.',
    cat='unas')

TIPOS['PALAS/ESMERILES'] = T(
    'esmeril para pies', 'elimina la piel dura del talón y devuelve suavidad al pie',
    ['Retira callosidad de forma pareja y controlada.',
     'Resultado visible desde el primer uso.',
     'Mango que permite llegar cómodo al talón.',
     'Lavable y reutilizable.'],
    titulo_uso='Cómo usarlo',
    uso=['Remojá los pies 10 minutos en agua tibia.',
         'Secá bien y pasá el esmeril sobre la zona dura.',
         'No insistas hasta dejar la piel enrojecida.',
         'Terminá con crema para pies y usalo una vez por semana.'],
    ideal='pedicura en casa y talones resecos.',
    cat='unas')

TIPOS['REMOVEDORES CALLOS'] = T(
    'removedor de callos', 'ablanda la piel endurecida del pie para poder retirarla sin lastimar',
    ['Ablanda la callosidad y hace el trabajo mucho más fácil.',
     'Evita tener que forzar con herramientas.',
     'Aplicación puntual, solo donde hace falta.',
     'Buen complemento de la pedicura en casa.'],
    uso=['Aplicá sobre la zona endurecida, evitando la piel sana.',
         'Respetá el tiempo indicado en el envase.',
         'Retirá con esmeril o piedra pómez.',
         'Enjuagá e hidratá el pie.'],
    ideal='talones y zonas de callosidad.',
    cat='unas')

TIPOS['PATECABRAS'] = T(
    'cortacallos', 'retira la piel dura del pie con precisión profesional',
    ['Herramienta de podología, precisa y eficaz.',
     'Cuchilla reemplazable para mantener el filo.',
     'Mango firme que da control.',
     'Resultado inmediato en callosidades marcadas.'],
    titulo_uso='Cómo usarlo',
    uso=['Remojá y secá el pie antes de empezar.',
         'Trabajá con pasadas finas y superficiales.',
         'Nunca cortes sobre piel sana ni en heridas.',
         'Si tenés diabetes o problemas de circulación, esto lo hace un profesional.'],
    ideal='pedicura profesional.',
    cat='unas')

TIPOS['ESPATULAS/PINZAS UNAS'] = T(
    'herramienta de manicura', 'da el control fino que la manicura necesita en los detalles',
    ['Precisión en trabajos donde el pulso importa.',
     'Acero resistente y fácil de desinfectar.',
     'Punta bien terminada, sin rebabas.',
     'Herramienta que dura años.'],
    titulo_uso='Cómo usarla',
    uso=['Desinfectá antes y después de cada uso.',
         'Trabajá con buena luz.',
         'Guardá en estuche para proteger la punta.'],
    det='Esta',
    ideal='manicuristas y manicura cuidada en casa.',
    cat='unas')

TIPOS['PINCELES MANICURE'] = T(
    'pincel de manicura', 'permite hacer detalles y decoraciones que con el pincel del esmalte son imposibles',
    ['Punta fina que dibuja líneas nítidas.',
     'Pelo que recupera la forma después de cada trazo.',
     'Varios tamaños para distintas técnicas de nail art.',
     'Fácil de limpiar si lo hacés apenas terminás.'],
    titulo_uso='Cómo usarlo',
    uso=['Cargá el pincel con poco producto.',
         'Apoyá la mano para tener pulso firme.',
         'Limpiá el pincel con el limpiador adecuado inmediatamente después de usarlo.',
         'Guardalo horizontal o con la punta hacia arriba.'],
    ideal='nail art y trabajo de precisión.',
    cat='unas')

TIPOS['FRESAS/BROCAS UNAS'] = T(
    'fresa para uñas', 'trabaja cutícula, limado y retirado de producto con el torno',
    ['Desbasta rápido y parejo, mucho más veloz que a mano.',
     'Distintas formas y granos para cada etapa del trabajo.',
     'Material resistente al uso intensivo.',
     'Se esteriliza sin perder filo.'],
    titulo_uso='Cómo usarla',
    uso=['Elegí la fresa y la velocidad según la etapa del trabajo.',
         'Trabajá en movimiento constante, nunca fija en un punto.',
         'Mantené el ángulo correcto para no lastimar la lámina.',
         'Esterilizá después de cada cliente.'],
    det='Esta',
    ideal='manicuristas con torno.',
    tip='Si la fresa calienta, estás presionando de más o quedándote quieta en un punto.',
    cat='unas')

TIPOS['PULIDORES/DRILL UNAS'] = T(
    'torno de uñas', 'agiliza el trabajo de manicura y deja acabados que a mano llevarían el triple de tiempo',
    ['Reduce muchísimo el tiempo de preparación y retirado.',
     'Velocidad regulable para adaptarse a cada etapa.',
     'Compatible con fresas estándar.',
     'Herramienta clave para trabajar con volumen de clientas.'],
    titulo_uso='Cómo usarlo',
    uso=['Colocá la fresa y asegurá el mandril.',
         'Empezá con velocidad baja hasta tomar confianza.',
         'Mantené el torno en movimiento sobre la uña.',
         'Limpiá y guardá el equipo después de cada jornada.'],
    ideal='manicuristas profesionales.',
    cat='unas')

TIPOS['LAMPARAS UNAS'] = T(
    'lámpara de uñas', 'cura el semipermanente y el gel de forma pareja en todos los dedos',
    ['Curado uniforme: no quedan zonas blandas que después se levanten.',
     'Tiempos preseleccionados para no adivinar.',
     'LED de larga vida, sin cambiar tubos.',
     'Espacio cómodo para la mano completa.'],
    titulo_uso='Cómo usarla',
    uso=['Colocá la mano completa dentro, con los dedos bien apoyados.',
         'Seleccioná el tiempo que indique tu marca de esmalte.',
         'Curá el pulgar aparte si no entra en la misma posición.',
         'Limpiá el interior con un paño seco cada tanto.'],
    det='Esta',
    ideal='manicura semipermanente y en gel.',
    cat='unas')

TIPOS['MONOMEROS'] = T(
    'monómero', 'es el líquido que activa el polímero acrílico para poder esculpir la uña',
    ['Mezcla de trabajo con el tiempo justo antes de endurecer.',
     'Permite modelar con comodidad sin que el producto se vuelva pegajoso.',
     'Acabado transparente y resistente.',
     'Compatible con sistemas acrílicos estándar.'],
    uso=['Trabajá siempre en un espacio bien ventilado.',
         'Cargá el pincel con monómero y sacá el exceso.',
         'Tomá la perla de polímero y modelá sobre la uña.',
         'Cerrá el frasco apenas termines para evitar la evaporación.'],
    ideal='uñas esculpidas en acrílico.',
    cat='unas')

TIPOS['UNAS POSTIZAS'] = T(
    'uña postiza', 'da largo y forma al instante, sin esperar a que crezca la uña natural',
    ['Resultado inmediato: manicura lista en minutos.',
     'Formas y largos variados para elegir.',
     'Se pueden limar y pintar como una uña natural.',
     'Reutilizables en varios modelos.'],
    det='Esta',
    uso=['Elegí el tamaño que mejor se ajuste a cada dedo.',
         'Prepará la uña natural: limá el brillo y limpiá.',
         'Aplicá pegante y presioná la uña postiza 10 segundos.',
         'Limá la forma y el largo, y pintá si querés.'],
    ideal='eventos y manicura rápida.',
    cat='unas')

TIPOS['APLIQUES/STICKERS'] = T(
    'aplique para uñas', 'decora en segundos sin necesidad de saber dibujar',
    ['Diseños que a mano llevarían mucho tiempo y pulso.',
     'Aplicación simple, no hace falta experiencia.',
     'Resultado que se ve profesional.',
     'Muchos diseños por lámina: rinde para varias manicuras.'],
    titulo_uso='Cómo usarlo',
    uso=['Pintá y dejá secar el esmalte base.',
         'Despegá el aplique con una pinza.',
         'Colocalo sobre la uña y presioná desde el centro hacia los bordes.',
         'Sellá con top coat cubriendo todo, incluido el borde libre.'],
    ideal='nail art fácil y manicura decorada.',
    cat='unas')

TIPOS['COMPLEMENTOS MANICURE/PEDICURE'] = T(
    'complemento de manicura', 'resuelve ese paso de la manicura que sin la herramienta correcta se complica',
    ['Hace más simple un paso que a mano cuesta.',
     'Material resistente y fácil de higienizar.',
     'Tamaño cómodo para trabajar.',
     'Buena inversión si hacés manicura seguido.'],
    titulo_uso='Cómo usarlo',
    uso=['Usalo en el paso correspondiente de tu rutina de manicura.',
         'Desinfectá antes y después.',
         'Guardalo limpio y seco.'],
    ideal='manicura y pedicura en casa o en cabina.',
    cat='unas')

TIPOS['KIT MANICURE/PEDICURE'] = T(
    'kit de manicura', 'reúne en un solo estuche todo lo necesario para una manicura completa',
    ['Todas las herramientas juntas y ordenadas: no falta nada a mitad del proceso.',
     'Sale mejor de precio que comprar pieza por pieza.',
     'Estuche que las mantiene protegidas y a mano.',
     'Buena opción para regalar.'],
    titulo_uso='Cómo usarlo',
    uso=['Seguí el orden habitual: remojo, cutícula, limado, pulido y esmaltado.',
         'Desinfectá las herramientas después de cada uso.',
         'Guardá todo en el estuche para que no se dañen las puntas.'],
    ideal='manicura y pedicura en casa.',
    cat='unas')

TIPOS['MANICURE & PEDICURE'] = T(
    'producto de manicura y pedicura', 'completa tu set de manicura con una pieza que se usa más de lo que imaginás',
    ['Pensado para el trabajo de manos y pies.',
     'Fácil de usar y de higienizar.',
     'Resistente al uso frecuente.',
     'Se integra con el resto de tus herramientas.'],
    titulo_uso='Cómo usarlo',
    uso=['Usalo en el paso correspondiente de la rutina.',
         'Desinfectá antes y después de cada uso.'],
    ideal='manicura y pedicura.',
    cat='unas')

TIPOS['MALETAS UNAS'] = T(
    'maleta de manicura', 'ordena y transporta todo el equipo de trabajo sin que se dañe nada',
    ['Compartimentos que mantienen cada cosa en su lugar.',
     'Protege frascos y herramientas en el traslado.',
     'Imprescindible si trabajás a domicilio.',
     'Material resistente al uso diario.'],
    titulo_uso='Cómo usarla',
    uso=['Distribuí los frascos en los compartimentos fijos para que no se vuelquen.',
         'Guardá las herramientas en sus estuches.',
         'Limpiá el interior cada tanto.'],
    det='Esta',
    ideal='manicuristas a domicilio.',
    cat='unas')

TIPOS['LIMPIADORES UNAS'] = T(
    'limpiador de uñas', 'retira la capa pegajosa y deshidrata la lámina para que el producto agarre bien',
    ['Deja la uña lista para que la base adhiera de verdad.',
     'Retira la capa pegajosa del semipermanente y revela el brillo final.',
     'Evaporación rápida, sin dejar residuo.',
     'Paso corto que decide la duración de todo el trabajo.'],
    uso=['Aplicá con un pad sin pelusa sobre la uña.',
         'Usalo antes de la base para deshidratar.',
         'Usalo al final, después de curar el top coat, para retirar la capa pegajosa.',
         'No toques la uña con los dedos entre paso y paso.'],
    ideal='manicura semipermanente y en gel.',
    cat='unas')

TIPOS['HIGIENE/CUIDADO UNAS'] = T(
    'producto de cuidado de uñas', 'mantiene la uña sana, que es la base de cualquier manicura que dure',
    ['Cuida la lámina y el contorno, no solo el aspecto.',
     'Uso rápido, fácil de sostener en el tiempo.',
     'Complementa cualquier tipo de manicura.',
     'Formato práctico para tener a mano.'],
    uso=['Aplicá sobre uñas limpias.',
         'Usalo con regularidad; los resultados son acumulativos.',
         'Combinalo con aceite de cutícula por la noche.'],
    ideal='uñas débiles o quebradizas.',
    cat='unas')

TIPOS['ANTIHONGOS'] = T(
    'producto antihongos', 'acompaña el cuidado de uñas y piel con problemas de hongos',
    ['Aplicación localizada y sencilla.',
     'Formato pensado para usarse de forma constante.',
     'Se integra con la rutina diaria de higiene.',
     'Presentación práctica para llevar.'],
    uso=['Lavá y secá muy bien la zona antes de aplicar.',
         'Seguí exactamente las indicaciones del envase.',
         'Mantené el tratamiento durante todo el período indicado, aunque veas mejoría antes.',
         'Si no ves cambios o el cuadro empeora, consultá con un profesional de la salud.'],
    ideal='cuidado complementario de uñas y piel.',
    tip='Este tipo de producto no reemplaza el diagnóstico médico. Ante dudas, consultá.',
    cat='unas')

# ==========================================================================
# FACIAL
# ==========================================================================
TIPOS['CREMAS FACIALES'] = T(
    'crema facial', 'hidrata, protege y mantiene la barrera de la piel en condiciones día tras día',
    ['Hidratación que se sostiene durante horas, no solo el rato después de aplicarla.',
     'Textura que absorbe sin dejar película grasosa.',
     'Deja la piel lista para el maquillaje o para dormir.',
     'Paso base de cualquier rutina: sin hidratación, el resto rinde menos.'],
    uso=['Limpiá el rostro y aplicá tónico si usás.',
         'Tomá una cantidad del tamaño de una avellana.',
         'Repartí en frente, mejillas, nariz y mentón.',
         'Extendé con movimientos suaves de adentro hacia afuera y hacia arriba, incluyendo el cuello.'],
    det='Esta',
    ideal='rutina facial diaria, de mañana y de noche.',
    tip='Aplicala con la piel apenas húmeda: la hidratación se sella mucho mejor.',
    cat='facial')

TIPOS['SERUM FACIALES'] = T(
    'sérum facial', 'concentra activos en una textura ligera que penetra más que una crema',
    ['Mayor concentración de activos que una crema común.',
     'Textura ligera que absorbe en segundos.',
     'Se puede combinar con tu hidratante habitual sin cambiar toda la rutina.',
     'Unas gotas alcanzan: el frasco pequeño rinde meses.'],
    uso=['Aplicá sobre la piel limpia, antes de la crema hidratante.',
         'Poné 3 o 4 gotas en la palma y presioná sobre el rostro, sin frotar.',
         'Esperá un minuto a que absorba.',
         'Sellá con tu crema hidratante y, de día, con protector solar.'],
    ideal='quien quiere resultados concretos y ya tiene una rutina básica armada.',
    tip='El orden importa: del producto más líquido al más denso. El sérum siempre va antes de la crema.',
    cat='facial')

TIPOS['AMPOLLETAS/BALSAMOS FACIALES'] = T(
    'ampolleta facial', 'entrega una dosis intensiva de activos en el momento en que la piel más lo necesita',
    ['Concentración alta en una dosis única.',
     'Efecto visible en piel apagada o cansada, ideal antes de un evento.',
     'Envase individual: el activo llega fresco, sin oxidarse.',
     'Se usa de forma puntual o en cura de varias semanas.'],
    det='Esta',
    uso=['Limpiá muy bien el rostro.',
         'Aplicá el contenido sobre rostro, cuello y escote.',
         'Presioná con las palmas hasta que absorba.',
         'Sellá con crema hidratante.'],
    ideal='piel apagada, rutinas de choque y preparación para eventos.',
    cat='facial')

TIPOS['TONICOS FACIALES'] = T(
    'tónico facial', 'reequilibra la piel después de la limpieza y la prepara para lo que viene después',
    ['Retira los últimos restos de limpiador y de agua dura.',
     'Deja la piel receptiva: lo que apliques después penetra mejor.',
     'Refresca y calma al instante.',
     'Paso rápido que mejora el resultado de toda la rutina.'],
    uso=['Aplicá después de limpiar el rostro.',
         'Poné el producto en un algodón o en las palmas.',
         'Pasá por todo el rostro evitando el contorno de ojos.',
         'No enjuagues. Seguí con sérum y crema.'],
    ideal='cualquier rutina facial que ya tenga limpieza e hidratación.',
    cat='facial')

TIPOS['AGUAS FACIALES'] = T(
    'agua micelar', 'limpia y desmaquilla en un solo paso, sin frotar y sin enjuagar',
    ['Arrastra maquillaje, protector solar y contaminación sin agredir.',
     'No deja sensación de tirantez ni película grasosa.',
     'Apta para contorno de ojos y labios.',
     'Práctica para la noche y para viajes.'],
    det='Esta',
    uso=['Empapá un algodón con el producto.',
         'Apoyá sobre el ojo o la zona maquillada unos segundos antes de arrastrar.',
         'Repetí con algodón limpio hasta que salga sin restos.',
         'Si usaste maquillaje pesado o protector solar, hacé después una limpieza con gel o jabón.'],
    ideal='desmaquillado diario y limpieza rápida.',
    tip='Apoyar y esperar en lugar de frotar evita irritar el contorno de ojos.',
    cat='facial')

TIPOS['GELES FACIALES'] = T(
    'gel facial', 'limpia en profundidad con una textura fresca que no deja la piel tirante',
    ['Arrastra grasa e impurezas sin llevarse la hidratación necesaria.',
     'Textura gel que enjuaga limpio, sin residuos.',
     'Sensación de frescura inmediata.',
     'Apto para uso diario, mañana y noche.'],
    uso=['Mojá el rostro con agua tibia.',
         'Emulsioná una pequeña cantidad entre las manos.',
         'Masajeá en círculos durante 30 segundos.',
         'Enjuagá y secá con toques de toalla, sin frotar.'],
    ideal='pieles mixtas y grasas.',
    cat='facial')

TIPOS['ESPUMAS FACIALES'] = T(
    'espuma limpiadora', 'limpia de forma suave con una textura aireada que se reparte sola',
    ['Espuma lista: no hay que emulsionar, se aplica directo.',
     'Limpieza suave, ideal para pieles sensibles.',
     'Enjuaga sin dejar residuo.',
     'Rinde muchísimo porque el dosificador controla la cantidad.'],
    det='Esta',
    uso=['Mojá el rostro.',
         'Dosificá una o dos pulsaciones en la mano.',
         'Masajeá suave por todo el rostro.',
         'Enjuagá con agua tibia.'],
    ideal='pieles sensibles y limpieza diaria.',
    cat='facial')

TIPOS['JABONES FACIALES'] = T(
    'jabón facial', 'limpia el rostro de forma efectiva con un formato práctico y rendidor',
    ['Limpieza profunda de grasa e impurezas.',
     'Formato que rinde muchísimo más que un limpiador líquido.',
     'Fácil de llevar, no cuenta como líquido en el equipaje.',
     'Fórmulas pensadas para el rostro, no jabón de manos reciclado.'],
    uso=['Mojá el rostro y el jabón.',
         'Frotá el jabón entre las manos hasta hacer espuma.',
         'Aplicá la espuma en el rostro y masajeá 30 segundos.',
         'Enjuagá y guardá el jabón en una jabonera que drene.'],
    ideal='limpieza facial diaria.',
    cat='facial')

TIPOS['LIMPIEZA FACIAL'] = T(
    'limpiador facial', 'retira lo que el día dejó sobre la piel para que la rutina pueda funcionar',
    ['Limpieza efectiva sin resecar.',
     'Primer paso de cualquier rutina que funcione.',
     'Textura agradable de usar a diario.',
     'Deja la piel lista para el resto de los productos.'],
    uso=['Aplicá sobre el rostro húmedo.',
         'Masajeá en círculos suaves.',
         'Enjuagá con agua tibia.',
         'Secá con toques y seguí con tónico y crema.'],
    ideal='rutina facial diaria.',
    cat='facial')

TIPOS['EXFOLIANTES FACIALES'] = T(
    'exfoliante facial', 'renueva la superficie de la piel y devuelve luminosidad a un rostro apagado',
    ['Elimina células muertas que apagan el rostro.',
     'La piel queda más suave al tacto desde el primer uso.',
     'Los productos que apliques después penetran mejor.',
     'Ayuda a mantener los poros despejados.'],
    uso=['Aplicá sobre el rostro húmedo y limpio.',
         'Masajeá en círculos suaves 30 segundos, evitando el contorno de ojos.',
         'Enjuagá con agua tibia.',
         'Usalo una o dos veces por semana, nunca a diario.'],
    ideal='piel apagada, con textura irregular o poros marcados.',
    tip='Exfoliar de más irrita y empeora todo. Dos veces por semana es el techo.',
    cat='facial')

TIPOS['MASCARILLAS FACIALES'] = T(
    'mascarilla facial', 'concentra un tratamiento intensivo en 15 minutos de dedicarte a vos',
    ['Resultado visible en una sola sesión.',
     'Tratamiento intensivo sin salir de casa.',
     'Se elige según lo que la piel necesite ese día.',
     'Ritual agradable que además funciona.'],
    det='Esta',
    uso=['Limpiá y secá el rostro.',
         'Aplicá una capa pareja evitando ojos y labios.',
         'Dejá actuar entre 10 y 20 minutos según el envase.',
         'Retirá o enjuagá y seguí con tónico y crema. Una o dos veces por semana.'],
    ideal='rutina semanal y preparación antes de eventos.',
    cat='facial')

TIPOS['VELOS FACIALES'] = T(
    'velo facial', 'entrega un baño de activos en 15 minutos con la comodidad de una mascarilla en tela',
    ['Aplicación limpia y sin desperdicio.',
     'La tela mantiene los activos en contacto con la piel todo el tiempo.',
     'Efecto inmediato de piel descansada y jugosa.',
     'Individual: siempre fresco y sin contaminar.'],
    uso=['Limpiá y secá el rostro.',
         'Desplegá el velo y ajustalo a los ojos, nariz y boca.',
         'Dejá actuar entre 15 y 20 minutos.',
         'Retirá y masajeá el suero sobrante hasta que absorba. No hace falta enjuagar.'],
    ideal='antes de un evento o cuando la piel está apagada.',
    cat='facial')

TIPOS['BANDAS FACIALES'] = T(
    'banda facial', 'retira los puntos negros de la nariz de forma mecánica y visible',
    ['Resultado que se ve en la banda al retirarla.',
     'Uso rápido: 10 o 15 minutos.',
     'Se aplica solo donde hace falta.',
     'Práctica para incluir en la rutina semanal.'],
    det='Esta',
    uso=['Humedecé bien la zona: sin agua, la banda no adhiere.',
         'Aplicá la banda y presioná para que se adapte.',
         'Esperá a que endurezca, entre 10 y 15 minutos.',
         'Retirá despacio desde los bordes hacia el centro y enjuagá.'],
    ideal='puntos negros en nariz, mentón y frente.',
    tip='Después de usarla, pasá un tónico: el poro queda abierto y conviene cerrarlo.',
    cat='facial')

TIPOS['TOALLITAS DESMAQUILLANTES'] = T(
    'toallita desmaquillante', 'desmaquilla en cualquier lugar y sin agua de por medio',
    ['Sin agua ni algodón: solo abrir y usar.',
     'Perfectas para viaje, gimnasio o después de un evento.',
     'Suaves, aptas para el contorno de ojos.',
     'Envase que se cierra y mantiene la humedad.'],
    det='Esta',
    uso=['Pasá la toallita sobre el rostro con movimientos suaves.',
         'Para los ojos, apoyá unos segundos antes de arrastrar.',
         'Usá una toallita nueva si queda maquillaje.',
         'Lavá el rostro después si podés: la toallita no reemplaza la limpieza completa.'],
    ideal='viajes, gimnasio y noches en las que no llegás al lavabo.',
    cat='facial')

TIPOS['DESMAQUILLANTES & BIFASICOS'] = T(
    'desmaquillante bifásico', 'disuelve el maquillaje más resistente, incluso el waterproof',
    ['Se lleva la pestañina waterproof y los labiales de larga duración, que es donde otros fallan.',
     'Fase oleosa que disuelve y fase acuosa que arrastra.',
     'No deja película grasosa en el ojo.',
     'Respeta el contorno de ojos si se usa sin frotar.'],
    uso=['Agitá el envase para mezclar las dos fases.',
         'Empapá un algodón.',
         'Apoyá sobre el ojo cerrado 15 segundos y arrastrá hacia afuera.',
         'Repetí hasta que salga limpio y hacé después una limpieza facial normal.'],
    ideal='maquillaje de ojos intenso y productos waterproof.',
    cat='facial')

TIPOS['LECHES/ACEITES FACIALES'] = T(
    'aceite facial', 'nutre y sella la hidratación con una textura que la piel seca agradece de inmediato',
    ['Nutrición profunda para pieles secas o deshidratadas.',
     'Sella el agua de los pasos anteriores para que no se evapore.',
     'Deja la piel con un aspecto luminoso, no grasoso, si se dosifica bien.',
     'Unas gotas alcanzan para todo el rostro.'],
    uso=['Aplicá al final de la rutina, después de la crema.',
         'Poné 3 o 4 gotas en la palma y calentá frotando las manos.',
         'Presioná sobre el rostro en lugar de frotar.',
         'De día, seguí con protector solar.'],
    ideal='piel seca, madura o deshidratada, y para la rutina de noche.',
    cat='facial')

TIPOS['BRUMAS FACIALES'] = T(
    'bruma facial', 'refresca e hidrata en cualquier momento del día, incluso sobre el maquillaje',
    ['Refresca al instante sin arruinar el maquillaje.',
     'Aporta hidratación extra en ambientes secos o con aire acondicionado.',
     'Formato bolsillo, siempre disponible.',
     'También sirve para difuminar polvos y quitar el efecto seco.'],
    det='Esta',
    uso=['Agitá antes de usar.',
         'Pulverizá a unos 20 cm del rostro con los ojos cerrados.',
         'Dejá secar al aire o presioná con las manos.',
         'Usala las veces que quieras durante el día.'],
    ideal='clima cálido, oficina con aire acondicionado y retoques.',
    cat='facial')

TIPOS['FACIAL'] = T(
    'producto facial', 'suma un paso de cuidado al rostro con una fórmula pensada para la piel de la cara',
    ['Formulado específicamente para la piel del rostro, más fina y sensible.',
     'Se integra sin problema con el resto de tu rutina.',
     'Textura agradable para uso diario.',
     'Resultado acumulativo con el uso constante.'],
    uso=['Aplicá sobre el rostro limpio.',
         'Seguí las indicaciones específicas del envase.',
         'Usalo de forma regular para notar el cambio.'],
    ideal='rutina facial diaria.',
    cat='facial')

TIPOS['KIT FACIALES'] = T(
    'kit facial', 'arma una rutina completa con productos que fueron pensados para trabajar juntos',
    ['Rutina completa sin tener que investigar qué combina con qué.',
     'Mejor precio que comprando cada paso por separado.',
     'Los productos de una misma línea se potencian entre sí.',
     'Muy buena opción para regalar o para empezar a cuidarse la piel.'],
    uso=['Seguí el orden indicado: limpieza, tónico, tratamiento e hidratación.',
         'Respetá los tiempos de cada paso.',
         'Sostené la rutina al menos 4 semanas para evaluar resultados.'],
    ideal='quien está armando su primera rutina facial o quiere cambiarla completa.',
    cat='facial')

TIPOS['ACCESORIOS DE LIMPIEZA FACIAL'] = T(
    'accesorio de limpieza facial', 'potencia la limpieza del rostro más allá de lo que hacen las manos',
    ['Limpieza más profunda que solo con los dedos.',
     'Ayuda a que el limpiador rinda mejor.',
     'Reutilizable y fácil de higienizar.',
     'Se nota la diferencia en la textura de la piel.'],
    titulo_uso='Cómo usarlo',
    uso=['Humedecé el accesorio y aplicá el limpiador.',
         'Masajeá con movimientos suaves y circulares.',
         'Enjuagá el rostro y el accesorio.',
         'Dejalo secar al aire y reemplazalo según indique el fabricante.'],
    ideal='limpieza facial profunda, una o dos veces por semana.',
    tip='Si tenés acné activo o rosácea, mejor limpiá solo con las manos.',
    cat='facial')

TIPOS['MASAJEADORES FACIALES'] = T(
    'masajeador facial', 'activa la circulación y ayuda a desinflamar el rostro en pocos minutos',
    ['Desinflama la cara hinchada de la mañana.',
     'Momento de autocuidado que además relaja de verdad.',
     'Ayuda a que las cremas y sérums penetren mejor.',
     'Uso simple, no hace falta técnica profesional.'],
    titulo_uso='Cómo usarlo',
    uso=['Aplicá antes un sérum o aceite para que deslice.',
         'Trabajá siempre de adentro hacia afuera y de abajo hacia arriba.',
         'Dedicá entre 5 y 10 minutos.',
         'Limpiá el masajeador después de cada uso.'],
    ideal='rostro hinchado, rutina de noche y momentos de autocuidado.',
    tip='Guardalo en la heladera: frío desinflama el doble.',
    cat='facial')

# ==========================================================================
# CORPORAL, SOLAR Y DEPILACION
# ==========================================================================
TIPOS['CREMAS CORPORALES'] = T(
    'crema corporal', 'devuelve suavidad e hidratación a toda la piel del cuerpo, que también necesita atención',
    ['Hidratación que dura horas, no solo el momento de aplicarla.',
     'Absorbe rápido: podés vestirte sin esperar.',
     'Alivia la tirantez y la aspereza de codos, rodillas y piernas.',
     'Textura agradable que hace que no te saltes el paso.'],
    det='Esta',
    uso=['Aplicá sobre la piel limpia, preferentemente apenas salís de la ducha.',
         'Masajeá con movimientos circulares ascendentes.',
         'Insistí en codos, rodillas, talones y cualquier zona reseca.',
         'Usala a diario, mañana o noche.'],
    ideal='hidratación diaria de todo el cuerpo.',
    tip='Con la piel todavía húmeda la crema atrapa el agua y la hidratación rinde el doble.',
    cat='corporal')

TIPOS['MANTEQUILLAS CORPORALES'] = T(
    'manteca corporal', 'nutre en profundidad las zonas que una crema ligera no alcanza a resolver',
    ['Textura densa para pieles muy secas.',
     'Se funde con el calor de la piel y se extiende sin esfuerzo.',
     'Ideal para codos, rodillas, talones y manos castigadas.',
     'Una capa a la noche y amanecés con otra piel.'],
    det='Esta',
    uso=['Tomá una porción y calentala entre las palmas.',
         'Masajeá sobre la piel limpia hasta que absorba.',
         'Insistí en las zonas más ásperas.',
         'Para un efecto intensivo, aplicá de noche y cubrí con medias o guantes de algodón.'],
    ideal='piel muy seca, invierno y zonas ásperas.',
    cat='corporal')

TIPOS['LECHES/BALSAMOS CORPORALES'] = T(
    'leche corporal', 'hidrata todo el cuerpo con una textura ligera que absorbe en segundos',
    ['Textura fluida que se reparte fácil en superficies grandes.',
     'Absorbe rápido, sin dejar el cuerpo pegajoso.',
     'Perfecta para clima cálido, cuando una crema densa resulta pesada.',
     'Rinde muchísimo.'],
    det='Esta',
    uso=['Aplicá sobre la piel limpia y húmeda.',
         'Extendé con movimientos ascendentes.',
         'Dejá absorber un minuto antes de vestirte.',
         'Usala a diario.'],
    ideal='hidratación diaria en clima cálido.',
    cat='corporal')

TIPOS['ACEITES CORPORALES'] = T(
    'aceite corporal', 'nutre, sella la hidratación y deja la piel con un acabado luminoso precioso',
    ['Nutrición intensa con un acabado satinado que se ve muy bien en la piel.',
     'Sella el agua de la ducha y evita que se evapore.',
     'Sirve también para masaje.',
     'Unas gotas cubren una pierna entera: rinde muchísimo.'],
    uso=['Aplicá sobre la piel húmeda, apenas salís de la ducha.',
         'Calentá unas gotas entre las manos.',
         'Masajeá con movimientos ascendentes hasta que absorba.',
         'Esperá un minuto antes de vestirte.'],
    ideal='piel seca, masaje y acabado luminoso para eventos.',
    tip='Sobre piel húmeda absorbe rápido y no queda grasoso. Sobre piel seca, sí.',
    cat='corporal')

TIPOS['GELES CORPORALES'] = T(
    'gel corporal', 'refresca e hidrata con una textura ligera que no deja sensación pegajosa',
    ['Sensación de frescura inmediata, muy agradable en verano.',
     'Absorbe en segundos.',
     'No mancha la ropa.',
     'Ideal para después del sol o del ejercicio.'],
    uso=['Aplicá sobre la piel limpia.',
         'Extendé con movimientos suaves.',
         'Dejá absorber unos segundos.',
         'Repetí las veces que necesites.'],
    ideal='clima cálido, piernas cansadas y después del sol.',
    tip='Guardalo en la heladera en verano: el efecto frío es otra cosa.',
    cat='corporal')

TIPOS['GELES/CREMAS REDUCTORAS'] = T(
    'gel reductor', 'acompaña las rutinas de firmeza corporal con activos y masaje',
    ['Textura pensada para el masaje prolongado.',
     'Efecto frío o calor según la fórmula, muy agradable de usar.',
     'Se integra bien a una rutina que incluya ejercicio y alimentación.',
     'Uso simple, se vuelve un hábito fácil de sostener.'],
    uso=['Aplicá sobre la piel limpia en la zona a trabajar.',
         'Masajeá con movimientos circulares ascendentes de 5 a 10 minutos.',
         'Usalo una o dos veces al día de forma constante.',
         'Acompañalo de hidratación, movimiento y buena alimentación.'],
    ideal='rutinas de cuidado corporal y masaje.',
    tip='Ningún producto cosmético reemplaza la actividad física; lo que hace es acompañarla.',
    cat='corporal')

TIPOS['TONICOS CORPORALES'] = T(
    'tónico corporal', 'refresca y tonifica la piel del cuerpo como paso previo a la hidratación',
    ['Sensación tonificante inmediata.',
     'Prepara la piel para que la crema penetre mejor.',
     'Textura ligera que no deja residuo.',
     'Agradable de usar a diario.'],
    uso=['Aplicá sobre la piel limpia y seca.',
         'Pulverizá o extendé con algodón.',
         'Dejá secar unos segundos.',
         'Seguí con tu crema o aceite corporal.'],
    ideal='rutina corporal completa.',
    cat='corporal')

TIPOS['EXFOLIANTES/MASCARILLAS CORPORALES'] = T(
    'exfoliante corporal', 'renueva la piel del cuerpo y la deja suave al tacto desde la primera vez',
    ['Elimina células muertas y deja la piel visiblemente más lisa.',
     'La hidratación posterior penetra muchísimo mejor.',
     'Ayuda a prevenir vellos encarnados si lo usás antes de depilarte.',
     'Momento de ducha que se disfruta.'],
    uso=['Usalo sobre la piel húmeda, dentro de la ducha.',
         'Masajeá en círculos ascendentes durante 2 o 3 minutos.',
         'Insistí en codos, rodillas y talones.',
         'Enjuagá e hidratá. Una o dos veces por semana.'],
    ideal='piel áspera, preparación para depilación o autobronceado.',
    tip='Exfoliar 24 horas antes de depilarte reduce muchísimo los vellos encarnados.',
    cat='corporal')

TIPOS['JABONES CORPORALES'] = T(
    'jabón corporal', 'limpia el cuerpo respetando la barrera natural de la piel',
    ['Limpieza efectiva sin dejar la piel tirante.',
     'Espuma agradable que rinde bastante.',
     'Formatos que duran mucho más que un gel de ducha.',
     'Fórmulas pensadas para el cuerpo, no jabón de manos.'],
    uso=['Mojá el cuerpo con agua tibia.',
         'Hacé espuma con las manos o con una esponja.',
         'Masajeá y enjuagá.',
         'Secá con toques e hidratá enseguida.'],
    ideal='higiene diaria.',
    cat='corporal')

TIPOS['JABONES/GELES INTIMOS'] = T(
    'jabón íntimo', 'higieniza la zona íntima con un pH adaptado, que es lo que un jabón común no respeta',
    ['pH específico para la zona íntima.',
     'Fórmula suave, sin perfumes agresivos.',
     'Uso diario sin alterar la flora natural.',
     'Formato práctico y discreto.'],
    uso=['Usalo solo en la zona externa.',
         'Aplicá con las manos limpias y una pequeña cantidad.',
         'Enjuagá bien con agua.',
         'Secá con toques suaves.'],
    ideal='higiene íntima diaria.',
    tip='Un jabón común altera el pH de la zona. Esa es toda la razón por la que existe este producto.',
    cat='corporal')

TIPOS['ANTITRANSPIRANTES'] = T(
    'antitranspirante', 'controla la transpiración y el olor durante toda la jornada',
    ['Control real de la transpiración, no solo perfume encima.',
     'Protección que aguanta el día completo.',
     'Secado rápido, sin manchar la ropa.',
     'Formato práctico para llevar al trabajo o al gimnasio.'],
    uso=['Aplicá sobre la piel limpia y completamente seca.',
         'La mejor aplicación es de noche, antes de dormir: el activo trabaja mientras la glándula está en reposo.',
         'Dejá secar antes de vestirte.',
         'No lo apliques sobre piel recién depilada o irritada.'],
    ideal='uso diario, deporte y jornadas largas.',
    tip='Aplicarlo de noche y no a la mañana es el cambio que más resultados da.',
    cat='corporal')

TIPOS['ACCESORIOS CORPORALES'] = T(
    'accesorio corporal', 'completa la rutina de cuidado del cuerpo con la herramienta adecuada',
    ['Hace más efectivo el paso al que acompaña.',
     'Material resistente al uso en húmedo.',
     'Fácil de higienizar y secar.',
     'Práctico para tener en la ducha.'],
    titulo_uso='Cómo usarlo',
    uso=['Usalo según la rutina que estés siguiendo.',
         'Enjuagá y dejá secar al aire después de cada uso.',
         'Reemplazalo cuando pierda firmeza.'],
    ideal='rutina corporal diaria.',
    cat='corporal')

TIPOS['ACCESORIOS PEZONES'] = T(
    'accesorio de pezones', 'resuelve con discreción una necesidad cotidiana',
    ['Discreto bajo cualquier prenda.',
     'Material suave y cómodo para llevar horas.',
     'Fácil de colocar y retirar.',
     'Práctico para el día a día y para ocasiones especiales.'],
    titulo_uso='Cómo usarlo',
    uso=['Colocá sobre la piel limpia y seca.',
         'Presioná suavemente para que adhiera.',
         'Retirá con cuidado al final del día.'],
    ideal='uso diario y prendas sin sostén.',
    cat='corporal')

TIPOS['MADEROTERAPIA'] = T(
    'herramienta de maderoterapia', 'permite hacer masaje corporal con la técnica que usan en cabina',
    ['Madera torneada que se adapta a cada zona del cuerpo.',
     'Permite trabajar con presión constante sin cansar las manos.',
     'Muy usada en rutinas de masaje reductor y drenaje.',
     'Duradera y fácil de mantener.'],
    titulo_uso='Cómo usarla',
    uso=['Aplicá antes un gel o aceite para que deslice.',
         'Trabajá siempre en dirección ascendente, hacia el corazón.',
         'Empezá con presión suave y aumentá de a poco.',
         'Limpiá la madera con un paño seco después de usarla, nunca la sumerjas en agua.'],
    det='Esta',
    ideal='masaje corporal en casa o en cabina.',
    cat='corporal')

TIPOS['CORPORAL'] = T(
    'producto corporal', 'suma cuidado a la piel del cuerpo, que suele quedar relegada frente al rostro',
    ['Pensado específicamente para la piel del cuerpo.',
     'Fácil de sumar a tu rutina de ducha.',
     'Textura pensada para cubrir superficies grandes.',
     'Resultado que se nota con el uso constante.'],
    uso=['Aplicá sobre la piel limpia.',
         'Seguí las indicaciones del envase.',
         'Usalo con regularidad.'],
    ideal='cuidado corporal diario.',
    cat='corporal')

TIPOS['CUIDADO CORPORAL'] = T(
    'producto de cuidado corporal', 'completa la rutina del cuerpo con un paso específico',
    ['Formulado para la piel del cuerpo.',
     'Se integra con el resto de tus productos.',
     'Práctico de usar a diario.',
     'Resultado acumulativo.'],
    uso=['Aplicá sobre la piel limpia y seguí las indicaciones del envase.'],
    ideal='rutina corporal.',
    cat='corporal')

TIPOS['KIT CORPORALES'] = T(
    'kit corporal', 'reúne una rutina completa de cuidado corporal en un solo combo',
    ['Productos coordinados entre sí.',
     'Mejor precio que comprarlos sueltos.',
     'Excelente opción de regalo.',
     'Rutina lista, sin tener que decidir nada.'],
    uso=['Seguí el orden del kit: limpieza, exfoliación e hidratación.',
         'Usalo con constancia durante algunas semanas.'],
    ideal='regalo y rutina corporal completa.',
    cat='corporal')

TIPOS['ACLARADORES BELLOS CORPORALES'] = T(
    'aclarador de vello corporal', 'aclara el vello para que se note menos, sin necesidad de depilarlo',
    ['Alternativa a la depilación en zonas donde no querés arrancar el vello.',
     'Resultado que dura hasta que el vello crece de nuevo.',
     'Aplicación rápida en casa.',
     'Sin tirones ni irritación por arrancado.'],
    uso=['Hacé una prueba en una zona pequeña 24 horas antes.',
         'Mezclá los componentes según el envase.',
         'Aplicá sobre la zona y respetá el tiempo exacto indicado.',
         'Enjuagá con agua abundante e hidratá.'],
    ideal='vello facial y corporal fino y visible.',
    cat='corporal')

TIPOS['DECOLORANTES CORPORALES'] = T(
    'decolorante corporal', 'aclara el vello del cuerpo para disimularlo sin arrancarlo',
    ['Resultado en pocos minutos.',
     'Sin tirones ni cera caliente.',
     'Buena opción para zonas amplias o sensibles.',
     'Aplicación simple en casa.'],
    uso=['Prueba de sensibilidad 24 horas antes, siempre.',
         'Mezclá los componentes según indica el envase.',
         'Aplicá, respetá el tiempo y no lo superes.',
         'Enjuagá muy bien e hidratá la zona.'],
    ideal='vello corporal visible en brazos y piernas.',
    cat='corporal')

# --- solar ---------------------------------------------------------------
TIPOS['BLOQUEADORES FACIALES'] = T(
    'protector solar facial', 'protege el rostro de la radiación UV, que es lo que más envejece la piel',
    ['El producto antiedad más eficaz que existe, y por bastante margen.',
     'Textura pensada para el rostro: no deja la cara grasosa ni pesada.',
     'Se puede usar bajo el maquillaje sin que haga bolitas.',
     'Protección diaria, también en días nublados y en interiores con ventanas.'],
    uso=['Aplicá como último paso de la rutina de la mañana, después de la hidratante.',
         'Usá cantidad suficiente: unos dos dedos de producto para rostro y cuello.',
         'Esperá 15 minutos antes de exponerte al sol.',
         'Reaplicá cada 2 horas si estás al aire libre.'],
    ideal='todos los días del año, en cualquier tipo de piel.',
    tip='Si solo vas a sumar un producto a tu rutina, que sea este. Ninguna crema compensa el daño solar.',
    cat='solar')

TIPOS['BLOQUEADORES CORPORALES'] = T(
    'protector solar corporal', 'protege la piel del cuerpo de las quemaduras y del daño acumulado del sol',
    ['Protección amplia frente a UVA y UVB.',
     'Textura que se reparte fácil en superficies grandes.',
     'Resistente al agua en muchas fórmulas: ideal para playa y piscina.',
     'Evita quemaduras, que son el daño que más se acumula.'],
    uso=['Aplicá 15 o 20 minutos antes de exponerte al sol.',
         'Usá cantidad generosa y cubrí todas las zonas expuestas, incluidas orejas y empeines.',
         'Reaplicá cada 2 horas y después de cada baño.',
         'Evitá el sol directo entre las 10 y las 16.'],
    ideal='playa, piscina, deporte al aire libre y cualquier día de sol.',
    tip='La mayoría de la gente usa la mitad de producto del necesario. Poné más de lo que creés.',
    cat='solar')

TIPOS['BRONCEADORES'] = T(
    'bronceador', 'acompaña el bronceado dejando la piel hidratada y con un acabado parejo',
    ['Bronceado más parejo y más duradero que al sol solo.',
     'Hidrata mientras estás expuesta, que es cuando la piel más lo necesita.',
     'Acabado luminoso sobre la piel.',
     'Aroma de verano que es parte del ritual.'],
    uso=['Exfoliá la piel el día anterior para un bronceado parejo.',
         'Aplicá de forma pareja sobre la piel limpia.',
         'Reaplicá cada 2 horas y después de nadar.',
         'Usá siempre protector solar: un bronceador no protege por sí solo salvo que indique SPF.'],
    ideal='playa, piscina y vacaciones.',
    tip='Bronceado sin protección no es bronceado, es daño. Combiná siempre con SPF.',
    cat='solar')

TIPOS['AUTOBRONCEADORES'] = T(
    'autobronceador', 'da color a la piel sin una sola hora de exposición al sol',
    ['Bronceado sin daño solar: la opción más sensata que existe.',
     'Color que se desarrolla en pocas horas y dura varios días.',
     'Se puede graduar la intensidad aplicando más o menos capas.',
     'Ideal para preparar la piel antes de un evento.'],
    uso=['Exfoliá y depilá 24 horas antes.',
         'Aplicá con guante aplicador, en movimientos circulares y parejos.',
         'Usá menos cantidad en rodillas, codos y tobillos, que absorben más.',
         'Lavá las manos enseguida y esperá entre 6 y 8 horas antes de ducharte.'],
    ideal='bronceado sin sol, eventos y piel muy clara.',
    tip='La exfoliación previa es lo que separa un bronceado parejo de uno con manchas.',
    cat='solar')

TIPOS['ACELERADORES'] = T(
    'acelerador de bronceado', 'ayuda a que el bronceado aparezca antes y se vea más parejo',
    ['El color aparece en menos sesiones de sol.',
     'Hidrata la piel mientras estás expuesta.',
     'Bronceado más uniforme.',
     'Aroma característico de producto de playa.'],
    uso=['Aplicá sobre la piel limpia antes de la exposición.',
         'Repartí de forma pareja en todo el cuerpo.',
         'Combiná siempre con protector solar.',
         'Reaplicá según indique el envase.'],
    ideal='playa y piscina.',
    cat='solar')

# --- depilacion ----------------------------------------------------------
TIPOS['CERAS CALIENTES'] = T(
    'cera depilatoria', 'arranca el vello desde la raíz y deja la piel lisa por semanas, no por días',
    ['Resultado que dura entre 3 y 4 semanas, muy por encima del afeitado.',
     'El vello vuelve a crecer más fino con el tiempo.',
     'Arranca también el vello corto, que otros métodos no toman.',
     'Rinde mucho: un envase cubre varias sesiones.'],
    uso=['Calentá la cera según indique el envase y probá la temperatura en el antebrazo antes.',
         'Aplicá sobre la piel limpia y seca, en el sentido del crecimiento del vello.',
         'Retirá de un tirón firme en sentido contrario al crecimiento, sujetando la piel.',
         'Retirá los restos con aceite e hidratá. No te expongas al sol las siguientes 24 horas.'],
    det='Esta',
    ideal='depilación de piernas, axilas, ingles y rostro.',
    tip='El vello tiene que medir al menos 5 mm para que la cera lo tome bien.',
    cat='depilacion')

TIPOS['BANDAS DEPILATORIAS'] = T(
    'banda depilatoria', 'depila en frío, sin calentar nada y sin ensuciar la casa',
    ['Sin calentar: se activan con el calor de las manos.',
     'Listas para usar, sin preparación ni utensilios.',
     'Prácticas para viajes y retoques.',
     'Resultado de varias semanas, igual que la cera caliente.'],
    det='Esta',
    uso=['Frotá la banda entre las manos unos segundos para activarla.',
         'Separá las dos mitades y aplicá sobre la piel limpia y seca, en el sentido del vello.',
         'Alisá con la mano y retirá de un tirón en sentido contrario.',
         'Retirá restos con la toallita incluida e hidratá.'],
    ideal='depilación en casa, viajes y retoques rápidos.',
    cat='depilacion')

TIPOS['CREMAS DEPILATORIAS'] = T(
    'crema depilatoria', 'disuelve el vello a ras de piel, sin tirones ni dolor',
    ['Sin dolor: es la principal razón para elegirla.',
     'Resultado más duradero que el afeitado.',
     'No deja la punta áspera que deja la máquina de afeitar.',
     'Rápida: entre 5 y 10 minutos y listo.'],
    det='Esta',
    uso=['Hacé una prueba en una zona pequeña 24 horas antes.',
         'Aplicá una capa gruesa y pareja sobre la piel seca, sin masajear.',
         'Respetá el tiempo exacto del envase. Nunca lo superes.',
         'Retirá con la espátula, enjuagá con agua abundante e hidratá.'],
    ideal='piernas, brazos y zonas amplias sin dolor.',
    tip='No la uses sobre piel irritada, con heridas o recién expuesta al sol.',
    cat='depilacion')

TIPOS['CALENTADORES CERA'] = T(
    'calentador de cera', 'derrite la cera a temperatura constante, que es lo que evita quemaduras',
    ['Temperatura controlada: ni fría e inservible ni demasiado caliente.',
     'Mantiene la cera lista durante toda la sesión.',
     'Capacidad pensada para trabajar varias zonas sin recargar.',
     'Imprescindible si depilás con cera seguido.'],
    titulo_uso='Cómo usarlo',
    uso=['Colocá la cera en el recipiente y encendé el equipo.',
         'Esperá el tiempo de calentado indicado.',
         'Probá siempre la temperatura en el antebrazo antes de aplicar.',
         'Limpiá el recipiente con la cera todavía tibia.'],
    ideal='depilación con cera en casa y en cabina.',
    cat='depilacion')

TIPOS['COMPLEMENTOS DEPILACION'] = T(
    'complemento de depilación', 'completa el kit de depilación con lo que hace el trabajo más prolijo',
    ['Hace la sesión más limpia y ordenada.',
     'Mejora el resultado final de la depilación.',
     'Práctico y económico.',
     'Imprescindible si depilás en casa con frecuencia.'],
    titulo_uso='Cómo usarlo',
    uso=['Prepará todo antes de calentar la cera.',
         'Usalo según la zona a depilar.',
         'Limpiá o descartá después de cada sesión.'],
    ideal='depilación con cera en casa o en cabina.',
    cat='depilacion')

# ==========================================================================
# BROCHAS Y ACCESORIOS DE MAQUILLAJE
# ==========================================================================
TIPOS['BROCHAS/PINCELES'] = T(
    'brocha de maquillaje', 'aplica y difumina el producto mucho mejor de lo que jamás lo harán los dedos',
    ['El acabado cambia por completo: la buena herramienta rinde más que el buen producto.',
     'Cerdas suaves que no rascan ni sueltan pelo.',
     'Densidad pensada para la función específica de cada brocha.',
     'Mango equilibrado que da control en los detalles.'],
    titulo_uso='Cómo usarla',
    uso=['Cargá poco producto y sacudí el exceso antes de llevar la brocha a la cara.',
         'Aplicá con toques o movimientos circulares según el acabado que busques.',
         'Difuminá siempre los bordes con una brocha limpia.',
         'Lavala con jabón neutro una vez por semana y dejala secar en horizontal.'],
    det='Esta',
    ideal='maquillaje diario y profesional.',
    tip='Secá las brochas con las cerdas hacia abajo o en horizontal: si el agua llega a la virola, se despegan.',
    cat='maquillaje')

TIPOS['BROCHAS'] = T(
    'brocha', 'reparte el producto de forma pareja y deja el acabado profesional que buscás',
    ['Cerdas suaves y densas que no dejan marcas.',
     'Recoge la cantidad justa de producto.',
     'Mango cómodo y bien equilibrado.',
     'Fácil de lavar y de secar.'],
    titulo_uso='Cómo usarla',
    uso=['Sacudí el exceso de producto antes de aplicar.',
         'Trabajá con movimientos suaves.',
         'Lavala semanalmente con jabón neutro.',
         'Secá en horizontal, nunca de pie con las cerdas hacia arriba.'],
    det='Esta',
    ideal='maquillaje de rostro.',
    cat='maquillaje')

TIPOS['POMOS/BORLAS/ESPONJAS'] = T(
    'esponja de maquillaje', 'difumina la base hasta fundirla con la piel, sin dejar un solo borde',
    ['Acabado natural: funde el producto en lugar de arrastrarlo.',
     'Humedecida da un efecto piel jugoso que una brocha no consigue.',
     'Forma pensada para llegar a lagrimal, aletas de nariz y contorno de labios.',
     'Rinde bien si la lavás con frecuencia.'],
    det='Esta',
    titulo_uso='Cómo usarla',
    uso=['Mojala con agua y escurrí bien hasta que esté húmeda, no empapada.',
         'Aplicá con toques suaves, nunca arrastrando.',
         'Usá la punta para las zonas pequeñas y la base redonda para las mejillas.',
         'Lavala después de cada uso y reemplazala cada 3 meses.'],
    ideal='aplicación de base, corrector y polvo suelto.',
    tip='Una esponja sucia reparte bacterias en la cara. Lavala después de cada uso, sin excepción.',
    cat='maquillaje')

TIPOS['LIMPIEZA BROCHAS/ESPONJAS'] = T(
    'limpiador de brochas', 'deja las brochas limpias de verdad, que es una cuestión de higiene además de resultado',
    ['Arrastra el producto acumulado y las bacterias.',
     'Las cerdas recuperan la suavidad original.',
     'El maquillaje se ve mejor con herramientas limpias, sin excepción.',
     'Fórmula que no reseca ni desarma el pegamento de la virola.'],
    uso=['Mojá las cerdas con agua tibia, sin mojar el mango.',
         'Aplicá el limpiador y masajeá en la palma o en una alfombrilla.',
         'Enjuagá hasta que el agua salga transparente.',
         'Escurrí, dale forma y secá en horizontal.'],
    ideal='mantenimiento semanal de brochas y esponjas.',
    cat='maquillaje')

TIPOS['LIMPIADORES CEPILLOS'] = T(
    'limpiador de cepillos', 'quita el residuo acumulado en cepillos y herramientas',
    ['Devuelve la higiene a las herramientas de uso diario.',
     'Arrastra grasa y restos de producto.',
     'Uso rápido y sencillo.',
     'Alarga la vida útil de tus herramientas.'],
    uso=['Retirá primero los pelos o residuos sólidos.',
         'Aplicá el limpiador y frotá según indique el envase.',
         'Enjuagá bien.',
         'Dejá secar completamente antes de volver a usar.'],
    ideal='mantenimiento de cepillos y herramientas.',
    cat='capilar')

TIPOS['COMPLEMENTOS MAQUILLAJE'] = T(
    'complemento de maquillaje', 'resuelve ese detalle que hace que el maquillaje quede realmente terminado',
    ['Pequeño pero se vuelve indispensable rápido.',
     'Mejora la precisión del paso al que acompaña.',
     'Práctico de guardar y de llevar.',
     'Fácil de higienizar.'],
    titulo_uso='Cómo usarlo',
    uso=['Usalo en el paso correspondiente del maquillaje.',
         'Limpialo con regularidad.',
         'Guardalo en el neceser para tenerlo siempre a mano.'],
    ideal='maquillaje diario y de evento.',
    cat='maquillaje')

TIPOS['ACCESORIOS MAQUILLAJE'] = T(
    'accesorio de maquillaje', 'facilita la aplicación y mejora el acabado final',
    ['Hace más simple un paso que sin él cuesta bastante.',
     'Material resistente al uso diario.',
     'Tamaño cómodo de manejar.',
     'Se higieniza sin problema.'],
    titulo_uso='Cómo usarlo',
    uso=['Usalo en el paso correspondiente del maquillaje.',
         'Higienizalo con regularidad.'],
    ideal='maquillaje en casa y profesional.',
    cat='maquillaje')

TIPOS['KIT MAQUILLAJE'] = T(
    'kit de maquillaje', 'reúne en un estuche los productos base para armar un look completo',
    ['Todo coordinado: los tonos combinan entre sí.',
     'Mejor precio que comprando cada producto suelto.',
     'Excelente para regalar o para arrancar en el maquillaje.',
     'Estuche que mantiene todo ordenado.'],
    uso=['Seguí el orden habitual: base, corrector, polvo, rubor, ojos y labios.',
         'Difuminá bien entre paso y paso.',
         'Sellá con fijador si querés que dure más.'],
    ideal='regalo y neceser de iniciación.',
    cat='maquillaje')

TIPOS['COSMETIQUERAS/NECESER'] = T(
    'cosmetiquera', 'mantiene todo el maquillaje ordenado y protegido, en casa y de viaje',
    ['Todo en un solo lugar: se acabó buscar el corrector en el fondo del bolso.',
     'Protege los productos de golpes y derrames.',
     'Interior fácil de limpiar si algo se abre.',
     'Tamaño pensado para llevar en cartera o valija.'],
    det='Esta',
    titulo_uso='Cómo usarla',
    uso=['Guardá los líquidos en posición vertical.',
         'Separá brochas de productos para que no se ensucien.',
         'Limpiá el interior cada tanto.'],
    ideal='viajes, gimnasio y organización diaria.',
    cat='maquillaje')

TIPOS['ESPEJOS'] = T(
    'espejo', 'te deja ver lo que estás haciendo, que en maquillaje es más de la mitad del trabajo',
    ['Reflejo nítido y sin distorsión.',
     'Tamaño pensado para maquillarse con comodidad.',
     'Muchos modelos incluyen aumento para cejas y delineado.',
     'Resistente y fácil de limpiar.'],
    titulo_uso='Cómo usarlo',
    uso=['Ubicalo donde tengas la mejor luz posible, idealmente natural.',
         'Usá la cara con aumento para cejas, delineado y pestañas.',
         'Limpiá la superficie con un paño suave.'],
    ideal='maquillaje en casa y de viaje.',
    tip='La luz importa más que el espejo: maquillate siempre de frente a una ventana si podés.',
    cat='maquillaje')

# ==========================================================================
# ELECTRICOS
# ==========================================================================
TIPOS['PLANCHAS'] = T(
    'plancha de cabello', 'alisa, define y da forma al cabello con control de temperatura',
    ['Alisa en pocas pasadas: menos calor acumulado, menos daño.',
     'Placas que deslizan sin tironear ni enganchar el pelo.',
     'Temperatura regulable para adaptarse a cada tipo de cabello.',
     'También sirve para hacer ondas y puntas hacia adentro.'],
    titulo_uso='Cómo usarla',
    uso=['Usá siempre termoprotector. No es opcional si planchás seguido.',
         'El cabello tiene que estar 100 % seco antes de empezar.',
         'Trabajá por mechones finos, con una sola pasada firme y continua.',
         'Regulá la temperatura: 160-180 °C para cabello fino, hasta 200 °C para cabello grueso.'],
    det='Esta',
    ideal='alisado en casa y peinados con plancha.',
    tip='Dos pasadas a temperatura baja dañan menos que una a máxima potencia.',
    cat='electricos')

TIPOS['SECADORES/DIFUSORES'] = T(
    'secador de cabello', 'seca rápido y da forma al peinado con el control que el aire libre no ofrece',
    ['Secado rápido, que significa menos tiempo de calor sobre la fibra.',
     'Varias velocidades y temperaturas para adaptarse al tipo de cabello.',
     'El golpe de aire frío fija el peinado y sella la cutícula.',
     'Con difusor, define rizos sin generar frizz.'],
    titulo_uso='Cómo usarlo',
    uso=['Retirá el exceso de agua con la toalla y aplicá termoprotector.',
         'Secá al 80 % con aire medio antes de empezar a dar forma.',
         'Mantené el secador a unos 15 cm y dirigí el aire de raíz a puntas.',
         'Terminá con aire frío para fijar y dar brillo.'],
    ideal='secado y brushing en casa.',
    tip='Dirigir el aire de la raíz hacia las puntas cierra la cutícula. Al revés, la abre y genera frizz.',
    cat='electricos')

TIPOS['RIZADORAS'] = T(
    'rizadora', 'crea rizos y ondas definidas que duran todo el día',
    ['Rizos que aguantan, no que se caen a la media hora.',
     'Temperatura regulable según el tipo de cabello.',
     'Distintos diámetros dan desde ondas suaves hasta rizos marcados.',
     'Calentado rápido: no hay que esperar.'],
    det='Esta',
    titulo_uso='Cómo usarla',
    uso=['Aplicá termoprotector sobre el cabello seco.',
         'Tomá mechones finos y enrollá desde la mitad hacia la punta.',
         'Mantené entre 8 y 12 segundos y soltá con cuidado.',
         'Dejá enfriar el rizo antes de tocarlo y fijá con laca.'],
    ideal='peinados con ondas y rizos definidos.',
    tip='Dejar enfriar el rizo en la mano antes de soltarlo es lo que hace que dure todo el día.',
    cat='electricos')

TIPOS['PINZAS ELECTRICAS'] = T(
    'pinza eléctrica', 'da forma al cabello combinando calor y presión con mucho control',
    ['Resultado profesional con una sola herramienta.',
     'Temperatura regulable.',
     'Placas o superficie que no tironean el cabello.',
     'Calentado rápido y apagado automático en muchos modelos.'],
    det='Esta',
    titulo_uso='Cómo usarla',
    uso=['Trabajá sobre cabello seco y con termoprotector.',
         'Dividí en mechones finos.',
         'Aplicá el calor el tiempo justo, sin insistir.',
         'Dejá enfriar antes de peinar.'],
    ideal='peinados con calor en casa.',
    cat='electricos')

TIPOS['MAQUINAS/AFEITADORAS'] = T(
    'máquina de corte', 'corta y perfila el cabello y la barba con precisión de barbería',
    ['Motor que corta parejo incluso en cabello grueso.',
     'Peines guía para trabajar distintos largos sin adivinar.',
     'Cuchilla que se puede ajustar y reemplazar.',
     'Con cable o batería según el modelo: se adapta a cómo trabajés.'],
    det='Esta',
    titulo_uso='Cómo usarla',
    uso=['Trabajá sobre cabello seco y desenredado.',
         'Empezá con el peine guía más largo y bajá de a poco: no hay vuelta atrás.',
         'Movés la máquina contra la dirección del crecimiento.',
         'Limpiá y lubricá la cuchilla después de cada uso.'],
    ideal='barberías, peluquerías y corte en casa.',
    tip='Lubricar la cuchilla después de cada corte es lo que hace que la máquina dure años.',
    cat='electricos')

TIPOS['TRIMMER/DEPILADORAS'] = T(
    'trimmer', 'perfila los detalles donde la máquina grande no llega',
    ['Precisión en patillas, contorno de barba, nuca y cejas.',
     'Cabezal fino que permite ver lo que estás haciendo.',
     'Liviano y cómodo de manejar.',
     'Complemento perfecto de la máquina de corte.'],
    titulo_uso='Cómo usarlo',
    uso=['Trabajá sobre piel seca y limpia.',
         'Definí primero la línea de contorno y después rellená.',
         'Usá movimientos cortos y controlados.',
         'Limpiá y lubricá el cabezal después de cada uso.'],
    ideal='perfilado de barba, patillas y nuca.',
    cat='electricos')

TIPOS['CEPILLOS ELECTRICOS'] = T(
    'cepillo eléctrico', 'combina cepillado y calor para dar forma al cabello en un solo paso',
    ['Hace brushing y alisado sin necesidad de dos manos expertas.',
     'Mucho más fácil de manejar que secador y cepillo por separado.',
     'Temperatura regulable.',
     'Resultado con volumen y movimiento, no plano como el de la plancha.'],
    titulo_uso='Cómo usarlo',
    uso=['Usalo sobre cabello seco o apenas húmedo, según el modelo.',
         'Aplicá termoprotector siempre.',
         'Trabajá por secciones, deslizando de raíz a puntas.',
         'Terminá con aire frío o dejá enfriar antes de peinar.'],
    ideal='brushing en casa sin práctica previa.',
    cat='electricos')

TIPOS['ELECTROMENORES'] = T(
    'electrodoméstico de belleza', 'suma tecnología a tu rutina para conseguir en casa lo que antes era solo de salón',
    ['Resultados de salón sin salir de casa.',
     'Fácil de usar, con controles simples.',
     'Tamaño pensado para guardar sin ocupar medio baño.',
     'Se amortiza rápido frente al costo de los servicios.'],
    titulo_uso='Cómo usarlo',
    uso=['Leé el manual antes del primer uso.',
         'Empezá siempre por la intensidad más baja.',
         'Limpiá el equipo después de cada uso.',
         'Guardalo seco y desenchufado.'],
    ideal='rutinas de belleza en casa.',
    cat='electricos')

TIPOS['ACCESORIOS/REPUESTOS/LUBRICANTES ELECTRI'] = T(
    'repuesto para equipos eléctricos', 'mantiene la herramienta funcionando como el primer día',
    ['Alarga muchísimo la vida útil del equipo.',
     'Mantiene el rendimiento del corte o del calor.',
     'Cambio o aplicación sencilla.',
     'Mucho más barato que reemplazar la máquina.'],
    titulo_uso='Cómo usarlo',
    uso=['Desenchufá el equipo antes de cualquier mantenimiento.',
         'Reemplazá o aplicá según indique el manual.',
         'Lubricá las cuchillas después de cada uso.',
         'Guardá el equipo limpio y seco.'],
    ideal='mantenimiento de máquinas y planchas.',
    cat='electricos')

# ==========================================================================
# FRAGANCIAS
# ==========================================================================
TIPOS['SPLASH'] = T(
    'splash corporal', 'perfuma el cuerpo con una estela fresca y ligera, ideal para el día',
    ['Fragancia fresca que no satura ni marea.',
     'Se puede reaplicar durante el día sin que resulte excesivo.',
     'Sensación refrescante al aplicar.',
     'Formato que rinde y se puede llevar en la cartera.'],
    uso=['Aplicá sobre la piel limpia y seca, después de la ducha.',
         'Pulverizá a unos 20 cm sobre cuello, escote, muñecas y detrás de las rodillas.',
         'No frotes las muñecas entre sí: rompe las notas de la fragancia.',
         'Reaplicá durante el día cuando quieras.'],
    ideal='uso diario, clima cálido y público joven.',
    tip='Sobre la piel hidratada la fragancia dura bastante más. Aplicá crema antes.',
    cat='fragancia')

TIPOS['COLONIAS'] = T(
    'colonia', 'deja una estela suave y agradable, perfecta para el día a día',
    ['Concentración ligera: perfuma sin abrumar.',
     'Apta para usar en oficina o espacios cerrados.',
     'Fresca y fácil de llevar.',
     'Muchas son aptas para toda la familia.'],
    det='Esta',
    uso=['Aplicá sobre la piel limpia y seca.',
         'Pulverizá en cuello, muñecas y detrás de las orejas.',
         'Reaplicá durante el día si querés mantener la estela.'],
    ideal='uso diario y ambientes de trabajo.',
    cat='fragancia')

TIPOS['AGUAS PERFUMES'] = T(
    'perfume', 'define tu presencia con una fragancia que se recuerda',
    ['Concentración que da horas de duración real.',
     'Evolución de notas: no huele igual al aplicarla que cuatro horas después.',
     'Estela que deja huella sin resultar invasiva.',
     'Frasco que luce en el tocador.'],
    uso=['Aplicá sobre la piel limpia e hidratada.',
         'Pulverizá a 15 o 20 cm en los puntos de pulso: cuello, muñecas, detrás de las orejas.',
         'No frotes: aplastás las notas de salida.',
         'Para más duración, pulverizá también sobre el cabello o la ropa.'],
    ideal='uso diario, eventos y como regalo.',
    tip='Guardá el frasco lejos de la luz y del calor del baño: el perfume se oxida más rápido de lo que creés.',
    cat='fragancia')

TIPOS['KITS DE PERFUMERIA'] = T(
    'kit de perfumería', 'reúne fragancia y productos complementarios en un estuche listo para regalar',
    ['Presentación pensada para regalo, no hay que envolver nada.',
     'Los productos comparten la misma fragancia y la potencian entre sí.',
     'Mejor precio que comprando cada pieza suelta.',
     'Permite llevar la fragancia en varios formatos.'],
    uso=['Usá primero el gel o la crema de la línea en la ducha.',
         'Aplicá la fragancia sobre la piel hidratada.',
         'El efecto capa hace que la estela dure bastante más.'],
    ideal='regalos y quien quiere estirar la duración de su perfume.',
    cat='fragancia')

TIPOS['FRAGANCIAS CAPILARES'] = T(
    'perfume capilar', 'perfuma el cabello sin el alcohol que resecaría la fibra',
    ['Formulado para el cabello: no reseca como un perfume común.',
     'El cabello retiene la fragancia durante horas.',
     'Muchas fórmulas suman brillo y control de frizz.',
     'Perfecto para refrescar el pelo entre lavados.'],
    uso=['Pulverizá a unos 20 o 30 cm del cabello seco.',
         'Repartí sobre el largo, evitando la raíz.',
         'Peiná para distribuir.',
         'Reaplicá durante el día cuando quieras.'],
    ideal='refrescar el cabello entre lavados y sumar brillo.',
    tip='Nunca uses perfume común en el pelo: el alcohol lo reseca y lo apaga.',
    cat='fragancia')

TIPOS['AROMATERAPIA'] = T(
    'producto de aromaterapia', 'transforma el ambiente y acompaña momentos de relajación',
    ['Cambia por completo la sensación de un espacio.',
     'Acompaña rituales de descanso, meditación o lectura.',
     'Aroma que se percibe sin resultar invasivo.',
     'También funciona muy bien como regalo.'],
    uso=['Usalo en un espacio ventilado.',
         'Seguí las indicaciones de dosificación del envase.',
         'Mantené fuera del alcance de niños y mascotas.',
         'No lo apliques directamente sobre la piel salvo que el envase lo indique.'],
    ideal='relajación, descanso y ambientar espacios.',
    cat='fragancia')

TIPOS['KITS AROMATERAPIA'] = T(
    'kit de aromaterapia', 'reúne todo lo necesario para armar un ritual de relajación completo',
    ['Set completo: no falta nada para empezar.',
     'Aromas seleccionados que combinan entre sí.',
     'Presentación de regalo.',
     'Buena puerta de entrada si nunca probaste aromaterapia.'],
    uso=['Leé las indicaciones de cada componente del kit.',
         'Usalo en un espacio ventilado.',
         'Empezá con dosis bajas hasta encontrar tu punto.'],
    ideal='regalo y rituales de descanso.',
    cat='fragancia')

# ==========================================================================
# BARBERIA
# ==========================================================================
TIPOS['AFEITADO'] = T(
    'producto de afeitado', 'prepara la piel y la cuchilla para un afeitado al ras y sin irritación',
    ['Menos irritación y menos cortes: la cuchilla desliza en lugar de arrastrar.',
     'Levanta el vello y ablanda la barba antes del paso de la hoja.',
     'Deja la piel cómoda después del afeitado.',
     'Rinde bastante: se usa poca cantidad por afeitada.'],
    uso=['Lavá el rostro con agua tibia para abrir el poro y ablandar la barba.',
         'Aplicá el producto y dejá actuar un minuto.',
         'Afeitá en el sentido del crecimiento del vello, con la hoja limpia.',
         'Enjuagá con agua fría y aplicá after shave o bálsamo hidratante.'],
    ideal='afeitado diario y cuidado de la barba.',
    tip='Afeitar a contrapelo apura el resultado pero es la principal causa de los vellos encarnados.',
    cat='barberia')

TIPOS['COMPLEMENTOS/ACCESORIOS BARBERIA'] = T(
    'accesorio de barbería', 'es de esas cosas que en la barbería se usan todo el día y nadie ve',
    ['Pensado para uso profesional intensivo.',
     'Materiales que aguantan la jornada completa.',
     'Agiliza el servicio y mejora el acabado.',
     'Fácil de higienizar entre cliente y cliente.'],
    titulo_uso='Cómo usarlo',
    uso=['Usalo en el paso del servicio que corresponda.',
         'Desinfectá entre un cliente y otro.',
         'Guardalo limpio y seco.'],
    ideal='barberías y cuidado masculino en casa.',
    cat='barberia')

# ==========================================================================
# ASEO PERSONAL Y BOTIQUIN
# ==========================================================================
TIPOS['ALGODÓN'] = T(
    'algodón', 'es ese básico que no se nota hasta que se te termina',
    ['Suave y absorbente, no deja pelusa en la cara.',
     'Sirve para desmaquillar, aplicar tónico y retirar esmalte.',
     'Rinde muchísimo por el precio.',
     'Formato práctico de guardar.'],
    titulo_uso='Cómo usarlo',
    uso=['Empapá con el producto que vayas a usar.',
         'Para desmaquillar, apoyá unos segundos antes de arrastrar.',
         'Usá un algodón limpio por cada zona.'],
    ideal='desmaquillado, tónico y manicura.',
    cat='aseo')

TIPOS['COPITOS'] = T(
    'hisopo', 'corrige los detalles con una precisión que ninguna otra cosa da',
    ['Precisión milimétrica para corregir delineados y labiales.',
     'Punta suave, apta para zonas delicadas.',
     'Rinde muchísimo y ocupa casi nada.',
     'Indispensable en cualquier neceser.'],
    titulo_uso='Cómo usarlo',
    uso=['Humedecé la punta con desmaquillante para corregir bordes de maquillaje.',
         'Usá la punta seca para difuminar sombras y delineadores.',
         'Descartá después de cada uso.'],
    ideal='correcciones de maquillaje y detalles de manicura.',
    tip='Un hisopo con desmaquillante deja el borde del delineado perfecto en dos segundos.',
    cat='aseo')

TIPOS['PANITOS HUMEDOS'] = T(
    'paño húmedo', 'limpia en cualquier lugar, sin agua ni toalla de por medio',
    ['Listo para usar, en cualquier momento y lugar.',
     'Suave con la piel.',
     'Envase que cierra y conserva la humedad.',
     'Práctico para el bolso, el auto y el trabajo.'],
    titulo_uso='Cómo usarlo',
    uso=['Abrí el envase y retirá un paño.',
         'Limpiá la zona con movimientos suaves.',
         'Cerrá el envase para que no se sequen los demás.',
         'Descartá el paño usado en la basura, nunca en el inodoro.'],
    ideal='viajes, trabajo y salidas.',
    cat='aseo')

TIPOS['PANITOS INTIMOS'] = T(
    'paño íntimo', 'resuelve la higiene íntima fuera de casa con un pH adecuado',
    ['pH pensado para la zona íntima.',
     'Formato individual y discreto.',
     'Sin perfumes agresivos.',
     'Práctico para viajes, trabajo y deporte.'],
    titulo_uso='Cómo usarlo',
    uso=['Usalo solo en la zona externa.',
         'Limpiá de adelante hacia atrás.',
         'Descartá en la basura, nunca en el inodoro.'],
    ideal='higiene íntima fuera de casa.',
    cat='aseo')

TIPOS['ALCOHOL'] = T(
    'alcohol', 'desinfecta superficies y herramientas, que en belleza es una necesidad diaria',
    ['Desinfección rápida y efectiva de herramientas.',
     'Imprescindible para higienizar entre cliente y cliente.',
     'También sirve para limpiar brochas y pinzas.',
     'Rinde muchísimo.'],
    titulo_uso='Cómo usarlo',
    uso=['Aplicá sobre la herramienta limpia y seca.',
         'Dejá actuar unos segundos y dejá secar al aire.',
         'Mantené el envase cerrado y lejos del calor.',
         'No lo uses sobre heridas abiertas ni mucosas.'],
    ideal='desinfección de herramientas de manicura, maquillaje y barbería.',
    cat='aseo')

TIPOS['ANTIBACTERIALES/DESINFECTANTES'] = T(
    'antibacterial', 'higieniza las manos en cualquier lugar, sin agua ni jabón',
    ['Higiene rápida donde no hay lavabo.',
     'Secado rápido, sin dejar residuo pegajoso.',
     'Formato de bolsillo.',
     'Muchas fórmulas incluyen humectantes para no resecar.'],
    titulo_uso='Cómo usarlo',
    uso=['Aplicá una cantidad suficiente en la palma.',
         'Frotá cubriendo dorso, entre los dedos y las uñas.',
         'Seguí frotando hasta que seque, sin enjuagar.',
         'Si las manos están visiblemente sucias, lavalas con agua y jabón.'],
    ideal='uso diario fuera de casa.',
    cat='aseo')

TIPOS['CAPSULAS DURAS'] = T(
    'suplemento en cápsulas', 'acompaña desde adentro las rutinas de cuidado de piel, cabello y uñas',
    ['Formato de cápsula, fácil de sostener como hábito diario.',
     'Complementa lo que hacés por fuera con productos tópicos.',
     'Presentación que rinde varias semanas.',
     'Cómodo de llevar y de tomar.'],
    uso=['Seguí la dosis indicada en el envase.',
         'Tomá con un vaso de agua, preferentemente a la misma hora todos los días.',
         'Sostené el tratamiento el tiempo indicado para poder evaluar resultados.',
         'Consultá con un profesional de la salud antes de empezar, sobre todo si tomás medicación o estás embarazada.'],
    ideal='acompañar rutinas de belleza desde adentro.',
    tip='Un suplemento no reemplaza una alimentación equilibrada ni un tratamiento médico.',
    cat='aseo')

TIPOS['REPELENTES'] = T(
    'repelente', 'mantiene los insectos a distancia durante horas',
    ['Protección que dura varias horas por aplicación.',
     'Apto para usar sobre la piel expuesta.',
     'Formato práctico para llevar de viaje.',
     'Imprescindible en zonas tropicales.'],
    uso=['Aplicá sobre la piel expuesta, evitando ojos y boca.',
         'Si usás protector solar, ponelo primero y el repelente después.',
         'Reaplicá según indique el envase.',
         'Lavá la piel al volver a casa.'],
    ideal='viajes, actividades al aire libre y zonas cálidas.',
    cat='aseo')

TIPOS['BIENESTAR TERAPEUTICO'] = T(
    'producto de bienestar', 'acompaña momentos de descanso y recuperación',
    ['Pensado para rutinas de relajación y bienestar.',
     'Fácil de incorporar al día a día.',
     'Formato práctico.',
     'También funciona como regalo.'],
    uso=['Seguí las indicaciones del envase.',
         'Usalo en un momento tranquilo del día.',
         'Ante cualquier condición de salud, consultá con un profesional antes de usarlo.'],
    ideal='rutinas de descanso y bienestar.',
    cat='aseo')

TIPOS['BOLSAS DE PAPEL/CAJAS'] = T(
    'empaque de regalo', 'convierte cualquier producto en un regalo presentable en dos minutos',
    ['Presentación cuidada sin tener que envolver nada.',
     'Material resistente que aguanta el peso de varios productos.',
     'Reutilizable.',
     'Cierra bien la experiencia de regalar.'],
    titulo_uso='Cómo usarlo',
    uso=['Colocá el producto con papel de seda para proteger.',
         'Cerrá con cinta o etiqueta.',
         'Guardá la bolsa para volver a usarla.'],
    ideal='regalos y ventas.',
    cat='aseo')

TIPOS['BOLSAS DE TELA'] = T(
    'bolsa de tela', 'reemplaza la bolsa descartable y además luce bastante mejor',
    ['Reutilizable: se amortiza en pocos usos.',
     'Resistente, aguanta bastante peso.',
     'Lavable.',
     'Opción más amable con el ambiente.'],
    det='Esta',
    titulo_uso='Cómo usarla',
    uso=['Usala para llevar tus compras o como neceser grande.',
         'Lavala a mano o en máquina con agua fría.',
         'Dejá secar al aire.'],
    ideal='compras y uso diario.',
    cat='aseo')

TIPOS['CAPILAR'] = T(
    'producto capilar', 'suma un paso más al cuidado del cabello',
    ['Pensado específicamente para el cabello.',
     'Se integra con el resto de tu rutina.',
     'Fácil de usar a diario.',
     'Resultado que mejora con la constancia.'],
    uso=['Aplicá según las indicaciones del envase.',
         'Usalo de forma regular.'],
    ideal='rutina capilar.',
    cat='capilar')
