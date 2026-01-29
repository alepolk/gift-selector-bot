import sqlite3

conn = sqlite3.connect("gifts.db")
cursor = conn.cursor()
cursor.execute("SELECT interest_tags FROM gifts")
all_tags = cursor.fetchall()
conn.close()

# Собираем уникальные теги
unique_tags = set()
for row in all_tags:
    tags = str(row[0] or '')
    for part in tags.split(','):
        part = part.strip()
        if part and ':' in part:
            tag_name = part.split(':')[0]
            unique_tags.add(tag_name)

print("INTEREST теги в базе:")
for tag in sorted(unique_tags):
    print(f"  - {tag}")