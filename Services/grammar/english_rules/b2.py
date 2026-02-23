from .shared import *

class PresentPerfectContinuousRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        tokens = analysis.tokens
        for i, token in enumerate(tokens):
            if token not in {"have", "has"}:
                continue
            if i > 0 and (tokens[i - 1] in MODAL_VERBS or tokens[i - 1] in BASE_AUXILIARIES):
                continue
            if i + 1 < len(tokens) and tokens[i + 1] == "been":
                next_form = _verb_form_at(analysis, i + 2) if i + 2 < len(tokens) else None
                if i + 2 >= len(tokens) or (next_form != "participle_ing" and not _is_ing(tokens[i + 2])):
                    return ValidationIssue(
                        rule_id=self.rule_id,
                        severity=self.severity,
                        message="Present perfect continuous uses have/has been + verb-ing.",
                    )
        return None


class PastPerfectRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        tokens = analysis.tokens
        for i, token in enumerate(tokens[:-1]):
            if token != "had":
                continue
            nxt = tokens[i + 1]
            if nxt == "been":
                continue
            nxt_form = _verb_form_at(analysis, i + 1)
            if (nxt_form in {"base", "v3sg"}) or (_looks_like_clear_base_verb(nxt) and not _looks_like_participle(nxt)):
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="Past perfect uses had + past participle (e.g. 'had finished').",
                )
        return None


class PastPerfectContinuousRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        tokens = analysis.tokens
        idx = _find_sequence(tokens, ["had", "been"])
        if idx is None:
            return None
        next_form = _verb_form_at(analysis, idx + 2) if idx + 2 < len(tokens) else None
        if idx + 2 >= len(tokens) or (next_form != "participle_ing" and not _is_ing(tokens[idx + 2])):
            return ValidationIssue(
                rule_id=self.rule_id,
                severity=self.severity,
                message="Past perfect continuous uses had been + verb-ing.",
            )
        return None


class FutureContinuousRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        tokens = analysis.tokens
        idx = _find_sequence(tokens, ["will", "be"])
        if idx is None:
            return None
        next_form = _verb_form_at(analysis, idx + 2) if idx + 2 < len(tokens) else None
        if idx + 2 >= len(tokens) or (next_form != "participle_ing" and not _is_ing(tokens[idx + 2])):
            return ValidationIssue(
                rule_id=self.rule_id,
                severity=self.severity,
                message="Future continuous uses will be + verb-ing.",
            )
        return None


class FuturePerfectRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        tokens = analysis.tokens
        idx = _find_sequence(tokens, ["will", "have"])
        if idx is None:
            return None
        if idx + 2 >= len(tokens):
            return ValidationIssue(
                rule_id=self.rule_id,
                severity=self.severity,
                message="Future perfect uses will have + past participle.",
            )
        nxt = tokens[idx + 2]
        if nxt == "been":
            return None
        nxt_form = _verb_form_at(analysis, idx + 2)
        if nxt_form != "participle_ed" and not _looks_like_participle(nxt):
            return ValidationIssue(
                rule_id=self.rule_id,
                severity=self.severity,
                message="Future perfect uses will have + past participle (e.g. 'will have finished').",
            )
        return None


class FuturePerfectContinuousRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        tokens = analysis.tokens
        idx = _find_sequence(tokens, ["will", "have", "been"])
        if idx is None:
            return None
        next_form = _verb_form_at(analysis, idx + 3) if idx + 3 < len(tokens) else None
        if idx + 3 >= len(tokens) or (next_form != "participle_ing" and not _is_ing(tokens[idx + 3])):
            return ValidationIssue(
                rule_id=self.rule_id,
                severity=self.severity,
                message="Future perfect continuous uses will have been + verb-ing.",
            )
        return None


class AdvancedConditionalRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        tokens = analysis.tokens
        clauses = _iter_clauses(analysis)
        if_clause = next((c for c in clauses if c.clause_type == "if_clause"), None)
        if if_clause is not None:
            if_tokens = _clause_tokens(analysis, if_clause)
            main_clause = next(
                (c for c in clauses if c.start_idx > if_clause.end_idx and c.clause_type == "main"),
                None,
            )
            main_tokens = _clause_tokens(analysis, main_clause) if main_clause is not None else tokens
            if "had" in if_tokens and "would" in main_tokens and "have" not in main_tokens:
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="Third conditional typically uses 'if + had + participle' and 'would have + participle'.",
                )

        if "if" in tokens:
            if_idx = tokens.index("if")
            if_clause = tokens[if_idx + 1 : if_idx + 7]
            if "had" in if_clause and "would" in tokens and "have" not in tokens:
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="Third conditional typically uses 'if + had + participle' and 'would have + participle'.",
                )

        # Alternatives to if: unless/provided/as long as
        for marker in ("unless",):
            if marker in tokens and "not" in tokens:
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="Avoid double negatives with 'unless' (it already means 'if not').",
                )
        if "provided" in tokens and "that" not in tokens:
            return ValidationIssue(
                rule_id=self.rule_id,
                severity=self.severity,
                message="Use 'provided that' / 'providing that' for this conditional linker.",
            )
        if "long" in tokens and "as" in tokens:
            idx = _find_sequence(tokens, ["as", "long", "as"])
            if idx is None:
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="Use the linker 'as long as' as a fixed expression.",
                )
        return None


class AdvancedModalPerfectRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        tokens = analysis.tokens
        modal_set = {"must", "might", "may", "could", "should", "can't", "cannot"}
        for i, token in enumerate(tokens[:-1]):
            if token not in modal_set:
                continue
            if i + 1 < len(tokens) and tokens[i + 1] == "have":
                next_form = _verb_form_at(analysis, i + 2) if i + 2 < len(tokens) else None
                if i + 2 >= len(tokens) or (next_form != "participle_ed" and not _looks_like_participle(tokens[i + 2])):
                    return ValidationIssue(
                        rule_id=self.rule_id,
                        severity=self.severity,
                        message="Modal perfect forms use modal + have + past participle (e.g. 'should have gone').",
                    )
        return None


class AdvancedPassiveVoiceRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        tokens = analysis.tokens
        # has been done / will be done / must be done
        patterns = [["has", "been"], ["have", "been"], ["will", "be"]]
        for pat in patterns:
            idx = _find_sequence(tokens, pat)
            if idx is None:
                continue
            if pat == ["have", "been"] and idx > 0 and tokens[idx - 1] in {"will", "would"}:
                continue
            end = idx + len(pat)
            end_form = _verb_form_at(analysis, end) if end < len(tokens) else None
            # Allow active perfect continuous / progressive continuations: have/has been + V-ing
            if end_form == "participle_ing" or (end < len(tokens) and _is_ing(tokens[end])):
                continue
            if end >= len(tokens) or (end_form != "participle_ed" and not _looks_like_participle(tokens[end])):
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message=f"Passive form usually needs a past participle after {' '.join(pat)}.",
                )

        for i, token in enumerate(tokens[:-1]):
            if token in MODAL_VERBS and tokens[i + 1] == "be":
                next_form = _verb_form_at(analysis, i + 2) if i + 2 < len(tokens) else None
                if i + 2 >= len(tokens) or (next_form != "participle_ed" and not _looks_like_participle(tokens[i + 2])):
                    return ValidationIssue(
                        rule_id=self.rule_id,
                        severity=self.severity,
                        message="Passive with modals uses modal + be + past participle (e.g. 'must be done').",
                    )

        # "It is said that..." fixed impersonal passive pattern
        idx = _find_sequence(tokens, ["it", "is"])
        if idx is not None and idx + 2 < len(tokens) and tokens[idx + 2] in {"say", "tell"}:
            return ValidationIssue(
                rule_id=self.rule_id,
                severity=self.severity,
                message="Use impersonal passive as 'It is said that...' (past participle after 'is').",
            )
        return None


class ReportedSpeechAdvancedRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        tokens = analysis.tokens
        clauses = _iter_clauses(analysis)
        obj_like = {"me", "him", "her", "us", "them", "you"}
        for i in range(len(tokens) - 1):
            head = _normalize_simple_verb_lemma(tokens[i])
            if head == "suggest" and tokens[i + 1] == "to":
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="Use 'suggest + -ing' or 'suggest (that) + clause' (not usually 'suggest to do').",
                )
            if (
                head == "suggest"
                and i + 2 < len(tokens)
                and (tokens[i + 1] in obj_like or _is_simple_subject_start(tokens[i + 1]))
                and tokens[i + 2] == "to"
            ):
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="Use 'suggest + -ing' or 'suggest (that) + clause' (not usually 'suggest someone to do').",
                )
            if tokens[i] in {"advise", "warn"} and i + 1 < len(tokens) and tokens[i + 1] == "that":
                # valid, allow
                continue
        # Clause-aware inversion inside reported advanced complements after reporting verbs.
        for idx, clause in enumerate(clauses):
            clause_tokens = _clause_tokens(analysis, clause)
            if len(clause_tokens) < 2:
                continue
            if clause_tokens[0] not in {"whether", "if"} and clause_tokens[0] not in WH_QUESTION_WORDS:
                continue
            if clause_tokens[1] not in QUESTION_AUXILIARIES:
                continue
            if idx == 0:
                continue
            prev_tokens = _clause_tokens(analysis, clauses[idx - 1])
            if any(t in REPORTING_VERBS | {"wonder", "wonders", "wondered"} for t in prev_tokens):
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="In reported clauses after reporting verbs, use statement order (avoid question inversion).",
                )
        return None


class RelativeClauseAdvancedRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        tokens = analysis.tokens
        for i in range(1, len(tokens) - 1):
            if tokens[i] in {"which", "whom"} and tokens[i - 1] in COMMON_PREPOSITIONS:
                # valid advanced pattern: "to which", "with whom"
                continue
            if tokens[i] == "whose" and tokens[i - 1] in SUBJECT_DETERMINERS:
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="Use 'whose' after a noun antecedent (e.g. 'the man whose car...'), not after a determiner.",
                )
            if tokens[i] == "that" and _has_punctuation_before_word_index(analysis, i, ","):
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="In non-restrictive relative clauses (after commas), use 'which/who' rather than 'that'.",
                )
            if tokens[i] == "whose" and (i + 1 >= len(tokens) or _pos_at(analysis, i + 1) not in {"noun", "adjective"}):
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="'Whose' is usually followed by a noun phrase (e.g. 'whose car').",
                )
        return None


class InversionEmphasisRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        tokens = analysis.tokens
        clauses = _iter_clauses(analysis)
        if not tokens:
            return None
        if tokens[0] in {"never", "rarely", "seldom", "hardly", "scarcely"}:
            if len(tokens) >= 3 and tokens[1] not in QUESTION_AUXILIARIES | MODAL_VERBS | TO_BE_FORMS:
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="After negative adverbials in formal inversion, use auxiliary + subject (e.g. 'Never have I seen...').",
                )
        if _find_sequence(tokens, ["not", "only"]) is not None and "but" in tokens and "also" in tokens:
            idx = _find_sequence(tokens, ["not", "only"])
            if idx == 0 and len(tokens) > 2 and tokens[2] not in QUESTION_AUXILIARIES | MODAL_VERBS | TO_BE_FORMS:
                first_clause = clauses[0] if clauses else None
                if first_clause is not None and first_clause.linker_tokens == ["not", "only"]:
                    first_clause_tokens = _clause_tokens(analysis, first_clause)
                    if len(first_clause_tokens) > 2 and first_clause_tokens[2] in QUESTION_AUXILIARIES | MODAL_VERBS | TO_BE_FORMS:
                        return None
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="With fronted 'Not only...', formal English often uses inversion (e.g. 'Not only did he...').",
                )
        if len(tokens) >= 4 and tokens[:2] == ["no", "sooner"]:
            if tokens[2] not in QUESTION_AUXILIARIES | MODAL_VERBS | TO_BE_FORMS:
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="With fronted 'No sooner...', formal inversion uses auxiliary + subject (e.g. 'No sooner had I...').",
                )
            if "than" not in tokens:
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="Use 'No sooner ... than ...' as a fixed correlative pattern.",
                )
        if len(tokens) >= 4 and tokens[:2] == ["not", "until"]:
            lookahead = tokens[2:7]
            if not any(t in QUESTION_AUXILIARIES | MODAL_VERBS | TO_BE_FORMS for t in lookahead):
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="When fronting 'Not until ...', formal inversion is common in the main clause (e.g. 'Not until later did I understand').",
                )
        return None


class CleftSentenceRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        tokens = analysis.tokens
        clauses = _iter_clauses(analysis)
        if tokens and tokens[0] == "what":
            if ("is" not in tokens and "was" not in tokens) and len(tokens) >= 4:
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="Wh-cleft sentences usually contain a linking verb (e.g. 'What I need is...').",
                )
        if len(tokens) >= 4 and tokens[0] == "it" and tokens[1] in {"is", "was"}:
            # If a clause linker associated with a following clause is present, this often fits a cleft/pseudo-cleft.
            if any(
                c.start_idx >= 3 and c.clause_type in {"relative_clause", "when_clause", "where_clause"}
                for c in clauses
            ):
                return None
            focus_pos = _pos_at(analysis, 2)
            # Avoid false positives in ordinary predicates: "It is important/clear/possible..."
            if focus_pos in {"adverb"}:
                return None
            if tokens[2] in COMMON_ADJECTIVES | {"important", "clear", "possible", "necessary"}:
                return None
            if focus_pos == "adjective" and len(tokens) >= 5 and tokens[3] not in ENGLISH_SUBJECT_PRONOUNS:
                return None
            if not any(t in {"who", "that", "when", "where"} for t in tokens[3:]):
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="It-cleft structures typically use a relative connector (e.g. 'It was John who...').",
                )
        return None


class GerundInfinitiveMeaningRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        tokens = analysis.tokens
        # Detect obvious malformed patterns in high-value pairs.
        for i in range(len(tokens) - 2):
            next_form = _verb_form_at(analysis, i + 2)
            if tokens[i] in {"stop", "remember"} and tokens[i + 1] == "to" and (next_form == "participle_ing" or _is_ing(tokens[i + 2])):
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="After 'stop/remember + to', use a base verb (e.g. 'remember to call').",
                )
        return None


class NounClauseComplexRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        tokens = analysis.tokens
        clauses = _iter_clauses(analysis)
        # "The fact is that..." / "The fact that..."
        idx = _find_sequence(tokens, ["the", "fact"])
        if idx is not None and idx + 2 < len(tokens):
            if tokens[idx + 2] not in {"that", "is"}:
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="Common noun-clause pattern: 'the fact that...' or 'The fact is that...'.",
                )

        # "whether/if" + inversion in noun clause
        for i in range(len(tokens) - 2):
            if tokens[i] in {"whether", "if"} and tokens[i + 1] in QUESTION_AUXILIARIES:
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="In noun clauses with 'whether/if', use statement order (not question inversion).",
                )
        for idx, clause in enumerate(clauses):
            clause_tokens = _clause_tokens(analysis, clause)
            if len(clause_tokens) < 2 or clause_tokens[0] not in {"whether", "if"}:
                continue
            if clause_tokens[1] not in QUESTION_AUXILIARIES:
                continue
            if idx > 0:
                prev_tokens = _clause_tokens(analysis, clauses[idx - 1])
                if any(t in NOUN_CLAUSE_TRIGGERS for t in prev_tokens):
                    return ValidationIssue(
                        rule_id=self.rule_id,
                        severity=self.severity,
                        message="After noun-clause triggers, use statement order in 'whether/if' clauses (not inversion).",
                    )
        for idx, clause in enumerate(clauses):
            clause_tokens = _clause_tokens(analysis, clause)
            if len(clause_tokens) < 2:
                continue
            if clause_tokens[0] not in WH_QUESTION_WORDS:
                continue
            if clause_tokens[1] not in QUESTION_AUXILIARIES:
                continue
            if idx == 0:
                continue
            prev_tokens = _clause_tokens(analysis, clauses[idx - 1])
            if any(t in NOUN_CLAUSE_TRIGGERS for t in prev_tokens):
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="In embedded noun clauses (what/where/why/how...), use statement order rather than question inversion.",
                )
        # Fallback for flat clause segmentation: trigger + wh + auxiliary inside one main clause.
        for i, tok in enumerate(tokens[:-2]):
            if tok not in NOUN_CLAUSE_TRIGGERS:
                continue
            for j in range(i + 1, min(len(tokens) - 1, i + 6)):
                if tokens[j] in WH_QUESTION_WORDS and j + 1 < len(tokens) and tokens[j + 1] in QUESTION_AUXILIARIES:
                    return ValidationIssue(
                        rule_id=self.rule_id,
                        severity=self.severity,
                        message="In embedded noun clauses (what/where/why/how...), use statement order rather than question inversion.",
                    )
        return None


class LinkingDeviceRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        tokens = analysis.tokens
        if not tokens:
            return None

        # Sentence-initial discourse connectors often take a comma.
        if tokens[0] in {"however", "therefore", "moreover"} and len(tokens) >= 3:
            if not _has_punctuation_after_word_index(analysis, 0, ","):
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message=f"Sentence-initial linker '{tokens[0]}' is often followed by a comma (e.g. '{tokens[0].capitalize()}, ...').",
                )

        # "despite" should be followed by noun/gerund, not a full clause subject+verb.
        for i, token in enumerate(tokens[:-2]):
            if token == "despite":
                if tokens[i + 1] in ENGLISH_SUBJECT_PRONOUNS and (
                    tokens[i + 2] in TO_BE_FORMS or _looks_like_base_verb(tokens[i + 2]) or _looks_like_past(tokens[i + 2])
                ):
                    return ValidationIssue(
                        rule_id=self.rule_id,
                        severity=self.severity,
                        message="After 'despite', use a noun phrase or gerund (e.g. 'despite the rain' / 'despite being late').",
                    )
            if token == "although" and i + 1 < len(tokens) and tokens[i + 1] in {"of", "despite"}:
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="Use 'although + clause' (not 'although of/despite').",
                )
        return None


class QuantifiersDeterminersAdvancedRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        tokens = analysis.tokens
        for np in getattr(analysis, "noun_phrases", []) or []:
            q = np.quantifier
            if q is None:
                continue
            c = np.countability_guess
            if q in {"each", "every", "either", "neither"} and c == "countable_plural":
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message=f"'{q}' is usually followed by a singular noun.",
                )
            if q == "both" and c in {"countable", "countable_singular_or_unknown"}:
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="'Both' is usually followed by a plural noun or pronoun.",
                )
            if (
                q == "such"
                and np.determiner in {"a", "an"}
                and c == "countable_plural"
            ):
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="With plural nouns, use 'such + plural noun' (not 'such a/an ...').",
                )

        for i in range(len(tokens) - 1):
            q = tokens[i]
            n = tokens[i + 1]
            if q in {"each", "every", "either", "neither"} and _is_plural_like_noun(n):
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message=f"'{q}' is usually followed by a singular noun.",
                )
            if q == "both" and not _is_plural_like_noun(n) and n not in {"of", "the", "them", "us", "you"}:
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="'Both' is usually followed by a plural noun or pronoun.",
                )
            if q == "so" and n in COUNTABLE_HINT_NOUNS:
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="Use 'such + noun' (or 'so + adjective') in this pattern.",
                )
            if q == "such" and n in COMMON_ADJECTIVES and i + 2 < len(tokens) and _is_likely_noun(tokens[i + 2]):
                np_from_such = _noun_phrase_starting_at(analysis, i)
                if np_from_such is not None and np_from_such.countability_guess in {"countable_plural", "uncountable"}:
                    pass
                else:
                    return ValidationIssue(
                        rule_id=self.rule_id,
                        severity=self.severity,
                        message="Use 'such a/an + adjective + noun' with singular countable nouns (e.g. 'such a big house').",
                    )
            if q == "such" and i + 1 < len(tokens) and tokens[i + 1] in {"a", "an"}:
                np = _noun_phrase_starting_at(analysis, i + 2)
                if np is not None and np.countability_guess == "countable_plural":
                    return ValidationIssue(
                        rule_id=self.rule_id,
                        severity=self.severity,
                        message="With plural nouns, use 'such + plural noun' (not 'such a/an ...').",
                    )
        for i in range(len(tokens) - 2):
            if tokens[i] in COMMON_ADJECTIVES and tokens[i + 1] == "enough" and tokens[i + 2] == "to":
                continue
            if tokens[i] == "enough" and tokens[i + 1] in COMMON_ADJECTIVES and _is_likely_noun(tokens[i + 2]):
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="'Enough' usually follows adjectives (e.g. 'big enough').",
                )
        return None


class PhrasalVerbAdvancedRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        tokens = analysis.tokens
        for i in range(len(tokens) - 1):
            verb = tokens[i]
            part = tokens[i + 1]
            verb_lemma = _normalize_simple_verb_lemma(verb)
            pos = _pos_at(analysis, i)
            if pos not in {"verb", "verb_participle", "auxiliary", None}:
                continue
            if verb_lemma in PHRASAL_ADVANCED and part in COMMON_PREPOSITIONS | {"up", "out", "with"}:
                if part not in PHRASAL_ADVANCED[verb_lemma]:
                    expected = "/".join(sorted(PHRASAL_ADVANCED[verb_lemma]))
                    return ValidationIssue(
                        rule_id=self.rule_id,
                        severity=self.severity,
                        message=f"Common advanced phrasal pattern here is usually '{verb_lemma} {expected}'.",
                    )
        # Multi-particle pattern: put up with
        for i in range(len(tokens) - 1):
            if _normalize_simple_verb_lemma(tokens[i]) == "put" and tokens[i + 1] == "up":
                if i + 2 < len(tokens) and tokens[i + 2] != "with":
                    return ValidationIssue(
                        rule_id=self.rule_id,
                        severity=self.severity,
                        message="Use 'put up with' as a fixed phrasal verb for 'tolerate'.",
                    )
        return None


class WordFormationRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        tokens = analysis.tokens
        # High-frequency family: decide / decision / decisive
        for i in range(len(tokens) - 1):
            if tokens[i] in {"a", "an", "the"} and tokens[i + 1] == "decide":
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="After an article, this word usually needs a noun form (e.g. 'a decision').",
                )
            if tokens[i] in {"very", "so", "too"} and tokens[i + 1] == "decision":
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="After degree adverbs like 'very', use an adjective form (e.g. 'decisive').",
                )
            if tokens[i] in {"a", "an", "the"} and tokens[i + 1] == "different":
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="After an article, use a noun form (e.g. 'difference'), not the adjective 'different'.",
                )
            if tokens[i] in {"very", "so", "too"} and tokens[i + 1] == "success":
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="After degree adverbs, use an adjective (e.g. 'successful'), not the noun 'success'.",
                )
        return None
