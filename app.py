from flask import Flask, render_template, request, redirect, url_for, abort, flash, Response
from init_db import init_db, db, Deck, Card, Tag, DeckTagJunction, User, CardTagJunction
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from peewee import JOIN
import os
import json
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class AuthUser(UserMixin):
    def __init__(self, user):
        self.id = user.id
        self.username = user.username
        self._user = user

    def check_password(self, password):
        return self._user.check_password(password)

@login_manager.user_loader
def load_user(user_id):
    user = User.get_or_none(User.id == int(user_id))
    return AuthUser(user) if user else None


init_db()

@app.before_request
def before_request():
    db.connect(reuse_if_open=True)

@app.teardown_request
def teardown_request(exc):
    if not db.is_closed():
        db.close()

@app.route("/")
@login_required
def index():
    decks = Deck.select().where(Deck.owner == current_user.id)
    return render_template("index.html", decks=decks)

@app.route("/decks")
@login_required
def show_decks():
# Get search query from URL parameters
    search_query = request.args.get("search", "").strip()
# Default query returns all decks
    decks = Deck.select().where(Deck.owner == current_user.id).distinct()
    # If user entered a search query
    if search_query:
        # Search decks by deck name OR tag name
        decks = (
            Deck
            .select()
            .join(DeckTagJunction, JOIN.LEFT_OUTER)
            .join(Tag, JOIN.LEFT_OUTER)
            .where(
                (Deck.owner == current_user.id) &
                (
                    (Deck.name.contains(search_query)) |
                    (Tag.name.contains(search_query)) 
                )
            )
            .distinct()
        )
    return render_template("decks.html", decks=decks)

# creating decks
@app.route("/decks/create", methods=["GET", "POST"])
@login_required
def create_deck():
    # If the user clicks "Save Deck" (Submitting the form)
    if request.method == "POST":
        name = request.form["name"]
        description = request.form.get("description", "")
        tags = request.form.get("tags", "")
        
        if not name:
            flash("Deck name is required.")
            return redirect(url_for("create_deck"))
            
        deck = Deck.create(name=name, description=description, owner=current_user.id)
        
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
@login_required
def view_deck(deck_id):
    try:
        deck = Deck.get_by_id(deck_id)
    except Deck.DoesNotExist:
        flash(f"Deck {deck_id} not found. It may have been deleted or doesn't exist.")
        return redirect(url_for("show_decks"))
    if deck.owner_id != current_user.id:
        flash("The deck you are attempting to access does not belong to you.")
        return redirect(url_for("show_decks"))
    cards = Card.select().where(Card.deck == deck_id)
    return render_template("decks.html", deck=deck, cards=cards)

# creating cards
@app.route("/decks/<int:deck_id>/card/create", methods=["POST"])
@login_required
def create_card(deck_id):
    deck = Deck.get_or_none(Deck.id == deck_id)
    if not deck:
        flash("Error: Deck not found")
        return redirect(url_for("show_decks"))
    if deck.owner_id != current_user.id:
        flash("The deck you are attempting to access does not belong to you.")
        return redirect(url_for("show_decks"))
    
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
@login_required
def delete_deck(deck_id):
    """
    Deletes a flashcard deck using Peewee ORM
    """
    try:
        # Get the deck
        deck = Deck.get_by_id(deck_id)

        # Verify Ownership
        if deck.owner_id != current_user.id:
            flash("The deck you are attempting to access does not belong to you.")
            return redirect(url_for("show_decks"))

        # Delete deck + related cards
        deck.delete_instance(recursive=True)
        flash("Deck deleted successfully.")
    except Deck.DoesNotExist:
        flash(f"Error: Could not locate deck with id {deck_id}")
    # Redirect back to decks page
    return redirect(url_for("show_decks"))
    
# Update Flashcard
@app.route("/decks/<int:deck_id>/card/<int:card_id>/update", methods=["POST"])
@login_required
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
    deck = card.deck
    if deck.owner_id != current_user.id:
        flash("The deck you are attempting to access does not belong to you.")
        return redirect(url_for("show_decks"))
    #get data
    front = request.form.get("front", "").strip()
    back = request.form.get("back", "").strip()
    tags = request.form.get("tags", "").strip()
    hint = request.form.get("hint", "").strip()

    #Validation
    if not front or not back:
        flash("Error: Please enter valid front and backsides for flashcards.")
        return redirect(url_for("view_deck", deck_id=deck_id))
    
    #save card front/back
    card.front = front
    card.back = back
    card.hint = hint
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
@login_required
def delete_card(deck_id, card_id):
    deck = Deck.get_or_none(Deck.id == deck_id)
    if not deck:
        flash(f"Error: Could not locate deck with provided deck id {deck_id}")
        return redirect(url_for("view_deck", deck_id=deck_id))
    
    # Verify Ownership
    if deck.owner_id != current_user.id:
        flash("The deck you are attempting to access does not belong to you.")
        return redirect(url_for("show_decks"))
    
    card = Card.get_or_none((Card.id == card_id) & (Card.deck == deck_id))
    if not card: 
        flash(f"Error: Could not locate flashcard with provided card id {card_id}")
        return redirect(url_for("view_deck", deck_id=deck_id))
        
    card.delete_instance()
    flash(f"Card {card_id} deleted successfully.")
    return redirect(url_for("view_deck", deck_id=deck_id))

# Route to About Us page
@app.route("/aboutus")
def aboutus():
    return render_template("aboutus.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    '''
    if User.select().count() > 0:
        flash("Registration is closed.")
        return redirect(url_for("login"))
    '''
    if request.method == "POST":
        invite = request.form.get("invite_code")
        if invite != os.environ.get("INVITE_CODE"):
            flash("Invalid invite code.")
            return redirect(url_for("register"))
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.create(username=username, password_hash="")
        user.set_password(password)
        user.save()
        flash("Account created. Please log in.")
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.get_or_none(User.username == username)
        if not user:
            flash("Invalid credentials.")
            return redirect(url_for("login"))
        auth_user = AuthUser(user)
        if not auth_user.check_password(password):
            flash("Invalid credentials.")
            return redirect(url_for("login"))
        login_user(auth_user)
        return redirect(url_for("index"))
    return render_template("login.html")


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# flashcard write mode
@app.route("/decks/<int:deck_id>/write")
@login_required
def write_mode(deck_id):
    deck = Deck.get_or_none(Deck.id == deck_id)
    if not deck:
        # If deck does not exist, show error and redirect
        flash(f"Error: Could not locate deck with provided deck id {deck_id}")
        return redirect(url_for("show_decks"))
    # Verify Ownership
    if deck.owner_id != current_user.id:
        flash("The deck you are attempting to access does not belong to you.")
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
@login_required
def write_answer(card_id):
    card = Card.get_or_none(Card.id == card_id)
    if not card:
        # If card not found
        flash(f"Error: Could not locate flashcard with provided card id {card_id}")
        return redirect(url_for("show_decks"))
    # Verify Ownership
    deck = card.deck
    if deck.owner_id != current_user.id:
        flash("The deck you are attempting to access does not belong to you.")
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
    return redirect(url_for("write_mode", deck_id=deck.id, index=next_index))

# flashcard flip mode
@app.route("/decks/<int:deck_id>/flip")
@login_required
def flip_mode(deck_id):
    deck = Deck.get_or_none(Deck.id == deck_id)
    if not deck:
        # If deck does not exist, show error and redirect
        flash(f"Error: Could not locate deck with provided deck id {deck_id}")
        return redirect(url_for("show_decks"))
    if deck.owner_id != current_user.id:
        flash("The deck you are attempting to access does not belong to you.")
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
@login_required
def flip_answer(card_id):
    card = Card.get_or_none(Card.id == card_id)
    if not card:
        # If card not found
        flash(f"Error: Could not locate flashcard with provided card id {card_id}")
        return redirect(url_for("show_decks"))
    deck = card.deck
    if deck.owner_id != current_user.id:
        flash("The deck you are attempting to access does not belong to you.")
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
        return redirect(url_for("flip_mode", deck_id=deck.id))
    # Save updated values to database
    card.save()
    next_index = request.form.get("index", 0, type=int) + 1
    # Redirect to next card
    return redirect(url_for("flip_mode", deck_id=deck.id, index=next_index))

# UPDATE DECK
@app.route("/decks/<int:deck_id>/update", methods=["POST"])
@login_required
def update_deck(deck_id):
    deck = Deck.get_or_none(Deck.id == deck_id)
    if not deck:
        flash(f"Error: Could not locate deck with id {deck_id}")
        return redirect(url_for("show_decks"))
    if deck.owner_id != current_user.id:
        flash("The deck you are attempting to access does not belong to you.")
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
    return redirect(url_for("show_decks", deck_id=deck.id))

# EXPORT DECK
@app.route("/decks/<int:deck_id>/export")
@login_required
def export_deck(deck_id):
    deck = Deck.get_or_none(Deck.id == deck_id)
    # Validation
    if not deck:
        flash("Error: Deck not found.")
        return redirect(url_for("show_decks"))
    # Ownership check
    if deck.owner_id != current_user.id:
        flash("You do not have permission to export this deck.")
        return redirect(url_for("show_decks"))
    # Get cards
    cards = Card.select().where(Card.deck == deck)
    # Convert deck into JSON format
    deck_data = {
        "name": deck.name,
        "description": deck.description,
        "cards": [],
        "deck_tags": []
    }
    #store deck tags
    for deck_tag in deck.tags:
        deck_data["deck_tags"].append(deck_tag.tags.name)
    #store cards + card tags
    for card in cards:
        card_tags = []
        for card_tag in card.card_link:
            card_tags.append(card_tag.tags.name)
        deck_data["cards"].append({
            "front": card.front,
            "back": card.back,
            "hint": card.hint,
            "card_tags": card_tags
        })
    # Convert Python dictionary into JSON string
    json_data = json.dumps(deck_data, indent=4)
    # Return downloadable JSON file
    return Response(
        json_data,
        mimetype="application/json",
        headers={
            "Content-Disposition": f"attachment; filename={deck.name}.json"
        }
    )

# IMPORT DECK
@app.route("/decks/import", methods=["GET", "POST"])
@login_required
def import_deck():
    if request.method == "POST":
        # Get uploaded file
        uploaded_file = request.files.get("deck_file")
        # Validation
        if not uploaded_file:
            flash("Error: No file uploaded.")
            return redirect(url_for("show_decks"))
        try:
            # Load JSON data
            deck_data = json.load(uploaded_file)
            # Create deck
            deck = Deck.create(
                name=deck_data["name"],
                description=deck_data.get("description"),
                owner=current_user.id
            )
            # Create deck tags
            for tag_name in deck_data.get("deck_tags", []):
                tag, _ = Tag.get_or_create(name=tag_name)
                DeckTagJunction.create(decks=deck, tags=tag)
            # Create cards + tags
            for card_data in deck_data.get("cards", []):
                card = Card.create(
                    deck=deck,
                    front=card_data["front"],
                    back=card_data["back"],
                    hint=card_data.get("hint")
                )
                for tag_name in card_data.get("card_tags", []):
                    tag, _ = Tag.get_or_create(name=tag_name)
                    CardTagJunction.create(cards=card, tags=tag)
            flash("Deck imported successfully.")
            return redirect(url_for("view_deck", deck_id=deck.id))
        except (json.JSONDecodeError, KeyError):
            flash("Error: Invalid deck file.")
            return redirect(url_for("show_decks"))
    return render_template("import.html")

if __name__ == "__main__":
    app.run(debug=True)