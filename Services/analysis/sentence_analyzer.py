from dataclasses import dataclass, replace
from collections.abc import Callable
import re

from Services.analysis.english_heuristics import (
    BASE_COMMON_ADJECTIVES,
    BASE_COMMON_ADVERBS,
    BASE_PREPOSITIONS,
    LIKELY_ADJECTIVAL_ED_FORMS,
    LIKELY_ADJECTIVAL_ING_FORMS,
    guess_noun_countability,
)

ENGLISH_SUBJECT_PRONOUNS = {
    "i",
    "you",
    "he",
    "she",
    "it",
    "we",
    "they",
}

COMMON_VERBS = {
    "am",
    "is",
    "are",
    "was",
    "were",
    "be",
    "have",
    "has",
    "had",
    "do",
    "does",
    "did",
    "go",
    "goes",
    "went",
    "run",
    "runs",
    "eat",
    "eats",
    "study",
    "studies",
    "work",
    "works",
    "like",
    "likes",
    "love",
    "loves",
    "want",
    "wants",
    "need",
    "needs",
    "live",
    "lives",
    "learn",
    "learns",
    "speak",
    "speaks",
    "read",
    "reads",
    "write",
    "writes",
    "watch",
    "watches",
    "visit",
    "visits",
    "depend",
    "depends",
    "interest",
    "interests",
    "get",
    "gets",
    "got",
    "turn",
    "turns",
    "find",
    "finds",
    "found",
    "carry",
    "carries",
    "put",
    "puts",
    "build",
    "builds",
    "built",
    "say",
    "says",
    "said",
    "tell",
    "tells",
    "told",
    "ask",
    "asks",
    "asked",
    "enjoy",
    "enjoys",
    "remember",
    "remembers",
    "stop",
    "stops",
    "decide",
    "decides",
    "suggest",
    "suggests",
    "advise",
    "advises",
    "sit",
    "open",
    "close",
}

IMPERATIVE_STARTERS = {
    "please",
    "do",
    "don't",
}

QUESTION_AUXILIARIES = {
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
    "may",
    "might",
    "must",
    "will",
    "would",
    "shall",
    "should",
    "have",
    "has",
    "had",
}

WH_QUESTION_WORDS = {
    "what",
    "where",
    "when",
    "why",
    "who",
    "whom",
    "whose",
    "which",
    "how",
}

TO_BE_FORMS = {"am", "is", "are", "was", "were"}
MODAL_VERBS = {"can", "could", "should", "must", "may", "might", "will", "would"}
BASE_AUXILIARIES = {"do", "does", "did"}
SUBJECT_DETERMINERS = {
    "my",
    "your",
    "his",
    "her",
    "its",
    "our",
    "their",
    "the",
    "a",
    "an",
    "this",
    "that",
    "these",
    "those",
}

COORDINATORS = {"and", "or", "but"}
NP_QUANTIFIERS = {
    "many",
    "much",
    "few",
    "little",
    "some",
    "any",
    "both",
    "each",
    "every",
    "either",
    "neither",
    "enough",
    "several",
    "such",
}
PREPOSITIONS = {
    *BASE_PREPOSITIONS,
}
COMMON_ADVERBS = {*BASE_COMMON_ADVERBS}
COMMON_ADJECTIVES = {*BASE_COMMON_ADJECTIVES}
LIKELY_ADJECTIVAL_ING = {*LIKELY_ADJECTIVAL_ING_FORMS}
LIKELY_ADJECTIVAL_ED = {*LIKELY_ADJECTIVAL_ED_FORMS}
AMBIGUOUS_NOUN_VERB_BASES = {
    "work",
    "study",
    "watch",
    "love",
    "drink",
    "walk",
    "play",
    "cook",
    "dance",
    "phone",
    "answer",
    "visit",
}
COMMON_IRREGULAR_PAST = {
    "went",
    "got",
    "found",
    "built",
    "said",
    "told",
    "read",
    "ran",
    "ate",
    "wrote",
    "came",
    "saw",
    "made",
    "took",
    "did",
}
COMMON_IRREGULAR_PARTICIPLES = {
    "been",
    "gone",
    "done",
    "seen",
    "made",
    "taken",
    "written",
    "eaten",
    "read",
    "built",
    "found",
    "told",
    "said",
}


@dataclass
class TokenFeature:
    token: str
    index: int
    pos_guess: str
    pos_candidates: list[str]
    verb_confidence: str
    verb_form_guess: str | None
    noun_countability_guess: str | None
    notes: list[str]
    external_pos: str | None = None


@dataclass
class RawTokenSpan:
    text: str
    kind: str  # "word" | "punct"
    start_char: int
    end_char: int
    word_index: int | None = None


@dataclass
class ClauseAnalysis:
    start_idx: int
    end_idx: int
    clause_type: str
    subject_idx: int | None
    main_verb_idx: int | None
    aux_chain: list[str]
    tense_guess: str | None
    polarity: str
    linker_tokens: list[str]
    subject_phrase_span: tuple[int, int] | None = None


@dataclass
class NounPhraseAnalysis:
    start_idx: int
    end_idx: int
    determiner: str | None
    quantifier: str | None
    pattern: str | None
    head_idx: int
    head_token: str
    head_pos_guess: str
    countability_guess: str | None
    role_guess: str  # "subject" | "object" | "predicate_nominal" | "other"
    is_generic_candidate: bool


@dataclass
class SentenceAnalysis:
    original_text: str
    cleaned_text: str
    tokens: list[str]
    sentence_type: str
    is_complete_sentence: bool
    has_explicit_subject: bool
    has_verb: bool
    subject_requirement: str
    polarity: str
    first_token: str | None
    second_token: str | None
    subject_token: str | None
    starts_with_auxiliary: bool
    uses_to_be: bool
    modal_token: str | None
    subject_number_guess: str | None
    be_form_token: str | None
    token_features: list[TokenFeature]
    tense_guesses: list[str]
    primary_tense_guess: str | None
    raw_token_stream: list[RawTokenSpan]
    clause_boundaries: list[tuple[int, int]]
    clauses: list[ClauseAnalysis]
    clause_linkers_detected: list[str]
    sentence_span: tuple[int, int] | None
    noun_phrases: list[NounPhraseAnalysis]


class SentenceAnalyzer:
    def __init__(
        self,
        external_pos_tagger: Callable[[list[str]], list[str | None]] | None = None,
    ) -> None:
        # Optional support layer: external POS can refine low-confidence heuristic guesses.
        self.external_pos_tagger = external_pos_tagger

    def analyze_english(self, text: str) -> SentenceAnalysis:
        cleaned_text = text.strip()
        tokens = self._tokenize(cleaned_text)
        raw_token_stream = self._tokenize_with_punctuation(cleaned_text)
        token_features = self._build_token_features(tokens)

        sentence_type = self._detect_sentence_type(cleaned_text, tokens, token_features)
        has_explicit_subject = self._detect_explicit_subject(tokens, sentence_type)
        has_verb = self._detect_verb(tokens, token_features)
        polarity = self._detect_polarity(tokens)
        tense_guesses = self._detect_tense_guesses(tokens, token_features)
        clauses = self._segment_clauses(tokens, token_features, cleaned_text, raw_token_stream)
        noun_phrases = self._extract_noun_phrases(tokens, token_features, clauses)
        subject_requirement = (
            "optional-implicit" if sentence_type == "imperative" else "required"
        )
        is_complete_sentence = bool(tokens) and has_verb

        return SentenceAnalysis(
            original_text=text,
            cleaned_text=cleaned_text,
            tokens=tokens,
            sentence_type=sentence_type,
            is_complete_sentence=is_complete_sentence,
            has_explicit_subject=has_explicit_subject,
            has_verb=has_verb,
            subject_requirement=subject_requirement,
            polarity=polarity,
            first_token=tokens[0] if tokens else None,
            second_token=tokens[1] if len(tokens) > 1 else None,
            subject_token=self._detect_subject_token(tokens, sentence_type),
            starts_with_auxiliary=bool(tokens and tokens[0] in QUESTION_AUXILIARIES),
            uses_to_be=any(token in TO_BE_FORMS for token in tokens),
            modal_token=self._detect_modal(tokens),
            subject_number_guess=self._guess_subject_number(tokens, sentence_type),
            be_form_token=self._detect_be_form_token(tokens),
            token_features=token_features,
            tense_guesses=tense_guesses,
            primary_tense_guess=self._pick_primary_tense_guess(tense_guesses),
            raw_token_stream=raw_token_stream,
            clause_boundaries=[(cl.start_idx, cl.end_idx) for cl in clauses],
            clauses=clauses,
            clause_linkers_detected=self._extract_clause_linkers(clauses),
            sentence_span=(0, len(tokens) - 1) if tokens else None,
            noun_phrases=noun_phrases,
        )

    def _tokenize(self, text: str) -> list[str]:
        return re.findall(r"[A-Za-z']+", text.lower())

    def _tokenize_with_punctuation(self, text: str) -> list[RawTokenSpan]:
        items: list[RawTokenSpan] = []
        word_index = 0
        for match in re.finditer(r"[A-Za-z']+|[.,;:?!]", text):
            raw = match.group(0)
            kind = "word" if re.fullmatch(r"[A-Za-z']+", raw) else "punct"
            items.append(
                RawTokenSpan(
                    text=raw.lower() if kind == "word" else raw,
                    kind=kind,
                    start_char=match.start(),
                    end_char=match.end(),
                    word_index=(word_index if kind == "word" else None),
                )
            )
            if kind == "word":
                word_index += 1
        return items

    def _detect_sentence_type(
        self, text: str, tokens: list[str], token_features: list[TokenFeature]
    ) -> str:
        if not tokens:
            return "fragment"

        if text.strip().endswith("?"):
            return "interrogative"

        first = tokens[0]
        second = tokens[1] if len(tokens) > 1 else None
        if first in IMPERATIVE_STARTERS:
            return "imperative"

        if first in QUESTION_AUXILIARIES:
            return "interrogative"

        if first in WH_QUESTION_WORDS and second in QUESTION_AUXILIARIES:
            return "interrogative"

        first_feature = token_features[0] if token_features else None
        if (
            first in COMMON_VERBS
            and first not in ENGLISH_SUBJECT_PRONOUNS
            and first_feature is not None
            and first_feature.pos_guess in {"verb", "auxiliary"}
        ):
            return "imperative"

        return "declarative"

    def _detect_explicit_subject(self, tokens: list[str], sentence_type: str) -> bool:
        if not tokens:
            return False

        if sentence_type == "imperative":
            return tokens[0] in ENGLISH_SUBJECT_PRONOUNS

        if sentence_type == "interrogative":
            if tokens[0] in ENGLISH_SUBJECT_PRONOUNS:
                return True
            if len(tokens) > 1 and tokens[1] in SUBJECT_DETERMINERS:
                return True
            return any(token in ENGLISH_SUBJECT_PRONOUNS for token in tokens[1:4])

        if tokens[0] in ENGLISH_SUBJECT_PRONOUNS:
            return True

        # Heuristic: a noun phrase before the first verb/to-be counts as explicit subject.
        first_verb_idx = self._find_first_verb_index(tokens)
        if first_verb_idx is None or first_verb_idx == 0:
            return False

        if tokens[0] in SUBJECT_DETERMINERS:
            return True

        # Simple noun-like token before verb (e.g. "students are", "john works")
        return tokens[0].isalpha()

    def _detect_subject_token(self, tokens: list[str], sentence_type: str) -> str | None:
        if not tokens:
            return None

        if sentence_type == "interrogative":
            if tokens[0] in ENGLISH_SUBJECT_PRONOUNS:
                return tokens[0]
            for token in tokens[1:4]:
                if token in ENGLISH_SUBJECT_PRONOUNS:
                    return token
            return None

        return tokens[0] if tokens[0] in ENGLISH_SUBJECT_PRONOUNS else None

    def _detect_verb(self, tokens: list[str], token_features: list[TokenFeature]) -> bool:
        if not tokens:
            return False

        if any(token in MODAL_VERBS for token in tokens):
            return True

        # Token features reduce false positives for noun/verb ambiguity (e.g. "work").
        for feature in token_features:
            if feature.pos_guess in {"verb", "auxiliary", "verb_participle"}:
                return True
            if (
                feature.verb_confidence == "medium"
                and any(tag in feature.pos_candidates for tag in {"verb", "verb_participle"})
            ):
                return True
        return False

    def _detect_polarity(self, tokens: list[str]) -> str:
        negatives = {"not", "no", "never", "don't", "doesn't", "didn't", "can't", "won't"}
        return "negative" if any(token in negatives for token in tokens) else "affirmative"

    def _detect_modal(self, tokens: list[str]) -> str | None:
        for token in tokens:
            if token in MODAL_VERBS:
                return token
        return None

    def _find_first_verb_index(self, tokens: list[str]) -> int | None:
        features = self._build_token_features(tokens)
        for idx, token in enumerate(tokens):
            if token in MODAL_VERBS:
                return idx
            feature = features[idx]
            if feature.pos_guess in {"verb", "auxiliary", "verb_participle"}:
                return idx
            if (
                feature.verb_confidence == "medium"
                and any(tag in feature.pos_candidates for tag in {"verb", "verb_participle"})
            ):
                return idx
        return None

    def _guess_subject_number(self, tokens: list[str], sentence_type: str) -> str | None:
        if not tokens:
            return None

        first_verb_idx = self._find_first_verb_index(tokens)
        subject_zone = tokens[:first_verb_idx] if first_verb_idx is not None else tokens[:6]

        # Coordinated subjects: "my brother and my sister are..."
        if "and" in subject_zone:
            and_idx = subject_zone.index("and")
            left = subject_zone[:and_idx]
            right = subject_zone[and_idx + 1 :]
            if self._looks_subject_phrase(left) and self._looks_subject_phrase(right):
                return "plural"

        # Either/Neither ... or/nor: agreement often follows the closest element.
        if "either" in subject_zone or "neither" in subject_zone:
            for splitter in ("or", "nor"):
                if splitter in subject_zone:
                    split_idx = len(subject_zone) - 1 - subject_zone[::-1].index(splitter)
                    rhs = [t for t in subject_zone[split_idx + 1 :] if t not in SUBJECT_DETERMINERS]
                    if rhs:
                        return self._guess_number_from_single_subject_head(rhs[0])

        # Pronoun-based guess (works for declaratives and many questions).
        if sentence_type == "interrogative":
            candidates = tokens[:4]
        else:
            candidates = tokens[:3]

        for token in candidates:
            if token in {"i", "he", "she", "it"}:
                return "singular"
            if token in {"we", "they"}:
                return "plural"
            if token == "you":
                return "plural_or_singular"

        # Quantity subject patterns:
        # "the number of students" -> singular
        # "a number of students" -> plural
        if len(subject_zone) >= 3 and subject_zone[:3] == ["the", "number", "of"]:
            return "singular"
        if len(subject_zone) >= 3 and subject_zone[:3] == ["a", "number", "of"]:
            return "plural"
        if len(subject_zone) >= 3 and subject_zone[:3] == ["a", "lot", "of"]:
            tail = [t for t in subject_zone[3:] if t not in SUBJECT_DETERMINERS]
            if tail:
                for tok in reversed(tail):
                    if tok.isalpha():
                        return self._guess_number_from_single_subject_head(tok)
        if len(subject_zone) >= 2 and subject_zone[:2] in (["lots", "of"], ["plenty", "of"]):
            tail = [t for t in subject_zone[2:] if t not in SUBJECT_DETERMINERS]
            if tail:
                for tok in reversed(tail):
                    if tok.isalpha():
                        return self._guess_number_from_single_subject_head(tok)

        # Noun phrase heuristic: determiner + noun (e.g. "my uncles")
        if len(tokens) >= 2 and tokens[0] in SUBJECT_DETERMINERS:
            noun = tokens[1]
            # "the list of items" -> agreement with head noun "list"
            if len(tokens) >= 4 and tokens[2] == "of":
                noun = tokens[1]
            if noun.endswith("s") and not noun.endswith("ss"):
                return "plural"
            return "singular"

        # Bare noun heuristic: "students are", "teacher is"
        noun = tokens[0]
        if noun not in COMMON_VERBS and noun not in QUESTION_AUXILIARIES:
            if noun.endswith("s") and not noun.endswith("ss"):
                return "plural"
            return "singular"

        return None

    @staticmethod
    def _looks_subject_phrase(tokens: list[str]) -> bool:
        if not tokens:
            return False
        filtered = [t for t in tokens if t not in SUBJECT_DETERMINERS]
        if not filtered:
            return False
        head = filtered[-1]
        return head.isalpha() and head not in QUESTION_AUXILIARIES and head not in MODAL_VERBS

    @staticmethod
    def _guess_number_from_single_subject_head(token: str) -> str | None:
        if token in {"i", "he", "she", "it"}:
            return "singular"
        if token in {"we", "they"}:
            return "plural"
        if token == "you":
            return "plural_or_singular"
        if token.endswith("s") and not token.endswith("ss"):
            return "plural"
        if token.isalpha():
            return "singular"
        return None

    def _detect_be_form_token(self, tokens: list[str]) -> str | None:
        for token in tokens:
            if token in {"is", "are", "was", "were", "am"}:
                return token
        return None

    def _build_token_features(self, tokens: list[str]) -> list[TokenFeature]:
        features: list[TokenFeature] = []
        for idx, token in enumerate(tokens):
            prev_token = tokens[idx - 1] if idx > 0 else None
            next_token = tokens[idx + 1] if idx + 1 < len(tokens) else None
            features.append(self._classify_token(token, idx, prev_token, next_token))
        self._apply_external_pos_support(tokens, features)
        return features

    def _classify_token(
        self,
        token: str,
        index: int,
        prev_token: str | None,
        next_token: str | None,
    ) -> TokenFeature:
        candidates: set[str] = set()
        notes: list[str] = []
        pos_guess = "unknown"
        verb_confidence = "low"
        verb_form_guess: str | None = None
        noun_countability_guess: str | None = None

        if token in ENGLISH_SUBJECT_PRONOUNS:
            candidates.add("pronoun")
            pos_guess = "pronoun"
            notes.append("subject_pronoun")
        elif token in SUBJECT_DETERMINERS:
            candidates.add("determiner")
            pos_guess = "determiner"
            notes.append("determiner")
        elif token in TO_BE_FORMS or token in BASE_AUXILIARIES:
            candidates.update({"auxiliary", "verb"})
            pos_guess = "auxiliary"
            verb_confidence = "high"
            if token in {"am", "is", "are", "do", "does", "have", "has"}:
                verb_form_guess = "present_aux"
            elif token in {"was", "were", "did", "had"}:
                verb_form_guess = "past_aux"
            notes.append("core_auxiliary")
        elif token in MODAL_VERBS:
            candidates.update({"auxiliary", "verb"})
            pos_guess = "auxiliary"
            verb_confidence = "high"
            verb_form_guess = "modal"
            notes.append("modal")
        elif token in QUESTION_AUXILIARIES:
            candidates.update({"auxiliary", "verb"})
            pos_guess = "auxiliary"
            verb_confidence = "high"
            verb_form_guess = "present_aux"
            notes.append("question_auxiliary")
        elif token in COMMON_ADVERBS:
            candidates.add("adverb")
            pos_guess = "adverb"
            notes.append("common_adverb")
        elif token in COMMON_ADJECTIVES:
            candidates.add("adjective")
            pos_guess = "adjective"
            notes.append("common_adjective")

        if token.endswith("ing") and len(token) > 4:
            candidates.update({"verb_participle", "adjective", "noun"})
            notes.append("suffix_ing")
            if prev_token in TO_BE_FORMS:
                if token in LIKELY_ADJECTIVAL_ING and not self._looks_direct_object_after_ing(next_token):
                    pos_guess = "adjective"
                    verb_confidence = "low"
                    notes.append("common_ing_predicative_adj_after_be")
                elif next_token and next_token not in PREPOSITIONS and self._looks_noun_like(next_token):
                    pos_guess = "adjective"
                    verb_confidence = "low"
                    notes.append("be_plus_ing_before_noun_adj")
                else:
                    pos_guess = "verb_participle"
                    verb_confidence = "high"
                    verb_form_guess = "participle_ing"
                    notes.append("progressive_after_be")
            elif prev_token in {"very", "so", "too"}:
                pos_guess = "adjective"
                verb_confidence = "low"
                notes.append("degree_word_before_ing")
            elif prev_token in SUBJECT_DETERMINERS:
                if next_token and self._looks_noun_like(next_token):
                    pos_guess = "adjective"
                    notes.append("det_ing_noun_phrase_modifier")
                else:
                    pos_guess = "noun"
                    notes.append("determiner_plus_gerund_noun")
            elif next_token and self._looks_noun_like(next_token):
                pos_guess = "adjective"
                notes.append("ing_before_noun_adj")
            elif token in LIKELY_ADJECTIVAL_ING:
                pos_guess = "adjective"
                notes.append("common_ing_adjective")
            elif prev_token in {"am", "is", "are", "was", "were"}:
                pos_guess = "verb_participle"
                verb_confidence = "high"
                verb_form_guess = "participle_ing"
            else:
                if pos_guess == "unknown":
                    pos_guess = "verb_participle"
                    verb_confidence = "medium"
                    verb_form_guess = "participle_ing"

        if self._looks_likely_ed_inflection(token):
            candidates.update({"verb_participle", "adjective"})
            notes.append("suffix_ed")
            if prev_token in TO_BE_FORMS:
                if next_token in PREPOSITIONS or token in LIKELY_ADJECTIVAL_ED:
                    pos_guess = "adjective"
                    verb_confidence = "low"
                    notes.append("be_plus_ed_predicative_adj")
                else:
                    pos_guess = "verb_participle"
                    verb_confidence = "medium"
                    verb_form_guess = "participle_ed"
                    notes.append("be_plus_ed_possible_passive")
            elif prev_token in ENGLISH_SUBJECT_PRONOUNS or prev_token in COORDINATORS:
                pos_guess = "verb"
                verb_confidence = "high"
                verb_form_guess = "past"
                notes.append("subject_plus_past_verb")
            elif prev_token in {"have", "has", "had"}:
                pos_guess = "verb_participle"
                verb_confidence = "high"
                verb_form_guess = "participle_ed"
                notes.append("perfect_participle")
            else:
                if pos_guess == "unknown":
                    pos_guess = "verb"
                    verb_confidence = "medium"
                    verb_form_guess = "past"

        if token.endswith("s") and len(token) > 2 and not token.endswith("ss"):
            candidates.update({"verb", "noun"})
            notes.append("suffix_s")
            if prev_token in ENGLISH_SUBJECT_PRONOUNS - {"i", "you", "we", "they"}:
                pos_guess = "verb"
                verb_confidence = "high"
                verb_form_guess = "v3sg"
                notes.append("third_person_s_after_subject")
            elif prev_token in SUBJECT_DETERMINERS:
                pos_guess = "noun"
                notes.append("plural_noun_after_determiner")
            elif next_token in TO_BE_FORMS:
                pos_guess = "noun"
                notes.append("plural_subject_before_be")
            elif prev_token in MODAL_VERBS or prev_token == "to":
                pos_guess = "noun"
                notes.append("s_form_after_modal_or_to_unlikely_verb")
            elif pos_guess == "unknown":
                pos_guess = "noun"

        if token in COMMON_VERBS:
            candidates.add("verb")
            notes.append("in_common_verbs")
            if token in AMBIGUOUS_NOUN_VERB_BASES:
                candidates.add("noun")
                notes.append("noun_verb_ambiguous")
                if prev_token in SUBJECT_DETERMINERS:
                    pos_guess = "noun"
                    verb_confidence = "low"
                    notes.append("ambiguous_after_determiner_noun")
                elif next_token in TO_BE_FORMS:
                    pos_guess = "noun"
                    verb_confidence = "low"
                    notes.append("ambiguous_before_be_noun_subject")
                elif prev_token in MODAL_VERBS or prev_token == "to":
                    pos_guess = "verb"
                    verb_confidence = "high"
                    verb_form_guess = "base"
                    notes.append("ambiguous_after_modal_to_verb")
                elif prev_token in ENGLISH_SUBJECT_PRONOUNS:
                    pos_guess = "verb"
                    verb_confidence = "high"
                    if prev_token in {"he", "she", "it"} and token.endswith("s"):
                        verb_form_guess = "v3sg"
                    else:
                        verb_form_guess = "base"
                    notes.append("ambiguous_after_subject_verb")
                elif index == 0 and (next_token in SUBJECT_DETERMINERS or self._looks_noun_like(next_token)):
                    pos_guess = "verb"
                    verb_confidence = "medium"
                    verb_form_guess = "base"
                    notes.append("initial_command_like_verb")
                elif pos_guess == "unknown":
                    pos_guess = "noun"
                    notes.append("default_ambiguous_to_noun")
            else:
                if pos_guess == "unknown":
                    pos_guess = "verb"
                    verb_confidence = "high"
                    if token in COMMON_IRREGULAR_PAST:
                        verb_form_guess = "past"
                    elif token.endswith("s"):
                        verb_form_guess = "v3sg"
                    else:
                        verb_form_guess = "base"

        if token in PREPOSITIONS:
            candidates.add("preposition")
            if pos_guess == "unknown":
                pos_guess = "preposition"
            notes.append("preposition")

        if pos_guess == "unknown" and self._looks_likely_adjective(token, prev_token):
            candidates.add("adjective")
            pos_guess = "adjective"
            notes.append("adjective_shape_or_context")

        if pos_guess == "unknown":
            if self._looks_noun_like(token):
                candidates.add("noun")
                pos_guess = "noun"
                notes.append("default_noun_like")
            else:
                candidates.add("unknown")

        if pos_guess in {"verb", "auxiliary", "verb_participle"} and verb_confidence == "low":
            verb_confidence = "medium"

        if pos_guess in {"verb", "auxiliary"}:
            candidates.add("verb")

        if token in COMMON_IRREGULAR_PAST and pos_guess == "verb" and verb_form_guess is None:
            verb_form_guess = "past"
            notes.append("irregular_past")
        if token in COMMON_IRREGULAR_PARTICIPLES and prev_token in {"have", "has", "had"}:
            if pos_guess in {"verb", "verb_participle", "unknown", "noun"}:
                pos_guess = "verb_participle"
                verb_confidence = "high"
                verb_form_guess = "participle_ed"
                notes.append("irregular_perfect_participle")
                candidates.update({"verb_participle", "verb"})
        if token in COMMON_IRREGULAR_PARTICIPLES and prev_token in TO_BE_FORMS and token != "been":
            if pos_guess in {"unknown", "noun", "verb"}:
                pos_guess = "verb_participle"
                verb_confidence = "medium"
                verb_form_guess = "participle_ed"
                notes.append("irregular_be_participle")

        if pos_guess == "verb" and verb_form_guess is None:
            if token.endswith("s") and len(token) > 2 and not token.endswith("ss"):
                verb_form_guess = "v3sg"
            else:
                verb_form_guess = "base"
        if pos_guess == "verb_participle" and verb_form_guess is None:
            if token.endswith("ing"):
                verb_form_guess = "participle_ing"
            elif token.endswith("ed") or token in COMMON_IRREGULAR_PARTICIPLES:
                verb_form_guess = "participle_ed"

        if pos_guess == "noun" or "noun" in candidates:
            noun_countability_guess = guess_noun_countability(token)

        return TokenFeature(
            token=token,
            index=index,
            pos_guess=pos_guess,
            pos_candidates=sorted(candidates),
            verb_confidence=verb_confidence,
            verb_form_guess=verb_form_guess,
            noun_countability_guess=noun_countability_guess,
            notes=notes,
        )

    def _apply_external_pos_support(
        self, tokens: list[str], features: list[TokenFeature]
    ) -> None:
        if not self.external_pos_tagger or not tokens or not features:
            return
        try:
            external_tags = self.external_pos_tagger(tokens)
        except Exception:
            return
        if not isinstance(external_tags, list) or len(external_tags) != len(tokens):
            return

        for feature, raw_tag in zip(features, external_tags):
            normalized = self._normalize_external_pos(raw_tag)
            feature.external_pos = normalized
            if normalized is None:
                continue
            feature.pos_candidates = sorted(set(feature.pos_candidates) | {normalized})
            feature.notes.append("external_pos_support")

            # Keep heuristics as the pedagogical base; external POS only resolves low-confidence cases.
            if feature.pos_guess in {"unknown", "noun"} and normalized in {"adjective", "adverb"}:
                feature.pos_guess = normalized
                feature.notes.append("external_pos_refined_guess")
                continue
            if (
                feature.verb_confidence in {"low", "medium"}
                and feature.pos_guess in {"verb_participle", "verb", "noun"}
                and normalized in {"adjective", "noun", "adverb", "verb"}
            ):
                feature.pos_guess = normalized
                if normalized in {"verb"}:
                    feature.verb_confidence = "medium"
                else:
                    feature.verb_confidence = "low"
                feature.notes.append("external_pos_refined_guess")

    @staticmethod
    def _normalize_external_pos(tag: str | None) -> str | None:
        if not tag:
            return None
        t = str(tag).strip().lower()
        mapping = {
            "adj": "adjective",
            "adjective": "adjective",
            "jj": "adjective",
            "adv": "adverb",
            "adverb": "adverb",
            "rb": "adverb",
            "noun": "noun",
            "n": "noun",
            "nn": "noun",
            "verb": "verb",
            "v": "verb",
            "vb": "verb",
            "vbg": "verb_participle",
            "gerund": "verb_participle",
            "participle": "verb_participle",
            "pron": "pronoun",
            "pronoun": "pronoun",
            "det": "determiner",
            "determiner": "determiner",
            "prep": "preposition",
            "preposition": "preposition",
            "aux": "auxiliary",
            "auxiliary": "auxiliary",
        }
        return mapping.get(t)

    @staticmethod
    def _looks_noun_like(token: str | None) -> bool:
        if not token:
            return False
        if token in ENGLISH_SUBJECT_PRONOUNS | SUBJECT_DETERMINERS:
            return False
        if token in QUESTION_AUXILIARIES or token in MODAL_VERBS:
            return False
        if token in PREPOSITIONS or token in COORDINATORS:
            return False
        if token in COMMON_ADVERBS:
            return False
        if token.endswith("ly"):
            return False
        return token.isalpha()

    @staticmethod
    def _looks_direct_object_after_ing(token: str | None) -> bool:
        if not token:
            return False
        if token in PREPOSITIONS or token in COMMON_ADVERBS:
            return False
        if token in SUBJECT_DETERMINERS or token in ENGLISH_SUBJECT_PRONOUNS:
            return True
        return token.isalpha()

    @staticmethod
    def _looks_likely_adjective(token: str, prev_token: str | None) -> bool:
        if token in COMMON_ADJECTIVES:
            return True
        if prev_token in TO_BE_FORMS and token.isalpha() and not token.endswith(("ing", "ed", "s")):
            return True
        adjective_suffixes = ("ous", "ful", "able", "ible", "ive", "al", "ic", "ish", "less")
        return token.endswith(adjective_suffixes)

    @staticmethod
    def _looks_likely_ed_inflection(token: str) -> bool:
        if not (token.endswith("ed") and len(token) > 3):
            return False
        if token in {"red"}:
            return False
        stem_candidates = {
            token[:-2],          # worked -> work, asked -> ask
            f"{token[:-1]}",     # lived -> live
            f"{token[:-3]}y" if token.endswith("ied") and len(token) > 4 else "",
            token[:-3] if len(token) > 4 and token[-3] == token[-4] else "",  # stopped -> stop
        }
        stem_candidates = {s for s in stem_candidates if s}
        if token in LIKELY_ADJECTIVAL_ED:
            return True
        return any(stem in COMMON_VERBS for stem in stem_candidates)

    def _segment_clauses(
        self,
        tokens: list[str],
        token_features: list[TokenFeature],
        raw_text: str,
        raw_token_stream: list[RawTokenSpan],
    ) -> list[ClauseAnalysis]:
        if not tokens:
            return []

        break_starts: set[int] = {0}
        for idx in self._punctuation_clause_break_indices(raw_token_stream):
            if 0 < idx < len(tokens):
                break_starts.add(idx)
        for idx in self._linker_clause_break_indices(tokens):
            if 0 < idx < len(tokens):
                break_starts.add(idx)

        ordered_starts = sorted(break_starts)
        clauses: list[ClauseAnalysis] = []
        for i, start in enumerate(ordered_starts):
            end = (ordered_starts[i + 1] - 1) if i + 1 < len(ordered_starts) else (len(tokens) - 1)
            if end < start:
                continue
            clause_tokens = tokens[start : end + 1]
            clause_features = [
                replace(feature, index=local_idx)
                for local_idx, feature in enumerate(token_features[start : end + 1])
            ]
            main_verb_idx = self._find_clause_main_verb_index(clause_features)
            subject_idx = self._find_clause_subject_index(clause_tokens, clause_features, start, main_verb_idx)
            aux_chain = self._find_clause_aux_chain(clause_features, start, main_verb_idx)
            tense_guesses = self._detect_tense_guesses(clause_tokens, clause_features)
            linker_tokens = self._detect_clause_leading_linkers(clause_tokens)
            clauses.append(
                ClauseAnalysis(
                    start_idx=start,
                    end_idx=end,
                    clause_type=self._guess_clause_type(clause_tokens),
                    subject_idx=subject_idx,
                    main_verb_idx=(start + main_verb_idx) if main_verb_idx is not None else None,
                    aux_chain=aux_chain,
                    tense_guess=self._pick_primary_tense_guess(tense_guesses),
                    polarity=self._detect_polarity(clause_tokens),
                    linker_tokens=linker_tokens,
                    subject_phrase_span=self._guess_clause_subject_phrase_span(
                        clause_tokens, clause_features, start, main_verb_idx
                    ),
                )
            )
        return clauses

    def _punctuation_clause_break_indices(self, raw_token_stream: list[RawTokenSpan]) -> list[int]:
        breaks: list[int] = []
        for idx, item in enumerate(raw_token_stream):
            if item.kind != "punct" or item.text not in {",", ";", ":"}:
                continue
            for nxt in raw_token_stream[idx + 1 :]:
                if nxt.kind == "word" and nxt.word_index is not None:
                    breaks.append(nxt.word_index)
                    break
        return breaks

    def _linker_clause_break_indices(self, tokens: list[str]) -> list[int]:
        indices: list[int] = []
        single_linkers = {
            "if",
            "when",
            "because",
            "although",
            "though",
            "that",
            "who",
            "which",
            "whose",
            "whom",
            "despite",
            "unless",
            "whether",
            "while",
        }
        for i, token in enumerate(tokens):
            if token in single_linkers:
                indices.append(i)
        for seq in (["as", "long", "as"], ["provided", "that"], ["not", "only"]):
            for i in range(len(tokens) - len(seq) + 1):
                if tokens[i : i + len(seq)] == seq:
                    indices.append(i)
        return indices

    @staticmethod
    def _detect_clause_leading_linkers(clause_tokens: list[str]) -> list[str]:
        if not clause_tokens:
            return []
        if len(clause_tokens) >= 3 and clause_tokens[:3] == ["as", "long", "as"]:
            return ["as", "long", "as"]
        if len(clause_tokens) >= 2 and clause_tokens[:2] in (["provided", "that"], ["not", "only"]):
            return clause_tokens[:2]
        if clause_tokens[0] in {
            "if",
            "when",
            "because",
            "although",
            "though",
            "that",
            "who",
            "which",
            "whose",
            "whom",
            "despite",
            "unless",
            "whether",
            "while",
        }:
            return [clause_tokens[0]]
        return []

    def _guess_clause_type(self, clause_tokens: list[str]) -> str:
        if not clause_tokens:
            return "fragment"
        if len(clause_tokens) >= 3 and clause_tokens[:3] == ["as", "long", "as"]:
            return "subordinate"
        first = clause_tokens[0]
        if first == "if":
            return "if_clause"
        if first == "when":
            return "when_clause"
        if first in {"who", "which", "whose", "whom", "that"}:
            return "relative_clause"
        if first in {"because", "although", "though", "despite", "unless", "whether", "while"}:
            return "subordinate"
        return "main"

    @staticmethod
    def _find_clause_main_verb_index(clause_features: list[TokenFeature]) -> int | None:
        for feature in clause_features:
            if feature.pos_guess in {"verb", "verb_participle"}:
                return feature.index
        for feature in clause_features:
            if feature.pos_guess == "auxiliary":
                return feature.index
        return None

    def _find_clause_subject_index(
        self,
        clause_tokens: list[str],
        clause_features: list[TokenFeature],
        start_idx: int,
        main_verb_idx: int | None,
    ) -> int | None:
        if not clause_tokens:
            return None
        search_end_local = (
            len(clause_tokens)
            if main_verb_idx is None
            else max(1, (main_verb_idx - start_idx))
        )
        for local_idx in range(search_end_local):
            feature = clause_features[local_idx]
            token = clause_tokens[local_idx]
            if token in {"if", "when", "because", "although", "though", "that", "who", "which", "whose", "whom", "despite", "unless", "whether", "while"}:
                continue
            if feature.pos_guess in {"pronoun", "determiner", "noun"}:
                return start_idx + local_idx
        return None

    def _guess_clause_subject_phrase_span(
        self,
        clause_tokens: list[str],
        clause_features: list[TokenFeature],
        start_idx: int,
        main_verb_idx: int | None,
    ) -> tuple[int, int] | None:
        subject_idx = self._find_clause_subject_index(
            clause_tokens, clause_features, start_idx, main_verb_idx
        )
        if subject_idx is None:
            return None
        if main_verb_idx is None or main_verb_idx <= subject_idx:
            return (subject_idx, subject_idx)
        return (subject_idx, main_verb_idx - 1)

    @staticmethod
    def _find_clause_aux_chain(
        clause_features: list[TokenFeature], start_idx: int, main_verb_idx: int | None
    ) -> list[str]:
        if main_verb_idx is None:
            return []
        chain: list[str] = []
        for feature in clause_features:
            if feature.index >= main_verb_idx:
                break
            if feature.pos_guess == "auxiliary":
                chain.append(feature.token)
        return chain

    @staticmethod
    def _extract_clause_linkers(clauses: list[ClauseAnalysis]) -> list[str]:
        linkers: list[str] = []
        for clause in clauses:
            if not clause.linker_tokens:
                continue
            key = " ".join(clause.linker_tokens)
            if key not in linkers:
                linkers.append(key)
        return linkers

    def _extract_noun_phrases(
        self,
        tokens: list[str],
        token_features: list[TokenFeature],
        clauses: list[ClauseAnalysis],
    ) -> list[NounPhraseAnalysis]:
        if not tokens or not token_features:
            return []

        nps: list[NounPhraseAnalysis] = []
        seen_spans: set[tuple[int, int]] = set()

        role_overrides: dict[tuple[int, int], str] = {}
        subject_start_overrides: dict[int, str] = {}
        for clause in clauses:
            if clause.subject_phrase_span is not None:
                role_overrides[clause.subject_phrase_span] = "subject"
            if clause.subject_idx is not None:
                subject_start_overrides[clause.subject_idx] = "subject"
            if clause.main_verb_idx is not None and clause.main_verb_idx + 1 <= clause.end_idx:
                obj_span = self._guess_object_np_span(
                    tokens, token_features, clause.main_verb_idx + 1, clause.end_idx
                )
                if obj_span is not None:
                    role_overrides.setdefault(obj_span, "object")
            if (
                clause.main_verb_idx is not None
                and tokens[clause.main_verb_idx] in TO_BE_FORMS
                and clause.main_verb_idx + 1 <= clause.end_idx
            ):
                pred_span = self._guess_predicate_nominal_np_span(
                    tokens, token_features, clause.main_verb_idx + 1, clause.end_idx
                )
                if pred_span is not None:
                    role_overrides.setdefault(pred_span, "predicate_nominal")

        idx = 0
        while idx < len(tokens):
            span = self._guess_np_span_at(tokens, token_features, idx)
            if span is None:
                idx += 1
                continue
            start_idx, end_idx = span
            if (start_idx, end_idx) in seen_spans:
                idx = end_idx + 1
                continue
            seen_spans.add((start_idx, end_idx))
            head_idx = self._guess_np_head_index(tokens, token_features, start_idx, end_idx)
            if head_idx is None:
                idx = end_idx + 1
                continue
            head_feature = token_features[head_idx]
            determiner = tokens[start_idx] if tokens[start_idx] in SUBJECT_DETERMINERS else None
            quantifier = tokens[start_idx] if tokens[start_idx] in NP_QUANTIFIERS else None
            pattern = None
            if start_idx + 1 <= end_idx and tokens[start_idx : start_idx + 2] == ["lots", "of"]:
                quantifier = "lots_of"
                pattern = "lots_of"
                if start_idx + 2 <= end_idx and tokens[start_idx + 2] in {"the", "a", "an"}:
                    determiner = tokens[start_idx + 2]
                    pattern = "lots_of_det_np"
            if start_idx + 1 <= end_idx and tokens[start_idx : start_idx + 2] == ["plenty", "of"]:
                quantifier = "plenty_of"
                pattern = "plenty_of"
                if start_idx + 2 <= end_idx and tokens[start_idx + 2] in {"the", "a", "an"}:
                    determiner = tokens[start_idx + 2]
                    pattern = "plenty_of_det_np"
            if start_idx + 2 <= end_idx and tokens[start_idx : start_idx + 3] == ["a", "number", "of"]:
                quantifier = "a_number_of"
                pattern = "a_number_of"
                determiner = "a"
                if start_idx + 3 <= end_idx and tokens[start_idx + 3] in {"the", "a", "an"}:
                    determiner = tokens[start_idx + 3]
                    pattern = "a_number_of_det_np"
            if start_idx + 2 <= end_idx and tokens[start_idx : start_idx + 3] == ["a", "bit", "of"]:
                quantifier = "a_bit_of"
                pattern = "a_bit_of"
                determiner = "a"
                if start_idx + 3 <= end_idx and tokens[start_idx + 3] in {"the", "a", "an"}:
                    determiner = tokens[start_idx + 3]
                    pattern = "a_bit_of_det_np"
            if start_idx + 2 <= end_idx and tokens[start_idx : start_idx + 3] == ["a", "piece", "of"]:
                quantifier = "a_piece_of"
                pattern = "a_piece_of"
                determiner = "a"
                if start_idx + 3 <= end_idx and tokens[start_idx + 3] in {"the", "a", "an"}:
                    determiner = tokens[start_idx + 3]
                    pattern = "a_piece_of_det_np"
            if start_idx + 2 <= end_idx and tokens[start_idx : start_idx + 3] == ["a", "pair", "of"]:
                quantifier = "a_pair_of"
                pattern = "a_pair_of"
                determiner = "a"
                if start_idx + 3 <= end_idx and tokens[start_idx + 3] in {"the", "a", "an"}:
                    determiner = tokens[start_idx + 3]
                    pattern = "a_pair_of_det_np"
            if start_idx + 2 <= end_idx and tokens[start_idx : start_idx + 3] == ["the", "number", "of"]:
                quantifier = "the_number_of"
                pattern = "the_number_of"
                determiner = "the"
                if start_idx + 3 <= end_idx and tokens[start_idx + 3] in {"the", "a", "an"}:
                    determiner = tokens[start_idx + 3]
                    pattern = "the_number_of_det_np"
            if start_idx + 1 <= end_idx and tokens[start_idx] == "a" and tokens[start_idx + 1] in {"few", "little"}:
                quantifier = tokens[start_idx + 1]
                pattern = f"a_{tokens[start_idx + 1]}"
                determiner = "a"
            if quantifier == "such" and start_idx + 1 <= end_idx and tokens[start_idx + 1] in {"a", "an", "the"}:
                determiner = tokens[start_idx + 1]
                pattern = "such_det_np"
            if start_idx + 2 <= end_idx and tokens[start_idx : start_idx + 3] == ["a", "lot", "of"]:
                quantifier = "a_lot_of"
                pattern = "a_lot_of"
                determiner = "a"
                if start_idx + 3 <= end_idx and tokens[start_idx + 3] in {"the", "a", "an"}:
                    determiner = tokens[start_idx + 3]
                    pattern = "a_lot_of_det_np"
            countability = head_feature.noun_countability_guess
            role = role_overrides.get((start_idx, end_idx), subject_start_overrides.get(start_idx, "other"))
            is_generic_candidate = (
                quantifier is None and determiner is None and countability in {"countable_plural", "uncountable"}
            ) or (
                quantifier is None and determiner == "the" and countability in {"countable_plural", "uncountable"}
            )
            nps.append(
                NounPhraseAnalysis(
                    start_idx=start_idx,
                    end_idx=end_idx,
                    determiner=determiner,
                    quantifier=quantifier,
                    pattern=pattern,
                    head_idx=head_idx,
                    head_token=tokens[head_idx],
                    head_pos_guess=head_feature.pos_guess,
                    countability_guess=countability,
                    role_guess=role,
                    is_generic_candidate=is_generic_candidate,
                )
            )
            idx = end_idx + 1
        return nps

    def _guess_np_span_at(
        self, tokens: list[str], token_features: list[TokenFeature], idx: int
    ) -> tuple[int, int] | None:
        token = tokens[idx]
        feature = token_features[idx]
        if idx + 1 < len(tokens) and tokens[idx] == "a" and tokens[idx + 1] in {"few", "little"}:
            end = idx + 1
            j = idx + 2
            while j < len(tokens):
                pos = token_features[j].pos_guess
                if pos in {"adjective", "adverb"}:
                    end = j
                    j += 1
                    continue
                if pos == "noun":
                    end = j
                    return (idx, end)
                break
            return None
        if idx + 1 < len(tokens) and tokens[idx : idx + 2] == ["plenty", "of"]:
            end = idx + 1
            j = idx + 2
            if j < len(tokens) and tokens[j] in {"the", "a", "an"}:
                end = j
                j += 1
            while j < len(tokens):
                pos = token_features[j].pos_guess
                if pos in {"adjective", "adverb"}:
                    end = j
                    j += 1
                    continue
                if pos == "noun":
                    end = j
                    return (idx, end)
                break
            return None
        if idx + 2 < len(tokens) and tokens[idx : idx + 3] == ["a", "number", "of"]:
            end = idx + 2
            j = idx + 3
            if j < len(tokens) and tokens[j] in {"the", "a", "an"}:
                end = j
                j += 1
            while j < len(tokens):
                pos = token_features[j].pos_guess
                if pos in {"adjective", "adverb"}:
                    end = j
                    j += 1
                    continue
                if pos == "noun":
                    end = j
                    return (idx, end)
                break
            return None
        if idx + 2 < len(tokens) and tokens[idx : idx + 3] == ["a", "bit", "of"]:
            end = idx + 2
            j = idx + 3
            if j < len(tokens) and tokens[j] in {"the", "a", "an"}:
                end = j
                j += 1
            while j < len(tokens):
                pos = token_features[j].pos_guess
                if pos in {"adjective", "adverb"}:
                    end = j
                    j += 1
                    continue
                if pos == "noun":
                    end = j
                    return (idx, end)
                break
            return None
        if idx + 2 < len(tokens) and tokens[idx : idx + 3] in (
            ["a", "piece", "of"],
            ["a", "pair", "of"],
            ["the", "number", "of"],
        ):
            end = idx + 2
            j = idx + 3
            if j < len(tokens) and tokens[j] in {"the", "a", "an"}:
                end = j
                j += 1
            while j < len(tokens):
                pos = token_features[j].pos_guess
                if pos in {"adjective", "adverb"}:
                    end = j
                    j += 1
                    continue
                if pos == "noun":
                    end = j
                    return (idx, end)
                break
            return None
        if idx + 1 < len(tokens) and tokens[idx : idx + 2] == ["lots", "of"]:
            end = idx + 1
            j = idx + 2
            if j < len(tokens) and tokens[j] in {"the", "a", "an"}:
                end = j
                j += 1
            while j < len(tokens):
                pos = token_features[j].pos_guess
                if pos in {"adjective", "adverb"}:
                    end = j
                    j += 1
                    continue
                if pos == "noun":
                    end = j
                    return (idx, end)
                break
            return None
        if idx + 2 < len(tokens) and tokens[idx : idx + 3] == ["a", "lot", "of"]:
            end = idx + 2
            j = idx + 3
            if j < len(tokens) and tokens[j] in {"the", "a", "an"}:
                end = j
                j += 1
            while j < len(tokens):
                pos = token_features[j].pos_guess
                if pos in {"adjective", "adverb"}:
                    end = j
                    j += 1
                    continue
                if pos == "noun":
                    end = j
                    return (idx, end)
                break
            return None
        if token in SUBJECT_DETERMINERS:
            end = idx
            j = idx + 1
            while j < len(tokens):
                pos = token_features[j].pos_guess
                if pos in {"adjective", "adverb"}:
                    end = j
                    j += 1
                    continue
                if pos == "noun":
                    end = j
                    return (idx, end)
                break
            return None
        if token in NP_QUANTIFIERS:
            end = idx
            j = idx + 1
            # Handle "such a/an + adj + noun" and "a lot of + noun" elsewhere; this is a minimal NP extractor.
            if j < len(tokens) and tokens[j] in {"a", "an", "the"}:
                end = j
                j += 1
            while j < len(tokens):
                pos = token_features[j].pos_guess
                if pos in {"adjective", "adverb"}:
                    end = j
                    j += 1
                    continue
                if pos == "noun":
                    end = j
                    return (idx, end)
                break
            return None
        if feature.pos_guess == "noun":
            return (idx, idx)
        return None

    @staticmethod
    def _guess_np_head_index(
        tokens: list[str], token_features: list[TokenFeature], start_idx: int, end_idx: int
    ) -> int | None:
        for i in range(end_idx, start_idx - 1, -1):
            if token_features[i].pos_guess == "noun":
                return i
        return None

    def _guess_object_np_span(
        self,
        tokens: list[str],
        token_features: list[TokenFeature],
        start_idx: int,
        end_limit: int,
    ) -> tuple[int, int] | None:
        i = start_idx
        while i <= end_limit and tokens[i] in {"not"}:
            i += 1
        if i > end_limit:
            return None
        return self._guess_np_span_at(tokens, token_features, i)

    def _guess_predicate_nominal_np_span(
        self,
        tokens: list[str],
        token_features: list[TokenFeature],
        start_idx: int,
        end_limit: int,
    ) -> tuple[int, int] | None:
        i = start_idx
        while i <= end_limit and token_features[i].pos_guess == "adverb":
            i += 1
        if i > end_limit:
            return None
        span = self._guess_np_span_at(tokens, token_features, i)
        return span

    def _detect_tense_guesses(
        self, tokens: list[str], token_features: list[TokenFeature]
    ) -> list[str]:
        if not tokens or not token_features:
            return []

        guesses: list[str] = []
        by_idx = {f.index: f for f in token_features}

        def add(name: str) -> None:
            if name not in guesses:
                guesses.append(name)

        for i, token in enumerate(tokens):
            nxt = by_idx.get(i + 1)
            nxt2 = by_idx.get(i + 2)
            nxt3 = by_idx.get(i + 3)
            is_be_going_to_future = (
                token in TO_BE_FORMS
                and nxt is not None
                and nxt.token == "going"
                and nxt2 is not None
                and nxt2.token == "to"
                and nxt3 is not None
                and nxt3.pos_guess in {"verb", "auxiliary"}
            )

            if (
                token in {"am", "is", "are"}
                and nxt
                and nxt.verb_form_guess == "participle_ing"
                and not is_be_going_to_future
            ):
                add("present_continuous")
            if (
                token in {"was", "were"}
                and nxt
                and nxt.verb_form_guess == "participle_ing"
                and not is_be_going_to_future
            ):
                add("past_continuous")
            if token in {"have", "has"} and nxt and nxt.verb_form_guess == "participle_ed":
                add("present_perfect")
            if token == "will":
                if nxt and nxt.pos_guess in {"verb", "auxiliary"} and nxt.verb_form_guess in {"base", None}:
                    add("future_will")
            if is_be_going_to_future:
                add("future_going_to")
            if token == "did":
                if nxt and nxt.pos_guess in {"verb", "auxiliary"}:
                    add("past_simple")

        if not any(
            tense in guesses
            for tense in {
                "present_continuous",
                "past_continuous",
                "present_perfect",
                "future_will",
                "future_going_to",
            }
        ):
            if any(
                f.pos_guess == "verb" and f.verb_form_guess == "past"
                for f in token_features
            ):
                add("past_simple")
            elif any(
                f.pos_guess == "verb" and f.verb_form_guess in {"base", "v3sg"}
                for f in token_features
            ):
                add("present_simple")

        return guesses

    def _pick_primary_tense_guess(self, guesses: list[str]) -> str | None:
        if not guesses:
            return None
        priority = [
            "future_going_to",
            "future_will",
            "present_perfect",
            "past_continuous",
            "present_continuous",
            "past_simple",
            "present_simple",
        ]
        for tense in priority:
            if tense in guesses:
                return tense
        return guesses[0]
