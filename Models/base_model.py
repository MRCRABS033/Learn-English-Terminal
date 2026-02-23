from peewee import Model, SqliteDatabase

db = SqliteDatabase(
    "app.db",
    pragmas={
        "foreign_keys": 1,
    },
)

class BaseModel(Model):
    class Meta:
        database = db
