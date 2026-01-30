import sqlite3

DB_PATH = "gifts.db"
ANALYTICS_DB_PATH = "analytics.db"

# Порядок бюджетов
BUDGET_ORDER = ["budget_2000", "budget_5000", "budget_10000", "budget_15000",
                "budget_20000", "budget_30000", "budget_50000", "budget_100000"]


def get_collaborative_score(gift_id: int, filters: dict) -> float:
    """
    Рассчитывает бонус на основе лайков похожих пользователей.
    
    Ищет сессии с похожим профилем (пол, возраст, повод) и смотрит их оценки.
    """
    try:
        conn = sqlite3.connect(ANALYTICS_DB_PATH)
        cursor = conn.cursor()
        
        # Находим похожие сессии (совпадение по gender, age, occasion)
        cursor.execute('''
            SELECT a.session_id 
            FROM answers a
            WHERE a.gender = ? 
              AND a.age = ?
              AND a.occasion = ?
        ''', (
            filters.get('gender'),
            filters.get('age'),
            filters.get('occasion')
        ))
        
        similar_sessions = [row[0] for row in cursor.fetchall()]
        
        if not similar_sessions:
            conn.close()
            return 0.0
        
        # Считаем лайки и дизлайки этого подарка
        placeholders = ','.join(['?' for _ in similar_sessions])
        cursor.execute(f'''
            SELECT 
                SUM(CASE WHEN rating = 1 THEN 1 ELSE 0 END) as likes,
                SUM(CASE WHEN rating = -1 THEN 1 ELSE 0 END) as dislikes
            FROM ratings
            WHERE session_id IN ({placeholders}) AND gift_id = ?
        ''', similar_sessions + [gift_id])
        
        row = cursor.fetchone()
        conn.close()
        
        likes = row[0] or 0
        dislikes = row[1] or 0
        
        total = likes + dislikes
        if total == 0:
            return 0.0
        
        # Рассчитываем скор от -1 до +1
        score = (likes - dislikes) / total
        
        # Учитываем количество оценок (больше оценок = больше доверия)
        confidence = min(total / 10, 1.0)  # Максимум при 10+ оценках
        
        return score * confidence * 3.0  # До ±3 баллов
        
    except Exception as e:
        # Если база аналитики не существует — возвращаем 0
        return 0.0


def calculate_budget_score(user_max_budget: str, gift_budget_tags: str) -> float:
    """
    Рассчитывает баллы за соответствие бюджета.
    """
    if not user_max_budget or not gift_budget_tags:
        return 0.0
    
    if user_max_budget not in BUDGET_ORDER:
        return 0.0
    user_index = BUDGET_ORDER.index(user_max_budget)
    
    gift_indices = []
    for i, tag in enumerate(BUDGET_ORDER):
        if tag in gift_budget_tags:
            gift_indices.append(i)
    
    if not gift_indices:
        return 0.0
    
    gift_min_index = min(gift_indices)
    gift_max_index = max(gift_indices)
    
    if user_index < gift_min_index:
        return -10.0
    
    if user_index > gift_max_index:
        diff = user_index - gift_max_index
        if diff == 1:
            return 0.5
        elif diff == 2:
            return 0.0
        else:
            return -0.5 * (diff - 2)
    
    if gift_max_index == gift_min_index:
        return 2.0
    
    position = (user_index - gift_min_index) / (gift_max_index - gift_min_index)
    
    if position <= 0.25:
        return -1.0
    elif position <= 0.5:
        return 0.0
    elif position <= 0.75:
        return 1.0
    else:
        return 2.0


def filter_and_score_gifts(filters: dict, value_weights: dict, interest_weights: dict):
    """
    Фильтрует подарки по PRIMARY тегам и считает score по VALUE/INTERESTS + ЛАЙКИ
    """
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM gifts")
    all_gifts = cursor.fetchall()
    conn.close()
    
    results = []
    
    for gift in all_gifts:
        gift_id = gift[0]
        name = gift[1]
        price = gift[2]
        description = gift[3]
        budget_tags = str(gift[4] or '')
        gender_tags = str(gift[5] or '')
        age_tags = str(gift[6] or '')
        relationship_tags = str(gift[7] or '')
        occasion_tags = str(gift[8] or '')
        value_tags = str(gift[9] or '')
        interest_tags = str(gift[10] or '')
        
        # === PRIMARY ФИЛЬТРАЦИЯ ===
        
        if 'budget' in filters:
            budget_match = any(b in budget_tags for b in filters['budget'])
            if not budget_match:
                continue
        
        if 'gender' in filters:
            if filters['gender'] not in gender_tags:
                continue
        
        if 'age' in filters:
            if filters['age'] not in age_tags:
                continue
        
        if 'relationship' in filters:
            if filters['relationship'] not in relationship_tags:
                continue
        
        if 'occasion' in filters:
            if filters['occasion'] not in occasion_tags:
                continue
        
        # === ПАРСИМ ТЕГИ ПОДАРКА ===
        def get_tag_value(tags_str, tag_name):
            for part in tags_str.split(','):
                part = part.strip()
                if tag_name in part and ':' in part:
                    try:
                        return float(part.split(':')[1])
                    except:
                        pass
            return 0.0
        
        gift_practical = get_tag_value(value_tags, 'gift_practical')
        gift_emotional = get_tag_value(value_tags, 'gift_emotional')
        gift_experience = get_tag_value(value_tags, 'gift_experience')
        gift_daily_use = get_tag_value(value_tags, 'gift_daily_use')
        gift_aesthetic = get_tag_value(value_tags, 'gift_aesthetic')
        
        # === ЖЁСТКАЯ ФИЛЬТРАЦИЯ ПО ВЕЩЬ/ВПЕЧАТЛЕНИЕ ===
        user_experience = value_weights.get('gift_experience', 0.5)
        
        if user_experience == 0 and gift_experience > 0.7:
            continue
        
        if user_experience == 1 and gift_experience < 0.3:
            continue
        
        # === SCORING ===
        score = 0.0
        
        # 0. БЮДЖЕТ
        if 'budget' in filters and filters['budget']:
            user_max_budget = filters['budget'][-1]
            budget_score = calculate_budget_score(user_max_budget, budget_tags)
            score += budget_score
        
        # 1. Практичный vs Эмоциональный
        user_practical = value_weights.get('gift_practical', 0.5)
        user_emotional = value_weights.get('gift_emotional', 0.5)
        
        if user_practical == 1:
            score += gift_practical * 2.0
            score -= gift_emotional * 1.0
        elif user_emotional == 1:
            score += gift_emotional * 2.0
            score -= gift_practical * 0.5
        else:
            score += gift_practical * 0.5
            score += gift_emotional * 0.5
        
        # 2. Для ежедневного использования
        user_daily = value_weights.get('gift_daily_use', 0.5)
        
        if user_daily == 1:
            score += gift_daily_use * 1.5
            if gift_daily_use < 0.3:
                score -= 0.5
        elif user_daily == 0:
            if gift_daily_use > 0.7:
                score -= 0.3
        
        # 3. Эстетика
        user_aesthetic = value_weights.get('gift_aesthetic', 0.5)
        
        if user_aesthetic == 1:
            score += gift_aesthetic * 1.5
            if gift_aesthetic < 0.3:
                score -= 0.5
        
        # 4. INTERESTS
        interest_bonus = 0.0
        interest_matches = 0
        
        for tag, user_weight in interest_weights.items():
            if user_weight > 0:
                tag_value = get_tag_value(interest_tags, tag)
                if tag_value > 0:
                    interest_bonus += tag_value * 3.0
                    interest_matches += 1
        
        score += interest_bonus
        
        if interest_matches >= 2:
            score += 1.0
        if interest_matches >= 3:
            score += 1.5
        
        # 5. КОЛЛАБОРАТИВНАЯ ФИЛЬТРАЦИЯ — лайки похожих пользователей
        collaborative_score = get_collaborative_score(gift_id, filters)
        score += collaborative_score
        
        results.append({
            'id': gift_id,
            'name': name,
            'price': price,
            'description': description,
            'score': score,
            'interest_matches': interest_matches,
            'collaborative_score': collaborative_score
        })
    
    # Сортируем по score
    results.sort(key=lambda x: x['score'], reverse=True)
    
    return results


def get_top_gifts(filters: dict, value_weights: dict, interest_weights: dict, limit: int = 5):
    """Возвращает топ-N подарков"""
    results = filter_and_score_gifts(filters, value_weights, interest_weights)
    return results[:limit]


# === ТЕСТ ===
if __name__ == "__main__":
    print("=" * 60)
    print("ТЕСТ: Подбор с учётом лайков")
    print("=" * 60)
    
    filters = {
        'budget': ['budget_2000', 'budget_5000', 'budget_10000'],
        'gender': 'gender_male',
        'age': 'age_26_35',
        'relationship': 'relationship_partner',
        'occasion': 'occasion_valentine'
    }
    
    value_weights = {
        'gift_practical': 0.5,
        'gift_emotional': 0.5,
        'gift_experience': 0.5,
        'gift_daily_use': 0.5,
        'gift_aesthetic': 0.5,
    }
    
    interest_weights = {}
    
    top_gifts = get_top_gifts(filters, value_weights, interest_weights, limit=10)
    
    print(f"\nТоп-10 подарков для парня на Валентина (до 10к):\n")
    
    for i, gift in enumerate(top_gifts, 1):
        collab = gift.get('collaborative_score', 0)
        collab_str = f" [👥 {collab:+.1f}]" if collab != 0 else ""
        print(f"{i}. {gift['name']}")
        print(f"   💰 {gift['price']}")
        print(f"   📊 Score: {gift['score']:.2f}{collab_str}")
        print()