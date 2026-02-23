from .shared import GrammarRule
from .core import *
from .tenses import *
from .b1 import *
from .b2 import *

def get_english_rules() -> list[GrammarRule]:
    return [
        RequiredVerbRule(
            rule_id="en.required_verb",
            severity="error",
            description="A complete sentence requires a verb.",
        ),
        ExplicitSubjectRule(
            rule_id="en.explicit_subject",
            severity="error",
            description="Most complete English sentences require an explicit subject.",
        ),
        ImperativeSubjectWarningRule(
            rule_id="en.imperative_subject_optional",
            severity="warning",
            description="Imperatives usually omit the subject.",
        ),
        QuestionAuxiliaryRule(
            rule_id="en.question_auxiliary",
            severity="warning",
            description="Questions usually begin with an auxiliary.",
        ),
        PresentSimpleStructureRule(
            rule_id="en.present_simple_structure",
            severity="warning",
            description="Basic present simple structure (affirmative/negative/interrogative).",
        ),
        ToBeWithoutDoRule(
            rule_id="en.to_be_no_do",
            severity="warning",
            description="Do not combine do/does with basic uses of 'to be'.",
        ),
        PresentSimpleDoNegationRule(
            rule_id="en.present_simple_do_negation",
            severity="warning",
            description="Present simple negatives use do/does + not + base verb.",
        ),
        ThirdPersonSingularSRule(
            rule_id="en.third_person_s",
            severity="warning",
            description="He/she/it takes -s in present simple.",
        ),
        ArticleSoundRule(
            rule_id="en.article_a_an_sound",
            severity="warning",
            description="Use a/an based on initial sound.",
        ),
        ArticleCountabilityRule(
            rule_id="en.article_countability",
            severity="warning",
            description="Basic article/countability patterns (uncountables, singular countable predicate nouns).",
        ),
        ArticleGenericReferenceRule(
            rule_id="en.article_generic_reference",
            severity="warning",
            description="Heuristics for generic zero-article plural statements.",
        ),
        ArticleBareSingularCountableRule(
            rule_id="en.article_bare_singular_countable",
            severity="warning",
            description="Singular countable nouns in subject position often need an article/determiner.",
        ),
        ArticleBareSingularObjectRule(
            rule_id="en.article_bare_singular_object",
            severity="warning",
            description="Singular countable objects often need an article/determiner.",
        ),
        ArticleUncountableGenericTheRule(
            rule_id="en.article_uncountable_generic_the",
            severity="warning",
            description="Heuristics for generic zero-article use with uncountable nouns.",
        ),
        AdjectiveNounOrderRule(
            rule_id="en.adjective_noun_order",
            severity="warning",
            description="Adjectives usually come before nouns in noun phrases.",
        ),
        BasicSVOOrderRule(
            rule_id="en.basic_svo_order",
            severity="warning",
            description="Basic English declaratives follow Subject + Verb + Complement.",
        ),
        PrepositionCollocationRule(
            rule_id="en.preposition_collocation",
            severity="warning",
            description="Common adjective/verb preposition collocations.",
        ),
        PhrasalVerbBasicRule(
            rule_id="en.phrasal_basic",
            severity="warning",
            description="Common basic phrasal verb combinations.",
        ),
        ModalBaseVerbRule(
            rule_id="en.modal_base_verb",
            severity="warning",
            description="Modals use base verb forms.",
        ),
        ModalCombinationRule(
            rule_id="en.modal_combination",
            severity="warning",
            description="Avoid direct combinations of core modals.",
        ),
        SemiModalHaveToRule(
            rule_id="en.semi_modal_have_to",
            severity="warning",
            description="Semi-modal 'have to' structure.",
        ),
        SubjectBeAgreementRule(
            rule_id="en.subject_be_agreement",
            severity="warning",
            description="Basic subject + to be agreement.",
        ),
        PresentContinuousRule(
            rule_id="en.present_continuous",
            severity="warning",
            description="Present continuous uses am/is/are + verb-ing.",
        ),
        StativeVerbContinuousRule(
            rule_id="en.stative_continuous",
            severity="warning",
            description="Many stative verbs are not normally used in continuous forms.",
        ),
        PastSimpleRule(
            rule_id="en.past_simple",
            severity="warning",
            description="Past simple structure and did-support.",
        ),
        PastContinuousInterruptionRule(
            rule_id="en.past_continuous_interruption",
            severity="warning",
            description="Past continuous + when-clause interruption pattern.",
        ),
        FutureWillRule(
            rule_id="en.future_will",
            severity="warning",
            description="Future with will uses will + base verb.",
        ),
        FuturePresentContinuousPlanRule(
            rule_id="en.future_plan_present_continuous",
            severity="warning",
            description="Future plans can use present continuous (am/is/are + verb-ing).",
        ),
        PresentSimpleScheduleRule(
            rule_id="en.future_schedule_present_simple",
            severity="warning",
            description="Schedules often use present simple.",
        ),
        GoingToFutureRule(
            rule_id="en.future_going_to",
            severity="warning",
            description="Future with going to uses am/is/are + going to + base verb.",
        ),
        PresentPerfectRule(
            rule_id="en.present_perfect",
            severity="warning",
            description="Present perfect uses have/has + past participle.",
        ),
        PresentPerfectVsPastSimpleUsageRule(
            rule_id="en.present_perfect_vs_past_simple_usage",
            severity="warning",
            description="Basic usage contrast: present perfect vs finished past time markers.",
        ),
        PresentPerfectContinuousRule(
            rule_id="en.present_perfect_continuous",
            severity="warning",
            description="Present perfect continuous uses have/has been + verb-ing.",
        ),
        PastPerfectRule(
            rule_id="en.past_perfect",
            severity="warning",
            description="Past perfect uses had + past participle.",
        ),
        PastPerfectContinuousRule(
            rule_id="en.past_perfect_continuous",
            severity="warning",
            description="Past perfect continuous uses had been + verb-ing.",
        ),
        PastContinuousRule(
            rule_id="en.past_continuous",
            severity="warning",
            description="Past continuous uses was/were + verb-ing.",
        ),
        FutureContinuousRule(
            rule_id="en.future_continuous",
            severity="warning",
            description="Future continuous uses will be + verb-ing.",
        ),
        FuturePerfectRule(
            rule_id="en.future_perfect",
            severity="warning",
            description="Future perfect uses will have + past participle.",
        ),
        FuturePerfectContinuousRule(
            rule_id="en.future_perfect_continuous",
            severity="warning",
            description="Future perfect continuous uses will have been + verb-ing.",
        ),
        ComparativeSuperlativeRule(
            rule_id="en.comparatives_superlatives",
            severity="warning",
            description="Comparative/superlative structures and as...as.",
        ),
        B1ConditionalRule(
            rule_id="en.conditionals_b1",
            severity="warning",
            description="First/second conditional structure heuristics.",
        ),
        AdvancedConditionalRule(
            rule_id="en.conditionals_b2",
            severity="warning",
            description="Third/mixed conditional and alternatives to if.",
        ),
        BasicPassiveVoiceRule(
            rule_id="en.passive_basic",
            severity="warning",
            description="Basic passive voice uses be + past participle.",
        ),
        AdvancedPassiveVoiceRule(
            rule_id="en.passive_advanced",
            severity="warning",
            description="Advanced passive voice structures.",
        ),
        ReportedSpeechBasicRule(
            rule_id="en.reported_speech_basic",
            severity="warning",
            description="Basic reported speech and indirect question forms.",
        ),
        ReportedSpeechAdvancedRule(
            rule_id="en.reported_speech_advanced",
            severity="warning",
            description="Advanced reported speech reporting-verb patterns.",
        ),
        IndirectQuestionFormRule(
            rule_id="en.indirect_questions",
            severity="warning",
            description="Indirect questions use statement order.",
        ),
        RelativeClauseBasicRule(
            rule_id="en.relative_clauses_basic",
            severity="warning",
            description="Basic relative clause heuristics.",
        ),
        RelativeClauseAdvancedRule(
            rule_id="en.relative_clauses_advanced",
            severity="warning",
            description="Advanced relative clause heuristics.",
        ),
        GerundInfinitiveCommonRule(
            rule_id="en.gerund_infinitive_common",
            severity="warning",
            description="Common gerund/infinitive patterns.",
        ),
        GerundInfinitiveMeaningRule(
            rule_id="en.gerund_infinitive_meaning_pairs",
            severity="warning",
            description="High-value gerund/infinitive meaning pairs.",
        ),
        DeterminersQuantifiersBasicRule(
            rule_id="en.determiners_quantifiers_basic",
            severity="warning",
            description="Basic determiners and quantifiers.",
        ),
        SomeAnyRule(
            rule_id="en.some_any",
            severity="warning",
            description="Some/any usage heuristics.",
        ),
        QuantifiersDeterminersAdvancedRule(
            rule_id="en.quantifiers_determiners_advanced",
            severity="warning",
            description="Advanced quantifiers and determiner patterns.",
        ),
        LinkingDeviceRule(
            rule_id="en.linking_devices",
            severity="warning",
            description="Linking devices and connector patterns.",
        ),
        AdvancedModalPerfectRule(
            rule_id="en.modal_advanced_perfect",
            severity="warning",
            description="Advanced modal perfect and deduction forms.",
        ),
        InversionEmphasisRule(
            rule_id="en.inversion_emphasis",
            severity="warning",
            description="Inversion after negative adverbials and emphasis patterns.",
        ),
        CleftSentenceRule(
            rule_id="en.cleft_sentences",
            severity="warning",
            description="Cleft sentence structures (wh-cleft / it-cleft).",
        ),
        NounClauseComplexRule(
            rule_id="en.noun_clauses_complex",
            severity="warning",
            description="Complex noun clause and subordination heuristics.",
        ),
        PhrasalVerbAdvancedRule(
            rule_id="en.phrasal_advanced",
            severity="warning",
            description="Intermediate-high phrasal verb combinations.",
        ),
        WordFormationRule(
            rule_id="en.word_formation",
            severity="warning",
            description="Basic word-formation family heuristics.",
        ),
    ]
