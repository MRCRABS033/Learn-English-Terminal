#Imports
from Models.language import Language
from Models.word_class_model import WordClass
from Models.base_model import BaseModel
from peewee import ForeignKeyField, TextField


#=======================================
#Model

class Word(BaseModel):
    """
    This class represent a word class.

    id: TextField(primary_key=True) word's id.
    """
    id = TextField(primary_key=True)
    word = TextField()
    word_normalized = TextField(default="")
    word_class = ForeignKeyField(WordClass, backref="words")
    language = ForeignKeyField(Language, backref="words")
    traduction = TextField()
