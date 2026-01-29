import sqlite3

conn = sqlite3.connect("gifts.db")
cursor = conn.cursor()
cursor.execute("SELECT name, interest_tags FROM gifts LIMIT 10")
rows = cursor.fetchall()
conn.close()

print("Примеры INTEREST тегов в базе:\n")
for i, row in enumerate(rows, 1):
    print(f"{i}. {row[0]}")
    print(f"   {row[1]}")
    print()