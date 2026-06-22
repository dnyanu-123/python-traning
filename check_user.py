import sqlite3

conn = sqlite3.connect("trip_planner.db")
cursor = conn.cursor()

cursor.execute("SELECT id, email FROM users")

print(cursor.fetchall())

conn.close()