#imports
from peewee import CharField, TextField

from Models.base_model import BaseModel

#=======================================
#Model
class Language(BaseModel):
    id = TextField(primary_key=True)
    name = CharField()