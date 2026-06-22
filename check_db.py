import sqlite3

for db in ["myproject.db", "trips.db", "trip_planner.db"]:
    print(f"\n===== {db} =====")

    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    print(cursor.fetchall())

    conn.close()