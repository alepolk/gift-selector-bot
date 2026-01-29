import sqlite3

DB_PATH = "gifts.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

# === ПРОСМОТР ===

def view_all_gifts():
    """Показать все подарки"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price FROM gifts ORDER BY id")
    gifts = cursor.fetchall()
    conn.close()
    
    print("\n📦 ВСЕ ПОДАРКИ:\n")
    for gift in gifts:
        print(f"{gift[0]}. {gift[1]} — {gift[2]}")
    print(f"\nВсего: {len(gifts)} подарков")

def view_gift(gift_id: int):
    """Показать один подарок подробно"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM gifts WHERE id = ?", (gift_id,))
    gift = cursor.fetchone()
    conn.close()
    
    if not gift:
        print(f"❌ Подарок с ID {gift_id} не найден")
        return
    
    print(f"\n🎁 ПОДАРОК #{gift[0]}:")
    print(f"Название: {gift[1]}")
    print(f"Цена: {gift[2]}")
    print(f"Описание: {gift[3]}")
    print(f"\nBudget теги: {gift[4]}")
    print(f"Gender теги: {gift[5]}")
    print(f"Age теги: {gift[6]}")
    print(f"Relationship теги: {gift[7]}")
    print(f"Occasion теги: {gift[8]}")
    print(f"Value теги: {gift[9]}")
    print(f"Interest теги: {gift[10]}")

def search_gifts(query: str):
    """Поиск подарков по названию"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price FROM gifts WHERE name LIKE ?", (f"%{query}%",))
    gifts = cursor.fetchall()
    conn.close()
    
    print(f"\n🔍 Результаты поиска '{query}':\n")
    for gift in gifts:
        print(f"{gift[0]}. {gift[1]} — {gift[2]}")
    print(f"\nНайдено: {len(gifts)}")

# === РЕДАКТИРОВАНИЕ ===

def update_gift_field(gift_id: int, field: str, new_value: str):
    """Обновить поле подарка"""
    allowed_fields = ['name', 'price', 'description', 'budget_tags', 
                      'gender_tags', 'age_tags', 'relationship_tags',
                      'occasion_tags', 'value_tags', 'interest_tags']
    
    if field not in allowed_fields:
        print(f"❌ Неверное поле. Доступные: {allowed_fields}")
        return
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"UPDATE gifts SET {field} = ? WHERE id = ?", (new_value, gift_id))
    conn.commit()
    conn.close()
    
    print(f"✅ Подарок #{gift_id}: поле '{field}' обновлено")

def add_gift(name: str, price: str, description: str, budget_tags: str,
             gender_tags: str, age_tags: str, relationship_tags: str,
             occasion_tags: str, value_tags: str, interest_tags: str):
    """Добавить новый подарок"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT MAX(id) FROM gifts")
    max_id = cursor.fetchone()[0] or 0
    new_id = max_id + 1
    
    cursor.execute('''
        INSERT INTO gifts (id, name, price, description, budget_tags,
                          gender_tags, age_tags, relationship_tags,
                          occasion_tags, value_tags, interest_tags)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (new_id, name, price, description, budget_tags, gender_tags,
          age_tags, relationship_tags, occasion_tags, value_tags, interest_tags))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Добавлен подарок #{new_id}: {name}")

def delete_gift(gift_id: int):
    """Удалить подарок"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM gifts WHERE id = ?", (gift_id,))
    conn.commit()
    conn.close()
    
    print(f"✅ Подарок #{gift_id} удалён")

# === ИНТЕРАКТИВНОЕ МЕНЮ ===

def main_menu():
    """Главное меню админки"""
    while True:
        print("\n" + "="*50)
        print("🔧 АДМИН-ПАНЕЛЬ ПОДАРКОВ")
        print("="*50)
        print("1. Показать все подарки")
        print("2. Посмотреть подарок по ID")
        print("3. Поиск по названию")
        print("4. Редактировать подарок")
        print("5. Добавить новый подарок")
        print("6. Удалить подарок")
        print("0. Выход")
        print("="*50)
        
        choice = input("Выбери действие: ").strip()
        
        if choice == "1":
            view_all_gifts()
        
        elif choice == "2":
            gift_id = input("Введи ID подарка: ").strip()
            if gift_id.isdigit():
                view_gift(int(gift_id))
            else:
                print("❌ Введи число")
        
        elif choice == "3":
            query = input("Введи текст для поиска: ").strip()
            search_gifts(query)
        
        elif choice == "4":
            gift_id = input("Введи ID подарка: ").strip()
            if not gift_id.isdigit():
                print("❌ Введи число")
                continue
            
            view_gift(int(gift_id))
            
            print("\nДоступные поля для редактирования:")
            print("name, price, description, budget_tags, gender_tags,")
            print("age_tags, relationship_tags, occasion_tags, value_tags, interest_tags")
            
            field = input("\nКакое поле изменить: ").strip()
            new_value = input("Новое значение: ").strip()
            
            update_gift_field(int(gift_id), field, new_value)
        
        elif choice == "5":
            print("\n📝 ДОБАВЛЕНИЕ НОВОГО ПОДАРКА:")
            name = input("Название: ").strip()
            price = input("Цена (например '5,000–15,000₽'): ").strip()
            description = input("Описание: ").strip()
            budget_tags = input("Budget теги (например 'budget_5000, budget_10000'): ").strip()
            gender_tags = input("Gender теги (например 'gender_male, gender_female'): ").strip()
            age_tags = input("Age теги (например 'age_20_25, age_26_35'): ").strip()
            relationship_tags = input("Relationship теги: ").strip()
            occasion_tags = input("Occasion теги: ").strip()
            value_tags = input("Value теги (например 'gift_practical:0.8'): ").strip()
            interest_tags = input("Interest теги (например 'interest_tech:1.0'): ").strip()
            
            add_gift(name, price, description, budget_tags, gender_tags,
                    age_tags, relationship_tags, occasion_tags, value_tags, interest_tags)
        
        elif choice == "6":
            gift_id = input("Введи ID подарка для удаления: ").strip()
            if gift_id.isdigit():
                confirm = input(f"Точно удалить подарок #{gift_id}? (да/нет): ").strip()
                if confirm.lower() == "да":
                    delete_gift(int(gift_id))
            else:
                print("❌ Введи число")
        
        elif choice == "0":
            print("👋 Пока!")
            break
        
        else:
            print("❌ Неверный выбор")

if __name__ == "__main__":
    main_menu()