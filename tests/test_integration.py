import pytest
from init_db import Deck, Card

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

    def test_list_decks(self, test_client, seeded_data):
        """Testing Getting ALL Decks."""
        response = test_client.get("/decks")
        
        assert response.status_code == 200
        assert b"Biology" in response.data  

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