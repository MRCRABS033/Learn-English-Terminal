import unittest

from Services.analysis.sentence_analyzer import SentenceAnalyzer


class SentenceAnalyzerTokenFeatureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.analyzer = SentenceAnalyzer()

    @staticmethod
    def _feature(analysis, token: str):
        for feature in analysis.token_features:
            if feature.token == token:
                return feature
        raise AssertionError(f"Token feature not found for: {token}")

    def test_work_family_base_verb_after_subject(self) -> None:
        analysis = self.analyzer.analyze_english("I work today.")
        feature = self._feature(analysis, "work")
        self.assertEqual(feature.pos_guess, "verb")
        self.assertTrue(analysis.has_verb)

    def test_work_family_base_as_noun_subject_not_imperative(self) -> None:
        analysis = self.analyzer.analyze_english("Work is important.")
        feature = self._feature(analysis, "work")
        self.assertEqual(feature.pos_guess, "noun")
        self.assertEqual(analysis.sentence_type, "declarative")
        self.assertTrue(analysis.has_explicit_subject)

    def test_work_family_third_person_s_form(self) -> None:
        analysis = self.analyzer.analyze_english("She works here.")
        feature = self._feature(analysis, "works")
        self.assertEqual(feature.pos_guess, "verb")
        self.assertTrue(analysis.has_verb)

    def test_work_family_ing_progressive_after_be(self) -> None:
        analysis = self.analyzer.analyze_english("They are working now.")
        feature = self._feature(analysis, "working")
        self.assertEqual(feature.pos_guess, "verb_participle")
        self.assertIn("progressive_after_be", feature.notes)

    def test_work_family_ed_past_after_subject(self) -> None:
        analysis = self.analyzer.analyze_english("We worked yesterday.")
        feature = self._feature(analysis, "worked")
        self.assertEqual(feature.pos_guess, "verb")
        self.assertIn("subject_plus_past_verb", feature.notes)

    def test_ing_adjective_disambiguation_before_noun(self) -> None:
        analysis = self.analyzer.analyze_english("I want interesting books.")
        feature = self._feature(analysis, "interesting")
        self.assertEqual(feature.pos_guess, "adjective")

    def test_ing_predicative_adjective_after_be_common_case(self) -> None:
        analysis = self.analyzer.analyze_english("She is interesting.")
        feature = self._feature(analysis, "interesting")
        self.assertEqual(feature.pos_guess, "adjective")

    def test_ed_adjective_disambiguation_after_be_with_preposition(self) -> None:
        analysis = self.analyzer.analyze_english("I am interested in music.")
        feature = self._feature(analysis, "interested")
        self.assertEqual(feature.pos_guess, "adjective")

    def test_base_verb_ending_ed_does_not_trigger_past_suffix_heuristic(self) -> None:
        analysis = self.analyzer.analyze_english("I need a working phone.")
        feature = self._feature(analysis, "need")
        self.assertEqual(feature.pos_guess, "verb")
        self.assertNotIn("suffix_ed", feature.notes)

    def test_works_as_plural_noun_subject(self) -> None:
        analysis = self.analyzer.analyze_english("The works are closed.")
        feature = self._feature(analysis, "works")
        self.assertEqual(feature.pos_guess, "noun")
        self.assertTrue(analysis.has_explicit_subject)

    def test_building_noun_vs_verb_participle(self) -> None:
        noun_analysis = self.analyzer.analyze_english("The building is tall.")
        verb_analysis = self.analyzer.analyze_english("They are building a house.")
        self.assertEqual(self._feature(noun_analysis, "building").pos_guess, "noun")
        self.assertEqual(self._feature(verb_analysis, "building").pos_guess, "verb_participle")

    def test_common_adjective_and_adverb_are_classified(self) -> None:
        analysis = self.analyzer.analyze_english("The building is tall today.")
        self.assertEqual(self._feature(analysis, "tall").pos_guess, "adjective")
        self.assertEqual(self._feature(analysis, "today").pos_guess, "adverb")

    def test_external_pos_tagger_support_refines_low_confidence_guess(self) -> None:
        analyzer = SentenceAnalyzer(external_pos_tagger=lambda tokens: [None, None, "adjective"])
        analysis = analyzer.analyze_english("The house tall")
        feature = self._feature(analysis, "tall")
        self.assertEqual(feature.external_pos, "adjective")
        self.assertEqual(feature.pos_guess, "adjective")
        self.assertIn("external_pos_support", feature.notes)

    def test_verb_form_guess_present_simple_base_and_v3sg(self) -> None:
        a1 = self.analyzer.analyze_english("I work.")
        a2 = self.analyzer.analyze_english("He works.")
        self.assertEqual(self._feature(a1, "work").verb_form_guess, "base")
        self.assertEqual(self._feature(a2, "works").verb_form_guess, "v3sg")

    def test_verb_form_guess_past_and_ing_participle(self) -> None:
        a1 = self.analyzer.analyze_english("We worked.")
        a2 = self.analyzer.analyze_english("They are working.")
        self.assertEqual(self._feature(a1, "worked").verb_form_guess, "past")
        self.assertEqual(self._feature(a2, "working").verb_form_guess, "participle_ing")

    def test_tense_guess_present_simple(self) -> None:
        analysis = self.analyzer.analyze_english("He works every day.")
        self.assertIn("present_simple", analysis.tense_guesses)
        self.assertEqual(analysis.primary_tense_guess, "present_simple")

    def test_tense_guess_present_continuous(self) -> None:
        analysis = self.analyzer.analyze_english("She is working now.")
        self.assertIn("present_continuous", analysis.tense_guesses)
        self.assertEqual(analysis.primary_tense_guess, "present_continuous")

    def test_tense_guess_past_simple(self) -> None:
        analysis = self.analyzer.analyze_english("They worked yesterday.")
        self.assertIn("past_simple", analysis.tense_guesses)
        self.assertEqual(analysis.primary_tense_guess, "past_simple")

    def test_tense_guess_past_continuous(self) -> None:
        analysis = self.analyzer.analyze_english("They were working.")
        self.assertIn("past_continuous", analysis.tense_guesses)
        self.assertEqual(analysis.primary_tense_guess, "past_continuous")

    def test_tense_guess_present_perfect(self) -> None:
        analysis = self.analyzer.analyze_english("I have worked.")
        self.assertIn("present_perfect", analysis.tense_guesses)
        self.assertEqual(analysis.primary_tense_guess, "present_perfect")

    def test_tense_guess_future_will(self) -> None:
        analysis = self.analyzer.analyze_english("I will work tomorrow.")
        self.assertIn("future_will", analysis.tense_guesses)
        self.assertEqual(analysis.primary_tense_guess, "future_will")

    def test_tense_guess_future_going_to(self) -> None:
        analysis = self.analyzer.analyze_english("They are going to study.")
        self.assertIn("future_going_to", analysis.tense_guesses)
        self.assertEqual(analysis.primary_tense_guess, "future_going_to")

    def test_raw_token_stream_preserves_punctuation(self) -> None:
        analysis = self.analyzer.analyze_english("If it rains, we stay home.")
        puncts = [t.text for t in analysis.raw_token_stream if t.kind == "punct"]
        self.assertIn(",", puncts)
        self.assertIn(".", puncts)

    def test_clause_segmentation_detects_if_clause_and_main_clause(self) -> None:
        analysis = self.analyzer.analyze_english("If it rains, we stay home.")
        self.assertGreaterEqual(len(analysis.clauses), 2)
        self.assertIn("if", analysis.clause_linkers_detected)
        self.assertEqual(analysis.clauses[0].clause_type, "if_clause")
        self.assertEqual(analysis.clauses[1].clause_type, "main")

    def test_clause_segmentation_detects_relative_clause(self) -> None:
        analysis = self.analyzer.analyze_english("The book, which I like, is new.")
        clause_types = [c.clause_type for c in analysis.clauses]
        self.assertIn("relative_clause", clause_types)
        self.assertIn("which", analysis.clause_linkers_detected)

    def test_clause_analysis_includes_subject_and_main_verb_indices(self) -> None:
        analysis = self.analyzer.analyze_english("When she worked, we were eating.")
        when_clause = analysis.clauses[0]
        main_clause = analysis.clauses[-1]
        self.assertEqual(when_clause.clause_type, "when_clause")
        self.assertIsNotNone(when_clause.subject_idx)
        self.assertIsNotNone(when_clause.main_verb_idx)
        self.assertEqual(main_clause.tense_guess, "past_continuous")
        self.assertIn("were", main_clause.aux_chain)

    def test_subject_number_guess_coordinated_subject_is_plural(self) -> None:
        analysis = self.analyzer.analyze_english("My brother and my sister are here.")
        self.assertEqual(analysis.subject_number_guess, "plural")

    def test_subject_number_guess_of_phrase_uses_head_noun(self) -> None:
        analysis = self.analyzer.analyze_english("The list of items is long.")
        self.assertEqual(analysis.subject_number_guess, "singular")

    def test_subject_number_guess_number_of_pattern(self) -> None:
        singular_number = self.analyzer.analyze_english("The number of students is high.")
        plural_number = self.analyzer.analyze_english("A number of students are waiting.")
        self.assertEqual(singular_number.subject_number_guess, "singular")
        self.assertEqual(plural_number.subject_number_guess, "plural")

    def test_subject_number_guess_either_or_uses_nearest_element(self) -> None:
        analysis = self.analyzer.analyze_english("Either the teacher or the students are here.")
        self.assertEqual(analysis.subject_number_guess, "plural")

    def test_noun_countability_guess_is_exposed_in_token_features(self) -> None:
        analysis = self.analyzer.analyze_english("The teacher has information.")
        teacher = self._feature(analysis, "teacher")
        information = self._feature(analysis, "information")
        self.assertEqual(teacher.noun_countability_guess, "countable")
        self.assertEqual(information.noun_countability_guess, "uncountable")

    def test_noun_phrases_are_extracted_with_basic_roles(self) -> None:
        analysis = self.analyzer.analyze_english("The dogs are friendly and need water.")
        subject_nps = [np for np in analysis.noun_phrases if np.role_guess == "subject"]
        object_nps = [np for np in analysis.noun_phrases if np.role_guess == "object"]
        self.assertTrue(any(np.head_token == "dogs" and np.determiner == "the" for np in subject_nps))
        self.assertTrue(any(np.head_token == "water" for np in object_nps))

    def test_noun_phrase_marks_generic_candidate(self) -> None:
        analysis = self.analyzer.analyze_english("Dogs are friendly.")
        self.assertTrue(any(np.head_token == "dogs" and np.is_generic_candidate for np in analysis.noun_phrases))

    def test_noun_phrase_supports_quantifier_led_phrases(self) -> None:
        analysis = self.analyzer.analyze_english("Many important books are here.")
        np = next((np for np in analysis.noun_phrases if np.head_token == "books"), None)
        self.assertIsNotNone(np)
        self.assertEqual(np.quantifier, "many")
        self.assertEqual(np.countability_guess, "countable_plural")

    def test_noun_phrase_supports_a_lot_of_pattern(self) -> None:
        analysis = self.analyzer.analyze_english("A lot of useful information is available.")
        np = next((np for np in analysis.noun_phrases if np.head_token == "information"), None)
        self.assertIsNotNone(np)
        self.assertEqual(np.quantifier, "a_lot_of")
        self.assertEqual(np.pattern, "a_lot_of")
        self.assertEqual(np.determiner, "a")
        self.assertEqual(np.countability_guess, "uncountable")

    def test_noun_phrase_supports_such_determiner_pattern(self) -> None:
        analysis = self.analyzer.analyze_english("Such a big house is expensive.")
        np = next((np for np in analysis.noun_phrases if np.head_token == "house"), None)
        self.assertIsNotNone(np)
        self.assertEqual(np.quantifier, "such")
        self.assertEqual(np.pattern, "such_det_np")
        self.assertEqual(np.determiner, "a")

    def test_noun_phrase_supports_lots_of_pattern(self) -> None:
        analysis = self.analyzer.analyze_english("Lots of books are expensive.")
        np = next((np for np in analysis.noun_phrases if np.head_token == "books"), None)
        self.assertIsNotNone(np)
        self.assertEqual(np.quantifier, "lots_of")
        self.assertEqual(np.pattern, "lots_of")
        self.assertIsNone(np.determiner)

    def test_noun_phrase_supports_a_lot_of_with_internal_determiner(self) -> None:
        analysis = self.analyzer.analyze_english("A lot of the students are here.")
        np = next((np for np in analysis.noun_phrases if np.head_token == "students"), None)
        self.assertIsNotNone(np)
        self.assertEqual(np.quantifier, "a_lot_of")
        self.assertEqual(np.pattern, "a_lot_of_det_np")
        self.assertEqual(np.determiner, "the")
        self.assertFalse(np.is_generic_candidate)

    def test_noun_phrase_supports_lots_of_with_internal_determiner(self) -> None:
        analysis = self.analyzer.analyze_english("Lots of the students are here.")
        np = next((np for np in analysis.noun_phrases if np.head_token == "students"), None)
        self.assertIsNotNone(np)
        self.assertEqual(np.quantifier, "lots_of")
        self.assertEqual(np.pattern, "lots_of_det_np")
        self.assertEqual(np.determiner, "the")

    def test_noun_phrase_supports_a_few_and_a_little_patterns(self) -> None:
        a_few = self.analyzer.analyze_english("A few good books are enough.")
        a_little = self.analyzer.analyze_english("A little money is enough.")
        np_few = next((np for np in a_few.noun_phrases if np.head_token == "books"), None)
        np_little = next((np for np in a_little.noun_phrases if np.head_token == "money"), None)
        self.assertIsNotNone(np_few)
        self.assertIsNotNone(np_little)
        self.assertEqual(np_few.quantifier, "few")
        self.assertEqual(np_few.pattern, "a_few")
        self.assertEqual(np_few.determiner, "a")
        self.assertEqual(np_little.quantifier, "little")
        self.assertEqual(np_little.pattern, "a_little")
        self.assertEqual(np_little.determiner, "a")

    def test_noun_phrase_supports_plenty_number_and_bit_of_patterns(self) -> None:
        plenty = self.analyzer.analyze_english("Plenty of books are here.")
        number = self.analyzer.analyze_english("A number of students are waiting.")
        bit = self.analyzer.analyze_english("A bit of time is enough.")
        np_plenty = next((np for np in plenty.noun_phrases if np.head_token == "books"), None)
        np_number = next((np for np in number.noun_phrases if np.head_token == "students"), None)
        np_bit = next((np for np in bit.noun_phrases if np.head_token == "time"), None)
        self.assertIsNotNone(np_plenty)
        self.assertIsNotNone(np_number)
        self.assertIsNotNone(np_bit)
        self.assertEqual(np_plenty.quantifier, "plenty_of")
        self.assertEqual(np_plenty.pattern, "plenty_of")
        self.assertEqual(np_number.quantifier, "a_number_of")
        self.assertEqual(np_number.pattern, "a_number_of")
        self.assertEqual(np_bit.quantifier, "a_bit_of")
        self.assertEqual(np_bit.pattern, "a_bit_of")

    def test_noun_phrase_supports_piece_pair_and_the_number_of_patterns(self) -> None:
        piece = self.analyzer.analyze_english("A piece of advice is useful.")
        pair = self.analyzer.analyze_english("A pair of shoes is new.")
        the_number = self.analyzer.analyze_english("The number of students is high.")
        np_piece = next((np for np in piece.noun_phrases if np.head_token == "advice"), None)
        np_pair = next((np for np in pair.noun_phrases if np.head_token == "shoes"), None)
        np_the_number = next((np for np in the_number.noun_phrases if np.head_token == "students"), None)
        self.assertIsNotNone(np_piece)
        self.assertIsNotNone(np_pair)
        self.assertIsNotNone(np_the_number)
        self.assertEqual(np_piece.quantifier, "a_piece_of")
        self.assertEqual(np_piece.pattern, "a_piece_of")
        self.assertEqual(np_pair.quantifier, "a_pair_of")
        self.assertEqual(np_pair.pattern, "a_pair_of")
        self.assertEqual(np_the_number.quantifier, "the_number_of")
        self.assertEqual(np_the_number.pattern, "the_number_of")


if __name__ == "__main__":
    unittest.main()
