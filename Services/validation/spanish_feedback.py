import re


RULE_MESSAGES_ES = {
    "en.required_verb": "La oracion necesita un verbo para estar completa.",
    "en.explicit_subject": "La oracion necesita un sujeto explicito en ingles.",
    "en.imperative_subject_optional": "En imperativos, el sujeto suele omitirse porque se sobreentiende.",
    "en.question_auxiliary": "Las preguntas en ingles normalmente usan un auxiliar al inicio (o despues de la palabra wh-).",
    "en.present_simple_structure": "La estructura del presente simple no esta bien formada.",
    "en.to_be_no_do": "Con 'to be' normalmente no se usa do/does/did en preguntas o negaciones basicas.",
    "en.present_simple_do_negation": "La negacion en presente simple debe usar do/does + not + verbo base.",
    "en.third_person_s": "Con he/she/it en presente simple, el verbo normalmente lleva -s.",
    "en.article_a_an_sound": "El articulo indefinido (a/an) no coincide con el sonido inicial de la palabra.",
    "en.adjective_noun_order": "En ingles, el adjetivo normalmente va antes del sustantivo.",
    "en.basic_svo_order": "El orden basico suele ser Sujeto + Verbo + Complemento.",
    "en.preposition_collocation": "La preposicion/collocation usada no es la mas natural en ingles.",
    "en.phrasal_basic": "La combinacion del phrasal verb no coincide con un patron comun.",
    "en.modal_base_verb": "Despues de un modal, se usa el verbo en forma base.",
    "en.modal_combination": "No se suelen combinar dos modales seguidos (por ejemplo, 'can should').",
    "en.semi_modal_have_to": "La estructura de 'have to / has to' no esta bien formada.",
    "en.subject_be_agreement": "No hay concordancia correcta entre el sujeto y 'to be'.",
    "en.present_continuous": "El presente continuo debe usar am/is/are + verbo-ing.",
    "en.past_simple": "La estructura de pasado simple no esta bien formada.",
    "en.past_continuous_interruption": "En el patron con 'when', normalmente se usa pasado simple en la accion que interrumpe.",
    "en.future_will": "El futuro con 'will' debe usar 'will + verbo base'.",
    "en.future_plan_present_continuous": "Para planes futuros con presente continuo, usa am/is/are + verbo-ing.",
    "en.future_schedule_present_simple": "Para horarios/programaciones se suele usar presente simple.",
    "en.future_going_to": "El futuro con 'going to' debe usar am/is/are + going to + verbo base.",
    "en.present_perfect": "El presente perfecto debe usar have/has + participio.",
    "en.present_perfect_vs_past_simple_usage": "No se suele usar present perfect con marcadores de tiempo terminado (yesterday/last/ago).",
    "en.present_perfect_continuous": "El presente perfecto continuo debe usar have/has been + verbo-ing.",
    "en.past_perfect": "El past perfect debe usar had + participio.",
    "en.past_perfect_continuous": "El past perfect continuous debe usar had been + verbo-ing.",
    "en.past_continuous": "El pasado continuo debe usar was/were + verbo-ing.",
    "en.future_continuous": "El future continuous debe usar will be + verbo-ing.",
    "en.future_perfect": "El future perfect debe usar will have + participio.",
    "en.future_perfect_continuous": "El future perfect continuous debe usar will have been + verbo-ing.",
    "en.comparatives_superlatives": "La estructura de comparativo/superlativo no esta bien formada.",
    "en.conditionals_b1": "La estructura del condicional (B1) no coincide con el patron esperado.",
    "en.conditionals_b2": "La estructura del condicional avanzado (B2) no coincide con el patron esperado.",
    "en.passive_basic": "La voz pasiva basica debe usar be + participio.",
    "en.passive_advanced": "La voz pasiva avanzada no esta bien formada.",
    "en.reported_speech_basic": "En reported speech/pregunta indirecta no debe mantenerse el orden de pregunta directa.",
    "en.reported_speech_advanced": "La estructura con reporting verbs no esta bien formada.",
    "en.indirect_questions": "Las preguntas indirectas usan orden de enunciado, no de pregunta directa.",
    "en.relative_clauses_basic": "La relativa basica no esta bien formada (por ejemplo, pronombre repetido).",
    "en.relative_clauses_advanced": "La relativa avanzada no esta bien formada.",
    "en.gerund_infinitive_common": "El patron de gerundio/infinitivo no coincide con el verbo usado.",
    "en.gerund_infinitive_meaning_pairs": "La combinacion gerundio/infinitivo en este verbo esta mal formada.",
    "en.determiners_quantifiers_basic": "El determinante/cuantificador no coincide con el tipo de sustantivo.",
    "en.some_any": "El uso de some/any no coincide con el tipo de oracion.",
    "en.quantifiers_determiners_advanced": "La estructura de cuantificadores/determinantes avanzados no esta bien formada.",
    "en.linking_devices": "El conector esta usado con una estructura no natural en ingles.",
    "en.modal_advanced_perfect": "La estructura modal avanzada debe usar modal + have + participio.",
    "en.inversion_emphasis": "La inversion de enfasis no esta bien formada.",
    "en.cleft_sentences": "La estructura enfatica (cleft sentence) no esta bien formada.",
    "en.noun_clauses_complex": "La subordinacion / noun clause no esta bien formada.",
    "en.phrasal_advanced": "La combinacion del phrasal verb avanzado no coincide con el patron esperado.",
    "en.word_formation": "La forma de palabra (sustantivo/adjetivo/verbo) no coincide con el contexto.",
}

SUGGESTION_MESSAGES_ES = {
    "Intenta escribir una oracion completa con sujeto + verbo.": "Intenta escribir una oracion completa con sujeto + verbo.",
    "Las oraciones imperativas son validas sin sujeto explicito (ej.: 'Sit down.').": "Las oraciones imperativas son validas sin sujeto explicito (ej.: 'Sit down.').",
    "Agrega un sujeto explicito, por ejemplo: I / you / he / she / it / we / they.": "Agrega un sujeto explicito, por ejemplo: I / you / he / she / it / we / they.",
    "Para preguntas basicas, empieza con un auxiliar: do / does / did / is / are / can...": "Para preguntas basicas, empieza con un auxiliar: do / does / did / is / are / can...",
    "Recuerda la concordancia en presente simple: he / she / it normalmente usa verbo + s.": "Recuerda la concordancia en presente simple: he / she / it normalmente usa verbo + s.",
    "Despues de verbos modales (can / should / must), usa el verbo en forma base (ej.: 'can swim').": "Despues de verbos modales (can / should / must), usa el verbo en forma base (ej.: 'can swim').",
    "Si el sujeto es plural (por ejemplo, 'my uncles'), usa 'are' en lugar de 'is'.": "Si el sujeto es plural (por ejemplo, 'my uncles'), usa 'are' en lugar de 'is'.",
    "Si el sujeto es singular, normalmente usa 'is' en lugar de 'are'.": "Si el sujeto es singular, normalmente usa 'is' en lugar de 'are'.",
}


def _tokens(text: str) -> list[str]:
    return re.findall(r"[A-Za-z']+", text)


def _same_words_example(rule_id: str, original_text: str) -> str | None:
    tokens = _tokens(original_text)
    lower = [t.lower() for t in tokens]
    if not tokens:
        return None

    if rule_id == "en.adjective_noun_order":
        for i in range(len(lower) - 2):
            if lower[i] in {"a", "an", "the", "my", "your", "his", "her", "our", "their"}:
                if not (
                    len(tokens) in {3, 4}
                    and (i + 3 == len(tokens) or lower[-1] in {"is", "are", "was", "were"})
                ):
                    continue
                # det + noun + adj -> det + adj + noun
                det, noun, adj = tokens[i], tokens[i + 1], tokens[i + 2]
                reordered = tokens[:i] + [det, adj, noun] + tokens[i + 3 :]
                return " ".join(reordered)

    if rule_id == "en.basic_svo_order" and len(tokens) == 3 and lower[0] in {"i", "you", "he", "she", "it", "we", "they"}:
        # patron comun: sujeto + complemento + verbo -> sujeto + verbo + complemento
        subj, mid, verb = tokens[0], tokens[1], tokens[2]
        if lower[2] not in {
            "eat", "eats", "like", "likes", "study", "studies", "work", "works", "play", "plays",
            "read", "reads", "write", "writes", "watch", "watches", "visit", "visits",
        }:
            return None
        reordered = [subj, verb, mid] + tokens[3:]
        return " ".join(reordered)

    if rule_id == "en.article_a_an_sound" and len(tokens) >= 2:
        if lower[0] in {"a", "an"}:
            next_word = tokens[1]
            starts_vowel = next_word[:1].lower() in {"a", "e", "i", "o", "u"}
            expected = "an" if starts_vowel else "a"
            # excepciones muy comunes
            if next_word.lower().startswith(("hour", "honest", "honor", "heir", "herb")):
                expected = "an"
            if next_word.lower().startswith(("university", "unicorn", "uni", "euro", "user", "use")):
                expected = "a"
            return " ".join([expected] + tokens[1:])

    if rule_id == "en.present_simple_do_negation":
        if len(lower) >= 3 and lower[1] == "not":
            subj = lower[0]
            aux = "does" if subj in {"he", "she", "it"} else "do"
            return " ".join([tokens[0], aux, "not"] + tokens[2:])
        if any(t in {"don't", "doesn't"} for t in lower):
            fixed = tokens[:]
            for i, t in enumerate(lower):
                if t == "don't" and lower[0] in {"he", "she", "it"}:
                    fixed[i] = "doesn't"
                if t == "doesn't" and lower[0] in {"i", "you", "we", "they"}:
                    fixed[i] = "don't"
                if t in {"don't", "doesn't"} and i + 1 < len(fixed):
                    # quitar -s simple en el siguiente verbo si aplica
                    nxt = fixed[i + 1]
                    if nxt.lower().endswith("ies"):
                        fixed[i + 1] = nxt[:-3] + "y"
                    elif nxt.lower().endswith("s") and not nxt.lower().endswith("ss"):
                        fixed[i + 1] = nxt[:-1]
            return " ".join(fixed)

    if rule_id == "en.third_person_s" and len(tokens) >= 2 and lower[0] in {"he", "she", "it"}:
        v = tokens[1]
        if not lower[1].endswith("s"):
            if lower[1].endswith("y"):
                v2 = v[:-1] + "ies"
            elif lower[1].endswith(("ch", "sh", "x", "z", "o")):
                v2 = v + "es"
            else:
                v2 = v + "s"
            return " ".join([tokens[0], v2] + tokens[2:])

    return None


def format_issue_es(rule_id: str, original_text: str | None = None) -> str:
    base = RULE_MESSAGES_ES.get(rule_id, f"Se detecto un problema gramatical ({rule_id}).")
    if not original_text:
        return base

    example = _same_words_example(rule_id, original_text)
    if example and example.strip().lower() != original_text.strip().lower():
        return f"{base} Ejemplo con tus palabras: '{example}'."
    return base


def format_suggestion_es(suggestion: str) -> str:
    return SUGGESTION_MESSAGES_ES.get(suggestion, suggestion)
