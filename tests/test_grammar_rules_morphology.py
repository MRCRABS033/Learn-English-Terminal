import unittest

from Services.validation.rule_engine import RuleEngine


class GrammarRulesMorphologyRegressionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = RuleEngine()

    def _warning_ids(self, text: str) -> set[str]:
        result = self.engine.validate_sentence(text)
        return {issue.rule_id for issue in result.warnings}

    def test_past_simple_rule_did_requires_base(self) -> None:
        self.assertIn("en.past_simple", self._warning_ids("Did you worked yesterday?"))
        self.assertNotIn("en.past_simple", self._warning_ids("Did you work yesterday?"))

    def test_future_will_rule_requires_base(self) -> None:
        self.assertIn("en.future_will", self._warning_ids("I will worked tomorrow."))
        self.assertNotIn("en.future_will", self._warning_ids("I will work tomorrow."))

    def test_going_to_future_rule_requires_base(self) -> None:
        self.assertIn("en.future_going_to", self._warning_ids("They are going to studied."))
        self.assertNotIn("en.future_going_to", self._warning_ids("They are going to study."))

    def test_present_perfect_rule_requires_participle(self) -> None:
        self.assertIn("en.present_perfect", self._warning_ids("I have working all day."))
        self.assertNotIn("en.present_perfect", self._warning_ids("I have worked all day."))

    def test_present_simple_structure_after_does_requires_base(self) -> None:
        self.assertIn("en.present_simple_structure", self._warning_ids("He does studies at night."))
        self.assertNotIn("en.present_simple_structure", self._warning_ids("He does study at night."))

    def test_present_simple_do_negation_after_doesnt_requires_base(self) -> None:
        self.assertIn("en.present_simple_do_negation", self._warning_ids("He doesn't studies."))
        self.assertNotIn("en.present_simple_do_negation", self._warning_ids("He doesn't study."))

    def test_modal_base_verb_rule_uses_morphology(self) -> None:
        self.assertIn("en.modal_base_verb", self._warning_ids("She can working now."))
        self.assertNotIn("en.modal_base_verb", self._warning_ids("She can work now."))

    def test_have_to_rule_requires_base(self) -> None:
        self.assertIn("en.semi_modal_have_to", self._warning_ids("I have to studying."))
        self.assertNotIn("en.semi_modal_have_to", self._warning_ids("I have to study."))

    def test_future_plan_present_continuous_rule_accepts_ing(self) -> None:
        self.assertIn("en.future_plan_present_continuous", self._warning_ids("I am meet him tomorrow."))
        self.assertNotIn("en.future_plan_present_continuous", self._warning_ids("I am meeting him tomorrow."))

    def test_present_perfect_continuous_rule_requires_ing_after_been(self) -> None:
        self.assertIn("en.present_perfect_continuous", self._warning_ids("I have been work all morning."))
        self.assertNotIn("en.present_perfect_continuous", self._warning_ids("I have been working all morning."))

    def test_past_perfect_rule_requires_participle(self) -> None:
        self.assertIn("en.past_perfect", self._warning_ids("She had go before noon."))
        self.assertNotIn("en.past_perfect", self._warning_ids("She had gone before noon."))

    def test_future_continuous_rule_requires_ing(self) -> None:
        self.assertIn("en.future_continuous", self._warning_ids("I will be study tomorrow."))
        self.assertNotIn("en.future_continuous", self._warning_ids("I will be studying tomorrow."))

    def test_future_perfect_rule_requires_participle(self) -> None:
        self.assertIn("en.future_perfect", self._warning_ids("They will have finish by 5."))
        self.assertNotIn("en.future_perfect", self._warning_ids("They will have finished by 5."))

    def test_modal_perfect_rule_requires_participle(self) -> None:
        self.assertIn("en.modal_advanced_perfect", self._warning_ids("She should have go earlier."))
        self.assertNotIn("en.modal_advanced_perfect", self._warning_ids("She should have gone earlier."))

    def test_advanced_passive_rule_requires_participle(self) -> None:
        self.assertIn("en.passive_advanced", self._warning_ids("The plan was will be complete."))
        self.assertIn("en.passive_advanced", self._warning_ids("The work will be finish soon."))
        self.assertNotIn("en.passive_advanced", self._warning_ids("The work will be finished soon."))

    def test_gerund_infinitive_meaning_rule_stop_remember_to_plus_ing(self) -> None:
        self.assertIn("en.gerund_infinitive_meaning_pairs", self._warning_ids("Remember to going early."))
        self.assertNotIn("en.gerund_infinitive_meaning_pairs", self._warning_ids("Remember to go early."))

    def test_gerund_infinitive_common_rule_to_infinitive_verbs_reject_ing(self) -> None:
        self.assertIn("en.gerund_infinitive_common", self._warning_ids("I want going now."))
        self.assertNotIn("en.gerund_infinitive_common", self._warning_ids("I want to go now."))

    def test_past_continuous_interruption_rule_detects_ing_with_morphology(self) -> None:
        self.assertIn(
            "en.past_continuous_interruption",
            self._warning_ids("I was studying when she was calling me."),
        )

    def test_stative_continuous_rule_flags_common_stative_verb(self) -> None:
        self.assertIn("en.stative_continuous", self._warning_ids("I am knowing the answer."))
        self.assertNotIn("en.stative_continuous", self._warning_ids("I am having lunch."))

    def test_b1_conditional_rule_uses_if_clause_and_main_clause(self) -> None:
        self.assertIn("en.conditionals_b1", self._warning_ids("If it rains, I would stay home."))
        self.assertNotIn("en.conditionals_b1", self._warning_ids("If it rains, I will stay home."))

    def test_b2_conditional_rule_third_conditional_shape(self) -> None:
        self.assertIn("en.conditionals_b2", self._warning_ids("If I had studied, I would pass."))
        self.assertNotIn("en.conditionals_b2", self._warning_ids("If I had studied, I would have passed."))

    def test_reported_speech_basic_rule_with_clause_segmentation(self) -> None:
        self.assertIn("en.reported_speech_basic", self._warning_ids("He asked, where do you live?"))
        self.assertNotIn("en.reported_speech_basic", self._warning_ids("He asked where you live."))

    def test_indirect_question_form_rule_with_clause_segmentation(self) -> None:
        self.assertIn("en.indirect_questions", self._warning_ids("Do you know where do they live?"))
        self.assertNotIn("en.indirect_questions", self._warning_ids("Do you know where they live?"))

    def test_relative_clause_basic_rule_with_clause_segmentation(self) -> None:
        self.assertIn("en.relative_clauses_basic", self._warning_ids("The man, who he knows me, is here."))
        self.assertNotIn("en.relative_clauses_basic", self._warning_ids("The man who knows me is here."))

    def test_linking_device_rule_uses_punctuation_stream_for_initial_connector(self) -> None:
        self.assertIn("en.linking_devices", self._warning_ids("However I think this is fine."))
        self.assertNotIn("en.linking_devices", self._warning_ids("However, I think this is fine."))

    def test_article_countability_rule_flags_indefinite_article_with_uncountable(self) -> None:
        self.assertIn("en.article_countability", self._warning_ids("I need an information."))
        self.assertNotIn("en.article_countability", self._warning_ids("I need information."))

    def test_article_countability_rule_flags_missing_article_before_singular_countable_predicate(self) -> None:
        self.assertIn("en.article_countability", self._warning_ids("He is teacher."))
        self.assertNotIn("en.article_countability", self._warning_ids("He is a teacher."))

    def test_article_generic_reference_rule_flags_simple_generic_plural_with_the(self) -> None:
        self.assertIn("en.article_generic_reference", self._warning_ids("The dogs are friendly."))
        self.assertNotIn("en.article_generic_reference", self._warning_ids("Dogs are friendly."))

    def test_article_generic_reference_rule_avoids_specific_location_context(self) -> None:
        self.assertNotIn("en.article_generic_reference", self._warning_ids("The dogs are here."))

    def test_article_generic_reference_rule_avoids_relative_clause_specific_reference(self) -> None:
        self.assertNotIn("en.article_generic_reference", self._warning_ids("The dogs that live here are friendly."))
        self.assertNotIn("en.article_generic_reference", self._warning_ids("A lot of the students are friendly."))
        self.assertNotIn("en.article_generic_reference", self._warning_ids("Lots of the students are friendly."))

    def test_article_bare_singular_countable_rule_flags_common_subject(self) -> None:
        self.assertIn("en.article_bare_singular_countable", self._warning_ids("Dog is friendly."))
        self.assertIn("en.article_bare_singular_countable", self._warning_ids("Student studies a lot."))

    def test_article_bare_singular_countable_rule_avoids_valid_variants(self) -> None:
        self.assertNotIn("en.article_bare_singular_countable", self._warning_ids("A dog is friendly."))
        self.assertNotIn("en.article_bare_singular_countable", self._warning_ids("Dogs are friendly."))
        self.assertNotIn("en.article_bare_singular_countable", self._warning_ids("Water is important."))

    def test_article_bare_singular_object_rule_flags_common_object(self) -> None:
        self.assertIn("en.article_bare_singular_object", self._warning_ids("I bought car yesterday."))
        self.assertIn("en.article_bare_singular_object", self._warning_ids("We need teacher now."))

    def test_article_bare_singular_object_rule_avoids_valid_variants(self) -> None:
        self.assertNotIn("en.article_bare_singular_object", self._warning_ids("I bought a car yesterday."))
        self.assertNotIn("en.article_bare_singular_object", self._warning_ids("I need water now."))

    def test_article_uncountable_generic_the_rule_flags_simple_generic_statement(self) -> None:
        self.assertIn("en.article_uncountable_generic_the", self._warning_ids("The music is important."))
        self.assertNotIn("en.article_uncountable_generic_the", self._warning_ids("Music is important."))

    def test_article_uncountable_generic_the_rule_avoids_specific_context(self) -> None:
        self.assertNotIn("en.article_uncountable_generic_the", self._warning_ids("The music is in the room."))
        self.assertNotIn("en.article_uncountable_generic_the", self._warning_ids("The music that you chose is important."))

    def test_determiners_quantifiers_basic_rule_uses_noun_phrases_with_adjectives(self) -> None:
        self.assertIn("en.determiners_quantifiers_basic", self._warning_ids("many important information"))
        self.assertIn("en.determiners_quantifiers_basic", self._warning_ids("much big books"))
        self.assertIn("en.determiners_quantifiers_basic", self._warning_ids("a few important information"))
        self.assertIn("en.determiners_quantifiers_basic", self._warning_ids("a little big books"))
        self.assertNotIn("en.determiners_quantifiers_basic", self._warning_ids("a few important books"))
        self.assertNotIn("en.determiners_quantifiers_basic", self._warning_ids("a little money"))

    def test_determiners_quantifiers_basic_rule_flags_a_lot_of_singular_countable(self) -> None:
        self.assertIn("en.determiners_quantifiers_basic", self._warning_ids("I have a lot of car."))
        self.assertIn("en.determiners_quantifiers_basic", self._warning_ids("We saw lots of student there."))
        self.assertNotIn("en.determiners_quantifiers_basic", self._warning_ids("I have a lot of cars."))
        self.assertNotIn("en.determiners_quantifiers_basic", self._warning_ids("We saw lots of water there."))

    def test_determiners_quantifiers_basic_rule_flags_a_number_of_non_plural(self) -> None:
        self.assertIn("en.determiners_quantifiers_basic", self._warning_ids("A number of student are waiting."))
        self.assertIn("en.determiners_quantifiers_basic", self._warning_ids("A number of information is missing."))
        self.assertNotIn("en.determiners_quantifiers_basic", self._warning_ids("A number of students are waiting."))

    def test_subject_be_agreement_uses_number_of_subject_pattern(self) -> None:
        self.assertIn("en.subject_be_agreement", self._warning_ids("The number of students are high."))
        self.assertNotIn("en.subject_be_agreement", self._warning_ids("The number of students is high."))
        self.assertNotIn("en.subject_be_agreement", self._warning_ids("A number of students are waiting."))

    def test_quantifiers_determiners_advanced_rule_uses_noun_phrases(self) -> None:
        self.assertIn("en.quantifiers_determiners_advanced", self._warning_ids("each students passed"))
        self.assertIn("en.quantifiers_determiners_advanced", self._warning_ids("both student came"))
        self.assertNotIn("en.quantifiers_determiners_advanced", self._warning_ids("each student passed"))

    def test_quantifiers_determiners_advanced_rule_handles_such_a_plural_with_np_pattern(self) -> None:
        self.assertIn("en.quantifiers_determiners_advanced", self._warning_ids("Such a big houses are expensive."))
        self.assertNotIn("en.quantifiers_determiners_advanced", self._warning_ids("Such big houses are expensive."))

    def test_reported_speech_advanced_rule_flags_suggest_someone_to_do(self) -> None:
        self.assertIn("en.reported_speech_advanced", self._warning_ids("She suggested me to go early."))
        self.assertNotIn("en.reported_speech_advanced", self._warning_ids("She suggested going early."))

    def test_relative_clause_advanced_rule_handles_nonrestrictive_that_and_whose_shape(self) -> None:
        self.assertIn("en.relative_clauses_advanced", self._warning_ids("My car, that is red, is outside."))
        self.assertIn("en.relative_clauses_advanced", self._warning_ids("The man whose is here is my teacher."))
        self.assertNotIn("en.relative_clauses_advanced", self._warning_ids("The man whose car is here is my teacher."))
        self.assertNotIn("en.relative_clauses_advanced", self._warning_ids("The topic to which we referred was difficult."))
        self.assertNotIn("en.relative_clauses_advanced", self._warning_ids("My car, which is red, is outside."))

    def test_inversion_emphasis_rule_requires_auxiliary_after_fronted_negative(self) -> None:
        self.assertIn("en.inversion_emphasis", self._warning_ids("Never I have seen this."))
        self.assertNotIn("en.inversion_emphasis", self._warning_ids("Never have I seen this."))
        self.assertNotIn("en.inversion_emphasis", self._warning_ids("Hardly had I sat down when the phone rang."))
        self.assertIn("en.inversion_emphasis", self._warning_ids("Hardly I had sat down when the phone rang."))
        self.assertIn("en.inversion_emphasis", self._warning_ids("No sooner I arrived than he left."))
        self.assertNotIn("en.inversion_emphasis", self._warning_ids("No sooner had I arrived than he left."))
        self.assertIn("en.inversion_emphasis", self._warning_ids("No sooner had I arrived then he left."))
        self.assertIn("en.inversion_emphasis", self._warning_ids("Not until yesterday I understood."))
        self.assertNotIn("en.inversion_emphasis", self._warning_ids("Not until yesterday did I understand."))
        self.assertNotIn("en.inversion_emphasis", self._warning_ids("Not only did he apologize, but he also helped."))
        self.assertNotIn("en.inversion_emphasis", self._warning_ids("Not only did he apologize but he also helped."))

    def test_cleft_sentence_rule_avoids_false_positive_for_predicative_adjective(self) -> None:
        self.assertNotIn("en.cleft_sentences", self._warning_ids("It is important to study."))
        self.assertNotIn("en.cleft_sentences", self._warning_ids("It is possible to finish today."))
        self.assertNotIn("en.cleft_sentences", self._warning_ids("It was because he was late that we missed the train."))
        self.assertIn("en.cleft_sentences", self._warning_ids("It was John I saw."))
        self.assertNotIn("en.cleft_sentences", self._warning_ids("It was John who I saw."))
        self.assertNotIn("en.cleft_sentences", self._warning_ids("It was in June when we met."))
        self.assertIn("en.cleft_sentences", self._warning_ids("What I need a break."))
        self.assertNotIn("en.cleft_sentences", self._warning_ids("What I need is a break."))
        self.assertNotIn("en.cleft_sentences", self._warning_ids("What I like most is coffee."))

    def test_noun_clause_complex_rule_clause_aware_whether_inversion(self) -> None:
        self.assertIn("en.noun_clauses_complex", self._warning_ids("I wonder whether do they agree."))
        self.assertNotIn("en.noun_clauses_complex", self._warning_ids("I wonder whether they agree."))
        self.assertIn("en.noun_clauses_complex", self._warning_ids("I know where does he live."))
        self.assertNotIn("en.noun_clauses_complex", self._warning_ids("I know where he lives."))
        self.assertIn("en.noun_clauses_complex", self._warning_ids("The fact we arrived late is true."))
        self.assertNotIn("en.noun_clauses_complex", self._warning_ids("The fact that we arrived late is true."))
        self.assertNotIn("en.noun_clauses_complex", self._warning_ids("The fact is that we arrived late."))

    def test_phrasal_advanced_rule_handles_inflected_forms(self) -> None:
        self.assertIn("en.phrasal_advanced", self._warning_ids("She carried up the plan."))
        self.assertNotIn("en.phrasal_advanced", self._warning_ids("She carried out the plan."))
        self.assertIn("en.phrasal_advanced", self._warning_ids("He puts up noise."))
        self.assertNotIn("en.phrasal_advanced", self._warning_ids("He puts up with noise."))

    def test_word_formation_rule_extended_families(self) -> None:
        self.assertIn("en.word_formation", self._warning_ids("A different is clear."))
        self.assertIn("en.word_formation", self._warning_ids("It was very success."))
        self.assertNotIn("en.word_formation", self._warning_ids("A difference is clear."))
        self.assertNotIn("en.word_formation", self._warning_ids("It was very successful."))

    def test_preposition_collocation_rule_extended_noun_and_adjective_cases(self) -> None:
        self.assertIn("en.preposition_collocation", self._warning_ids("This is the reason of the problem."))
        self.assertIn("en.preposition_collocation", self._warning_ids("This answer for the question is wrong."))
        self.assertIn("en.preposition_collocation", self._warning_ids("This is different than mine."))
        self.assertNotIn("en.preposition_collocation", self._warning_ids("This is the reason for the problem."))
        self.assertNotIn("en.preposition_collocation", self._warning_ids("This is different from mine."))


if __name__ == "__main__":
    unittest.main()
