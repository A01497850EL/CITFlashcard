from flask import Flask, render_template, request, redirect, url_for, abort, flash
from init_db import init_db, db, Deck, Card, Tag, DeckTagJunction, CardTagJunction
from peewee import JOIN
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
    decks = Deck.select()
    return render_template("index.html", decks=decks)

@app.route("/decks")
def show_decks():
# Get search query from URL parameters
    search_query = request.args.get("search", "").strip()
# Default query returns all decks
    decks = Deck.select().distinct()
    # If user entered a search query
    if search_query:
        # Search decks by deck name OR tag name
        decks = (
            Deck
            .select()
            .join(DeckTagJunction, JOIN.LEFT_OUTER)
            .join(Tag, JOIN.LEFT_OUTER)
            .where(
                (Deck.name.contains(search_query)) |
                (Tag.name.contains(search_query))
            )
            .distinct()
        )
    return render_template("decks.html", decks=decks)

# creating decks
@app.route("/decks/create", methods=["GET", "POST"])
def create_deck():
    # If the user clicks "Save Deck" (Submitting the form)
    if request.method == "POST":
        name = request.form["name"]
        description = request.form.get("description", "")
        tags = request.form.get("tags", "")
        
        if not name:
            return "Deck name is required", 400
            
        deck = Deck.create(name=name, description=description)
        
        for tag_name in tags.split(","):
            tag_name = tag_name.strip()
            if tag_name:
                tag, created = Tag.get_or_create(name=tag_name)
                DeckTagJunction.create(decks=deck, tags=tag)
                
        return redirect(url_for("show_decks"))
        
    # If the user just clicks "Create Deck" in the navbar (Viewing the page)
    return render_template("createdeck.html")

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
    # Save the hint to the database
    front = request.form.get("front", "").strip()
    back = request.form.get("back", "").strip()
    tags = request.form.get("tags", "").strip()
    hint = request.form.get("hint", "").strip()
    card = Card.create(deck=deck_id, front=front, back=back, hint=hint)
    for tag_name in tags.split(","):
        tag_name = tag_name.strip()
        if tag_name:
            tag, created = Tag.get_or_create(name=tag_name)
            CardTagJunction.create(cards=card, tags=tag)
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
    
# Update Flashcard
@app.route("/decks/<int:deck_id>/card/<int:card_id>/update", methods=["POST"])
def update_card(deck_id, card_id):
    """
    Updates a card's information via a card's id
    """
    #Get Card via ID with validation
    card = Card.get_or_none((Card.id == card_id) & (Card.deck == deck_id))
    #Validation
    if not card:
        flash(f"Error: Could not locate card with {card_id}")
        return redirect(url_for("show_decks"))
    #get data
    front = request.form.get("front", "").strip()
    back = request.form.get("back", "").strip()
    tags = request.form.get("tags", "").strip()

    #Validation
    if not front or not back:
        flash("Error: Please enter valid front and backsides for flashcards.")
        return redirect(url_for("view_deck", deck_id=deck_id))
    
    #save card front/back
    card.front = front
    card.back = back
    card.save()

    #Delete former tag data
    CardTagJunction.delete().where(CardTagJunction.cards == card).execute()

    #Recreate tags
    for tag_name in tags.split(","):
        tag_name = tag_name.strip()
        if tag_name:
            tag, created = Tag.get_or_create(name=tag_name)
            CardTagJunction.create(cards=card, tags=tag)

    return redirect(url_for("view_deck", deck_id=deck_id))

@app.route("/decks/<int:deck_id>/card/<int:card_id>/delete", methods=["POST"])
def delete_card(deck_id, card_id):
    deck = Deck.get_or_none(Deck.id == deck_id)
    if not deck:
        flash(f"Error: Could not locate deck with provided deck id {deck_id}")
        return redirect(url_for("view_deck", deck_id=deck_id))
    
    card = Card.get_or_none((Card.id == card_id) & (Card.deck == deck_id))
    if not card: 
        flash(f"Error: Could not locate flashcard with provided card id {card_id}")
        return redirect(url_for("view_deck", deck_id=deck_id))
        
    card.delete_instance()
    flash(f"Card {card_id} deleted successsfully.")
    return redirect(url_for("view_deck", deck_id=deck_id))

# Route to About Us page
@app.route("/aboutus")
def aboutus():
    return render_template("aboutus.html")

# flashcard write mode
@app.route("/decks/<int:deck_id>/write")
def write_mode(deck_id):
    deck = Deck.get_or_none(Deck.id == deck_id)
    if not deck:
        # If deck does not exist, show error and redirect
        flash(f"Error: Could not locate deck with provided deck id {deck_id}")
        return redirect(url_for("show_decks"))
    # Get all cards in sequential order
    cards = Card.select().where(Card.deck == deck).order_by(Card.id)
    cards_list = list(cards)
    if not cards_list:
        # If no cards exist in deck
        flash("No cards available in this deck to study.")
        return redirect(url_for("view_deck", deck_id=deck_id))
    # Get current index from URL (default = 0)
    index = request.args.get("index", 0, type=int)
    # If user completed all flashcards
    if index >= len(cards_list):
        flash("You have completed all flashcards in this deck!")
        return redirect(url_for("view_deck", deck_id=deck_id))
    # Get current card
    card = cards_list[index]
    # Send card + index to frontend
    return render_template("write.html", deck=deck, card=card, index=index, total_cards=len(cards_list))


# Handle write mode answer
@app.route("/cards/<int:card_id>/write-answer", methods=["POST"])
def write_answer(card_id):
    card = Card.get_or_none(Card.id == card_id)
    if not card:
        # If card not found
        flash(f"Error: Could not locate flashcard with provided card id {card_id}")
        return redirect(url_for("show_decks"))
    # Get user's typed answer
    user_answer = request.form.get("answer", "").strip().lower()
    # Get correct flashcard answer
    correct_answer = card.back.strip().lower()
    # Check if user's answer matches the definition
    is_correct = user_answer == correct_answer
    # Allow user to override incorrect judgement
    override = request.form.get("override")

    if is_correct or override == "true":
        # Increase confidence score
        card.confidence_score += 1
        # Mark as mastered if confidence score reaches 3
        if card.confidence_score >= 3:
            card.mastered = True
    else:
        # Decrease confidence score but never below 0
        card.confidence_score = max(0, card.confidence_score - 1)
        # Remove mastered status if confidence score drops below 3
        if card.confidence_score < 3:
            card.mastered = False
    card.save()
    next_index = request.form.get("index", 0, type=int) + 1
    return redirect(url_for("write_mode", deck_id=card.deck.id, index=next_index))

# flashcard flip mode
@app.route("/decks/<int:deck_id>/flip")
def flip_mode(deck_id):
    deck = Deck.get_or_none(Deck.id == deck_id)
    if not deck:
        # If deck does not exist, show error and redirect
        flash(f"Error: Could not locate deck with provided deck id {deck_id}")
        return redirect(url_for("show_decks"))
    
    cards = Card.select().where(Card.deck == deck).order_by(Card.id)
    cards_list = list(cards)
    if not cards_list:
        # If no cards exist in deck
        flash("No cards available in this deck to study.")
        return redirect(url_for("view_deck", deck_id=deck_id))
    # Get current index from URL (default = 0)
    index = request.args.get("index", 0, type=int)
    # If user reached end of deck
    if index >= len(cards_list):
        flash("You have completed all flashcards in this deck!")
        return redirect(url_for("view_deck", deck_id=deck_id))
    # Get card in order
    card = cards_list[index]
    # Send card + index to frontend
    return render_template("flip.html", deck=deck, card=card, index=index, total_cards=len(cards_list))

# Handle user answer and update confidence
@app.route("/cards/<int:card_id>/flip-answer", methods=["POST"])
def flip_answer(card_id):
    card = Card.get_or_none(Card.id == card_id)
    if not card:
        # If card not found
        flash(f"Error: Could not locate flashcard with provided card id {card_id}")
        return redirect(url_for("show_decks"))
    # Get result from form 
    result = request.form.get("result")
    if result == "yes":
        card.confidence_score += 1
        if card.confidence_score >= 3:
            card.mastered = True

    elif result == "no":
        card.confidence_score = max(0, card.confidence_score - 1)
        if card.confidence_score < 3:
            card.mastered = False
    else:
        # Invalid input safety check
        flash("Invalid response received.")
        return redirect(url_for("flip_mode", deck_id=card.deck.id))
    # Save updated values to database
    card.save()
    next_index = request.form.get("index", 0, type=int) + 1
    # Redirect to next card
    return redirect(url_for("flip_mode", deck_id=card.deck.id, index=next_index))

# UPDATE DECK
@app.route("/decks/<int:deck_id>/update", methods=["POST"])
def update_deck(deck_id):
    deck = Deck.get_or_none(Deck.id == deck_id)
    if not deck:
        flash(f"Error: Could not locate deck with id {deck_id}")
        return redirect(url_for("show_decks"))
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    tags = request.form.get("tags", "")
    if not name:
        flash("Deck name is required.")
        return redirect(url_for("view_deck", deck_id=deck_id))
    
    deck.name = name
    deck.description = description
    deck.save()
    DeckTagJunction.delete().where(
        DeckTagJunction.decks == deck
    ).execute()
    # Add updated tags
    for tag_name in tags.split(","):
        tag_name = tag_name.strip()
        if tag_name:
          # Get or create tag
            tag, created = Tag.get_or_create(name=tag_name)
            # Create new deck-tag relationship
            DeckTagJunction.create(decks=deck, tags=tag)
    flash("Deck updated successfully.")
    return redirect(url_for("view_deck", deck_id=deck.id))

if __name__ == "__main__":
    app.run(debug=True)