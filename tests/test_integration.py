import pytest
from init_db import Deck, Card, Tag, DeckTagJunction, CardTagJunction

class TestDecks:
    def test_create_deck(self, test_client):
        """Testing Deck Creation."""
        response = test_client.post("/decks/create", data={
            "name": "Literature",
            "description": "Classic novels",
            "tags": "arts"
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b"Literature" in response.data
        assert Deck.select().where(Deck.name == "Literature").exists()

    def test_create_deck_empty_tag(self, test_client):
        """Testing Deck Creation without adding tags"""
        response = test_client.post("/decks/create", data={
            "name": "Chemistry",
            "description": "Periodic Table"
        }, follow_redirects=True)

        deck = Deck.get_or_none(Deck.name == "Chemistry")
        assert response.status_code == 200
        assert deck is not None
        assert deck.description == "Periodic Table"
        
        tag_count = DeckTagJunction.select().where(DeckTagJunction.decks == deck).count()
        assert tag_count == 0

    def test_create_deck_empty_name(self, test_client):
        """Testing Deck Creation without adding name"""
        response = test_client.post("/decks/create", data={
            "description": "Periodic Table"
        }, follow_redirects=True)

        assert response.status_code == 400

        deck = Deck.get_or_none(Deck.description == "Periodic Table")
        assert deck is None

        tag_count = DeckTagJunction.select().count()
        assert tag_count == 0

    def test_list_decks(self, test_client, seeded_data):
        """Testing Getting ALL Decks."""
        response = test_client.get("/decks")
        
        assert response.status_code == 200
        assert b"Biology" in response.data  

    def test_list_empty_decks(self, test_client):
        """Testing Getting ALL decks while no decks exist in db"""
        response = test_client.get("/decks")

        assert response.status_code == 200
        deck_count = Deck.select().count()
        assert deck_count == 0
        

    def test_view_single_deck(self, test_client, seeded_data):
        """Testing Getting Singular Deck."""
        deck, _ = seeded_data
        response = test_client.get(f"/decks/{deck.id}")
        
        assert response.status_code == 200
        assert b"notes for midterm" in response.data

    def test_delete_deck(self, test_client, seeded_data):
        """Testing Deck Deletion."""
        deck, _ = seeded_data
        response = test_client.post(f"/decks/{deck.id}/delete", follow_redirects=True)
        
        assert response.status_code == 200
        assert Deck.get_or_none(Deck.id == deck.id) is None
        # Verify cards were deleted (Recursive delete)
        assert Card.select().where(Card.deck == deck.id).count() == 0

    def test_update_deck(self, test_client, seeded_data):
        """Testing Deck Update"""
        deck, _ = seeded_data
        response = test_client.post(f"/decks/{deck.id}/update", data={
            "name": "English",
            "description": "Shakespeare Review",
            "tags": "arts"
        }, follow_redirects=True)

        assert response.status_code == 200
        assert Deck.select().where(Deck.name == "English").exists()


class TestCards:
    def test_create_card(self, test_client, seeded_data):
        """Tests Card Creation"""
        deck, _ = seeded_data
        response = test_client.post(f"/decks/{deck.id}/card/create", data={
            "front": "What is a Ribosome?",
            "back": "Protein factory"
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert Card.select().where(Card.front == "What is a Ribosome?").exists()

    def test_delete_card(self, test_client, seeded_data):
        """Tests Card Deletion"""
        deck, card = seeded_data
        
        response = test_client.post(
            f"/decks/{deck.id}/card/{card.id}/delete", 
            follow_redirects=True
        )
        
        assert response.status_code == 200
        assert Card.get_or_none(Card.id == card.id) is None

    def test_update_card(self, test_client, seeded_data):
        """Testing Deck Update"""
        deck, card = seeded_data
        response = test_client.post(f"/decks/{deck.id}/card/{card.id}/update", data={
            "front": "What is the Powerhouse of the cell?",
            "back": "Mitocondria"
        }, follow_redirects=True)

        assert response.status_code == 200
        assert Card.select().where(Card.front == "What is the Powerhouse of the cell?").exists()