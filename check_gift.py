import sqlite3

conn = sqlite3.connect("gifts.db")
cursor = conn.cursor()
cursor.execute("SELECT * FROM gifts WHERE id = 177")
row = cursor.fetchone()
conn.close()

print("ID:", row[0])
print("Название:", row[1])
print("Цена:", row[2])
print("Описание:", row[3][:50] if row[3] else None)
print("Бюджет:", row[4])
print("Пол:", row[5])
print("Возраст:", row[6])
print("Отношения:", row[7])
print("Повод:", row[8])
print("VALUE:", row[9])
print("INTERESTS:", row[10])