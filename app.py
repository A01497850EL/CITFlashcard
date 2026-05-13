from flask import Flask, render_template, request, redirect, url_for, abort, flash
from init_db import init_db, db, Deck, Card, Tag, DeckTagJunction
from fsrs import Scheduler, Card as FSRSCard, Rating, State
from datetime import datetime, timezone
 
import os
 
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")
 
init_db()
scheduler = Scheduler()
 
 
def _to_fsrs_card(card):
    """Build an FSRS Card from one of our DB Card rows."""
    fsrs_card = FSRSCard()
    fsrs_card.stability = card.stability
    fsrs_card.difficulty = card.difficulty
    fsrs_card.due = (
        card.due.replace(tzinfo=timezone.utc)
        if card.due else datetime.now(timezone.utc)
    )
    fsrs_card.state = State(card.state)
    fsrs_card.step = getattr(card, "step", 0)
    return fsrs_card
 
 
def _apply_fsrs_update(card, rating):
    """Run the FSRS scheduler for `rating` and persist the result on `card`."""
    fsrs_card = _to_fsrs_card(card)
    updated, _review_log = scheduler.review_card(fsrs_card, rating)
 
    card.stability = updated.stability
    card.difficulty = updated.difficulty
    card.due = updated.due
    card.state = updated.state.value
    card.last_review = datetime.now(timezone.utc)
    card.save()
 
 
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
    rating_map = {
        "again": Rating.Again,
        "hard": Rating.Hard,
        "good": Rating.Good,
        "easy": Rating.Easy,
    }
    rating = rating_map.get(request.form.get("rating"))
    if not rating:
        abort(400)
 
    card = Card.get_or_none((Card.id == card_id) & (Card.deck == deck_id))
    if not card:
        abort(404)
 
    _apply_fsrs_update(card, rating)
    return redirect(url_for("study_deck", deck_id=deck_id))
 
 
# WRITE MODE
@app.route("/decks/<int:deck_id>/write")
def write_mode(deck_id):
    deck = Deck.get_or_none(Deck.id == deck_id)
    if not deck:
        flash(f"Error: Could not locate deck with provided deck id {deck_id}")
        return redirect(url_for("show_decks"))
    cards_list = list(Card.select().where(Card.deck == deck).order_by(Card.id))
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
    override = request.form.get("override") == "true"
 
    if is_correct:
        rating = Rating.Good
    elif override:
        rating = Rating.Hard
    else:
        rating = Rating.Again
 
    # Confidence tracking
    if is_correct or override:
        card.confidence_score += 1
        if card.confidence_score >= 3:
            card.mastered = True
    else:
        card.confidence_score = max(0, card.confidence_score - 1)
        if card.confidence_score < 3:
            card.mastered = False
 
    _apply_fsrs_update(card, rating)
 
    next_index = request.form.get("index", 0, type=int) + 1
    return redirect(url_for("write_mode", deck_id=card.deck.id, index=next_index))
 
 
# FLIP MODE
@app.route("/decks/<int:deck_id>/flip")
def flip_mode(deck_id):
    deck = Deck.get_or_none(Deck.id == deck_id)
    if not deck:
        flash(f"Error: Could not locate deck with provided deck id {deck_id}")
        return redirect(url_for("show_decks"))
    cards_list = list(Card.select().where(Card.deck == deck).order_by(Card.id))
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
 
    _apply_fsrs_update(card, rating)
 
    next_index = request.form.get("index", 0, type=int) + 1
    return redirect(url_for("flip_mode", deck_id=card.deck.id, index=next_index))
 
 
if __name__ == "__main__":
    app.run(debug=True)
 
