import sqlite3

def init_db():
    conn = sqlite3.connect("flashcards.db")
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS decks (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS cards (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            deck_id  INTEGER NOT NULL,
            front    TEXT NOT NULL,
            back     TEXT NOT NULL,
            mastered BOOLEAN DEFAULT 0,
            FOREIGN KEY (deck_id) REFERENCES decks(id)
        );
    """)

    conn.commit()
    conn.close()
    print("Database initialized.")

if __name__ == "__main__":
    init_db()