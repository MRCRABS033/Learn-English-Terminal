"""Reglas de mapeo POS del diccionario (abreviaturas -> WordClass)."""

from __future__ import annotations


POS_TO_WORD_CLASS = {
    "noun": ("noun", "Noun"),
    "verb": ("verb", "Verb"),
    "adjective": ("adjective", "Adjective"),
    "adverb": ("adverb", "Adverb"),
    "preposition": ("preposition", "Preposition"),
    "pronoun": ("pronoun", "Pronoun"),
    "conjunction": ("conjunction", "Conjunction"),
    "interjection": ("interjection", "Interjection"),
    "determiner": ("determiner", "Determiner"),
    "auxiliary": ("auxiliary", "Auxiliary verb"),
    "abbreviation": ("abbreviation", "Abbreviation"),
    "unknown": ("unknown", "Unknown"),
}

RAW_DICT_POS_TO_NORMALIZED = {
    "n": "noun",
    "adj": "adjective",
    "adv": "adverb",
    "vt": "verb",
    "vi": "verb",
    "vt-vi": "verb",
    "vi-vt": "verb",
    "abbr": "abbreviation",
    "prep": "preposition",
    "pron": "pronoun",
    "conj": "conjunction",
    "int": "interjection",
    "det": "determiner",
    "aux": "auxiliary",
}


DICT_POS_RULE_EXPLANATIONS = [
    ("n", "noun", "Sustantivo", "Se guarda en WordClass 'noun'."),
    ("adj", "adjective", "Adjetivo", "Se guarda en WordClass 'adjective'."),
    ("adv", "adverb", "Adverbio", "Se guarda en WordClass 'adverb'."),
    ("vt", "verb", "Verbo transitivo", "Se normaliza a 'verb'."),
    ("vi", "verb", "Verbo intransitivo", "Se normaliza a 'verb'."),
    ("vt-vi", "verb", "Verbo transitivo/intransitivo", "Se normaliza a 'verb'."),
    ("vi-vt", "verb", "Verbo intransitivo/transitivo", "Se normaliza a 'verb'."),
    ("abbr", "abbreviation", "Abreviatura", "Se guarda en WordClass 'abbreviation'."),
    ("prep", "preposition", "Preposicion", "Se guarda en WordClass 'preposition'."),
    ("pron", "pronoun", "Pronombre", "Se guarda en WordClass 'pronoun'."),
    ("conj", "conjunction", "Conjuncion", "Se guarda en WordClass 'conjunction'."),
    ("int", "interjection", "Interjeccion", "Se guarda en WordClass 'interjection'."),
    ("det", "determiner", "Determinante", "Se guarda en WordClass 'determiner'."),
    ("aux", "auxiliary", "Auxiliar", "Se guarda en WordClass 'auxiliary'."),
]


PENDING_POS_RULES = [
    (
        "vpr",
        "Reflexivo / pronominal",
        "No mapeado en el importador EN->ES actual; aparece mas en entradas ES->EN.",
    ),
    (
        "n m / n f / nm / nf",
        "Genero en sustantivos",
        "No se preserva genero; hoy solo se clasifica como sustantivo cuando aplica.",
    ),
    (
        "loc / phr / idiom",
        "Locucion / frase hecha",
        "Falta clase especifica (ej. phrase/idiom) y parser mas robusto por columnas.",
    ),
    (
        "marcas compuestas",
        "Ej. 'adj-adv', subtipos o etiquetas adicionales",
        "Requiere ampliar parser y mapeo para no perder granularidad.",
    ),
]


def build_dictionary_pos_mapping_help_text() -> str:
    lines = [
        "Vista: Mapeo POS del diccionario -> tipos de palabra (WordClass)",
        "",
        "Reglas implementadas (usadas por el importador del PDF):",
    ]

    for raw_tag, normalized, human_label, note in DICT_POS_RULE_EXPLANATIONS:
        lines.append(f"- {raw_tag} -> {normalized} ({human_label}). {note}")

    lines.extend(
        [
            "",
            "Regla general de mapeo:",
            "- vt/vi/vt-vi/vi-vt se consolidan como 'verb' para simplificar reglas gramaticales.",
            "- Si el tag no se reconoce, cae en 'unknown'.",
            "",
            "Lo que falta / pendiente:",
        ]
    )

    for raw_tag, label, note in PENDING_POS_RULES:
        lines.append(f"- {raw_tag}: {label}. {note}")

    lines.extend(
        [
            "",
            "Notas de calidad:",
            "- El parser del PDF es heuristico (columnas); algunas filas pueden mezclarse.",
            "- Para mejorar precision faltan reglas anti-columnas y deteccion de lineas corruptas.",
        ]
    )

    return "\n".join(lines)
