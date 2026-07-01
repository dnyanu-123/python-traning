
import sqlite3

conn = sqlite3.connect("trip_planner.db")
conn.row_factory = sqlite3.Row

rows = conn.execute("SELECT * FROM travellers").fetchall()

for r in rows:
    print(dict(r))

conn.close()

'''import sqlite3

for db in ["myproject.db", "trips.db", "trip_planner.db"]:
    print(f"\n===== {db} =====")

    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    print(cursor.fetchall())

    conn.close()'''