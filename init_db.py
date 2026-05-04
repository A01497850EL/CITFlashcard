from peewee import *

db = SqliteDatabase("flashcards.db")

class BaseModel(Model):
    class Meta:
        database = db

class Deck(BaseModel):
    name = CharField()
    created_at = DateTimeField(constraints=[SQL("DEFAULT CURRENT_TIMESTAMP")])

class Card(BaseModel):
    deck = ForeignKeyField(Deck, backref="cards", on_delete="CASCADE")
    front = CharField()
    back = CharField()
    mastered = BooleanField(default=False)
    confidence_score = IntegerField(default=0)
def init_db():
    db.connect()
    db.create_tables([Deck, Card], safe=True)
    db.close()
    print("Database initialized.")

if __name__ == "__main__":
    init_db()

