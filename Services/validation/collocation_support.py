from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class CollocationSnapshot:
    verb_prep: dict[str, set[str]] = field(default_factory=dict)
    adjective_prep: dict[str, set[str]] = field(default_factory=dict)
    noun_prep: dict[str, set[str]] = field(default_factory=dict)

    @property
    def loaded(self) -> bool:
        return bool(self.verb_prep or self.adjective_prep or self.noun_prep)


class CollocationSupport:
    def __init__(self, json_path: str | None = None) -> None:
        default_path = Path(__file__).resolve().parent / "data" / "en_collocations.json"
        self.json_path = Path(json_path) if json_path else default_path
        self._snapshot = CollocationSnapshot()
        self._loaded = False

    def ensure_loaded(self) -> CollocationSnapshot:
        if self._loaded:
            return self._snapshot
        self._snapshot = self._load()
        self._loaded = True
        return self._snapshot

    def collocation_hints_for_analysis(self, analysis) -> list[str]:
        snapshot = self.ensure_loaded()
        if not snapshot.loaded:
            return []
        tokens = getattr(analysis, "tokens", [])
        features = getattr(analysis, "token_features", [])
        if not tokens or not features:
            return []

        hints: list[str] = []
        common_adverbs = {
            "very",
            "really",
            "quite",
            "deeply",
            "highly",
            "strongly",
            "closely",
            "directly",
        }
        for i in range(len(tokens) - 1):
            head = tokens[i]
            head_norm = self._normalize_headword(head)
            prep_idx = i + 1
            if prep_idx < len(tokens) and tokens[prep_idx] in common_adverbs and prep_idx + 1 < len(tokens):
                prep_idx += 1
            prep = tokens[prep_idx] if prep_idx < len(tokens) else ""
            if not prep or not prep.isalpha():
                continue
            feature = features[i] if i < len(features) else None
            pos = getattr(feature, "pos_guess", None)
            prep_feature = features[prep_idx] if prep_idx < len(features) else None
            prep_pos = getattr(prep_feature, "pos_guess", None)
            if prep_pos == "adverb":
                continue

            if (pos in {"verb", "verb_participle"} or head_norm in snapshot.verb_prep) and head_norm in snapshot.verb_prep:
                allowed = snapshot.verb_prep[head_norm]
                if prep not in allowed:
                    hints.append(
                        f"Con '{head}' se usa normalmente {self._format_allowed_preps(allowed)} (no '{prep}' en este contexto)."
                    )
                    continue

            if pos == "adjective" and head_norm in snapshot.adjective_prep:
                allowed = snapshot.adjective_prep[head_norm]
                if prep not in allowed:
                    hints.append(
                        f"Con el adjetivo '{head}' se usa normalmente {self._format_allowed_preps(allowed)}."
                    )
                    continue

            if pos == "noun" and head_norm in snapshot.noun_prep:
                allowed = snapshot.noun_prep[head_norm]
                if prep not in allowed:
                    hints.append(
                        f"Con el sustantivo '{head}' se usa normalmente {self._format_allowed_preps(allowed)}."
                    )
                    continue

            if len(hints) >= 3:
                break

        # Deduplicate preserving order
        out: list[str] = []
        seen: set[str] = set()
        for hint in hints:
            if hint in seen:
                continue
            seen.add(hint)
            out.append(hint)
        return out

    def _load(self) -> CollocationSnapshot:
        if not self.json_path.exists():
            return CollocationSnapshot()
        try:
            raw = json.loads(self.json_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return CollocationSnapshot()

        def normalize_map(value) -> dict[str, set[str]]:
            if not isinstance(value, dict):
                return {}
            out: dict[str, set[str]] = {}
            for k, v in value.items():
                if not isinstance(k, str) or not isinstance(v, list):
                    continue
                out[k.strip().lower()] = {str(x).strip().lower() for x in v if str(x).strip()}
            return out

        return CollocationSnapshot(
            verb_prep=normalize_map(raw.get("verb_prep")),
            adjective_prep=normalize_map(raw.get("adjective_prep")),
            noun_prep=normalize_map(raw.get("noun_prep")),
        )

    @staticmethod
    def _format_allowed_preps(allowed: set[str]) -> str:
        opts = sorted(allowed)
        if len(opts) == 1:
            return f"'{opts[0]}'"
        return " / ".join(f"'{x}'" for x in opts)

    @staticmethod
    def _normalize_headword(token: str) -> str:
        token = token.lower()
        irregular = {"came": "come"}
        if token in irregular:
            return irregular[token]
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
                stem = stem[:-1] + "y"
            if len(stem) >= 2 and stem[-1] == stem[-2]:
                stem = stem[:-1]
            return stem
        if token.endswith("s") and len(token) > 3 and not token.endswith("ss"):
            return token[:-1]
        return token
