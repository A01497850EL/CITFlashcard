from flask import Flask, render_template, request, redirect, url_for, abort 
from init_db import init_db, db, Deck, Card
import os
init_db()
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")

init_db()

# -----------------------------
# HOME PAGE 
# -----------------------------

@app.before_request
def before_request():
    db.connect(reuse_if_open=True)

@app.teardown_request
def teardown_request(exc):
    if not db.is_closed():
        db.close()


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
    try:
        deck = Deck.get_by_id(deck_id)
    except Deck.DoesNotExist:
        abort(404)
    cards = Card.select().where(Card.deck == deck_id)
    return render_template("decks.html", deck=deck, cards=cards)

@app.route("/decks/<int:deck_id>/card/create", methods=["POST"])
def create_card(deck_id):
    front = request.form["front"]
    back = request.form["back"]
    Card.create(deck=deck_id, front=front, back=back)
    return redirect(url_for("view_deck", deck_id=deck_id))

if __name__ == "__main__":
    app.run(debug=False)
