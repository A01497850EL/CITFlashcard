import pytest
import os
import tempfile
from app import app as flask_app_instance
from init_db import db, Card, Deck, Tag, CardTagJunction, DeckTagJunction 

@pytest.fixture(scope='session', autouse=True)
def test_db():
    """
    Creates a temporary file-based database for the session.
    """
    # Create a temp file for the database
    db_fd, db_path = tempfile.mkstemp()
    
    db.init(db_path)
    
    models = [Deck, Card, Tag, CardTagJunction, DeckTagJunction]
    db.bind(models)
    db.create_tables(models)
    
    yield db
    
    # Cleanup
    db.close()
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture(scope='function')
def test_client(test_db):
    """
    Provides a fresh test client for each test.
    """
    flask_app_instance.config.update({"TESTING": True})
    
    with flask_app_instance.test_client() as testing_client:
        yield testing_client

@pytest.fixture(scope='function')
def seeded_data(test_db):
    """Cleans tables and seeds fresh data for each test."""
    Card.delete().execute()
    Deck.delete().execute()
    
    deck = Deck.create(name="Biology", description="notes for midterm")
    card = Card.create(deck=deck, front="What is DNA?", back="Genetic material")
    return deck, card