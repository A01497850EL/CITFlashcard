from peewee import *
from datetime import datetime

db = SqliteDatabase("flashcards.db")

class BaseModel(Model):
    class Meta:
        database = db

class Tag(BaseModel):
    name = CharField()

class Deck(BaseModel):
    name = CharField()
    description = CharField(null=True)
    created_at = DateTimeField(default=datetime.now)

class DeckTagJunction(BaseModel):
    decks = ForeignKeyField(Deck, backref='tags', on_delete='CASCADE')
    tags = ForeignKeyField(Tag, backref='decks', on_delete='CASCADE')

class Card(BaseModel):
    deck = ForeignKeyField(Deck, backref="cards", on_delete="CASCADE")
    front = CharField()
    back = CharField()
    mastered = BooleanField(default=False)
    confidence_score = IntegerField(default=0)

class CardTagJunction(BaseModel):
    cards = ForeignKeyField(Card, backref='card_link', on_delete='CASCADE')
    tags = ForeignKeyField(Tag, backref='decks', on_delete='CASCADE')


def init_db():
    with db:
        db.create_tables([Deck, Card, Tag, DeckTagJunction, CardTagJunction], safe=True)

if __name__ == "__main__":
    init_db()

