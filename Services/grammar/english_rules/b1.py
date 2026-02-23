from .shared import *

class FuturePresentContinuousPlanRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        tokens = analysis.tokens
        if not _has_future_time_marker(tokens):
            return None
        for idx, token in enumerate(tokens):
            if token not in {"am", "is", "are"}:
                continue
            if idx + 1 < len(tokens) and tokens[idx + 1] == "going":
                continue
            next_idx, next_token = _find_verb_after_aux(tokens, idx)
            if next_token is None:
                continue
            if next_token in COMMON_ADJECTIVES or next_token in COMMON_ED_PREDICATE_ADJECTIVES:
                continue
            next_form = _verb_form_at(analysis, next_idx) if next_idx is not None else None
            if (next_form == "base") or (_looks_like_base_verb(next_token) and not _is_ing(next_token)):
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="For future plans with present continuous, use am/is/are + verb-ing (e.g. 'I am meeting her tomorrow').",
                )
        return None


class PresentSimpleScheduleRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        tokens = analysis.tokens
        if "schedule" not in analysis.cleaned_text.lower() and not any(t in {"train", "bus", "class", "flight"} for t in tokens):
            return None
        if "will" in tokens and any(t in {"at", "on"} for t in tokens):
            return ValidationIssue(
                rule_id=self.rule_id,
                severity=self.severity,
                message="For timetables/schedules, English often uses present simple (e.g. 'The train leaves at 6').",
            )
        return None


class SemiModalHaveToRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        tokens = analysis.tokens
        for idx, token in enumerate(tokens[:-1]):
            if token not in {"have", "has", "had"}:
                continue
            if tokens[idx + 1] != "to":
                continue
            if idx + 2 >= len(tokens):
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="Use 'have to + base verb' (e.g. 'I have to study').",
                )
            verb = tokens[idx + 2]
            verb_form = _verb_form_at(analysis, idx + 2)
            if verb_form in {"v3sg", "past", "participle_ed", "participle_ing"} or verb.endswith(("s", "ed", "ing")):
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="After 'have to', use the base form of the verb.",
                )

        if len(tokens) >= 3 and tokens[0] in SINGULAR_THIRD_SUBJECTS and tokens[1] == "have" and tokens[2] == "to":
            return ValidationIssue(
                rule_id=self.rule_id,
                severity=self.severity,
                message="Use 'has to' with he/she/it in present simple.",
            )
        return None


class ComparativeSuperlativeRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        tokens = analysis.tokens
        for i in range(len(tokens) - 1):
            a, b = tokens[i], tokens[i + 1]
            if a == "more" and (b.endswith("er") or b in {"better", "worse"}):
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="Avoid double comparatives (e.g. 'bigger' or 'more interesting', not 'more bigger').",
                )
            if a == "most" and (b in {"best", "worst"} or b.endswith("est")):
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="Avoid double superlatives (e.g. 'the best', not 'the most best').",
                )
            if a == "as" and i + 2 < len(tokens) and tokens[i + 2] == "than":
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="Use 'as ... as' (not 'as ... than').",
                )
        return None


class B1ConditionalRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        tokens = analysis.tokens
        clauses = _iter_clauses(analysis)
        if_clause = next((c for c in clauses if c.clause_type == "if_clause"), None)
        if if_clause is not None:
            main_clause = next(
                (c for c in clauses if c.start_idx > if_clause.end_idx and c.clause_type == "main"),
                None,
            )
            if_tokens = _clause_tokens(analysis, if_clause)
            main_tokens = _clause_tokens(analysis, main_clause) if main_clause is not None else tokens
            if if_clause.tense_guess == "present_simple" and "would" in main_tokens:
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="For first conditional, use present in the if-clause and usually 'will/can/may' in the main clause (not 'would').",
                )
            if if_clause.tense_guess in {"past_simple"} and "will" in main_tokens:
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="For second conditional, use 'would/could/might' in the main clause (e.g. 'If I had money, I would buy...').",
                )

        if "if" not in tokens:
            return None
        if_idx = tokens.index("if")
        clause = tokens[if_idx + 1 :]
        if len(clause) < 2:
            return None

        # First conditional mismatch: "If it rains, I would..."
        if any((_verb_form_at(analysis, if_idx + 1 + j) == "v3sg") or clause[j].endswith("s") for j in range(min(4, len(clause)))) and "would" in tokens:
            return ValidationIssue(
                rule_id=self.rule_id,
                severity=self.severity,
                message="For first conditional, use present in the if-clause and usually 'will/can/may' in the main clause (not 'would').",
            )

        # Second conditional mismatch: "If I had money, I will buy..."
        if any(
            (
                clause[j] in {"had", "were"}
                or _verb_form_at(analysis, if_idx + 1 + j) in {"past", "participle_ed"}
                or _is_ed(clause[j])
            )
            for j in range(min(5, len(clause)))
        ) and "will" in tokens:
            return ValidationIssue(
                rule_id=self.rule_id,
                severity=self.severity,
                message="For second conditional, use 'would/could/might' in the main clause (e.g. 'If I had money, I would buy...').",
            )
        return None


class BasicPassiveVoiceRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        tokens = analysis.tokens
        for idx, token in enumerate(tokens[:-1]):
            if token not in {"am", "is", "are", "was", "were"}:
                continue
            next_token = tokens[idx + 1]
            next_form = _verb_form_at(analysis, idx + 1)
            next_pos = _pos_at(analysis, idx + 1)
            if next_token in {"being", "going"}:
                continue
            if next_token in COMMON_ADJECTIVES or next_token in COMMON_ED_PREDICATE_ADJECTIVES:
                continue
            if next_pos == "adjective":
                continue
            if next_token in TRANSITIVE_BASES_FOR_PASSIVE or _looks_like_base_verb(next_token):
                if (
                    next_token not in {"be"}
                    and next_form not in {"participle_ed", "participle_ing"}
                    and not _looks_like_participle(next_token)
                    and not _is_ing(next_token)
                ):
                    return ValidationIssue(
                        rule_id=self.rule_id,
                        severity=self.severity,
                        message="Passive voice usually uses be + past participle (e.g. 'is made', 'was built').",
                    )
        return None


class ReportedSpeechBasicRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        tokens = analysis.tokens
        clauses = _iter_clauses(analysis)
        for idx, clause in enumerate(clauses):
            clause_tokens = _clause_tokens(analysis, clause)
            if len(clause_tokens) < 2:
                continue
            if clause_tokens[0] not in WH_QUESTION_WORDS or clause_tokens[1] not in QUESTION_AUXILIARIES:
                continue
            if idx == 0:
                continue
            prev_tokens = _clause_tokens(analysis, clauses[idx - 1])
            if any(t in REPORTING_VERBS for t in prev_tokens):
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="In reported/indirect questions, do not use question inversion (e.g. 'He asked where I lived').",
                )
        for i, token in enumerate(tokens[:-2]):
            if token not in REPORTING_VERBS:
                continue
            # Indirect question inversion error: "He asked where do I live"
            if tokens[i + 1] in WH_QUESTION_WORDS and tokens[i + 2] in QUESTION_AUXILIARIES:
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="In reported/indirect questions, do not use question inversion (e.g. 'He asked where I lived').",
                )
        return None


class RelativeClauseBasicRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        tokens = analysis.tokens
        clauses = _iter_clauses(analysis)
        for clause in clauses:
            if clause.clause_type != "relative_clause":
                continue
            clause_tokens = _clause_tokens(analysis, clause)
            if len(clause_tokens) >= 2 and clause_tokens[1] in ENGLISH_SUBJECT_PRONOUNS:
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="Relative clauses usually do not repeat the subject pronoun (e.g. 'the man who lives...', not 'who he lives').",
                )
        for i, token in enumerate(tokens[:-1]):
            if token in {"who", "which", "that", "where"}:
                if i == 0:
                    continue
                if tokens[i - 1] in {"the", "a", "an"}:
                    continue
                if token == "that" and tokens[i - 1] not in COMMON_NOUNS_FOR_RELATIVES and tokens[i - 1] not in {"all", "something", "anything"}:
                    continue
                # Common learner error: "The man who he..."
                if i + 1 < len(tokens) and tokens[i + 1] in ENGLISH_SUBJECT_PRONOUNS:
                    return ValidationIssue(
                        rule_id=self.rule_id,
                        severity=self.severity,
                        message="Relative clauses usually do not repeat the subject pronoun (e.g. 'the man who lives...', not 'who he lives').",
                    )
        return None


class GerundInfinitiveCommonRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        tokens = analysis.tokens
        for i, token in enumerate(tokens[:-1]):
            nxt = tokens[i + 1]
            nxt_form = _verb_form_at(analysis, i + 1)
            if token in GERUND_VERBS and nxt == "to":
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message=f"After '{token}', English commonly uses a gerund (e.g. '{token} doing').",
                )
            if token in TO_INFINITIVE_VERBS and (nxt_form == "participle_ing" or _is_ing(nxt)):
                if _is_likely_ing_adjective(tokens, i + 1):
                    continue
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message=f"After '{token}', English commonly uses 'to + base verb' (e.g. '{token} to do').",
                )
        return None


class DeterminersQuantifiersBasicRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        tokens = analysis.tokens
        noun_phrases = getattr(analysis, "noun_phrases", []) or []

        for np in noun_phrases:
            q = np.quantifier
            c = np.countability_guess
            if q in {"a_lot_of", "lots_of"} and c is not None:
                if c == "countable" or (c == "countable_singular_or_unknown" and np.head_token in COUNTABLE_HINT_NOUNS):
                    return ValidationIssue(
                        rule_id=self.rule_id,
                        severity=self.severity,
                        message="Use a plural countable noun (or an uncountable noun) after 'a lot of/lots of' (e.g. 'a lot of cars', 'lots of water').",
                    )
            if q == "a_number_of" and c is not None:
                if c in {"uncountable", "countable", "countable_singular_or_unknown"}:
                    return ValidationIssue(
                        rule_id=self.rule_id,
                        severity=self.severity,
                        message="Use a plural countable noun after 'a number of' (e.g. 'a number of students').",
                    )
            if q not in {"much", "many", "few", "little"} or c is None:
                continue
            if q == "much" and c in {"countable_plural"}:
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="Use 'many' with countable plural nouns (e.g. 'many books').",
                )
            if q == "many" and c == "uncountable":
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="Use 'much' with uncountable nouns (e.g. 'much information').",
                )
            if q == "few" and c == "uncountable":
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="Use 'little' with uncountable nouns (e.g. 'little money').",
                )
            if q == "little" and c in {"countable_plural"}:
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="Use 'few' with countable plural nouns (e.g. 'few books').",
                )

        for i in range(len(tokens) - 1):
            q, n = tokens[i], tokens[i + 1]
            if q == "much" and n in COUNTABLE_HINT_NOUNS:
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="Use 'many' with countable plural nouns (e.g. 'many books').",
                )
            if q == "many" and n in UNCOUNTABLE_HINT_NOUNS:
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="Use 'much' with uncountable nouns (e.g. 'much information').",
                )
            if q == "few" and n in UNCOUNTABLE_HINT_NOUNS:
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="Use 'little' with uncountable nouns (e.g. 'little money').",
                )
            if q == "little" and n in COUNTABLE_HINT_NOUNS:
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="Use 'few' with countable plural nouns (e.g. 'few books').",
                )
            if q == "a" and n == "lot" and (i + 2 >= len(tokens) or tokens[i + 2] != "of"):
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="Use 'a lot of' (include 'of').",
                )
        return None


class SomeAnyRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        tokens = analysis.tokens
        if analysis.sentence_type == "interrogative" and "some" in tokens and not any(t in {"would", "could"} for t in tokens):
            return ValidationIssue(
                rule_id=self.rule_id,
                severity=self.severity,
                message="In most questions, use 'any' rather than 'some' (except offers/requests like 'Would you like some...?').",
            )
        if analysis.polarity == "negative" and "some" in tokens:
            return ValidationIssue(
                rule_id=self.rule_id,
                severity=self.severity,
                message="In most negative sentences, use 'any' rather than 'some'.",
            )
        return None


class PhrasalVerbBasicRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        tokens = analysis.tokens
        for i in range(len(tokens) - 1):
            verb = tokens[i]
            part = tokens[i + 1]
            if verb in PHRASAL_BASIC and part in COMMON_PREPOSITIONS | {"up", "off", "on", "out"}:
                if part not in PHRASAL_BASIC[verb]:
                    expected = "/".join(sorted(PHRASAL_BASIC[verb]))
                    return ValidationIssue(
                        rule_id=self.rule_id,
                        severity=self.severity,
                        message=f"Common phrasal verb with '{verb}' here is usually '{verb} {expected}'.",
                    )
        return None


class IndirectQuestionFormRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        tokens = analysis.tokens
        triggers = {"know", "wonder", "ask", "tell", "say", "explain"}
        clauses = _iter_clauses(analysis)
        for idx, clause in enumerate(clauses):
            clause_tokens = _clause_tokens(analysis, clause)
            if len(clause_tokens) < 2:
                continue
            if clause_tokens[0] not in WH_QUESTION_WORDS or clause_tokens[1] not in QUESTION_AUXILIARIES:
                continue
            if idx == 0:
                continue
            prev_tokens = _clause_tokens(analysis, clauses[idx - 1])
            if prev_tokens and any(t in triggers for t in prev_tokens):
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="In indirect questions, use statement order (e.g. 'Do you know where he lives?').",
                )
        for i in range(len(tokens) - 3):
            if tokens[i] not in triggers:
                continue
            if tokens[i + 1] in WH_QUESTION_WORDS and tokens[i + 2] in QUESTION_AUXILIARIES:
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="In indirect questions, use statement order (e.g. 'Do you know where he lives?').",
                )
        return None
