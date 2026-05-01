from flask import Flask, render_template, request, redirect, url_for, flash
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

@app.route("/decks/<int:deck_id>/card/<int:card_id>/delete", methods=["POST"])
def delete_card(deck_id, card_id):
    deck = Deck.get_or_none(Deck.id == deck_id)
    if not deck:
        flash(f"Error: Could not locate deck with provided deck id {deck_id}")
        return redirect(url_for("view_deck", id=deck_id))
    
    card = Card.get_or_none((Card.id == card_id) & (Card.deck == deck_id))
    if not card: 
        flash(f"Error: Could not locate flashcard with provided card id {card_id}")
        return redirect(url_for("view_deck", id=deck_id))
        
    card.delete_instance()
    flash(f"Card {card_id} deleted successsfully.")
    return redirect(url_for("view_deck", id=deck_id))

if __name__ == "__main__":
    app.run(debug=True)
