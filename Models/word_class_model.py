#imports
from peewee import TextField
from Models.base_model import BaseModel
#=======================================
#Model
class WordClass(BaseModel):
    id = TextField(primary_key=True)
    name = TextField()
    description = TextField()