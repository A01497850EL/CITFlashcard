from flask import Flask, render_template, request, redirect, url_for
from init_db import init_db, db, Deck, Card
import random
from init_db import init_db, Deck
init_db()
app = Flask(__name__)


# -----------------------------
# HOME PAGE (REQUIRED)
# -----------------------------
@app.route("/")
def index():
    """
    Displays homepage with all decks
    """
    decks = Deck.select()
    return render_template("index.html", decks=decks)

# Edited by bareera
# creating decks 
@app.route("/deck/create", methods=["POST"])
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
    # Peewee automatically inserts it into the "decks" table
    Deck.create(
        name=name,
        description=description,
        tags=tags
    )
    # Redirect user back to homepage after creating deck
    return redirect(url_for("index"))

#creating cards 
@app.route("/deck/<int:deck_id>")
def view_deck(deck_id):
    db = get_db()
    deck = db.execute("SELECT * FROM decks WHERE id = ?", (deck_id,)).fetchone()
    cards = db.execute("SELECT * FROM cards WHERE deck_id = ?", (deck_id,)).fetchall()
    db.close()
    return render_template("deck.html", deck=deck, cards=cards)

@app.route("/decks/<int:deck_id>/card/create", methods=["POST"])
def create_card(deck_id):
    front = request.form["front"]
    back  = request.form["back"]
    Card.create(deck=deck_id, front=front, back=back)
    return redirect(url_for("view_deck", id=deck_id))

if __name__ == "__main__":
    app.run(debug=True)
