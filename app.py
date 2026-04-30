from flask import Flask, render_template, request, redirect, url_for
from init_db import init_db, db, Deck, Card
import random
from init_db import init_db, Deck
init_db()
app = Flask(__name__)


# -----------------------------
# HOME PAGE 
# -----------------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/decks")
def show_decks():
    decks = Deck.select()
    return render_template("decks.html", decks=decks)

# creating decks 
@app.route("/decks/create", methods=["POST"])
def create_deck():
    """
    Creates a new flashcard deck using Peewee ORM
    """
    # Get the deck name from the HTML form
    name = request.form["name"]
    description = request.form.get("description", "")
    tags = request.form.get("tags", "")
    # Basic validation: making sure name is not empty
    if not name:
        return "Deck name is required", 400
    # Create a new deck in the database
    Deck.create(
        name=name,
        description=description,
        tags=tags
    )
    # Redirect user back to show decks page after creating deck
    return redirect(url_for("show_decks"))

#creating cards 
@app.route("/decks/<int:deck_id>")
def view_deck(deck_id):
    deck = Deck.get_by_id(deck_id)
    cards = deck.cards
    return render_template("deck.html", deck=deck, cards=cards)

@app.route("/deck/<int:deck_id>/card/create", methods=["POST"])
def create_card(deck_id):
    front = request.form["front"]
    back = request.form["back"]
    db = get_db()
    db.execute(
        "INSERT INTO cards (deck_id, front, back) VALUES (?, ?, ?)",
        (deck_id, front, back)
    )

    db.commit()
    db.close()
    return redirect(url_for("view_deck", deck_id=deck_id))