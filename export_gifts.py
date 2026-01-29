import sqlite3
from openpyxl import Workbook

conn = sqlite3.connect("gifts.db")
cursor = conn.cursor()
cursor.execute("SELECT * FROM gifts")
rows = cursor.fetchall()
conn.close()

wb = Workbook()
ws = wb.active
ws.title = "Gifts"

# Заголовки
headers = ["ID", "Название", "Цена", "Описание", "Бюджет", "Пол", "Возраст", "Отношения", "Повод", "VALUE", "INTERESTS"]
ws.append(headers)

# Данные
for row in rows:
    ws.append(row)

wb.save("gifts_export.xlsx")
print(f"Экспортировано {len(rows)} подарков в gifts_export.xlsx")