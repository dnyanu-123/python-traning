import sqlite3

conn = sqlite3.connect("trip_planner.db")
conn.row_factory = sqlite3.Row

# 1. All users
print("USERS TABLE:")
users = conn.execute("SELECT id, username, email FROM users").fetchall()
for u in users:
    print(dict(u))

print("\nTRAVELLERS + USER MAP:")
rows = conn.execute("""
SELECT travellers.id, travellers.name, travellers.user_id, users.username
FROM travellers
INNER JOIN users
ON travellers.user_id = users.id
""").fetchall()

for r in rows:
    print(dict(r))

conn.close()



'''import sqlite3

conn = sqlite3.connect("trip_planner.db")
cursor = conn.cursor()

cursor.execute("SELECT id, email FROM users")

print(cursor.fetchall())

conn.close()'''