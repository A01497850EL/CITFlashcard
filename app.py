from flask import Flask, render_template, request, redirect, url_for, abort, flash
from init_db import init_db, db, Deck, Card
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")

init_db()

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
    name = request.form["name"]
    description = request.form.get("description", "")
    tags = request.form.get("tags", "")
    if not name:
        return "Deck name is required", 400
    Deck.create(name=name, description=description, tags=tags)
    return redirect(url_for("show_decks"))

# viewing a deck
@app.route("/decks/<int:deck_id>")
def view_deck(deck_id):
    try:
        deck = Deck.get_by_id(deck_id)
    except Deck.DoesNotExist:
        abort(404)
    cards = Card.select().where(Card.deck == deck_id)
    return render_template("decks.html", deck=deck, cards=cards)

# creating cards
@app.route("/decks/<int:deck_id>/card/create", methods=["POST"])
def create_card(deck_id):
    front = request.form["front"]
    back = request.form["back"]
    Card.create(deck=deck_id, front=front, back=back)
    return redirect(url_for("view_deck", deck_id=deck_id))

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
        flash("Deck deleted successfully.")
    except Deck.DoesNotExist:
        flash(f"Error: Could not locate deck with id {deck_id}")
    # Redirect back to decks page
    return redirect(url_for("show_decks"))

if __name__ == "__main__":
    app.run(debug=True)

@app.route("/aboutus")
def aboutus():
    return render_template("aboutus.html")
    app.run(debug=False)
