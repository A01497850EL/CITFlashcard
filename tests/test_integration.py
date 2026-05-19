import pytest
from init_db import Deck, Card, Tag, DeckTagJunction

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

 # Tests for Search Functionality
    def test_search_deck_by_name(self, test_client):
        """Testing Deck Search by Deck Name"""
        # Create test decks
        Deck.create(name="OOP", description="Object Oriented Programming")
        Deck.create(name="Linux", description="Linux Administration")
        # Search for OOP deck
        response = test_client.get("/decks?search=OOP")
        assert response.status_code == 200
        assert b"OOP" in response.data
        assert b"Linux" not in response.data

    def test_search_deck_by_tag(self, test_client):
        """Testing Deck Search by Tag Name"""
        # Create test decks
        oop_deck = Deck.create(name="OOP", description="Object Oriented Programming")
        linux_deck = Deck.create(name="Linux", description="Linux Administration")
        # Create tags
        java_tag = Tag.create(name="java")
        linux_tag = Tag.create(name="ubuntu")
        # Create deck-tag relationships
        DeckTagJunction.create(decks=oop_deck, tags=java_tag)
        DeckTagJunction.create(decks=linux_deck, tags=linux_tag)
        # Search using tag name
        response = test_client.get("/decks?search=java")
        assert response.status_code == 200
        assert b"OOP" in response.data
        assert b"Linux" not in response.data

    # Tests for Flip Mode Functionality
    def test_flip_mode_page_loads(self, test_client, seeded_data):
        """Testing Flip Mode Page Load"""
        deck, card = seeded_data
        response = test_client.get(f"/decks/{deck.id}/flip")
        assert response.status_code == 200
        assert b"What is DNA?" in response.data

    def test_flip_mode_yes_increases_confidence(self, test_client, seeded_data):
        """Testing Flip Mode Yes Response"""
        deck, card = seeded_data
        response = test_client.post(
            f"/cards/{card.id}/flip-answer",
            data={
                "result": "yes",
                "index": 0
            },
            follow_redirects=True
        )
        updated_card = Card.get_by_id(card.id)
        assert response.status_code == 200
        assert updated_card.confidence_score == 1

    def test_flip_mode_no_decreases_confidence(self, test_client, seeded_data):
        """Testing Flip Mode No Response"""
        deck, card = seeded_data
        # Set confidence score before decreasing
        card.confidence_score = 2
        card.save()
        response = test_client.post(
            f"/cards/{card.id}/flip-answer",
            data={
                "result": "no",
                "index": 0
            },
            follow_redirects=True
        )
        updated_card = Card.get_by_id(card.id)
        assert response.status_code == 200
        assert updated_card.confidence_score == 1

    def test_flip_mode_confidence_does_not_go_below_zero(self, test_client, seeded_data):
        """Testing Flip Mode Confidence Floor"""
        deck, card = seeded_data
        response = test_client.post(
            f"/cards/{card.id}/flip-answer",
            data={
                "result": "no",
                "index": 0
            },
            follow_redirects=True
        )
        updated_card = Card.get_by_id(card.id)
        assert response.status_code == 200
        assert updated_card.confidence_score == 0

    def test_flip_mode_invalid_response(self, test_client, seeded_data):
        """Testing Invalid Flip Mode Response"""
        deck, card = seeded_data
        response = test_client.post(
            f"/cards/{card.id}/flip-answer",
            data={
                "result": "invalid",
                "index": 0
            },
            follow_redirects=True
        )
        assert response.status_code == 200
        
 # Tests for write mode functionality
    def test_write_mode_page_loads(self, test_client, seeded_data):
        """Testing Write Mode Page Load"""
        deck, card = seeded_data
        response = test_client.get(f"/decks/{deck.id}/write")
        assert response.status_code == 200
        assert b"What is DNA?" in response.data

    def test_write_mode_correct_answer_increases_confidence(self, test_client, seeded_data):
        """Testing Write Mode Correct Answer"""
        deck, card = seeded_data
        response = test_client.post(
            f"/cards/{card.id}/write-answer",
            data={
                "answer": "Genetic Material"
            },
            follow_redirects=True
        )
        updated_card = Card.get_by_id(card.id)
        assert response.status_code == 200
        assert updated_card.confidence_score == 1

    def test_write_mode_incorrect_answer_decreases_confidence(self, test_client, seeded_data):
        """Testing Write Mode Incorrect Answer"""
        deck, card = seeded_data
        # Set confidence score before decreasing
        card.confidence_score = 2
        card.save()
        response = test_client.post(
            f"/cards/{card.id}/write-answer",
            data={
                "answer": "Wrong Answer"
            },
            follow_redirects=True
        )
        updated_card = Card.get_by_id(card.id)
        assert response.status_code == 200
        assert updated_card.confidence_score == 1

    def test_write_mode_confidence_does_not_go_below_zero(self, test_client, seeded_data):
        """Testing Write Mode Confidence Floor"""
        deck, card = seeded_data
        response = test_client.post(
            f"/cards/{card.id}/write-answer",
            data={
                "answer": "Wrong Answer"
            },
            follow_redirects=True
        )
        updated_card = Card.get_by_id(card.id)
        assert response.status_code == 200
        assert updated_card.confidence_score == 0
    
    def test_write_mode_case_insensitivity(self, test_client, seeded_data):
        """Testing Write Mode Case Insensitivity"""
        deck, card = seeded_data
        response = test_client.post(
            f"/cards/{card.id}/write-answer",
            data={
                "answer": "genetic material"
            },
            follow_redirects=True
        )
        updated_card = Card.get_by_id(card.id)
        assert response.status_code == 200
        assert updated_card.confidence_score == 1   

    def test_write_mode_override_increases_confidence(self, test_client, seeded_data):
        """Testing Write Mode Override"""
        deck, card = seeded_data
        response = test_client.post(
            f"/cards/{card.id}/write-answer",
            data={
                "answer": "Wrong Answer",
                "override": "true"
            },
            follow_redirects=True
        )
        updated_card = Card.get_by_id(card.id)
        assert response.status_code == 200
        assert updated_card.confidence_score == 1