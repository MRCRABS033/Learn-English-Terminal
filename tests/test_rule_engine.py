import unittest
from unittest.mock import patch

from Services.validation.rule_engine import RuleEngine


class RuleEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = RuleEngine()

    def test_detects_critical_warning_for_adjective_noun_order(self) -> None:
        result = self.engine.validate_sentence("the house big is")
        warning_ids = {issue.rule_id for issue in result.warnings}
        self.assertIn("en.adjective_noun_order", warning_ids)

    def test_wh_question_valid_does_not_warn_auxiliary(self) -> None:
        result = self.engine.validate_sentence("Where do you live?")
        warning_ids = {issue.rule_id for issue in result.warnings}
        self.assertNotIn("en.question_auxiliary", warning_ids)
        self.assertNotIn("en.present_simple_structure", warning_ids)

    def test_non_blocking_collocation_warning_exists(self) -> None:
        result = self.engine.validate_sentence("I am interested on music.")
        warning_ids = {issue.rule_id for issue in result.warnings}
        self.assertIn("en.preposition_collocation", warning_ids)

    def test_ing_adjective_after_want_does_not_trigger_gerund_infinitive_rule(self) -> None:
        result = self.engine.validate_sentence("I want interesting books.")
        warning_ids = {issue.rule_id for issue in result.warnings}
        self.assertNotIn("en.gerund_infinitive_common", warning_ids)

    def test_predicative_ing_adjective_after_be_does_not_trigger_present_continuous_rule(self) -> None:
        result = self.engine.validate_sentence("She is interesting.")
        warning_ids = {issue.rule_id for issue in result.warnings}
        self.assertNotIn("en.present_continuous", warning_ids)

    def test_pattern_hints_are_stored_separately_and_aggregated(self) -> None:
        result = self.engine.validate_sentence("He work every day.")
        self.assertTrue(result.pattern_hints)
        self.assertTrue(result.pattern_warnings)
        self.assertIn("en.pattern.third_person_s_hint", {issue.rule_id for issue in result.pattern_warnings})
        self.assertIn(
            "Recuerda la concordancia en presente simple: he / she / it normalmente usa verbo + s.",
            result.pattern_hints,
        )
        self.assertTrue(set(result.pattern_hints).issubset(set(result.suggestions)))

    def test_lexical_hints_are_stored_separately_and_aggregated(self) -> None:
        with patch.object(self.engine.dictionary_lexicon, "semantic_hints_for_tokens", return_value=["Lexical semantic hint"]):
            with patch.object(self.engine.dictionary_lexicon, "suggest_unknown_tokens", return_value=["Unknown token hint"]):
                result = self.engine.validate_sentence("I can blorf.")

        self.assertEqual(result.lexical_hints, ["Lexical semantic hint", "Unknown token hint"])
        self.assertTrue(set(result.lexical_hints).issubset(set(result.suggestions)))
        self.assertFalse(any(h in result.pattern_hints for h in result.lexical_hints))

    def test_third_person_s_hint_uses_present_simple_context(self) -> None:
        result = self.engine.validate_sentence("He worked yesterday.")
        pattern_ids = {issue.rule_id for issue in result.pattern_warnings}
        self.assertNotIn("en.pattern.third_person_s_hint", pattern_ids)

    def test_modal_base_hint_uses_verb_form_guess(self) -> None:
        bad = self.engine.validate_sentence("He can works.")
        ok = self.engine.validate_sentence("He can work.")
        bad_ids = {issue.rule_id for issue in bad.pattern_warnings}
        ok_ids = {issue.rule_id for issue in ok.pattern_warnings}
        self.assertIn("en.pattern.modal_base_verb_hint", bad_ids)
        self.assertNotIn("en.pattern.modal_base_verb_hint", ok_ids)

    def test_collocation_support_adds_lexical_hint_for_wrong_preposition(self) -> None:
        result = self.engine.validate_sentence("They depend of us.")
        self.assertTrue(any("depend" in hint and "'on'" in hint for hint in result.lexical_hints))

    def test_collocation_support_does_not_flag_allowed_preposition(self) -> None:
        result = self.engine.validate_sentence("They depend on us.")
        self.assertFalse(any("depend" in hint and "'on'" in hint for hint in result.lexical_hints))

    def test_collocation_support_allows_one_adverb_between_head_and_preposition(self) -> None:
        bad = self.engine.validate_sentence("They depend directly of us.")
        ok = self.engine.validate_sentence("They depend directly on us.")
        self.assertTrue(any("depend" in hint for hint in bad.lexical_hints))
        self.assertFalse(any("depend" in hint and "'on'" in hint for hint in ok.lexical_hints))

    def test_collocation_support_normalizes_inflected_verbs(self) -> None:
        bad = self.engine.validate_sentence("She depends of her team.")
        ok = self.engine.validate_sentence("She depends on her team.")
        self.assertTrue(any("depends" in hint for hint in bad.lexical_hints))
        self.assertFalse(any("depends" in hint and "'on'" in hint for hint in ok.lexical_hints))

    def test_collocation_support_normalizes_more_inflected_forms(self) -> None:
        bad = self.engine.validate_sentence("They applied for a job and focused in details.")
        ok = self.engine.validate_sentence("They applied for a job and focused on details.")
        self.assertTrue(any("focused" in hint and "se usa normalmente" in hint for hint in bad.lexical_hints))
        self.assertFalse(any("focused" in hint and "se usa normalmente" in hint for hint in ok.lexical_hints))


if __name__ == "__main__":
    unittest.main()
