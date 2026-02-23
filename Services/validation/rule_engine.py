from Services.analysis.sentence_analyzer import SentenceAnalyzer, WH_QUESTION_WORDS
from Services.grammar.english_ruleset import get_english_rules
from Services.validation.collocation_support import CollocationSupport
from Services.validation.dictionary_lexicon_support import DictionaryLexiconSupport
from Services.validation.validation_result import ValidationResult


class RuleEngine:
    def __init__(self) -> None:
        self.sentence_analyzer = SentenceAnalyzer()
        self.dictionary_lexicon = DictionaryLexiconSupport()
        self.collocation_support = CollocationSupport()
        self._lexicon_enriched = False

    def _ensure_dictionary_lexicon_ready(self) -> None:
        if self._lexicon_enriched:
            return
        self.dictionary_lexicon.enrich_rule_engine_lexicons()
        self._lexicon_enriched = True

    def lookup_dictionary_word(self, word: str) -> dict | None:
        record = self.dictionary_lexicon.lookup(word)
        if record is None:
            return None
        return {
            "word": record.word,
            "normalized": record.normalized,
            "pos_classes": sorted(record.pos_classes),
            "translations": sorted(t for t in record.translations if t),
        }

    def validate_sentence(self, text: str, language: str = "english") -> ValidationResult:
        if language.lower() != "english":
            result = ValidationResult(is_valid=False)
            result.add_suggestion(
                "Solo esta implementada la validacion para ingles en esta version inicial."
            )
            return result

        self._ensure_dictionary_lexicon_ready()
        analysis = self.sentence_analyzer.analyze_english(text)
        result = ValidationResult()
        features_by_index = {f.index: f for f in analysis.token_features}

        for rule in get_english_rules():
            issue = rule.evaluate(analysis)
            if issue is not None:
                result.add_issue(issue)

        if analysis.sentence_type == "fragment":
            result.add_pattern_warning(
                "en.pattern.fragment",
                "Intenta escribir una oracion completa con sujeto + verbo.",
            )
        elif analysis.sentence_type == "imperative":
            result.add_pattern_warning(
                "en.pattern.imperative_subject_optional",
                "Las oraciones imperativas son validas sin sujeto explicito (ej.: 'Sit down.').",
            )
        elif not analysis.has_explicit_subject and analysis.subject_requirement == "required":
            result.add_pattern_warning(
                "en.pattern.explicit_subject_missing",
                "Agrega un sujeto explicito, por ejemplo: I / you / he / she / it / we / they.",
            )

        wh_aux_ok = (
            len(analysis.tokens) >= 2
            and analysis.tokens[0] in WH_QUESTION_WORDS
            and analysis.tokens[1] in {
                "do",
                "does",
                "did",
                "is",
                "are",
                "am",
                "was",
                "were",
                "can",
                "could",
                "will",
                "would",
                "should",
                "have",
                "has",
                "had",
            }
        )
        if analysis.sentence_type == "interrogative" and not analysis.starts_with_auxiliary and not wh_aux_ok:
            result.add_pattern_warning(
                "en.pattern.question_auxiliary_hint",
                "Para preguntas basicas, empieza con un auxiliar: do / does / did / is / are / can...",
            )

        third_person_base_candidates = {"work", "like", "love", "want", "need", "eat", "run", "study", "play"}
        second_feature = features_by_index.get(1)
        if (
            analysis.subject_token in {"he", "she", "it"}
            and analysis.sentence_type == "declarative"
            and len(analysis.tokens) > 1
            and analysis.tokens[1] in third_person_base_candidates
            and analysis.primary_tense_guess == "present_simple"
            and second_feature is not None
            and second_feature.pos_guess == "verb"
            and second_feature.verb_form_guess == "base"
        ):
            result.add_pattern_warning(
                "en.pattern.third_person_s_hint",
                "Recuerda la concordancia en presente simple: he / she / it normalmente usa verbo + s.",
            )

        modal_problem = False
        if analysis.modal_token is not None:
            try:
                idx = analysis.tokens.index(analysis.modal_token)
                candidate_features = analysis.token_features[idx + 1 : idx + 5]
            except ValueError:
                candidate_features = []
            for feature in candidate_features:
                token = feature.token
                if token in {"i", "you", "he", "she", "it", "we", "they", "not"}:
                    continue
                if feature.pos_guess in {"adverb", "preposition", "determiner"}:
                    continue
                if feature.pos_guess in {"verb", "verb_participle"} and feature.verb_form_guess not in {"base"}:
                    modal_problem = True
                elif feature.pos_guess == "noun" and token.endswith(("s", "ed", "ing")):
                    modal_problem = True
                break

        if modal_problem:
            result.add_pattern_warning(
                "en.pattern.modal_base_verb_hint",
                "Despues de verbos modales (can / should / must), usa el verbo en forma base (ej.: 'can swim').",
            )

        if analysis.be_form_token in {"is", "are"} and analysis.subject_number_guess in {"singular", "plural"}:
            if analysis.subject_number_guess == "plural" and analysis.be_form_token == "is":
                result.add_pattern_warning(
                    "en.pattern.be_agreement_plural",
                    "Si el sujeto es plural (por ejemplo, 'my uncles'), usa 'are' en lugar de 'is'.",
                )
            elif analysis.subject_number_guess == "singular" and analysis.be_form_token == "are":
                result.add_pattern_warning(
                    "en.pattern.be_agreement_singular",
                    "Si el sujeto es singular, normalmente usa 'is' en lugar de 'are'.",
                )

        for hint in self.dictionary_lexicon.semantic_hints_for_tokens(analysis.tokens):
            result.add_lexical_hint(hint)

        for hint in self.collocation_support.collocation_hints_for_analysis(analysis):
            result.add_lexical_hint(hint)

        for hint in self.dictionary_lexicon.suggest_unknown_tokens(analysis.tokens):
            result.add_lexical_hint(hint)

        return result
