from peewee import *
from datetime import datetime

db = SqliteDatabase("flashcards.db")

class BaseModel(Model):
    class Meta:
        database = db

class Deck(BaseModel):
    name = CharField()
    description = CharField(null=True)
    tags = CharField(null=True)
    created_at = DateTimeField(default=datetime.now)

class Card(BaseModel):
    deck = ForeignKeyField(Deck, backref="cards", on_delete="CASCADE")
    front = CharField()
    back = CharField()
    mastered = BooleanField(default=False)

    #FSRS

    stability = FloatField(default=0)
    difficulty = FloatField(default=0)
    due = DateTimeField(default=datetime.now)
    state = IntegerField(default=0)
    last_review = DateTimeField(null=True)
    reps = IntegerField(default=0)
    lapses = IntegerField(default=0)

def init_db():
    with db:
        db.create_tables([Deck, Card], safe=True)

if __name__ == "__main__":
    init_db()

