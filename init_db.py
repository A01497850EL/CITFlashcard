from peewee import *
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

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
    hint = CharField(null=True)
    mastered = BooleanField(default=False)
    confidence_score = IntegerField(default=0)

class CardTagJunction(BaseModel):
    cards = ForeignKeyField(Card, backref='card_link', on_delete='CASCADE')
    tags = ForeignKeyField(Tag, backref='decks', on_delete='CASCADE')

class User(BaseModel):
    username = CharField(unique=True)
    password_hash = CharField()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)




def init_db():
    with db:
        db.create_tables([Deck, Card, Tag, DeckTagJunction, CardTagJunction, User], safe=True)

if __name__ == "__main__":
    init_db()

