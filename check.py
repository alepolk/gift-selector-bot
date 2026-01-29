import sqlite3

conn = sqlite3.connect("gifts.db")
cursor = conn.cursor()
cursor.execute("SELECT id, name, budget_tags, gender_tags FROM gifts WHERE name LIKE '%Парфюм%' OR name LIKE '%Стайлер%' OR name LIKE '%Утюжок%' OR name LIKE '%косметик%'")
rows = cursor.fetchall()
conn.close()

for row in rows:
    print(f"ID: {row[0]}")
    print(f"Название: {row[1]}")
    print(f"Бюджет: {row[2]}")
    print(f"Пол: {row[3]}")
    print()