import sqlite3

conn = sqlite3.connect("trip_planner.db")

# Old table delete
conn.execute("DROP TABLE IF EXISTS trips")

# New final table
conn.execute("""
CREATE TABLE trips (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    traveller_id INTEGER NOT NULL,

    trip_name TEXT,

    destination TEXT NOT NULL,

    travel_date DATE,

    days INTEGER NOT NULL,

    budget REAL NOT NULL,

    transport TEXT,

    status TEXT DEFAULT 'Planned',

    ai_itinerary TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (traveller_id)
    REFERENCES travellers(id)
)
""")

conn.commit()
conn.close()

print("Final Trips table created successfully!")