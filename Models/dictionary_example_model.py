from peewee import ForeignKeyField, IntegerField, TextField

from Models.base_model import BaseModel
from Models.dictionary_entry_model import DictionaryEntry


class DictionaryExample(BaseModel):
    id = TextField(primary_key=True)
    entry = ForeignKeyField(DictionaryEntry, backref="examples", on_delete="CASCADE")
    example_text = TextField(default="")
    example_translation = TextField(default="")
    raw_text = TextField(default="")
    source_page = IntegerField(default=0)
