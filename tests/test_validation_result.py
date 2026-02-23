import unittest

from Services.validation.validation_result import ValidationResult


class ValidationResultHintBucketsTests(unittest.TestCase):
    def test_separates_pattern_and_lexical_hints_and_keeps_aggregate_suggestions(self) -> None:
        result = ValidationResult()
        result.add_pattern_warning("en.pattern.test", "Pattern hint")
        result.add_lexical_hint("Lexical hint")

        self.assertEqual(len(result.pattern_warnings), 1)
        self.assertEqual(result.pattern_warnings[0].rule_id, "en.pattern.test")
        self.assertEqual(result.pattern_hints, ["Pattern hint"])
        self.assertEqual(result.lexical_hints, ["Lexical hint"])
        self.assertIn("Pattern hint", result.suggestions)
        self.assertIn("Lexical hint", result.suggestions)


if __name__ == "__main__":
    unittest.main()
