from peewee import *
from datetime import datetime

db = SqliteDatabase("flashcards.db")

class BaseModel(Model):
    class Meta:
        database = db

class DeckTag(BaseModel):
    name = CharField()

class Deck(BaseModel):
    name = CharField()
    description = CharField(null=True)
    tags = ForeignKeyField(DeckTag, backref="decks", on_delete="CASCADE")
    created_at = DateTimeField(default=datetime.now)

class CardTag(BaseModel):
    name = CharField()

class Card(BaseModel):
    deck = ForeignKeyField(Deck, backref="cards", on_delete="CASCADE")
    tag = ForeignKeyField(CardTag, backref="cards", on_delete="CASCADE")
    front = CharField()
    back = CharField()
    mastered = BooleanField(default=False)

def init_db():
    with db:
        db.create_tables([Deck, Card], safe=True)

if __name__ == "__main__":
    init_db()

