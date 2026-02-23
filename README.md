## Manual rapido: como jugar (Modo `Jugar`)

El modo `Jugar` te muestra una palabra en ingles y una oracion de ejemplo. Tu objetivo es adivinar:

1. La traduccion al espanol de la palabra.
2. Si la oracion esta en `presente`, `pasado` o `futuro`.

### Como iniciar

1. Abre la aplicacion.
2. En el menu izquierdo, pulsa `Jugar`.

### Que veras

- `Palabra en ingles` (la palabra a estudiar)
- `Ejemplo en ingles` (una oracion guardada con esa palabra)
- Un campo para escribir la `traduccion`
- Un campo para escribir el `tiempo` (`presente`, `pasado` o `futuro`)

### Como responder

- En `Traduccion`, escribe la traduccion esperada en espanol.
- En `Tiempo`, escribe solo una de estas opciones:
  - `presente`
  - `pasado`
  - `futuro`

### Botones del juego

- `Comprobar`: valida tu respuesta (traduccion + tiempo).
- `Siguiente`: carga otra palabra aleatoria.
- `Salir juego`: vuelve a la vista principal.

### Requisitos para que funcione bien

- Debes tener palabras guardadas en el vocabulario.
- Es recomendable que cada palabra tenga una oracion de ejemplo en ingles.
- El tiempo se detecta desde la oracion de ejemplo (motor gramatical).

### Nota

Si hay pocas palabras o faltan ejemplos, el juego puede no tener suficientes rondas utiles.

## Que nivel de ingles puedes practicar con este software

Este software esta pensado como una herramienta de practica y correccion gramatical con enfoque pedagogico.

### Cobertura aproximada por nivel

- `A1-A2` (fuerte): estructura basica, sujeto/verbo, preguntas con auxiliar, `to be`, presente simple/continuo, pasado simple, futuro basico, articulos y orden de palabras.
- `B1` (buena): condicionales basicos, pasiva basica, reported speech basico, gerund/infinitive frecuentes, cuantificadores.
- `B2` (parcial pero util): perfect tenses, modales avanzados, condicionales avanzados, linking devices, inversion, cleft sentences, relative clauses mas complejas.

### Que significa "parcial" en B2

- El sistema reconoce muchos patrones reales y errores frecuentes.
- Algunas reglas avanzadas son heuristicas (por forma), asi que en oraciones muy complejas puede haber falsos positivos o falsos negativos.

## Como funciona el software (explicado para usuarios)

Cuando escribes una oracion o guardas una palabra con ejemplo, el programa hace varias cosas:

1. **Analiza la oracion**
- Separa palabras (tokens).
- Intenta reconocer su tipo (verbo, sustantivo, adjetivo, etc.).
- Detecta formas verbales (`work`, `works`, `worked`, `working`) y tiempos (`present`, `past`, `future`, perfect, continuous, etc.).

2. **Aplica reglas gramaticales**
- Revisa estructura, tiempos, auxiliares, modales, articulos, cuantificadores, collocations y otras reglas.
- Genera avisos cuando detecta un patron probablemente incorrecto.

3. **Muestra feedback pedagogico**
- `Warnings`: errores gramaticales detectados por reglas.
- `Pattern warnings / hints`: avisos por patrones de uso comunes.
- `Lexical hints`: pistas de vocabulario/collocations (si hay datos disponibles).

4. **Usa tu vocabulario guardado para practicar**
- La tabla central guarda palabras y ejemplos.
- Al seleccionar una palabra puedes editarla.
- El modo `Jugar` reutiliza esas palabras para entrenar traduccion + tiempo verbal.

### Importante (como interpretar los resultados)

- El software **no es un parser sintactico completo** ni reemplaza a un profesor.
- Es una herramienta de entrenamiento y apoyo: muy buena para errores frecuentes y practica guiada.
- Si una oracion es muy larga o avanzada, revisa el feedback como ayuda, no como verdad absoluta.

# TerminalLearnEnglish - Rule Engine (English)

## Estado actual del motor

El motor de reglas de ingles valida estructuras gramaticales de forma heuristica (no usa un parser sintactico completo).

## Normalizacion de texto (evita falsos positivos)

- El analizador tokeniza y convierte el texto a minusculas.
- Esto significa que `i` y `I` se analizan igual para gramatica.
- Ejemplo: `i am happy` y `I am happy` producen los mismos tokens para validacion.
- Actualmente esto evita falsos positivos de gramatica por mayusculas, pero no corrige estilo/capitalizacion (por ejemplo, no marca que `I` deberia ir en mayuscula).

## Reglas implementadas actualmente (rule_id)

### Base / estructura general

- `en.required_verb` - Oraciones completas requieren verbo.
- `en.explicit_subject` - Oraciones completas suelen requerir sujeto explicito.
- `en.imperative_subject_optional` - Imperativos suelen omitir sujeto.
- `en.basic_svo_order` - Orden basico Sujeto + Verbo + Complemento.
- `en.adjective_noun_order` - Adjetivo antes del sustantivo.
- `en.article_a_an_sound` - Uso de `a/an` por sonido inicial.

### Preguntas y auxiliares

- `en.question_auxiliary` - Preguntas con auxiliar (incluye soporte para `wh-questions`).
- `en.present_simple_structure` - Estructura basica de present simple (afirmativa/negativa/interrogativa).
- `en.to_be_no_do` - No usar `do/does/did` con usos basicos de `to be`.
- `en.indirect_questions` - Preguntas indirectas usan orden de enunciado.

### Concordancia y presente simple

- `en.present_simple_do_negation` - Negacion en present simple con `do/does + not + verbo base`.
- `en.third_person_s` - `he/she/it + verbo + s` (casos comunes).
- `en.subject_be_agreement` - Concordancia basica sujeto + `to be`.

### Tiempos verbales (B1 / B2)

- `en.present_continuous` - `am/is/are + verbo-ing`
- `en.past_simple` - Pasado simple y `did + verbo base`
- `en.past_continuous` - `was/were + verbo-ing`
- `en.past_continuous_interruption` - Patron `past continuous + when + past simple`
- `en.future_will` - `will + verbo base`
- `en.future_plan_present_continuous` - Present continuous para planes futuros
- `en.future_schedule_present_simple` - Present simple para horarios/programaciones (heuristico)
- `en.future_going_to` - `am/is/are + going to + verbo base`
- `en.present_perfect` - `have/has + participio`
- `en.present_perfect_vs_past_simple_usage` - Contraste basico con marcadores de tiempo terminados (`yesterday`, `last`, `ago`)
- `en.present_perfect_continuous` - `have/has been + verbo-ing`
- `en.past_perfect` - `had + participio`
- `en.past_perfect_continuous` - `had been + verbo-ing`
- `en.future_continuous` - `will be + verbo-ing`
- `en.future_perfect` - `will have + participio`
- `en.future_perfect_continuous` - `will have been + verbo-ing`

### Modales y semi-modales

- `en.modal_base_verb` - Base verbal despues de modales (`can/should/must/...`)
- `en.modal_combination` - Evita combinaciones directas de modales (`can should`)
- `en.semi_modal_have_to` - Estructura de `have to / has to`
- `en.modal_advanced_perfect` - Modales avanzados con `have + participio` (`should have gone`, etc.)

### Comparacion y condicionales

- `en.comparatives_superlatives` - Comparativos/superlativos y `as...as`
- `en.conditionals_b1` - First y second conditional (heuristico)
- `en.conditionals_b2` - Third/mixed conditionals y alternativas a `if` (`unless`, `provided that`, `as long as`)

### Pasiva (B1 / B2)

- `en.passive_basic` - Pasiva basica `be + participio`
- `en.passive_advanced` - Pasiva avanzada (`has been done`, `will be done`, `must be done`, `It is said that...`)

### Reported speech y subordinacion

- `en.reported_speech_basic` - Reported speech basico y preguntas reportadas simples
- `en.reported_speech_advanced` - Patrones con reporting verbs (ej. `suggest`)
- `en.noun_clauses_complex` - Noun clauses / subordinacion (`the fact that`, `whether/if` sin inversion)

### Relative clauses

- `en.relative_clauses_basic` - Relativas basicas (incluye error comun de repetir pronombre)
- `en.relative_clauses_advanced` - Relativas avanzadas (heuristicas)

### Gerund / infinitive

- `en.gerund_infinitive_common` - Patrones comunes (`enjoy doing`, `want to do`)
- `en.gerund_infinitive_meaning_pairs` - Pares de alto valor (`stop/remember`)

### Determiners, quantifiers y articulos

- `en.determiners_quantifiers_basic` - `much/many`, `few/little`, `a lot of`
- `en.some_any` - Uso heuristico de `some/any`
- `en.quantifiers_determiners_advanced` - `each/every`, `both`, `so/such`, `enough`

### Prepositions, collocations y phrasal verbs

- `en.preposition_collocation` - Collocations frecuentes (`interested in`, `good at`, `depend on`)
- `en.phrasal_basic` - Phrasal verbs frecuentes (`get up`, `turn on`, `find out`)
- `en.phrasal_advanced` - Phrasal verbs intermedio-alto (`carry out`, `come up with`, `put up with`)

### B2: cohesion, enfasis y estilo estructural

- `en.linking_devices` - Conectores (`despite`, `although`, etc.) con validaciones de patron
- `en.inversion_emphasis` - Inversion por enfasis (`Never have I...`, `Not only...`)
- `en.cleft_sentences` - Cleft sentences (`What I need is...`, `It was John who...`)
- `en.word_formation` - Heuristicas basicas de formacion de palabras (familia `decide/decision/decisive`)

## Nota importante

- Muchas reglas B2 estan implementadas como heuristicas de forma (estructura), no como analisis semantico profundo.
- El motor ya cubre una gran parte de errores frecuentes de estudiantes, pero todavia puede haber falsos positivos/negativos en oraciones complejas.
