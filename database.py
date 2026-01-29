import sqlite3
import os

# Путь к базе данных
DB_PATH = "gifts.db"

def create_database():
    """Создаёт базу данных и таблицы"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Таблица товаров
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gifts (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price TEXT,
            description TEXT,
            budget_tags TEXT,
            gender_tags TEXT,
            age_tags TEXT,
            relationship_tags TEXT,
            occasion_tags TEXT,
            value_tags TEXT,
            interest_tags TEXT
        )
    ''')
    
    # Таблица сессий пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed BOOLEAN DEFAULT FALSE,
            answers TEXT
        )
    ''')
    
    # Таблица аналитики
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            gift_id INTEGER,
            action TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES user_sessions(id),
            FOREIGN KEY (gift_id) REFERENCES gifts(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ База данных создана!")

def get_all_gifts():
    """Получает все подарки из базы"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM gifts")
    gifts = cursor.fetchall()
    conn.close()
    return gifts

def get_gift_count():
    """Возвращает количество подарков в базе"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM gifts")
    count = cursor.fetchone()[0]
    conn.close()
    return count

if __name__ == "__main__":
    create_database()
    print(f"📦 Подарков в базе: {get_gift_count()}")