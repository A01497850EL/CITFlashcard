import pytest
from init_db import Card, Deck, Tag, DeckTagJunction, CardTagJunction

def test_new_deck():
    deck = Deck(name = "Biology", description = "notes for midterm")
    assert deck.name == "Biology"
    assert deck.description == "notes for midterm"

def test_new_card():
    temp_deck = Deck(name = "Biology", description = "notes for midterm")
    card = Card(deck=temp_deck, front="What is DNA?", back="Genetic material")

