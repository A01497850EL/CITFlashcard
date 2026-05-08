from flask import Flask, render_template, request, redirect, url_for, abort, flash
from init_db import init_db, db, Deck, Card
from fsrs import FSRS, Card as FSRSCard, Rating, State
from datetime import datetime, timezone

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
    app.run(debug=False)

# STUDY MODE (FSRS)
@app.route("/decks/<int:deck_id>/study")
def study_deck(deck_id):
    deck = Deck.get_or_none(Deck.id == deck_id)
    if not deck:
        abort(404)
    now = datetime.now(timezone.utc)
    card = (Card.select()
                .where((Card.deck == deck_id) & (Card.due <= now))
                .order_by(Card.due)
                .first())
    show_answer = request.args.get("show_answer")
    return render_template("study.html", deck=deck, card=card, show_answer=show_answer)

@app.route("/decks/<int:deck_id>/card/<int:card_id>/review", methods=["POST"])
def review_card(deck_id, card_id):
    rating_map = {"again": Rating.Again, "hard": Rating.Hard,
                  "good": Rating.Good, "easy": Rating.Easy}
    rating = rating_map.get(request.form["rating"])
    if not rating:
        abort(400)

    card = Card.get_or_none((Card.id == card_id) & (Card.deck == deck_id))
    if not card:
        abort(404)

    fsrs_card = FSRSCard()
    fsrs_card.stability  = card.stability
    fsrs_card.difficulty = card.difficulty
    fsrs_card.due = card.due.replace(tzinfo=timezone.utc) if card.due else datetime.now(timezone.utc)
    fsrs_card.state = State(card.state)
    fsrs_card.reps = card.reps
    fsrs_card.lapses = card.lapses

    scheduling_cards = scheduler.repeat(fsrs_card, datetime.now(timezone.utc))
    updated = scheduling_cards[rating].card

    card.stability = updated.stability
    card.difficulty = updated.difficulty
    card.due = updated.due
    card.state = updated.state.value
    card.last_review = datetime.now(timezone.utc)
    card.reps = updated.reps
    card.lapses = updated.lapses
    card.save()

    return redirect(url_for("study_deck", deck_id=deck_id))

# WRITE MODE
@app.route("/decks/<int:deck_id>/write")
def write_mode(deck_id):
    deck = Deck.get_or_none(Deck.id == deck_id)
    if not deck:
        flash(f"Error: Could not locate deck with provided deck id {deck_id}")
        return redirect(url_for("show_decks"))
    cards = Card.select().where(Card.deck == deck).order_by(Card.id)
    cards_list = list(cards)
    if not cards_list:
        flash("No cards available in this deck to study.")
        return redirect(url_for("view_deck", deck_id=deck_id))
    index = request.args.get("index", 0, type=int)
    if index >= len(cards_list):
        flash("You have completed all flashcards in this deck!")
        return redirect(url_for("view_deck", deck_id=deck_id))
    card = cards_list[index]
    return render_template("write.html", deck=deck, card=card, index=index)

@app.route("/cards/<int:card_id>/write-answer", methods=["POST"])
def write_answer(card_id):
    card = Card.get_or_none(Card.id == card_id)
    if not card:
        flash(f"Error: Could not locate flashcard with provided card id {card_id}")
        return redirect(url_for("show_decks"))

    user_answer = request.form.get("answer", "").strip().lower()
    correct_answer = card.back.strip().lower()
    is_correct = user_answer == correct_answer
    override = request.form.get("override")

    if is_correct:
        rating = Rating.Good
    elif override == "true":
        rating = Rating.Hard
    else:
        rating = Rating.Again

    if is_correct or override == "true":
        card.confidence_score += 1
        if card.confidence_score >= 3:
            card.mastered = True
    else:
        card.confidence_score = max(0, card.confidence_score - 1)
        if card.confidence_score < 3:
            card.mastered = False

    fsrs_card = FSRSCard()
    fsrs_card.stability  = card.stability
    fsrs_card.difficulty = card.difficulty
    fsrs_card.due = card.due.replace(tzinfo=timezone.utc) if card.due else datetime.now(timezone.utc)
    fsrs_card.state = State(card.state)
    fsrs_card.reps = card.reps
    fsrs_card.lapses = card.lapses

    scheduling_cards = scheduler.repeat(fsrs_card, datetime.now(timezone.utc))
    updated = scheduling_cards[rating].card

    card.stability = updated.stability
    card.difficulty  = updated.difficulty
    card.due = updated.due
    card.state = updated.state.value
    card.last_review = datetime.now(timezone.utc)
    card.reps = updated.reps
    card.lapses = updated.lapses

    card.save()
    next_index = request.form.get("index", 0, type=int) + 1
    return redirect(url_for("write_mode", deck_id=card.deck.id, index=next_index))

# FLIP MODE
@app.route("/decks/<int:deck_id>/flip")
def flip_mode(deck_id):
    deck = Deck.get_or_none(Deck.id == deck_id)
    if not deck:
        flash(f"Error: Could not locate deck with provided deck id {deck_id}")
        return redirect(url_for("show_decks"))
    cards = Card.select().where(Card.deck == deck).order_by(Card.id)
    cards_list = list(cards)
    if not cards_list:
        flash("No cards available in this deck to study.")
        return redirect(url_for("view_deck", deck_id=deck_id))
    index = request.args.get("index", 0, type=int)
    if index >= len(cards_list):
        flash("You have completed all flashcards in this deck!")
        return redirect(url_for("view_deck", deck_id=deck_id))
    card = cards_list[index]
    return render_template("flip.html", deck=deck, card=card, index=index)

@app.route("/cards/<int:card_id>/flip-answer", methods=["POST"])
def flip_answer(card_id):
    card = Card.get_or_none(Card.id == card_id)
    if not card:
        flash(f"Error: Could not locate flashcard with provided card id {card_id}")
        return redirect(url_for("show_decks"))

    result = request.form.get("result")

    if result == "yes":
        rating = Rating.Good
        card.confidence_score += 1
        if card.confidence_score >= 3:
            card.mastered = True
    elif result == "no":
        rating = Rating.Again
        card.confidence_score = max(0, card.confidence_score - 1)
        if card.confidence_score < 3:
            card.mastered = False
    else:
        flash("Invalid response received.")
        return redirect(url_for("flip_mode", deck_id=card.deck.id))

    fsrs_card = FSRSCard()
    fsrs_card.stability  = card.stability
    fsrs_card.difficulty = card.difficulty
    fsrs_card.due = card.due.replace(tzinfo=timezone.utc) if card.due else datetime.now(timezone.utc)
    fsrs_card.state = State(card.state)
    fsrs_card.reps = card.reps
    fsrs_card.lapses = card.lapses

    scheduling_cards = scheduler.repeat(fsrs_card, datetime.now(timezone.utc))
    updated = scheduling_cards[rating].card

    card.stability = updated.stability
    card.difficulty  = updated.difficulty
    card.due = updated.due
    card.state = updated.state.value
    card.last_review = datetime.now(timezone.utc)
    card.reps = updated.reps
    card.lapses = updated.lapses

    card.save()
    next_index = request.form.get("index", 0, type=int) + 1
    return redirect(url_for("flip_mode", deck_id=card.deck.id, index=next_index))

if __name__ == "__main__":
    app.run(debug=False)
    