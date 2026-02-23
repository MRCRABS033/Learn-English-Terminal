from peewee import ForeignKeyField, TextField

from Models.base_model import BaseModel
from Models.word_model import Word


class Oration(BaseModel):
    id = TextField(primary_key=True)
    word = ForeignKeyField(Word, backref="orations")
    text = TextField()
    traduction = TextField()
