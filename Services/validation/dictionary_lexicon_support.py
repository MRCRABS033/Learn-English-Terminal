from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import sqlite3
from typing import Iterable


FUNCTION_WORDS = {
    "a",
    "an",
    "the",
    "i",
    "you",
    "he",
    "she",
    "it",
    "we",
    "they",
    "am",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "to",
    "of",
    "in",
    "on",
    "at",
    "for",
    "with",
    "from",
    "by",
    "and",
    "or",
    "but",
    "if",
    "that",
    "this",
    "these",
    "those",
    "my",
    "your",
    "his",
    "her",
    "its",
    "our",
    "their",
    "do",
    "does",
    "did",
    "have",
    "has",
    "had",
    "can",
    "could",
    "will",
    "would",
    "should",
    "must",
    "may",
    "might",
    "not",
    "today",
    "yesterday",
    "tomorrow",
    "tonight",
    "now",
    "then",
    "here",
    "there",
    "very",
    "really",
    "already",
    "still",
    "just",
    "always",
    "usually",
    "often",
    "sometimes",
    "never",
}


@dataclass
class DictionaryWordRecord:
    word: str
    normalized: str
    pos_classes: set[str] = field(default_factory=set)
    translations: set[str] = field(default_factory=set)


@dataclass
class DictionaryLexiconSnapshot:
    words: dict[str, DictionaryWordRecord] = field(default_factory=dict)
    nouns: set[str] = field(default_factory=set)
    adjectives: set[str] = field(default_factory=set)
    adverbs: set[str] = field(default_factory=set)
    verbs_base: set[str] = field(default_factory=set)
    prepositions: set[str] = field(default_factory=set)
    pronouns: set[str] = field(default_factory=set)
    determiners: set[str] = field(default_factory=set)
    conjunctions: set[str] = field(default_factory=set)
    auxiliaries: set[str] = field(default_factory=set)
    abbreviations: set[str] = field(default_factory=set)
    phrasal_verbs: dict[str, set[str]] = field(default_factory=dict)

    @property
    def loaded(self) -> bool:
        return bool(self.words)


class DictionaryLexiconSupport:
    def __init__(self, db_path: str = "app.db") -> None:
        self.db_path = db_path
        self._snapshot = DictionaryLexiconSnapshot()
        self._loaded = False

    @property
    def snapshot(self) -> DictionaryLexiconSnapshot:
        return self._snapshot

    def ensure_loaded(self) -> DictionaryLexiconSnapshot:
        if self._loaded:
            return self._snapshot

        self._snapshot = self._load_snapshot()
        self._loaded = True
        return self._snapshot

    def lookup(self, token: str) -> DictionaryWordRecord | None:
        snapshot = self.ensure_loaded()
        return snapshot.words.get((token or "").strip().lower())

    def enrich_rule_engine_lexicons(self) -> None:
        snapshot = self.ensure_loaded()
        if not snapshot.loaded:
            return

        # Import lazily to avoid circular imports and keep RuleEngine usable without DB.
        from Services.analysis import sentence_analyzer as analyzer_mod
        from Services.grammar.english_rules import shared as shared_mod

        analyzer_mod.COMMON_VERBS.update(snapshot.verbs_base)
        analyzer_mod.COMMON_VERBS.update(snapshot.auxiliaries)

        shared_mod.COMMON_BASE_VERBS.update(snapshot.verbs_base)
        shared_mod.COMMON_ADJECTIVES.update(snapshot.adjectives)
        shared_mod.COMMON_PREPOSITIONS.update(snapshot.prepositions)
        shared_mod.COMMON_NOUNS_FOR_RELATIVES.update(
            {w for w in snapshot.nouns if " " not in w and len(w) > 1}
        )
        shared_mod.TRANSITIVE_BASES_FOR_PASSIVE.update(snapshot.verbs_base)
        shared_mod.REPORTING_VERBS.update(
            {w for w in snapshot.verbs_base if w in {"say", "tell", "ask", "explain", "report"}}
        )
        shared_mod.GERUND_VERBS.update(
            {w for w in snapshot.verbs_base if w in {"enjoy", "avoid", "mind", "finish", "suggest"}}
        )
        shared_mod.TO_INFINITIVE_VERBS.update(
            {w for w in snapshot.verbs_base if w in {"want", "need", "decide", "hope", "plan", "learn"}}
        )

        for base, particles in snapshot.phrasal_verbs.items():
            if base in shared_mod.PHRASAL_ADVANCED:
                shared_mod.PHRASAL_ADVANCED[base].update(particles)
                continue
            if base in shared_mod.PHRASAL_BASIC:
                shared_mod.PHRASAL_BASIC[base].update(particles)
                continue
            # Defaults to "basic" bucket to improve detection without changing severity.
            shared_mod.PHRASAL_BASIC[base] = set(particles)

    def _load_snapshot(self) -> DictionaryLexiconSnapshot:
        snapshot = DictionaryLexiconSnapshot()
        db_file = Path(self.db_path)
        if not db_file.exists():
            return snapshot

        try:
            con = sqlite3.connect(str(db_file))
        except sqlite3.Error:
            return snapshot

        try:
            cur = con.cursor()
            cur.execute(
                """
                SELECT word, word_normalized, word_class_id, traduction
                FROM word
                WHERE language_id = 'en'
                """
            )
        except sqlite3.Error:
            con.close()
            return snapshot

        for raw_word, raw_norm, word_class_id, traduction in cur.fetchall():
            word = (raw_word or "").strip()
            normalized = (raw_norm or "").strip().lower()
            if not normalized:
                continue

            rec = snapshot.words.setdefault(
                normalized,
                DictionaryWordRecord(word=word, normalized=normalized),
            )
            if word_class_id:
                rec.pos_classes.add(word_class_id)
            if traduction:
                rec.translations.add(str(traduction).strip())

            self._add_pos_to_snapshot(snapshot, normalized, word_class_id or "")

        con.close()
        return snapshot

    def _add_pos_to_snapshot(self, snapshot: DictionaryLexiconSnapshot, normalized: str, word_class_id: str) -> None:
        pos = (word_class_id or "").strip().lower()
        if pos == "noun":
            snapshot.nouns.add(normalized)
            return
        if pos == "adjective":
            snapshot.adjectives.add(normalized)
            return
        if pos == "adverb":
            snapshot.adverbs.add(normalized)
            return
        if pos == "preposition":
            snapshot.prepositions.add(normalized)
            return
        if pos == "pronoun":
            snapshot.pronouns.add(normalized)
            return
        if pos == "determiner":
            snapshot.determiners.add(normalized)
            return
        if pos == "conjunction":
            snapshot.conjunctions.add(normalized)
            return
        if pos == "auxiliary":
            snapshot.auxiliaries.add(normalized)
            return
        if pos == "abbreviation":
            snapshot.abbreviations.add(normalized)
            return
        if pos == "verb":
            self._add_verb(snapshot, normalized)

    def _add_verb(self, snapshot: DictionaryLexiconSnapshot, normalized: str) -> None:
        base = normalized
        if base.startswith("to "):
            base = base[3:].strip()
        if not base:
            return

        if " " in base:
            parts = [p for p in base.split() if p]
            if not parts:
                return
            snapshot.verbs_base.add(parts[0])
            if len(parts) >= 2:
                snapshot.phrasal_verbs.setdefault(parts[0], set()).add(parts[1])
            return

        snapshot.verbs_base.add(base)

    def suggest_unknown_tokens(self, tokens: Iterable[str]) -> list[str]:
        snapshot = self.ensure_loaded()
        if not snapshot.loaded:
            return []

        suggestions: list[str] = []
        seen: set[str] = set()
        for token in tokens:
            t = (token or "").strip().lower()
            if not t or t in seen:
                continue
            seen.add(t)

            if len(t) <= 2 or t in FUNCTION_WORDS:
                continue
            if t in snapshot.words:
                continue
            # Simple inflection fallback to reduce false positives.
            if t.endswith("s") and t[:-1] in snapshot.words:
                continue
            if t.endswith("ed") and t[:-2] in snapshot.words:
                continue
            if t.endswith("ing") and t[:-3] in snapshot.words:
                continue

            suggestions.append(f"No se encontro '{t}' en el diccionario importado (puede ser nombre propio o falta de importacion).")
            if len(suggestions) >= 3:
                break
        return suggestions

    def semantic_hints_for_tokens(self, tokens: list[str]) -> list[str]:
        snapshot = self.ensure_loaded()
        if not snapshot.loaded or not tokens:
            return []

        hints: list[str] = []

        # modal + next content token should be verb-like
        for i, token in enumerate(tokens[:-1]):
            if token not in {"can", "could", "should", "must", "may", "might", "will", "would"}:
                continue
            nxt = self._next_content_token(tokens, i + 1)
            if not nxt:
                continue
            rec = snapshot.words.get(nxt)
            if rec and "verb" not in rec.pos_classes and "auxiliary" not in rec.pos_classes:
                hints.append(
                    f"Despues de modal ('{token}'), '{nxt}' no aparece como verbo en el diccionario (POS: {', '.join(sorted(rec.pos_classes))})."
                )
                break

        # infinitive marker "to" + base verb
        for i, token in enumerate(tokens[:-1]):
            if token != "to":
                continue
            prev_token = tokens[i - 1] if i > 0 else None
            # Skip prepositional "to" contexts where verb expectation is weak.
            if prev_token in {"go", "went", "come", "came", "back", "up", "down", "from", "into"}:
                continue
            nxt = self._next_content_token(tokens, i + 1)
            if not nxt:
                continue
            rec = snapshot.words.get(nxt)
            if rec and rec.pos_classes.isdisjoint({"verb", "auxiliary"}):
                hints.append(
                    f"Despues de 'to', '{nxt}' no aparece como verbo en el diccionario (POS: {', '.join(sorted(rec.pos_classes))})."
                )
                break

        # "very" typically modifies adjectives/adverbs
        for i, token in enumerate(tokens[:-1]):
            if token != "very":
                continue
            nxt = self._next_content_token(tokens, i + 1)
            if not nxt:
                continue
            rec = snapshot.words.get(nxt)
            if rec and rec.pos_classes.isdisjoint({"adjective", "adverb"}):
                hints.append(
                    f"Despues de 'very', '{nxt}' no suele funcionar como adjetivo/adverbio (POS: {', '.join(sorted(rec.pos_classes))})."
                )
                break

        # Predicate after "be": prefer adjective/noun phrase/preposition, warn on clear verb-base misuse.
        for i, token in enumerate(tokens[:-1]):
            if token not in {"am", "is", "are", "was", "were"}:
                continue
            nxt = self._next_content_token(tokens, i + 1)
            if not nxt:
                continue
            rec = snapshot.words.get(nxt)
            if rec is None:
                continue
            if "verb" in rec.pos_classes and rec.pos_classes.isdisjoint({"adjective", "noun", "adverb"}):
                hints.append(
                    f"Despues de '{token}', '{nxt}' aparece principalmente como verbo; revisa si falta un adjetivo o forma en -ing/-ed."
                )
                break

        # article + noun phrase head heuristic
        for i, token in enumerate(tokens[:-1]):
            if token not in {"a", "an", "the", "this", "that", "these", "those"}:
                continue
            nxt = self._next_content_token(tokens, i + 1)
            if not nxt:
                continue
            rec = snapshot.words.get(nxt)
            if rec and rec.pos_classes.isdisjoint({"noun", "adjective", "determiner"}):
                hints.append(
                    f"Despues de '{token}', '{nxt}' tiene POS poco comun para una frase nominal ({', '.join(sorted(rec.pos_classes))})."
                )
                break

        return hints

    @staticmethod
    def _next_content_token(tokens: list[str], start: int) -> str | None:
        for token in tokens[start:]:
            if token in FUNCTION_WORDS:
                continue
            return token
        return None
