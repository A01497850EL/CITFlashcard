from peewee import *
from datetime import datetime

db = SqliteDatabase("flashcards.db")

class BaseModel(Model):
    class Meta:
        database = db
# Peewee ORM models for Deck
class Deck(BaseModel):
    name = CharField(unique=True)
    description = CharField(null=True)
    tags = CharField(null=True)
    created_at = DateTimeField(default=datetime.now)


class Card(BaseModel):
    deck = ForeignKeyField(Deck, backref="cards", on_delete="CASCADE")
    front = CharField()
    back = CharField()
    mastered = BooleanField(default=False)

def init_db():
    db.connect()
    db.create_tables([Deck, Card], safe=True)
    db.close()
    print("Database initialized.")

if __name__ == "__main__":
    init_db()

