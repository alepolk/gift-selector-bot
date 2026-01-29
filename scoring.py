import sqlite3

DB_PATH = "gifts.db"


def has_tag(tags_string: str, tag: str) -> bool:
    """Проверяет наличие тега в строке (точное совпадение, не подстрока)"""
    if not tags_string:
        return False
    tags_list = [t.strip() for t in tags_string.split(',')]
    return tag in tags_list


def filter_and_score_gifts(filters: dict, value_weights: dict, interest_weights: dict):
    """
    Фильтрует подарки по PRIMARY тегам и считает score по VALUE/INTERESTS
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
        
        # Бюджет (хотя бы один тег должен совпасть)
        if 'budget' in filters:
            budget_match = any(has_tag(budget_tags, b) for b in filters['budget'])
            if not budget_match:
                continue
        
        # Пол
        if 'gender' in filters:
            if not has_tag(gender_tags, filters['gender']):
                continue
        
        # Возраст
        if 'age' in filters:
            if not has_tag(age_tags, filters['age']):
                continue
        
        # Отношения
        if 'relationship' in filters:
            if not has_tag(relationship_tags, filters['relationship']):
                continue
        
        # Повод
        if 'occasion' in filters:
            if not has_tag(occasion_tags, filters['occasion']):
                continue
        
        # === ПАРСИМ ТЕГИ ПОДАРКА ===
        def get_tag_value(tags_str, tag_name):
            for part in tags_str.split(','):
                part = part.strip()
                if ':' in part:
                    t_name, t_val = part.split(':', 1)
                    if t_name.strip() == tag_name:
                        try:
                            return float(t_val)
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
        
        # 4. INTERESTS — главный множитель!
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
        
        results.append({
            'id': gift_id,
            'name': name,
            'price': price,
            'description': description,
            'score': score,
            'interest_matches': interest_matches
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
    print("ТЕСТ: Мужчина, до 2000₽, день рождения\n")
    
    filters = {
        'budget': ['budget_2000'],
        'gender': 'gender_male',
        'occasion': 'occasion_birthday'
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
    
    print(f"Найдено подарков: {len(top_gifts)}\n")
    
    for i, gift in enumerate(top_gifts, 1):
        print(f"{i}. {gift['name']}")
        print(f"   💰 {gift['price']}")
        print(f"   📊 Score: {gift['score']:.2f}")
        print()