from flask import Flask, render_template, request, redirect, url_for
from init_db import init_db, db, Deck, Card
import random

app = Flask(__name__)
init_db()


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/decks")
def decks():
    all_decks = Deck.select().order_by(Deck.created_at.desc())
    return render_template("decks.html", decks=all_decks)

@app.route("/decks/create", methods=["POST"])
def create_deck():
    name = request.form["name"]
    Deck.create(name=name)
    return redirect(url_for("decks"))


@app.route("/decks/<int:id>")
def view_deck(id):
    deck  = Deck.get_by_id(id)
    cards = Card.select().where(Card.deck == id)
    return render_template("deck.html", deck=deck, cards=cards)

@app.route("/decks/<int:deck_id>/card/create", methods=["POST"])
def create_card(deck_id):
    front = request.form["front"]
    back  = request.form["back"]
    Card.create(deck=deck_id, front=front, back=back)
    return redirect(url_for("view_deck", id=deck_id))

# DELETE DECK
@app.route("/decks/<int:deck_id>/delete", methods=["POST"])
def delete_deck(deck_id):
    """
    Deletes a flashcard deck using Peewee ORM
    """
    try:
        # Get the deck
        deck = Deck.get_by_id(deck_id)
        # Delete deck + related cards
        deck.delete_instance(recursive=True)
    except Deck.DoesNotExist:
        return "Deck not found", 404
    # Redirect back to decks page
    return redirect(url_for("show_decks"))

if __name__ == "__main__":
    app.run(debug=True)
