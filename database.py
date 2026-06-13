import sqlite3

conn = sqlite3.connect('trip_planner.db')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS travellers (
    trip_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    age INTEGER NOT NULL,
    contact_no TEXT NOT NULL
)
''')

conn.commit()
conn.close()
print("Database and table created successfully.")