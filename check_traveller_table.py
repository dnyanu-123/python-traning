import sqlite3

conn = sqlite3.connect("trip_planner.db")

cursor = conn.execute("PRAGMA table_info(travellers)")

for row in cursor:
    print(row)

conn.close()