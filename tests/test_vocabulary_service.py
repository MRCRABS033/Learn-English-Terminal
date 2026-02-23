import os
import tempfile
import unittest
from unittest.mock import patch

try:
    from peewee import IntegrityError
    from Models.base_model import db
    from Models.word_model import Word
    from Models.oration_model import Oration
    from Services.storage.vocabulary_service import (
        InvalidEnglishExampleError,
        VocabularyService,
        normalize_english_key,
    )
    PEEWEE_AVAILABLE = True
except ModuleNotFoundError:
    PEEWEE_AVAILABLE = False


@unittest.skipUnless(PEEWEE_AVAILABLE, "peewee is not installed in this Python environment")
class VocabularyServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        fd, self.db_path = tempfile.mkstemp(prefix="tle_test_", suffix=".db")
        os.close(fd)
        if not db.is_closed():
            db.close()
        db.init(self.db_path, pragmas={"foreign_keys": 1})
        self.service = VocabularyService()
        self.service.initialize_database()

    def tearDown(self) -> None:
        if not db.is_closed():
            db.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def _create_valid_entry(self, english_word: str = "house", example: str = "The house is big."):
        return self.service.create_vocabulary_entry(
            english_word=english_word,
            spanish_meaning="casa",
            example_english=example,
            example_spanish="La casa es grande.",
        )

    def test_blocks_critical_warning_in_hybrid_mode(self) -> None:
        with self.assertRaises(InvalidEnglishExampleError):
            self.service.create_vocabulary_entry(
                english_word="house",
                spanish_meaning="casa",
                example_english="the house big is",
                example_spanish="la casa grande es",
            )

    def test_allows_non_blocking_warning_and_saves(self) -> None:
        word, validation = self.service.create_vocabulary_entry(
            english_word="interest",
            spanish_meaning="interes",
            example_english="I am interested on music.",
            example_spanish="Estoy interesado en la musica.",
        )
        self.assertIsNotNone(word.id)
        self.assertTrue(any(issue.rule_id == "en.preposition_collocation" for issue in validation.warnings))
        self.assertEqual(Word.select().count(), 1)
        self.assertEqual(Oration.select().count(), 1)

    def test_rollback_when_oration_create_fails(self) -> None:
        def failing_create(*args, **kwargs):
            raise RuntimeError("boom")

        with patch.object(Oration, "create", side_effect=failing_create):
            with self.assertRaises(RuntimeError):
                self._create_valid_entry(english_word="book", example="The book is new.")

        self.assertEqual(Word.select().where(Word.word == "book").count(), 0)
        self.assertEqual(Oration.select().count(), 0)

    def test_duplicate_check_is_exact_not_like(self) -> None:
        self._create_valid_entry(english_word="ab%", example="I study English.")
        # This should not be treated as duplicate of 'ab%'.
        self._create_valid_entry(english_word="abx", example="I read books.")
        self.assertEqual(Word.select().count(), 2)

    def test_db_unique_constraint_on_language_and_word_normalized(self) -> None:
        self._create_valid_entry(english_word="House", example="The house is big.")
        en_lang_id = "en"
        unknown_class_id = "unknown"
        with self.assertRaises(IntegrityError):
            Word.create(
                id="forceddup",
                word="house",
                word_normalized=normalize_english_key("house"),
                word_class=unknown_class_id,
                language=en_lang_id,
                traduction="casa",
            )


if __name__ == "__main__":
    unittest.main()
