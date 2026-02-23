import unittest

from Services.validation.rule_engine import RuleEngine


class UserSimulationFlowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = RuleEngine()

    def _validate(self, text: str):
        return self.engine.validate_sentence(text)

    @staticmethod
    def _warning_ids(result) -> set[str]:
        return {issue.rule_id for issue in result.warnings}

    @staticmethod
    def _pattern_ids(result) -> set[str]:
        return {issue.rule_id for issue in result.pattern_warnings}

    def test_user_valid_complex_sentence_avoids_passive_false_positive(self) -> None:
        result = self._validate("I have been working all morning, but I still need a break.")
        warnings = self._warning_ids(result)
        self.assertNotIn("en.passive_advanced", warnings)
        self.assertNotIn("en.present_continuous", warnings)
        self.assertNotIn("en.passive_basic", warnings)

    def test_user_reported_speech_error_with_reason_clause(self) -> None:
        result = self._validate("She suggested me to go early because the weather was getting worse.")
        warnings = self._warning_ids(result)
        self.assertIn("en.reported_speech_advanced", warnings)

    def test_user_fronted_not_only_error(self) -> None:
        result = self._validate("Not only he apologized, but he also helped us with the problem.")
        warnings = self._warning_ids(result)
        self.assertIn("en.inversion_emphasis", warnings)

    def test_user_quantity_subject_number_agreement(self) -> None:
        result = self._validate("The number of students are waiting outside.")
        warnings = self._warning_ids(result)
        patterns = self._pattern_ids(result)
        self.assertIn("en.subject_be_agreement", warnings)
        self.assertIn("en.pattern.be_agreement_singular", patterns)

    def test_user_predicative_adjective_sentence_avoids_article_and_progressive_false_positives(self) -> None:
        result = self._validate("It is important to study regularly.")
        warnings = self._warning_ids(result)
        self.assertNotIn("en.article_countability", warnings)
        self.assertNotIn("en.cleft_sentences", warnings)
        self.assertNotIn("en.present_continuous", warnings)

    def test_user_nonrestrictive_relative_clause_only_gets_relative_warning(self) -> None:
        result = self._validate("My car, that is red, is outside.")
        warnings = self._warning_ids(result)
        self.assertIn("en.relative_clauses_advanced", warnings)
        self.assertNotIn("en.present_continuous", warnings)
        self.assertNotIn("en.passive_basic", warnings)

    def test_user_embedded_question_inversion_error(self) -> None:
        result = self._validate("I wonder where does he live.")
        warnings = self._warning_ids(result)
        self.assertIn("en.indirect_questions", warnings)
        self.assertIn("en.noun_clauses_complex", warnings)

    def test_user_collocation_with_intervening_adverb_uses_lexical_hint(self) -> None:
        result = self._validate("They depend directly of us for the solution.")
        warnings = self._warning_ids(result)
        self.assertNotIn("en.preposition_collocation", warnings)  # lexical support handles this variant
        self.assertTrue(any("depend" in hint and "se usa normalmente" in hint for hint in result.lexical_hints))

    def test_user_quantified_plural_subject_avoids_be_agreement_false_positive(self) -> None:
        result = self._validate("A lot of the students are friendly and interested in music.")
        warnings = self._warning_ids(result)
        patterns = self._pattern_ids(result)
        self.assertNotIn("en.subject_be_agreement", warnings)
        self.assertNotIn("en.pattern.be_agreement_singular", patterns)
        self.assertNotIn("en.present_continuous", warnings)
        self.assertNotIn("en.passive_basic", warnings)

    def test_user_quantifier_error_sentence_surfaces_targeted_quantifier_warning(self) -> None:
        result = self._validate("Such a big houses are expensive in this city.")
        warnings = self._warning_ids(result)
        self.assertIn("en.quantifiers_determiners_advanced", warnings)


if __name__ == "__main__":
    unittest.main()
