from dataclasses import dataclass

from Services.analysis.english_heuristics import (
    BASE_COMMON_ADJECTIVES,
    BASE_COMMON_ADVERBS,
    BASE_PREPOSITIONS,
    guess_noun_countability,
    is_ed_form,
    is_ing_form,
)
from Services.analysis.sentence_analyzer import (
    BASE_AUXILIARIES,
    ENGLISH_SUBJECT_PRONOUNS,
    MODAL_VERBS,
    QUESTION_AUXILIARIES,
    SUBJECT_DETERMINERS,
    TO_BE_FORMS,
    WH_QUESTION_WORDS,
    SentenceAnalysis,
)
from Services.validation.validation_result import ValidationIssue


NEGATIVE_TOKENS = {"not", "don't", "doesn't", "didn't", "won't", "can't"}
COMMON_PREPOSITIONS = {
    *BASE_PREPOSITIONS,
    "upon",
}
COMMON_ADVERBS = {
    *BASE_COMMON_ADVERBS,
    "already",
    "still",
    "just",
    "also",
    "quickly",
    "slowly",
}
COMMON_ADJECTIVES = {
    *BASE_COMMON_ADJECTIVES,
    "new",
    "old",
    "beautiful",
    "nice",
    "interesting",
    "boring",
    "easy",
    "difficult",
    "red",
    "blue",
    "green",
    "short",
}
COMMON_ED_PREDICATE_ADJECTIVES = {
    "interested",
    "bored",
    "tired",
    "excited",
    "worried",
    "married",
    "surprised",
    "confused",
}
PAST_TIME_MARKERS = {"yesterday", "ago", "last"}
COMMON_IRREGULAR_PAST = {
    "went",
    "ate",
    "saw",
    "made",
    "took",
    "came",
    "wrote",
    "read",
    "ran",
    "did",
    "had",
    "was",
    "were",
    "bought",
    "brought",
    "taught",
    "thought",
    "spoke",
    "learned",
    "learnt",
}
COMMON_IRREGULAR_PARTICIPLES = {
    "been",
    "gone",
    "done",
    "seen",
    "eaten",
    "made",
    "taken",
    "come",
    "written",
    "read",
    "run",
    "bought",
    "brought",
    "taught",
    "thought",
    "spoken",
    "known",
    "given",
    "gotten",
    "got",
}
COMMON_BASE_VERBS = {
    "be",
    "go",
    "run",
    "eat",
    "study",
    "work",
    "like",
    "love",
    "want",
    "need",
    "live",
    "learn",
    "speak",
    "read",
    "write",
    "watch",
    "visit",
    "depend",
    "play",
    "swim",
    "walk",
    "talk",
    "come",
    "make",
    "take",
    "see",
    "do",
    "have",
}
SINGULAR_THIRD_SUBJECTS = {"he", "she", "it"}
NON_THIRD_SUBJECTS = {"i", "you", "we", "they"}
FUTURE_TIME_MARKERS = {"tomorrow", "tonight", "next", "soon", "later"}
COUNTABLE_HINT_NOUNS = {
    "book",
    "books",
    "apple",
    "apples",
    "car",
    "cars",
    "student",
    "students",
    "idea",
    "ideas",
    "question",
    "questions",
}
UNCOUNTABLE_HINT_NOUNS = {
    "water",
    "money",
    "information",
    "advice",
    "homework",
    "furniture",
    "music",
    "work",
    "time",
}
REPORTING_VERBS = {"say", "says", "said", "tell", "tells", "told", "ask", "asks", "asked"}
GERUND_VERBS = {"enjoy", "avoid", "mind", "finish", "suggest"}
TO_INFINITIVE_VERBS = {"want", "need", "decide", "hope", "plan", "learn"}
STATIVE_VERBS = {
    "know",
    "believe",
    "understand",
    "love",
    "like",
    "hate",
    "want",
    "need",
    "remember",
    "mean",
    "belong",
    "seem",
}
ASPECT_SENSITIVE_VERBS = {
    "have",   # stative ("have a car") vs dynamic ("have lunch")
    "think",  # opinion vs process
    "see",    # perceive vs meet
}
PHRASAL_BASIC = {
    "get": {"up"},
    "turn": {"on", "off"},
    "find": {"out"},
}
PHRASAL_ADVANCED = {
    "carry": {"out"},
    "come": {"up"},
    "put": {"up"},
}
COMPARATIVE_MARKERS = {"than", "as"}
NEGATIVE_INVERSION_STARTERS = {"never", "rarely", "seldom", "hardly", "scarcely", "no sooner"}
LINKING_MARKERS = {"however", "although", "despite", "therefore", "whereas", "while", "moreover"}
NOUN_CLAUSE_TRIGGERS = {
    "think",
    "know",
    "wonder",
    "ask",
    "tell",
    "say",
    "explain",
    "the",
    "fact",
    "whether",
    "if",
}
COMMON_NOUNS_FOR_RELATIVES = {
    "man",
    "woman",
    "person",
    "people",
    "place",
    "city",
    "thing",
    "book",
    "car",
    "house",
    "student",
    "teacher",
}
TRANSITIVE_BASES_FOR_PASSIVE = {"make", "build", "do", "write", "carry", "find", "see"}


def _is_word(token: str) -> bool:
    return token.isalpha()


def _is_ing(token: str) -> bool:
    return is_ing_form(token)


def _is_ed(token: str) -> bool:
    return is_ed_form(token)


def _looks_like_participle(token: str) -> bool:
    return _is_ed(token) or token in COMMON_IRREGULAR_PARTICIPLES


def _looks_like_past(token: str) -> bool:
    return _is_ed(token) or token in COMMON_IRREGULAR_PAST


def _looks_like_base_verb(token: str) -> bool:
    if not _is_word(token):
        return False
    if token in TO_BE_FORMS or token in MODAL_VERBS or token in BASE_AUXILIARIES:
        return False
    if token in {"has", "had", "going"}:
        return False
    if _is_ing(token) or _is_ed(token):
        return False
    if token in COMMON_BASE_VERBS:
        return True
    if token.endswith("s") and token not in {"is"}:
        return False
    return True


def _looks_like_clear_base_verb(token: str) -> bool:
    if token in COMMON_BASE_VERBS:
        return True
    if not _is_word(token):
        return False
    if token in COMMON_PREPOSITIONS or token in SUBJECT_DETERMINERS:
        return False
    if token in COMMON_ADJECTIVES or token in COMMON_ED_PREDICATE_ADJECTIVES:
        return False
    if token in COMMON_IRREGULAR_PAST or token in COMMON_IRREGULAR_PARTICIPLES:
        return False
    if token.endswith(("s", "ed", "ing")):
        return False
    return False


def _find_next_token(tokens: list[str], start_idx: int, skip: set[str] | None = None) -> tuple[int | None, str | None]:
    skip = skip or set()
    for idx in range(start_idx, len(tokens)):
        if tokens[idx] in skip:
            continue
        return idx, tokens[idx]
    return None, None


def _find_verb_after_aux(tokens: list[str], aux_idx: int) -> tuple[int | None, str | None]:
    idx = aux_idx + 1
    while idx < len(tokens) and tokens[idx] in NEGATIVE_TOKENS:
        idx += 1

    if idx < len(tokens) and tokens[idx] in ENGLISH_SUBJECT_PRONOUNS:
        idx += 1
    elif idx + 1 < len(tokens) and tokens[idx] in SUBJECT_DETERMINERS:
        # Basic noun phrase subject in questions (e.g., "Does my brother ...")
        idx += 2

    while idx < len(tokens) and tokens[idx] in NEGATIVE_TOKENS:
        idx += 1

    if idx < len(tokens):
        return idx, tokens[idx]
    return None, None


def _iter_clauses(analysis: SentenceAnalysis):
    return getattr(analysis, "clauses", []) or []


def _clause_tokens(analysis: SentenceAnalysis, clause) -> list[str]:
    return analysis.tokens[clause.start_idx : clause.end_idx + 1]


def _has_punctuation_after_word_index(
    analysis: SentenceAnalysis, word_index: int, punct: str
) -> bool:
    stream = getattr(analysis, "raw_token_stream", None) or []
    seen_word = False
    for item in stream:
        if item.kind == "word" and item.word_index == word_index:
            seen_word = True
            continue
        if not seen_word:
            continue
        if item.kind == "punct":
            return item.text == punct
        if item.kind == "word":
            return False
    return False


def _has_punctuation_before_word_index(
    analysis: SentenceAnalysis, word_index: int, punct: str
) -> bool:
    stream = getattr(analysis, "raw_token_stream", None) or []
    prev_kind = None
    prev_text = None
    for item in stream:
        if item.kind == "word" and item.word_index == word_index:
            return prev_kind == "punct" and prev_text == punct
        prev_kind = item.kind
        prev_text = item.text
    return False


def _relative_clause_starts_after_np(analysis: SentenceAnalysis, np) -> bool:
    clauses = _iter_clauses(analysis)
    start = np.end_idx + 1
    for clause in clauses:
        if clause.start_idx == start and clause.clause_type == "relative_clause":
            return True
    return False


def _noun_phrase_starting_at(analysis: SentenceAnalysis, start_idx: int):
    for np in getattr(analysis, "noun_phrases", []) or []:
        if np.start_idx == start_idx:
            return np
    return None


def _feature_at(analysis: SentenceAnalysis, idx: int):
    if idx < 0:
        return None
    features = getattr(analysis, "token_features", None)
    if not features or idx >= len(features):
        return None
    return features[idx]


def _verb_form_at(analysis: SentenceAnalysis, idx: int) -> str | None:
    feature = _feature_at(analysis, idx)
    return getattr(feature, "verb_form_guess", None) if feature is not None else None


def _pos_at(analysis: SentenceAnalysis, idx: int) -> str | None:
    feature = _feature_at(analysis, idx)
    return getattr(feature, "pos_guess", None) if feature is not None else None


def _has_wh_aux_opening(tokens: list[str]) -> bool:
    return len(tokens) >= 2 and tokens[0] in WH_QUESTION_WORDS and tokens[1] in QUESTION_AUXILIARIES


def _expected_indefinite_article(next_word: str) -> str:
    word = next_word.lower()

    silent_h_prefixes = ("hour", "honest", "honor", "heir", "herb")
    consonant_sound_prefixes = (
        "uni",
        "use",
        "user",
        "usual",
        "ufo",
        "euro",
        "ewe",
        "one",
        "once",
    )

    if word.startswith(silent_h_prefixes):
        return "an"
    if word.startswith(consonant_sound_prefixes) or word.startswith(("university", "unicorn")):
        return "a"
    if word[:1] in {"a", "e", "i", "o", "u"}:
        return "an"
    return "a"


def _is_simple_subject_start(token: str) -> bool:
    return token in ENGLISH_SUBJECT_PRONOUNS or token in SUBJECT_DETERMINERS or _is_word(token)


def _is_plural_like_noun(token: str) -> bool:
    return token.endswith("s") and not token.endswith("ss")


def _is_likely_noun(token: str) -> bool:
    if not _is_word(token):
        return False
    if token in ENGLISH_SUBJECT_PRONOUNS | SUBJECT_DETERMINERS | QUESTION_AUXILIARIES | MODAL_VERBS | TO_BE_FORMS:
        return False
    if token in COMMON_PREPOSITIONS:
        return False
    if token in COMMON_ADVERBS:
        return False
    if _is_ing(token):
        return True
    if token in COMMON_ADJECTIVES or token in COMMON_ED_PREDICATE_ADJECTIVES:
        return False
    if token in COMMON_BASE_VERBS or token in COMMON_IRREGULAR_PAST or token in COMMON_IRREGULAR_PARTICIPLES:
        return False
    return True


def _find_sequence(tokens: list[str], seq: list[str]) -> int | None:
    if not seq or len(tokens) < len(seq):
        return None
    for i in range(len(tokens) - len(seq) + 1):
        if tokens[i : i + len(seq)] == seq:
            return i
    return None


def _has_past_time_marker(tokens: list[str]) -> bool:
    return any(token in PAST_TIME_MARKERS for token in tokens)


def _has_future_time_marker(tokens: list[str]) -> bool:
    return any(token in FUTURE_TIME_MARKERS for token in tokens)


def _has_perfect_marker(tokens: list[str]) -> bool:
    return any(token in {"ever", "never", "already", "yet", "just"} for token in tokens)


def _is_wh_word(token: str) -> bool:
    return token in WH_QUESTION_WORDS


def _is_likely_inflected_s_form(token: str) -> bool:
    return token.endswith("s") and not token.endswith("ss")


def _normalize_simple_verb_lemma(token: str) -> str:
    if token in {"came"}:
        return "come"
    if token in {"put", "puts", "putting"}:
        return "put"
    if token.endswith("ies") and len(token) > 4:
        return token[:-3] + "y"
    if token.endswith("ied") and len(token) > 4:
        return token[:-3] + "y"
    if token.endswith("ing") and len(token) > 5:
        stem = token[:-3]
        if len(stem) >= 2 and stem[-1] == stem[-2]:
            stem = stem[:-1]
        return stem
    if token.endswith("ed") and len(token) > 4:
        stem = token[:-2]
        if stem.endswith("i"):
            return stem[:-1] + "y"
        if len(stem) >= 2 and stem[-1] == stem[-2]:
            stem = stem[:-1]
        return stem
    if token.endswith("s") and len(token) > 3 and not token.endswith("ss"):
        return token[:-1]
    return token


def _classify_ing_usage(tokens: list[str], idx: int) -> str:
    """Heuristica simple para distinguir uso de token en -ing.

    Returns: "progressive_verb" | "gerund" | "adjective" | "unknown"
    """
    if idx < 0 or idx >= len(tokens):
        return "unknown"
    token = tokens[idx]
    if not _is_ing(token):
        return "unknown"

    prev = tokens[idx - 1] if idx > 0 else None
    next_token = tokens[idx + 1] if idx + 1 < len(tokens) else None

    if prev in {"am", "is", "are", "was", "were", "be", "been", "being"}:
        if token in COMMON_ADJECTIVES:
            return "adjective"
        if prev in {"be", "been", "being"} and next_token and _is_likely_noun(next_token):
            return "adjective"
        return "progressive_verb"

    if prev in COMMON_PREPOSITIONS | {"to"}:
        # "to" can be infinitive marker; if preceded by be-going-to or modal contexts, keep unknown.
        if prev == "to":
            prev2 = tokens[idx - 2] if idx > 1 else None
            if prev2 in {"going", "want", "need", "decide", "hope", "plan", "learn"}:
                return "unknown"
        return "gerund"

    if prev in GERUND_VERBS:
        return "gerund"

    if prev in SUBJECT_DETERMINERS | {"very", "so", "too", "more", "most"}:
        return "adjective"

    if next_token and _is_likely_noun(next_token):
        return "adjective"

    # Sentence-initial gerund subject: "Working at night is hard."
    if idx == 0 and next_token and next_token in COMMON_PREPOSITIONS | SUBJECT_DETERMINERS:
        return "gerund"

    return "unknown"


def _is_likely_ing_adjective(tokens: list[str], idx: int) -> bool:
    return _classify_ing_usage(tokens, idx) == "adjective"


def _is_likely_gerund(tokens: list[str], idx: int) -> bool:
    return _classify_ing_usage(tokens, idx) == "gerund"


@dataclass
class GrammarRule:
    rule_id: str
    severity: str
    description: str

    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        raise NotImplementedError


__all__ = [name for name in globals() if not name.startswith("__")]
