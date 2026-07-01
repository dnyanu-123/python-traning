import sqlite3

conn = sqlite3.connect("trip_planner.db")

cursor = conn.execute("""
SELECT *
FROM trips
""")

for row in cursor:
    print(row)

conn.close()