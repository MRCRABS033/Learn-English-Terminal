from .shared import *

class RequiredVerbRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        if not analysis.cleaned_text:
            return ValidationIssue(
                rule_id=self.rule_id,
                severity=self.severity,
                message="The sentence is empty.",
            )

        if analysis.has_verb:
            return None

        return ValidationIssue(
            rule_id=self.rule_id,
            severity=self.severity,
            message="Complete English sentences usually need a verb.",
        )


class ExplicitSubjectRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        if not analysis.cleaned_text or not analysis.is_complete_sentence:
            return None

        if analysis.subject_requirement != "required":
            return None

        if analysis.has_explicit_subject:
            return None

        return ValidationIssue(
            rule_id=self.rule_id,
            severity=self.severity,
            message="In English, complete declarative/interrogative sentences usually need an explicit subject.",
        )


class ImperativeSubjectWarningRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        if analysis.sentence_type != "imperative":
            return None

        if not analysis.has_explicit_subject:
            return None

        return ValidationIssue(
            rule_id=self.rule_id,
            severity=self.severity,
            message="Imperatives often omit the subject because 'you' is implied.",
        )


class QuestionAuxiliaryRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        if analysis.sentence_type != "interrogative":
            return None

        tokens = analysis.tokens
        if not tokens:
            return None

        if analysis.starts_with_auxiliary or _has_wh_aux_opening(tokens):
            return None

        return ValidationIssue(
            rule_id=self.rule_id,
            severity=self.severity,
            message="English questions usually begin with an auxiliary, including wh-questions (e.g. 'Where do you live?').",
        )


class ToBeWithoutDoRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        if not analysis.tokens:
            return None

        tokens = analysis.tokens
        if not any(token in TO_BE_FORMS for token in tokens):
            return None

        if not any(token in BASE_AUXILIARIES for token in tokens):
            return None

        return ValidationIssue(
            rule_id=self.rule_id,
            severity=self.severity,
            message="With 'to be', do/does/did is usually not used for basic questions or negatives.",
        )


class ThirdPersonSingularSRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        if analysis.sentence_type != "declarative":
            return None
        if analysis.subject_token not in SINGULAR_THIRD_SUBJECTS:
            return None
        if analysis.polarity == "negative":
            return None

        tokens = analysis.tokens
        if len(tokens) < 2:
            return None

        if tokens[1] in TO_BE_FORMS or tokens[1] in BASE_AUXILIARIES:
            return None

        if tokens[1] in {"work", "like", "love", "want", "need", "eat", "run", "study", "play", "live"}:
            return ValidationIssue(
                rule_id=self.rule_id,
                severity=self.severity,
                message="With he/she/it in present simple, the main verb usually takes -s (e.g. 'He works').",
            )

        return None


class PresentSimpleDoNegationRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        tokens = analysis.tokens
        if len(tokens) < 3:
            return None

        subject = analysis.subject_token or (tokens[0] if tokens else None)
        if subject not in ENGLISH_SUBJECT_PRONOUNS:
            return None

        # "He not study" -> needs do/does + not
        if analysis.sentence_type == "declarative" and len(tokens) >= 3 and tokens[1] == "not":
            if tokens[2] not in TO_BE_FORMS and tokens[2] not in MODAL_VERBS:
                aux = "does" if subject in SINGULAR_THIRD_SUBJECTS else "do"
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message=f"In present simple negatives, use '{aux} not + base verb' (e.g. '{subject} {aux} not study').",
                )

        # "He doesn't studies" / "They don't works"
        for idx, token in enumerate(tokens):
            if token not in {"don't", "doesn't"}:
                continue
            verb_idx, verb = _find_next_token(tokens, idx + 1, skip=NEGATIVE_TOKENS)
            if verb is None:
                continue
            if verb in ENGLISH_SUBJECT_PRONOUNS:
                continue
            verb_form = _verb_form_at(analysis, verb_idx) if verb_idx is not None else None
            if (
                verb_form in {"v3sg", "past", "participle_ed", "participle_ing"}
                or _is_likely_inflected_s_form(verb)
                or verb.endswith(("ed", "ing"))
            ):
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="After don't/doesn't, use the base form of the verb (e.g. 'doesn't study', not 'doesn't studies').",
                )

            if subject in SINGULAR_THIRD_SUBJECTS and token == "don't":
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="Use 'doesn't' with he/she/it in present simple negatives.",
                )
            if subject in NON_THIRD_SUBJECTS and token == "doesn't":
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="Use 'don't' with I/you/we/they in present simple negatives.",
                )

        return None


class ArticleSoundRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        tokens = analysis.tokens
        for idx, token in enumerate(tokens[:-1]):
            if token not in {"a", "an"}:
                continue
            next_word = tokens[idx + 1]
            if not _is_word(next_word):
                continue
            expected = _expected_indefinite_article(next_word)
            if token != expected:
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message=f"Use '{expected}' before '{next_word}' based on its initial sound.",
                )
        return None


class ArticleCountabilityRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        tokens = analysis.tokens
        if not tokens:
            return None

        # a/an + (adj)* + uncountable noun -> usually incorrect in learner usage.
        for i, token in enumerate(tokens[:-1]):
            if token not in {"a", "an"}:
                continue
            head_idx = None
            for j in range(i + 1, min(i + 4, len(tokens))):
                pos = _pos_at(analysis, j)
                if pos in {"adjective", "adverb"}:
                    continue
                head_idx = j
                break
            if head_idx is None:
                continue
            head = tokens[head_idx]
            if _verb_form_at(analysis, head_idx) in {"base", "v3sg", "past", "participle_ing", "participle_ed"}:
                continue
            noun_countability = getattr(_feature_at(analysis, head_idx), "noun_countability_guess", None)
            if noun_countability == "uncountable":
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message=f"'{head}' suele ser incontable; normalmente no se usa con '{token}' en este sentido (e.g. no 'an information').",
                )

        # pronoun + be + singular countable noun (without article/determiner) -> "He is teacher"
        if (
            len(tokens) >= 3
            and tokens[0] in ENGLISH_SUBJECT_PRONOUNS
            and tokens[1] in TO_BE_FORMS
            and tokens[2] not in SUBJECT_DETERMINERS
        ):
            f2 = _feature_at(analysis, 2)
            pos2 = getattr(f2, "pos_guess", None) if f2 is not None else None
            countability = getattr(f2, "noun_countability_guess", None) if f2 is not None else None
            if pos2 == "adjective" and countability is None:
                adjective_like_suffixes = ("ant", "ent", "ful", "ous", "ive", "able", "ible", "al", "ic")
                if (
                    tokens[2] in COMMON_ADJECTIVES
                    or tokens[2] in COMMON_ED_PREDICATE_ADJECTIVES
                    or (len(tokens) > 3 and tokens[3] == "to")
                    or tokens[2].endswith(adjective_like_suffixes)
                ):
                    return None
            if countability is None:
                countability = guess_noun_countability(tokens[2])
            if pos2 in {"verb", "verb_participle", "auxiliary"}:
                return None
            if countability in {"countable", "countable_singular_or_unknown"}:
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="With a singular countable predicate noun, English often needs an article/determiner (e.g. 'He is a teacher').",
                )

        return None


class ArticleGenericReferenceRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        tokens = analysis.tokens
        if len(tokens) < 4 or analysis.sentence_type != "declarative":
            return None

        for np in getattr(analysis, "noun_phrases", []):
            if np.role_guess != "subject" or np.start_idx != 0:
                continue
            if np.quantifier is not None:
                continue
            if np.determiner != "the" or np.countability_guess != "countable_plural":
                continue
            if _relative_clause_starts_after_np(analysis, np):
                continue
            if np.end_idx + 2 >= len(tokens):
                continue
            if tokens[np.end_idx + 1] not in {"are", "were"}:
                continue
            pred_pos = _pos_at(analysis, np.end_idx + 2)
            if pred_pos not in {"adjective", "noun"}:
                continue
            if any(t in {"in", "on", "at", "near", "here", "there", "these", "those"} for t in tokens[np.end_idx + 2 :]):
                continue
            if any(linker in {"which", "that", "who"} for linker in getattr(analysis, "clause_linkers_detected", [])):
                continue
            return ValidationIssue(
                rule_id=self.rule_id,
                severity=self.severity,
                message="For general statements about a whole class, English often uses a zero article plural (e.g. 'Dogs are friendly' rather than 'The dogs are friendly').",
            )

        # High-precision starter heuristic:
        # "The dogs are friendly." (generic claim) -> often prefer "Dogs are friendly."
        # We only flag simple noun phrase subjects at sentence start followed by be + adjective.
        if tokens[0] != "the":
            return None
        subj_feature = _feature_at(analysis, 1)
        be_feature = _feature_at(analysis, 2)
        pred_feature = _feature_at(analysis, 3)
        if subj_feature is None or be_feature is None or pred_feature is None:
            return None

        if subj_feature.pos_guess != "noun":
            return None
        if getattr(subj_feature, "noun_countability_guess", None) != "countable_plural":
            return None
        if tokens[2] not in {"are", "were"}:
            return None
        if pred_feature.pos_guess not in {"adjective", "noun"}:
            return None

        # Skip likely specific-reference contexts signaled by relative clause linkers/comma chunks.
        if any(linker in {"which", "that", "who"} for linker in getattr(analysis, "clause_linkers_detected", [])):
            return None
        if any(t in {"in", "on", "at", "near", "here", "there", "these", "those"} for t in tokens[3:]):
            return None

        return ValidationIssue(
            rule_id=self.rule_id,
            severity=self.severity,
            message="For general statements about a whole class, English often uses a zero article plural (e.g. 'Dogs are friendly' rather than 'The dogs are friendly').",
        )


class ArticleBareSingularCountableRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        tokens = analysis.tokens
        if len(tokens) < 2 or analysis.sentence_type != "declarative":
            return None
        if tokens[0] in ENGLISH_SUBJECT_PRONOUNS | SUBJECT_DETERMINERS:
            return None

        f0 = _feature_at(analysis, 0)
        if f0 is None:
            return None
        if f0.pos_guess in {"verb", "verb_participle", "auxiliary"}:
            return None

        countability = getattr(f0, "noun_countability_guess", None) or guess_noun_countability(tokens[0])
        if countability not in {"countable", "countable_singular_or_unknown"}:
            return None

        # Skip likely names/proper nouns (very rough): not in common noun lexicon and no article-related pattern.
        if tokens[0] not in COUNTABLE_HINT_NOUNS and tokens[0] not in COMMON_NOUNS_FOR_RELATIVES and countability != "countable":
            return None

        # Trigger only in simple high-confidence starter patterns.
        if tokens[1] in TO_BE_FORMS | BASE_AUXILIARIES | MODAL_VERBS:
            return ValidationIssue(
                rule_id=self.rule_id,
                severity=self.severity,
                message="A singular countable noun as subject usually needs an article/determiner (e.g. 'A dog is friendly') or a plural form for generic statements ('Dogs are friendly').",
            )
        f1 = _feature_at(analysis, 1)
        if f1 is not None and f1.pos_guess == "verb" and f1.verb_form_guess in {"v3sg", "base"}:
            return ValidationIssue(
                rule_id=self.rule_id,
                severity=self.severity,
                message="A singular countable noun as subject usually needs an article/determiner (e.g. 'A student studies...').",
            )
        if _is_likely_inflected_s_form(tokens[1]) and tokens[1] not in COMMON_PREPOSITIONS:
            return ValidationIssue(
                rule_id=self.rule_id,
                severity=self.severity,
                message="A singular countable noun as subject usually needs an article/determiner (e.g. 'A student studies...').",
            )
        return None


class ArticleBareSingularObjectRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        tokens = analysis.tokens
        if len(tokens) < 3 or analysis.sentence_type != "declarative":
            return None

        common_transitives = {
            "have",
            "has",
            "need",
            "want",
            "buy",
            "bought",
            "find",
            "found",
            "see",
            "saw",
            "read",
            "build",
            "built",
            "write",
            "wrote",
            "take",
            "took",
            "get",
            "got",
        }

        for np in getattr(analysis, "noun_phrases", []):
            if np.role_guess != "object":
                continue
            if np.determiner is not None:
                continue
            if np.countability_guess not in {"countable", "countable_singular_or_unknown"}:
                continue
            if np.head_idx <= 0:
                continue
            if tokens[np.head_idx - 1] not in common_transitives:
                continue
            # Avoid likely compounds ("car insurance") if next token is noun.
            if np.end_idx + 1 < len(tokens) and _pos_at(analysis, np.end_idx + 1) == "noun":
                continue
            return ValidationIssue(
                rule_id=self.rule_id,
                severity=self.severity,
                message="A singular countable object often needs an article/determiner (e.g. 'I bought a car').",
            )

        for i in range(len(tokens) - 1):
            if tokens[i] not in common_transitives:
                continue
            obj_idx = i + 1
            if tokens[obj_idx] in SUBJECT_DETERMINERS | ENGLISH_SUBJECT_PRONOUNS:
                continue
            obj_feature = _feature_at(analysis, obj_idx)
            obj_pos = getattr(obj_feature, "pos_guess", None) if obj_feature else None
            obj_countability = getattr(obj_feature, "noun_countability_guess", None) if obj_feature else None
            if obj_countability is None:
                obj_countability = guess_noun_countability(tokens[obj_idx])

            if obj_pos in {"verb", "verb_participle", "auxiliary"}:
                continue
            if obj_countability not in {"countable", "countable_singular_or_unknown"}:
                continue

            # Skip likely mass/discipline object phrases and compounds (e.g. "car insurance")
            if obj_idx + 1 < len(tokens):
                next_pos = _pos_at(analysis, obj_idx + 1)
                if next_pos == "noun":
                    continue
                if tokens[obj_idx + 1] in COMMON_PREPOSITIONS:
                    continue

            return ValidationIssue(
                rule_id=self.rule_id,
                severity=self.severity,
                message="A singular countable object often needs an article/determiner (e.g. 'I bought a car').",
            )

        return None


class ArticleUncountableGenericTheRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        tokens = analysis.tokens
        if len(tokens) < 4 or analysis.sentence_type != "declarative":
            return None
        if tokens[0] != "the":
            return None

        subject_np = next(
            (
                np
                for np in getattr(analysis, "noun_phrases", [])
                if np.role_guess == "subject" and np.start_idx == 0
            ),
            None,
        )
        if subject_np is not None and _relative_clause_starts_after_np(analysis, subject_np):
            return None

        noun_feature = _feature_at(analysis, 1)
        noun_countability = getattr(noun_feature, "noun_countability_guess", None) if noun_feature else None
        if noun_countability is None:
            noun_countability = guess_noun_countability(tokens[1])
        if noun_countability != "uncountable":
            return None

        if tokens[2] not in {"is", "was"}:
            return None
        pred_pos = _pos_at(analysis, 3)
        if pred_pos not in {"adjective", "noun"}:
            return None

        # Avoid clearly specific contexts.
        if any(t in {"here", "there", "this", "that", "these", "those"} for t in tokens[3:]):
            return None
        if any(t in COMMON_PREPOSITIONS for t in tokens[3:6]):
            return None
        if any(linker in {"which", "that", "who"} for linker in getattr(analysis, "clause_linkers_detected", [])):
            return None

        return ValidationIssue(
            rule_id=self.rule_id,
            severity=self.severity,
            message="For general statements with many uncountable nouns, English often uses zero article (e.g. 'Music is important') rather than 'the + noun'.",
        )


class AdjectiveNounOrderRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        tokens = analysis.tokens
        if len(tokens) < 3:
            return None

        for i in range(len(tokens) - 2):
            det, maybe_noun, maybe_adj = tokens[i], tokens[i + 1], tokens[i + 2]
            if det not in SUBJECT_DETERMINERS:
                continue
            if maybe_adj not in COMMON_ADJECTIVES:
                continue
            if maybe_noun in COMMON_ADJECTIVES or maybe_noun in TO_BE_FORMS or maybe_noun in MODAL_VERBS:
                continue
            if _looks_like_base_verb(maybe_noun) and maybe_noun not in {"house", "car", "book", "apple"}:
                continue

            return ValidationIssue(
                rule_id=self.rule_id,
                severity=self.severity,
                message="In English noun phrases, adjectives usually come before the noun (e.g. 'a big house').",
            )

        return None


class BasicSVOOrderRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        if analysis.sentence_type != "declarative":
            return None

        tokens = analysis.tokens
        if len(tokens) < 3:
            return None

        if tokens[0] not in ENGLISH_SUBJECT_PRONOUNS:
            return None

        # Allow adverbs after subject: "I really like..."
        if len(tokens) >= 3 and tokens[1] not in (TO_BE_FORMS | BASE_AUXILIARIES | MODAL_VERBS | {"have", "has", "had"}):
            if tokens[1] in NEGATIVE_TOKENS:
                return None
            if tokens[1] in COMMON_ADVERBS:
                return None

            if (
                not _looks_like_clear_base_verb(tokens[1])
                and len(tokens) >= 3
                and _looks_like_clear_base_verb(tokens[2])
            ):
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="Basic English declarative order is usually Subject + Verb + Complement (e.g. 'I eat pizza').",
                )

        return None


class PrepositionCollocationRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        tokens = analysis.tokens
        for idx, token in enumerate(tokens[:-1]):
            next_token = tokens[idx + 1]

            if token == "interested" and next_token in COMMON_PREPOSITIONS and next_token != "in":
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="Use 'interested in' (e.g. 'I am interested in music').",
                )

            if token.startswith("depend") and next_token in COMMON_PREPOSITIONS and next_token not in {"on", "upon"}:
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="Use 'depend on' (or 'depend upon') in this collocation.",
                )

            if token == "good" and next_token in {"in", "on", "of"}:
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="For skills/ability, English commonly uses 'good at' (e.g. 'good at math').",
                )
            if token == "different" and next_token == "than":
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="Common learner-safe collocations are usually 'different from' (and sometimes 'different to', dialect-dependent), not typically 'different than' here.",
                )
            if token in {"reason", "answer", "solution", "problem", "interest"} and next_token in COMMON_PREPOSITIONS:
                expected_map = {
                    "reason": {"for"},
                    "answer": {"to"},
                    "solution": {"to"},
                    "problem": {"with"},
                    "interest": {"in"},
                }
                allowed = expected_map.get(token, set())
                if next_token not in allowed:
                    opts = " / ".join(sorted(allowed))
                    return ValidationIssue(
                        rule_id=self.rule_id,
                        severity=self.severity,
                        message=f"Common collocation is usually '{token} {opts}'.",
                    )

        return None


class ModalBaseVerbRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        if analysis.modal_token is None:
            return None

        tokens = analysis.tokens
        try:
            idx = tokens.index(analysis.modal_token)
        except ValueError:
            return None

        next_idx, next_token = _find_verb_after_aux(tokens, idx)
        if next_token is None:
            return None

        if next_token == "to":
            return ValidationIssue(
                rule_id=self.rule_id,
                severity=self.severity,
                message="After modal verbs (can/should/must...), use the base verb directly (not 'to + verb').",
            )

        next_form = _verb_form_at(analysis, next_idx) if next_idx is not None else None
        next_pos = _pos_at(analysis, next_idx) if next_idx is not None else None
        if (
            next_token not in {"is", "was"}
            and (
                next_form in {"v3sg", "past", "participle_ed", "participle_ing"}
                or (
                    next_pos in {"verb", "verb_participle"}
                    and next_form not in {"base", None}
                )
                or _is_likely_inflected_s_form(next_token)
                or next_token.endswith(("ed", "ing"))
            )
        ):
            return ValidationIssue(
                rule_id=self.rule_id,
                severity=self.severity,
                message="After modal verbs (can/should/must...), use the base form of the verb.",
            )

        # Avoid combinations like "can is", "should are"
        if next_token in TO_BE_FORMS and next_token != "be":
            return ValidationIssue(
                rule_id=self.rule_id,
                severity=self.severity,
                message="After modals, use 'be' (base form), not 'is/are/was/were'.",
            )

        if next_idx is not None and next_idx + 1 < len(tokens):
            following = tokens[next_idx + 1]
            if next_token in BASE_AUXILIARIES and following in COMMON_BASE_VERBS:
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="Avoid stacking modal + do/does/did in simple clauses (e.g. use 'can go', not 'can do go').",
                )

        return None


class ModalCombinationRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        tokens = analysis.tokens
        for i in range(len(tokens) - 1):
            if tokens[i] in MODAL_VERBS and tokens[i + 1] in MODAL_VERBS:
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="English usually does not combine two core modals directly (e.g. not 'can should').",
                )
        return None


class SubjectBeAgreementRule(GrammarRule):
    def evaluate(self, analysis: SentenceAnalysis) -> ValidationIssue | None:
        if analysis.subject_number_guess is None or analysis.be_form_token is None:
            return None

        be_form = analysis.be_form_token
        subject_number = analysis.subject_number_guess

        if subject_number == "plural" and be_form in {"is", "was"}:
            return ValidationIssue(
                rule_id=self.rule_id,
                severity=self.severity,
                message="Plural subjects usually use 'are' (present) or 'were' (past), not 'is/was'.",
            )

        if subject_number == "singular" and be_form in {"are", "were"}:
            return ValidationIssue(
                rule_id=self.rule_id,
                severity=self.severity,
                message="Singular subjects usually use 'is' (present) or 'was' (past), not 'are/were'.",
            )

        if subject_number == "singular" and be_form == "am":
            if analysis.subject_token not in {"i"}:
                return ValidationIssue(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="Use 'am' with 'I' (e.g. 'I am ...').",
                )

        return None
