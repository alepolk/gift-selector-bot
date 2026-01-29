import sqlite3

conn = sqlite3.connect("gifts.db")
cursor = conn.cursor()
cursor.execute("SELECT interest_tags FROM gifts")
all_tags = cursor.fetchall()
conn.close()

# Считаем количество товаров по каждому тегу
tag_counts = {}

for row in all_tags:
    tags = str(row[0] or '')
    for part in tags.split(','):
        part = part.strip()
        if part and ':' in part:
            tag_name = part.split(':')[0]
            if tag_name not in tag_counts:
                tag_counts[tag_name] = 0
            tag_counts[tag_name] += 1

print("INTEREST теги — количество товаров:\n")
for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"{tag:<30} {count} товаров")