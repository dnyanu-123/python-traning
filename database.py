import sqlite3

DATABASE = "trips.db"

import sqlite3

def get_db():
    conn = sqlite3.connect("trips.db")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS travellers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        destination TEXT NOT NULL,
        budget INTEGER,
        days INTEGER
    )
    """)

    conn.commit()
    conn.close()