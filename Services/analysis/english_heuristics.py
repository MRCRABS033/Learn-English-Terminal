"""Shared heuristic constants and lightweight morphology helpers.

This module is intentionally dependency-light so both the analyzer and grammar rules
can import from it without creating circular imports.
"""

from __future__ import annotations


BASE_PREPOSITIONS = {
    "in",
    "on",
    "at",
    "for",
    "with",
    "from",
    "to",
    "of",
    "by",
    "about",
    "after",
    "before",
    "under",
    "over",
    "into",
    "through",
}

BASE_COMMON_ADVERBS = {
    "now",
    "here",
    "there",
    "today",
    "yesterday",
    "tomorrow",
    "always",
    "never",
    "often",
    "usually",
    "sometimes",
    "really",
    "very",
    "well",
}

BASE_COMMON_ADJECTIVES = {
    "important",
    "tall",
    "small",
    "big",
    "good",
    "bad",
    "happy",
    "sad",
    "ready",
    "late",
    "early",
    "different",
    "possible",
    "necessary",
}

LIKELY_ADJECTIVAL_ING_FORMS = {
    "interesting",
    "boring",
    "exciting",
    "amazing",
    "confusing",
    "surprising",
}

LIKELY_ADJECTIVAL_ED_FORMS = {
    "interested",
    "bored",
    "excited",
    "amazed",
    "confused",
    "surprised",
    "tired",
    "worried",
}

# Minimal lexical layer for article/countability heuristics (high-precision starter set).
UNCOUNTABLE_NOUNS = {
    "information",
    "advice",
    "furniture",
    "music",
    "homework",
    "work",
    "money",
    "water",
    "news",
    "equipment",
    "luggage",
    "bread",
}

COUNTABLE_COMMON_NOUNS = {
    "teacher",
    "student",
    "book",
    "car",
    "house",
    "dog",
    "cat",
    "idea",
    "problem",
    "question",
    "friend",
    "plan",
    "job",
}


def is_ing_form(token: str) -> bool:
    return len(token) > 4 and token.endswith("ing")


def is_ed_form(token: str) -> bool:
    return len(token) > 3 and token.endswith("ed")


def guess_noun_countability(token: str) -> str | None:
    t = (token or "").strip().lower()
    if not t:
        return None
    if t in UNCOUNTABLE_NOUNS:
        return "uncountable"
    if t in COUNTABLE_COMMON_NOUNS:
        return "countable"
    if t.endswith("s") and not t.endswith("ss"):
        return "countable_plural"
    if t.isalpha():
        return "countable_singular_or_unknown"
    return None
