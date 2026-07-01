import sqlite3

conn = sqlite3.connect("trip_planner.db")
conn.execute("DELETE FROM travellers")
conn.commit()
conn.close()

print("All travellers deleted")