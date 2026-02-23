from .shared import *

class PresentContinuousRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        tokens = analysis.tokens
        if not tokens:
            return None

        for idx, token in enumerate(tokens):
            if token not in {"am", "is", "are"}:
                continue

            next_idx, next_token = _find_verb_after_aux(tokens, idx)
            if next_token is None:
                continue
            next_pos = _pos_at(analysis, next_idx) if next_idx is not None else None
            if next_token in SUBJECT_DETERMINERS or next_token in COMMON_ADJECTIVES:
                continue
            if next_token in COMMON_ED_PREDICATE_ADJECTIVES:
                continue
            if next_pos == "adjective":
                continue
            if next_idx is not None and _is_likely_ing_adjective(tokens, next_idx):
                continue
            if next_token == "going":
                # likely "be going to" future
                continue
            if next_token in TO_BE_FORMS:
                continue
            next_form = _verb_form_at(analysis, next_idx) if next_idx is not None else None
            if next_form != "participle_ing" and not _is_ing(next_token):
                if _looks_like_base_verb(next_token) or _is_ed(next_token):
                    return ValidationIssue(
                        rule_id=self.rule_id,
                        severity=self.severity,
                        message="Present continuous uses am/is/are + verb-ing (e.g. 'She is studying').",
                    )

        return None


class StativeVerbContinuousRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        if analysis.primary_tense_guess not in {"present_continuous", "past_continuous"}:
            return None
        tokens = analysis.tokens
        for i, token in enumerate(tokens[:-1]):
            if token not in {"am", "is", "are", "was", "were"}:
                continue
            next_idx, next_token = _find_verb_after_aux(tokens, i)
            if next_idx is None or next_token is None:
                continue
            if _verb_form_at(analysis, next_idx) != "participle_ing":
                continue
            base_like = next_token[:-3] if next_token.endswith("ing") else next_token
            if next_token == "having":
                # Dynamic "have" uses are common: have lunch / have a shower.
                if any(t in {"lunch", "dinner", "breakfast", "shower", "bath", "fun", "trouble"} for t in tokens[next_idx + 1 :]):
                    continue
                base_like = "have"
            if next_token == "thinking":
                # "thinking about/of" is commonly dynamic.
                if any(t in {"about", "of"} for t in tokens[next_idx + 1 : next_idx + 3]):
                    continue
                base_like = "think"
            if next_token == "seeing":
                # "seeing someone" / meetings can be dynamic.
                if any(t in {"a", "an", "the", "him", "her", "them"} for t in tokens[next_idx + 1 : next_idx + 3]):
                    continue
                base_like = "see"

            if base_like in STATIVE_VERBS:
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="This verb is often stative and usually not used in continuous form in this meaning (e.g. 'I know', not 'I am knowing').",
                )
        return None


class PastContinuousRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        tokens = analysis.tokens
        for idx, token in enumerate(tokens):
            if token not in {"was", "were"}:
                continue

            next_idx, next_token = _find_verb_after_aux(tokens, idx)
            if next_token is None:
                continue
            next_pos = _pos_at(analysis, next_idx) if next_idx is not None else None
            if next_token in SUBJECT_DETERMINERS or next_token in COMMON_ADJECTIVES:
                continue
            if next_token in COMMON_ED_PREDICATE_ADJECTIVES:
                continue
            if next_pos == "adjective":
                continue
            if next_idx is not None and _is_likely_ing_adjective(tokens, next_idx):
                continue
            if next_token in TO_BE_FORMS:
                continue
            next_form = _verb_form_at(analysis, next_idx) if next_idx is not None else None
            if next_form != "participle_ing" and not _is_ing(next_token):
                if _looks_like_base_verb(next_token) or _is_ed(next_token):
                    return ValidationIssue(
                        rule_id=self.rule_id,
                        severity=self.severity,
                        message="Past continuous uses was/were + verb-ing (e.g. 'They were working').",
                    )

        return None


class PastSimpleRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        tokens = analysis.tokens
        if not tokens:
            return None

        # "did + base verb" (questions / negatives)
        for idx, token in enumerate(tokens):
            if token not in {"did", "didn't"}:
                continue
            verb_idx, verb = _find_verb_after_aux(tokens, idx)
            if verb is None or verb in TO_BE_FORMS:
                continue
            verb_form = _verb_form_at(analysis, verb_idx) if verb_idx is not None else None
            if verb_form in {"past", "participle_ed", "participle_ing", "v3sg"} or verb in COMMON_IRREGULAR_PAST:
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="After 'did/didn't', use the base form of the verb (e.g. 'Did you work?').",
                )

        # Regular past with time marker: "I work yesterday" -> likely missing -ed
        if any(token in PAST_TIME_MARKERS for token in tokens) and analysis.sentence_type == "declarative":
            if tokens[0] in ENGLISH_SUBJECT_PRONOUNS and len(tokens) > 1:
                main = tokens[1]
                if main in {"did", "was", "were", "had"}:
                    return None
                main_form = _verb_form_at(analysis, 1)
                if (
                    (_looks_like_base_verb(main) and not _looks_like_past(main))
                    or main_form == "base"
                ):
                    return ValidationIssue(
                        rule_id=self.rule_id,
                        severity=self.severity,
                        message="For past simple statements, use a past form (regular verbs usually end in -ed).",
                    )

        return None


class FutureWillRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        tokens = analysis.tokens
        if "will" not in tokens:
            return None

        idx = tokens.index("will")
        verb_idx, verb = _find_verb_after_aux(tokens, idx)
        if verb is None:
            return ValidationIssue(
                rule_id=self.rule_id,
                severity=self.severity,
                message="Future with 'will' normally needs a main verb (e.g. 'will study').",
            )

        verb_form = _verb_form_at(analysis, verb_idx) if verb_idx is not None else None
        verb_pos = _pos_at(analysis, verb_idx) if verb_idx is not None else None
        if (
            verb == "to"
            or verb in {"is", "are", "was", "were"}
            or (verb_pos in {"verb", "verb_participle"} and verb_form not in {"base"})
            or (_is_likely_inflected_s_form(verb) or verb.endswith(("ed", "ing")))
        ):
            return ValidationIssue(
                rule_id=self.rule_id,
                severity=self.severity,
                message="Use 'will + base verb' (e.g. 'will study', not 'will studies/worked/studying').",
            )

        return None


class GoingToFutureRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        tokens = analysis.tokens
        for idx in range(len(tokens) - 2):
            if tokens[idx] not in {"am", "is", "are"}:
                continue
            if tokens[idx + 1] != "going" or tokens[idx + 2] != "to":
                continue

            if idx + 3 >= len(tokens):
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="Future with 'going to' needs a base verb after 'to' (e.g. 'is going to study').",
                )

            verb = tokens[idx + 3]
            verb_form = _verb_form_at(analysis, idx + 3)
            verb_pos = _pos_at(analysis, idx + 3)
            if (
                verb in TO_BE_FORMS
                or (verb_pos in {"verb", "verb_participle"} and verb_form not in {"base"})
                or verb.endswith(("s", "ed", "ing"))
            ):
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="Use 'am/is/are + going to + base verb' (e.g. 'are going to play').",
                )

        return None


class PresentPerfectRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        tokens = analysis.tokens
        for idx, token in enumerate(tokens):
            if token not in {"have", "has"}:
                continue
            if idx > 0 and (tokens[idx - 1] in MODAL_VERBS or tokens[idx - 1] in BASE_AUXILIARIES):
                continue

            next_idx, next_token = _find_verb_after_aux(tokens, idx)
            if next_token is None:
                continue

            # Possession / noun phrase ("I have a car") is valid and not present perfect.
            if next_token in SUBJECT_DETERMINERS:
                continue
            if next_token in {"to", "a", "an", "the"}:
                continue

            if next_token in {"went", "ate", "saw", "did", "was", "were"}:
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="Present perfect uses 'have/has + past participle' (e.g. 'has gone', not 'has went').",
                )

            next_form = _verb_form_at(analysis, next_idx) if next_idx is not None else None
            if next_form != "participle_ed" and not _looks_like_participle(next_token):
                if _looks_like_clear_base_verb(next_token) or _is_ing(next_token) or next_form in {"base", "v3sg", "participle_ing"}:
                    return ValidationIssue(
                        rule_id=self.rule_id,
                        severity=self.severity,
                        message="Present perfect uses 'have/has + past participle' (e.g. 'have worked').",
                    )

        return None


class PresentSimpleStructureRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        tokens = analysis.tokens
        if not tokens:
            return None

        # Declarative present simple with subject pronoun.
        if analysis.sentence_type == "declarative" and tokens[0] in ENGLISH_SUBJECT_PRONOUNS and len(tokens) >= 2:
            first_after_subject = tokens[1]

            if first_after_subject in {"do", "does"}:
                verb_idx, verb = _find_verb_after_aux(tokens, 1)
                if verb is None:
                    return ValidationIssue(
                        rule_id=self.rule_id,
                        severity=self.severity,
                        message="Present simple negatives/questions with do/does still need a main verb in base form.",
                    )
                verb_form = _verb_form_at(analysis, verb_idx) if verb_idx is not None else None
                if verb_form in {"v3sg", "past", "participle_ed", "participle_ing"} or verb.endswith(("s", "ed", "ing")):
                    return ValidationIssue(
                        rule_id=self.rule_id,
                        severity=self.severity,
                        message="After do/does in present simple, use the base verb.",
                    )

        # Wh-question support: "Where you live?" -> needs auxiliary
        if analysis.sentence_type == "interrogative" and tokens[0] in WH_QUESTION_WORDS:
            if len(tokens) >= 2 and tokens[1] not in QUESTION_AUXILIARIES:
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="Most wh-questions need an auxiliary after the wh-word (e.g. 'Where do you live?').",
                )

        return None


class PresentPerfectVsPastSimpleUsageRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        tokens = analysis.tokens
        if not tokens:
            return None

        for idx, token in enumerate(tokens):
            if token not in {"have", "has"}:
                continue
            _, next_token = _find_verb_after_aux(tokens, idx)
            if next_token is None:
                continue
            if _looks_like_participle(next_token) and _has_past_time_marker(tokens):
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="Present perfect usually does not combine with finished past-time markers like 'yesterday/last/ago'.",
                )
        return None


class PastContinuousInterruptionRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        tokens = analysis.tokens
        if "when" not in tokens:
            return None

        when_idx = tokens.index("when")
        has_past_cont = False
        for i, token in enumerate(tokens[:when_idx]):
            next_form = _verb_form_at(analysis, i + 1) if i + 1 < len(tokens) else None
            if token in {"was", "were"} and i + 1 < len(tokens) and (next_form == "participle_ing" or _is_ing(tokens[i + 1])):
                has_past_cont = True
                break
        if not has_past_cont:
            return None

        after_when = tokens[when_idx + 1 :]
        if not after_when:
            return ValidationIssue(
                rule_id=self.rule_id,
                severity=self.severity,
                message="After 'when' in interruption patterns, add a clause (e.g. 'when he called').",
            )

        if any(
            after_when[j] in {"was", "were"}
            and j + 1 < len(after_when)
            and (
                _verb_form_at(analysis, when_idx + 1 + j + 1) == "participle_ing"
                or _is_ing(after_when[j + 1])
            )
            for j in range(len(after_when) - 1)
        ):
            return ValidationIssue(
                rule_id=self.rule_id,
                severity=self.severity,
                message="In patterns like 'I was studying when...', the 'when' clause is often in past simple.",
            )
        if any(t == "did" for t in after_when):
            return None
        if any(_looks_like_past(t) for t in after_when):
            return None
        return None
