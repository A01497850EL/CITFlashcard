from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import random
from init_db import init_db 

app = Flask(__name__)
init_db()

def get_db():
    conn = sqlite3.connect("flashcards.db")
    conn.row_factory = sqlite3.Row
    return conn



#creating decks 
@app.route("/")
def index():
    db = get_db()
    decks = db.execute("SELECT * FROM decks ORDER BY created_at DESC").fetchall()
    db.close()
    return render_template("index.html", decks=decks)


@app.route("/deck/create", methods=["POST"])
def create_deck():
    name = request.form["name"]
    db = get_db()
    db.execute("INSERT INTO decks (name) VALUES (?)", (name,))
    db.commit()
    db.close()
    return redirect(url_for("index"))

#creating cards 
@app.route("/deck/<int:deck_id>")
def view_deck(deck_id):
    db = get_db()
    deck = db.execute("SELECT * FROM decks WHERE id = ?", (deck_id,)).fetchone()
    cards = db.execute("SELECT * FROM cards WHERE deck_id = ?", (deck_id,)).fetchall()
    db.close()
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