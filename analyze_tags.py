import sqlite3

DB_PATH = "gifts.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("SELECT value_tags FROM gifts")
all_tags = cursor.fetchall()
conn.close()

# VALUE теги для анализа
value_tags_list = [
    'gift_practical',
    'gift_emotional', 
    'gift_romantic',
    'gift_memory',
    'gift_daily_use',
    'gift_luxury',
    'gift_experience',
    'gift_unique',
    'gift_humorous',
    'gift_surprise',
    'gift_aesthetic',
    'gift_practical_life',
]

print(f"Всего товаров: {len(all_tags)}\n")
print("="*60)
print("VALUE ТЕГИ - АНАЛИЗ:")
print("="*60)
print(f"{'Тег':<25} {'Всего':<10} {'Высокий >0.5':<15}")
print("-"*60)

for tag in value_tags_list:
    total = 0
    high = 0
    
    for row in all_tags:
        value_tags = str(row[0] or '')
        if tag in value_tags:
            total += 1
            for part in value_tags.split(','):
                part = part.strip()
                if tag in part and ':' in part:
                    try:
                        val = float(part.split(':')[1])
                        if val > 0.5:
                            high += 1
                    except:
                        pass
    
    pct = round(total / len(all_tags) * 100, 1)
    print(f"{tag:<25} {total:<10} {high:<15} {pct}%")