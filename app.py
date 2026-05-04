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

# flashcard flip mode
@app.route("/decks/<int:deck_id>/flip")
def flip_mode(deck_id):
    deck = Deck.get_or_none(Deck.id == deck_id)
    if not deck:
        # If deck does not exist, show error and redirect
        flash(f"Error: Could not locate deck with provided deck id {deck_id}")
        return redirect(url_for("decks"))
    
    cards = Card.select().where(Card.deck == deck)
    cards_list = list(cards)
    if not cards_list:
        # If no cards exist in deck
        flash("No cards available in this deck to study.")
        return redirect(url_for("view_deck", id=deck_id))
    # Get current index from URL (default = 0)
    index = request.args.get("index", 0, type=int)
    # If user reached end of deck
    if index >= len(cards_list):
        flash("You have completed all flashcards in this deck!")
        return redirect(url_for("view_deck", id=deck_id))
    # Get card in order
    card = cards_list[index]
    # Send card + index to frontend
    return render_template("flip.html", deck=deck, card=card, index=index)

# Handle user answer and update confidence
@app.route("/cards/<int:card_id>/flip-answer", methods=["POST"])
def flip_answer(card_id):
    card = Card.get_or_none(Card.id == card_id)
    if not card:
        # If card not found
        flash(f"Error: Could not locate flashcard with provided card id {card_id}")
        return redirect(url_for("decks"))
    # Get result from form 
    result = request.form.get("result")
    if result == "yes":
        card.confidence_score += 1
        if card.confidence_score >= 3:
            card.mastered = True

    elif result == "no":
        card.confidence_score = max(0, card.confidence_score - 1)
        card.mastered = False

    else:
        # Invalid input safety check
        flash("Invalid response received.")
        return redirect(url_for("flip_mode", deck_id=card.deck.id))
    # Save updated values to database
    card.save()
    # Get current index from form
    current_index = request.form.get("index", 0, type=int)
    # Move to next card
    next_index = current_index + 1
    # Redirect to next card
    return redirect(url_for("flip_mode", deck_id=card.deck.id, index=next_index))

if __name__ == "__main__":
    app.run(debug=True)
