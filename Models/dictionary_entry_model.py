from peewee import IntegerField, TextField

from Models.base_model import BaseModel


class DictionaryEntry(BaseModel):
    id = TextField(primary_key=True)
    source_name = TextField(default="superdiccionario")
    direction = TextField(default="en_es")
    import_batch = TextField(default="")
    source_page = IntegerField(default=0)
    raw_line = TextField()

    headword = TextField(default="")
    headword_normalized = TextField(default="")
    pos_raw = TextField(default="")
    pos_normalized = TextField(default="")

    translation_text = TextField(default="")
    translation_primary = TextField(default="")

    status = TextField(default="raw")

    class Meta:
        indexes = (
            (("source_name", "direction", "source_page", "raw_line"), True),
            (("headword_normalized", "pos_normalized"), False),
        )
