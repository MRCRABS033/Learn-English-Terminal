from dataclasses import dataclass
import re
from uuid import uuid4

from peewee import JOIN, IntegrityError

from Models.base_model import db
from Models.dictionary_entry_model import DictionaryEntry
from Models.dictionary_example_model import DictionaryExample
from Models.language import Language
from Models.oration_model import Oration
from Models.word_class_model import WordClass
from Models.word_model import Word
from Services.storage.dictionary_pos_rules import POS_TO_WORD_CLASS, RAW_DICT_POS_TO_NORMALIZED
from Services.validation.rule_engine import RuleEngine


@dataclass
class VocabularyEntry:
    word_id: str
    english_word: str
    spanish_meaning: str
    example_english: str
    example_spanish: str


@dataclass
class CatalogWordMatch:
    english_word: str
    english_word_normalized: str
    spanish_translation: str
    pos_normalized: str
    source: str
    source_detail: str = ""


class InvalidEnglishExampleError(ValueError):
    def __init__(self, validation_result) -> None:
        super().__init__("The English example sentence is not valid.")
        self.validation_result = validation_result


BLOCKING_WARNING_RULE_IDS = {
    "en.question_auxiliary",
    "en.present_simple_structure",
    "en.to_be_no_do",
    "en.present_simple_do_negation",
    "en.third_person_s",
    "en.article_a_an_sound",
    "en.adjective_noun_order",
    "en.basic_svo_order",
    "en.modal_base_verb",
    "en.modal_combination",
    "en.semi_modal_have_to",
    "en.subject_be_agreement",
    "en.present_continuous",
    "en.past_simple",
    "en.future_will",
    "en.future_plan_present_continuous",
    "en.future_going_to",
    "en.present_perfect",
    "en.present_perfect_continuous",
    "en.past_perfect",
    "en.past_perfect_continuous",
    "en.past_continuous",
    "en.future_continuous",
    "en.future_perfect",
    "en.future_perfect_continuous",
    "en.comparatives_superlatives",
    "en.conditionals_b1",
    "en.conditionals_b2",
    "en.passive_basic",
    "en.passive_advanced",
    "en.reported_speech_basic",
    "en.reported_speech_advanced",
    "en.indirect_questions",
    "en.relative_clauses_basic",
    "en.relative_clauses_advanced",
    "en.gerund_infinitive_common",
    "en.gerund_infinitive_meaning_pairs",
    "en.modal_advanced_perfect",
    "en.inversion_emphasis",
    "en.cleft_sentences",
    "en.noun_clauses_complex",
}


def normalize_english_key(text: str) -> str:
    # Lowercase + collapse internal whitespace to make duplicate detection deterministic.
    return re.sub(r"\s+", " ", text.strip().lower())


class VocabularyService:
    def __init__(self) -> None:
        self.rule_engine = RuleEngine()

    def initialize_database(self) -> None:
        if db.is_closed():
            db.connect()

        db.create_tables(
            [Language, WordClass, Word, Oration, DictionaryEntry, DictionaryExample],
            safe=True,
        )
        self._ensure_schema_updates()
        self._seed_languages()
        self._seed_word_classes()

    def close_database(self) -> None:
        if not db.is_closed():
            db.close()

    def _seed_languages(self) -> None:
        defaults = [
            {"id": "en", "name": "english"},
            {"id": "es", "name": "spanish"},
        ]
        for item in defaults:
            Language.get_or_create(id=item["id"], defaults={"name": item["name"]})

    def _seed_word_classes(self) -> None:
        for normalized_pos, (class_id, class_name) in POS_TO_WORD_CLASS.items():
            WordClass.get_or_create(
                id=class_id,
                defaults={
                    "name": class_name.lower(),
                    "description": (
                        "Word class not classified yet"
                        if class_id == "unknown"
                        else f"Word class imported/mapped from dictionary POS: {class_name}"
                    ),
                },
            )

    def _ensure_schema_updates(self) -> None:
        table_name = Word._meta.table_name
        columns = {column.name for column in db.get_columns(table_name)}

        if "word_normalized" not in columns:
            db.execute_sql(f"ALTER TABLE {table_name} ADD COLUMN word_normalized TEXT DEFAULT ''")

        # Backfill normalized values for existing rows.
        db.execute_sql(
            f"UPDATE {table_name} SET word_normalized = LOWER(TRIM(word)) "
            "WHERE word_normalized IS NULL OR word_normalized = ''"
        )

        # Enforce uniqueness at DB level (best effort on existing DBs).
        try:
            db.execute_sql(
                f"CREATE UNIQUE INDEX IF NOT EXISTS word_language_normalized_unique "
                f"ON {table_name} (language_id, word_normalized)"
            )
        except IntegrityError:
            # Existing duplicated rows can prevent index creation; app-level validation still runs.
            pass

    def _has_blocking_warnings(self, validation_result) -> bool:
        return any(issue.rule_id in BLOCKING_WARNING_RULE_IDS for issue in validation_result.warnings)

    def _normalize_catalog_pos(self, pos_normalized: str, pos_raw: str) -> str:
        pos_normalized = (pos_normalized or "").strip().lower()
        if pos_normalized:
            return pos_normalized
        return RAW_DICT_POS_TO_NORMALIZED.get((pos_raw or "").strip().lower(), "unknown")

    def lookup_catalog_word(self, english_word: str) -> CatalogWordMatch | None:
        english_word_normalized = normalize_english_key(english_word)
        if not english_word_normalized:
            return None

        entry = (
            DictionaryEntry.select()
            .where(
                (DictionaryEntry.direction == "en_es")
                & (DictionaryEntry.headword_normalized == english_word_normalized)
            )
            .order_by(
                DictionaryEntry.translation_primary.desc(),
                DictionaryEntry.source_page.asc(),
            )
            .first()
        )
        if entry is not None:
            translation = (entry.translation_primary or entry.translation_text or "").strip()
            return CatalogWordMatch(
                english_word=entry.headword or english_word.strip(),
                english_word_normalized=english_word_normalized,
                spanish_translation=translation,
                pos_normalized=self._normalize_catalog_pos(entry.pos_normalized, entry.pos_raw),
                source="dictionaryentry",
                source_detail=f"page {entry.source_page}" if entry.source_page else "",
            )

        # Fallback de compatibilidad: si el catalogo nuevo esta vacio pero cargaron el PDF en `word`.
        fallback = (
            Word.select()
            .where((Word.language_id == "en") & (Word.word_normalized == english_word_normalized))
            .first()
        )
        if fallback is None:
            return None
        return CatalogWordMatch(
            english_word=fallback.word,
            english_word_normalized=english_word_normalized,
            spanish_translation=(fallback.traduction or "").strip(),
            pos_normalized=(fallback.word_class_id or "unknown").strip().lower() or "unknown",
            source="word_fallback",
            source_detail="catalogo temporal desde tabla word",
        )

    def create_vocabulary_entry(
        self,
        english_word: str,
        spanish_meaning: str,
        example_english: str,
        example_spanish: str,
    ):
        english_word = english_word.strip()
        english_word_normalized = normalize_english_key(english_word)
        spanish_meaning = spanish_meaning.strip()
        example_english = example_english.strip()
        example_spanish = example_spanish.strip()

        catalog_match = self.lookup_catalog_word(english_word) if english_word else None
        if catalog_match is not None:
            english_word = catalog_match.english_word or english_word
            english_word_normalized = catalog_match.english_word_normalized
            if not spanish_meaning and catalog_match.spanish_translation:
                spanish_meaning = catalog_match.spanish_translation

        if not all([english_word, spanish_meaning, example_english, example_spanish]):
            raise ValueError("All fields are required.")

        if (
            Word.select()
            .where((Word.language_id == "en") & (Word.word_normalized == english_word_normalized))
            .exists()
        ):
            raise ValueError("That English word is already saved.")

        english_validation = self.rule_engine.validate_sentence(
            example_english, language="english"
        )

        if english_validation.errors or self._has_blocking_warnings(english_validation):
            raise InvalidEnglishExampleError(english_validation)

        english_language = Language.get(Language.id == "en")
        word_class_id = "unknown"
        if catalog_match is not None and catalog_match.pos_normalized in POS_TO_WORD_CLASS:
            word_class_id = POS_TO_WORD_CLASS[catalog_match.pos_normalized][0]
        selected_word_class = WordClass.get(WordClass.id == word_class_id)

        with db.atomic():
            word = Word.create(
                id=uuid4().hex,
                word=english_word,
                word_normalized=english_word_normalized,
                word_class=selected_word_class,
                language=english_language,
                traduction=spanish_meaning,
            )

            Oration.create(
                id=uuid4().hex,
                word=word,
                text=example_english,
                traduction=example_spanish,
            )

        return word, english_validation

    def update_vocabulary_entry(
        self,
        word_id: str,
        english_word: str,
        spanish_meaning: str,
        example_english: str,
        example_spanish: str,
    ):
        english_word = english_word.strip()
        english_word_normalized = normalize_english_key(english_word)
        spanish_meaning = spanish_meaning.strip()
        example_english = example_english.strip()
        example_spanish = example_spanish.strip()

        if not word_id:
            raise ValueError("Missing word id for update.")

        word = Word.get_or_none(Word.id == word_id)
        if word is None or word.language_id != "en":
            raise ValueError("The selected word no longer exists.")

        catalog_match = self.lookup_catalog_word(english_word) if english_word else None
        if catalog_match is not None:
            english_word = catalog_match.english_word or english_word
            english_word_normalized = catalog_match.english_word_normalized
            if not spanish_meaning and catalog_match.spanish_translation:
                spanish_meaning = catalog_match.spanish_translation

        if not all([english_word, spanish_meaning, example_english, example_spanish]):
            raise ValueError("All fields are required.")

        duplicate_exists = (
            Word.select()
            .where(
                (Word.language_id == "en")
                & (Word.word_normalized == english_word_normalized)
                & (Word.id != word_id)
            )
            .exists()
        )
        if duplicate_exists:
            raise ValueError("That English word is already saved.")

        english_validation = self.rule_engine.validate_sentence(example_english, language="english")
        if english_validation.errors or self._has_blocking_warnings(english_validation):
            raise InvalidEnglishExampleError(english_validation)

        word_class_id = word.word_class_id or "unknown"
        if catalog_match is not None and catalog_match.pos_normalized in POS_TO_WORD_CLASS:
            word_class_id = POS_TO_WORD_CLASS[catalog_match.pos_normalized][0]

        with db.atomic():
            word.word = english_word
            word.word_normalized = english_word_normalized
            word.traduction = spanish_meaning
            if word_class_id:
                word.word_class_id = word_class_id
            word.save()

            example = (
                Oration.select()
                .where(Oration.word == word)
                .order_by(Oration.id.asc())
                .first()
            )
            if example is None:
                Oration.create(
                    id=uuid4().hex,
                    word=word,
                    text=example_english,
                    traduction=example_spanish,
                )
            else:
                example.text = example_english
                example.traduction = example_spanish
                example.save()

        return word, english_validation

    def list_vocabulary_entries(self) -> list[VocabularyEntry]:
        query = (
            Word.select(Word, Oration)
            .join(Oration, JOIN.LEFT_OUTER)
            .where(Word.language_id == "en")
            .order_by(Word.word.asc())
        )

        entries: list[VocabularyEntry] = []
        for word in query:
            example = word.orations.first()
            entries.append(
                VocabularyEntry(
                    word_id=word.id,
                    english_word=word.word,
                    spanish_meaning=word.traduction,
                    example_english=example.text if example else "",
                    example_spanish=example.traduction if example else "",
                )
            )
        return entries
