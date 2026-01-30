from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from scoring import get_top_gifts
from analytics import (
    create_session, save_answers, save_rating, 
    save_event, complete_session, get_collaborative_score
)

# === ТОКЕН БОТА ===
BOT_TOKEN = "8513351241:AAGmH0ANaZqC-Iook7KJN0Vbo0qT8sKqgTU"

# === ВОПРОСЫ ===
QUESTIONS = [
    None,  # индекс 0 не используем
    {
        "text": "💰 Какой у вас бюджет на подарок?",
        "options": [
            ("До 2,000₽", "budget_2000"),
            ("До 5,000₽", "budget_5000"),
            ("До 10,000₽", "budget_10000"),
            ("До 15,000₽", "budget_15000"),
            ("До 20,000₽", "budget_20000"),
            ("До 30,000₽", "budget_30000"),
            ("До 50,000₽", "budget_50000"),
            ("До 100,000₽", "budget_100000"),
        ],
        "type": "primary",
        "tag": "budget"
    },
    {
        "text": "👤 Кому выбираете подарок?",
        "options": [
            ("Мужчине", "gender_male"),
            ("Женщине", "gender_female"),
        ],
        "type": "primary",
        "tag": "gender"
    },
    {
        "text": "🎂 Сколько лет получателю?",
        "options": [
            ("13-15 лет", "age_13_15"),
            ("16-19 лет", "age_16_19"),
            ("20-25 лет", "age_20_25"),
            ("26-35 лет", "age_26_35"),
            ("36-50 лет", "age_36_50"),
            ("51-65 лет", "age_51_65"),
            ("65+ лет", "age_65plus"),
        ],
        "type": "primary",
        "tag": "age"
    },
    {
        "text": "👨‍👩‍👧 Кем вам приходится этот человек?",
        "options": [
            ("Муж/Жена", "relationship_spouse"),
            ("Партнёр", "relationship_partner"),
            ("Родитель", "relationship_parent"),
            ("Бабушка/Дедушка", "relationship_grandparent"),
            ("Ребёнок", "relationship_child"),
            ("Брат/Сестра", "relationship_sibling"),
            ("Друг/Подруга", "relationship_friend"),
            ("Коллега/Начальник", "relationship_colleague"),
        ],
        "type": "primary",
        "tag": "relationship"
    },
    {
        "text": "🎉 По какому поводу дарите?",
        "options": [
            ("День рождения", "occasion_birthday"),
            ("Новый год", "occasion_newyear"),
            ("23 февраля / 8 марта", "occasion_8march_23feb"),
            ("День Валентина", "occasion_valentine"),
            ("Годовщина/Свадьба", "occasion_wedding"),
            ("Без повода", "occasion_noreason"),
        ],
        "type": "primary",
        "tag": "occasion"
    },
    {
        "text": "🎁 Что лучше подарить?",
        "options": [
            ("Вещь (материальный подарок)", "experience_0"),
            ("Впечатление (сертификат, билеты)", "experience_1"),
            ("Не знаю", "experience_0.5"),
        ],
        "type": "value",
        "tag": "gift_experience"
    },
    {
        "text": "🎯 Какой подарок предпочтительнее?",
        "options": [
            ("Практичный (полезный в быту)", "practical_1"),
            ("Эмоциональный (для радости)", "emotional_1"),
            ("Не знаю", "neutral_0.5"),
        ],
        "type": "value",
        "tag": "practical_emotional"
    },
    {
        "text": "📅 Подарок для ежедневного использования?",
        "options": [
            ("Да, на каждый день", "daily_1"),
            ("Нет, пусть будет особенным", "daily_0"),
            ("Не важно", "daily_0.5"),
        ],
        "type": "value",
        "tag": "gift_daily_use"
    },
    {
        "text": "✨ Насколько важна красота подарка?",
        "options": [
            ("Очень важна", "aesthetic_1"),
            ("Не очень важна", "aesthetic_0"),
            ("Не знаю", "aesthetic_0.5"),
        ],
        "type": "value",
        "tag": "gift_aesthetic"
    },
]

# Увлечения
INTERESTS_MALE = [
    ("📱 Техника и гаджеты", "interest_tech"),
    ("⚽ Спорт и фитнес", "interest_sports"),
    ("🚗 Авто и мото", "interest_car"),
    ("🏕️ Природа и туризм", "interest_nature"),
    ("🌻 Дача и сад", "interest_gardening"),
    ("🎮 Игры", "interest_gaming"),
    ("✈️ Путешествия", "interest_travel"),
    ("🎵 Музыка", "interest_music"),
    ("📸 Фото и видео", "interest_photography"),
    ("🍳 Кулинария", "interest_cooking"),
    ("📚 Книги и чтение", "interest_reading"),
    ("☕ Кофе и чай", "interest_coffee_tea"),
    ("💼 Бизнес и карьера", "interest_business"),
]

INTERESTS_FEMALE = [
    ("💄 Красота и уход", "interest_beauty"),
    ("👗 Мода и стиль", "interest_fashion"),
    ("💎 Украшения и аксессуары", "interest_accessories"),
    ("🧘 Спорт и фитнес", "interest_sports"),
    ("🍳 Кулинария", "interest_cooking"),
    ("🏠 Дом и уют", "interest_home"),
    ("✈️ Путешествия", "interest_travel"),
    ("📚 Книги и чтение", "interest_reading"),
    ("🎨 Творчество", "interest_creative"),
    ("🌸 Растения и сад", "interest_gardening"),
    ("🎭 Кино и театр", "interest_culture"),
    ("📸 Фото и видео", "interest_photography"),
    ("☕ Кофе и чай", "interest_coffee_tea"),
]

INTERESTS_ELDERLY = [
    ("🌻 Дача и сад", "interest_gardening"),
    ("💪 Здоровье и комфорт", "interest_health"),
    ("📚 Книги и чтение", "interest_reading"),
    ("🎨 Рукоделие", "interest_creative"),
    ("🍳 Кулинария", "interest_cooking"),
    ("🎭 Кино и театр", "interest_culture"),
    ("🏠 Дом и уют", "interest_home"),
    ("☕ Кофе и чай", "interest_coffee_tea"),
]

# Хранилище данных пользователей
user_data = {}


def get_budget_tags(selected_budget: str) -> list:
    all_budgets = ["budget_2000", "budget_5000", "budget_10000", "budget_15000",
                   "budget_20000", "budget_30000", "budget_50000", "budget_100000"]
    if selected_budget in all_budgets:
        index = all_budgets.index(selected_budget)
        return all_budgets[:index + 1]
    return all_budgets


def get_interests_for_user(gender: str, age: str) -> list:
    if age == "age_65plus":
        return INTERESTS_ELDERLY
    if gender == "gender_female":
        return INTERESTS_FEMALE
    return INTERESTS_MALE


def init_user_data(user_id: int):
    # Создаём сессию аналитики
    session_id = create_session(source="bot", user_id=str(user_id))
    save_event(session_id, "start")
    
    user_data[user_id] = {
        "session_id": session_id,
        "current_question": 1,
        "filters": {},
        "value_weights": {
            "gift_practical": 0.5,
            "gift_emotional": 0.5,
            "gift_experience": 0.5,
            "gift_daily_use": 0.5,
            "gift_aesthetic": 0.5,
        },
        "interest_weights": {},
        "selected_interests": [],
        "all_results": [],
        "current_gift_index": 0,
        "liked_gifts": [],
        "disliked_gifts": []
    }


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    init_user_data(user_id)

    await update.message.reply_text(
        "🎁 *Привет! Я помогу подобрать идеальный подарок!*\n\n"
        "Ответь на 10 вопросов, и я предложу лучшие варианты.\n\n"
        "Поехали! 👇",
        parse_mode="Markdown"
    )

    await send_question(update, context, user_id)


async def terms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📜 *Условия использования*\n\n"
        "1. Бот предоставляет рекомендации подарков.\n"
        "2. Мы не гарантируем наличие товаров.\n"
        "3. Используя бота, вы соглашаетесь с условиями.\n\n"
        "По вопросам: @cfc_consult",
        parse_mode="Markdown"
    )


async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🆘 *Поддержка*\n\n"
        "Вопросы или проблемы? Напиши: @cfc_consult\n\n"
        "Отвечаем в течение 24 часов.",
        parse_mode="Markdown"
    )


async def paysupport(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💳 *Поддержка по платежам*\n\n"
        "Проблемы с оплатой? Напиши: @cfc_consult",
        parse_mode="Markdown"
    )


async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    q_num = user_data[user_id]["current_question"]
    session_id = user_data[user_id]["session_id"]

    if q_num == 10:
        await send_interests_question(update, context, user_id)
        return

    if q_num > 10:
        await show_single_gift(update, context, user_id)
        return

    question = QUESTIONS[q_num]
    
    # Сохраняем событие
    save_event(session_id, f"question_{q_num}")

    keyboard = []
    for text, value in question["options"]:
        keyboard.append([InlineKeyboardButton(text, callback_data=f"q{q_num}_{value}")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    text = f"*Вопрос {q_num} из 10*\n\n{question['text']}"

    if update.callback_query:
        try:
            await update.callback_query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        except:
            await update.callback_query.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def send_interests_question(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    data = user_data[user_id]
    gender = data["filters"].get("gender", "gender_male")
    age = data["filters"].get("age", "age_26_35")
    session_id = data["session_id"]
    
    # Сохраняем событие только при первом показе
    if data["current_question"] == 10:
        save_event(session_id, "question_10_interests")
        user_data[user_id]["current_question"] = 10.5  # Помечаем что уже показали

    interests = get_interests_for_user(gender, age)
    selected = data.get("selected_interests", [])

    keyboard = []
    for text, tag in interests:
        checkmark = "✅ " if tag in selected else ""
        keyboard.append([InlineKeyboardButton(f"{checkmark}{text}", callback_data=f"interest_{tag}")])

    keyboard.append([InlineKeyboardButton("🤷 Не знаю увлечений", callback_data="interest_none")])
    keyboard.append([InlineKeyboardButton("✅ Готово — показать подарки", callback_data="interests_done")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    selected_count = len(selected)
    text = f"*Вопрос 10 из 10*\n\n"
    text += "🎯 *Какие увлечения есть у получателя?*\n"
    text += "_Выбери все подходящие и нажми «Готово»_\n\n"
    if selected_count > 0:
        text += f"Выбрано: {selected_count}"

    if update.callback_query:
        try:
            # Проверяем изменился ли текст
            current_text = update.callback_query.message.text
            if current_text != text or True:  # Всегда обновляем для кнопок
                await update.callback_query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        except Exception as e:
            # Игнорируем ошибку "message is not modified"
            if "message is not modified" not in str(e):
                await update.callback_query.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def show_single_gift(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Показывает один подарок с кнопками лайк/дизлайк"""
    data = user_data[user_id]
    session_id = data["session_id"]
    
    # Если результаты ещё не загружены
    if not data["all_results"]:
        all_gifts = get_top_gifts(
            filters=data["filters"],
            value_weights=data["value_weights"],
            interest_weights=data["interest_weights"],
            limit=100
        )
        user_data[user_id]["all_results"] = all_gifts
        
        # Сохраняем ответы в аналитику
        save_answers(
            session_id=session_id,
            filters=data["filters"],
            value_weights=data["value_weights"],
            interests=data["selected_interests"]
        )
        save_event(session_id, "results_loaded", {"count": len(all_gifts)})

    all_gifts = data["all_results"]
    current_index = data["current_gift_index"]

    # Если подарки закончились
    if current_index >= len(all_gifts):
        await show_summary(update, context, user_id)
        return

    gift = all_gifts[current_index]
    total = len(all_gifts)

    # Формируем текст
    text = f"🎁 *Подарок {current_index + 1} из {total}*\n\n"
    text += f"*{gift['name']}*\n"
    text += f"💰 {gift['price']}\n\n"
    if gift['description']:
        text += f"📝 {gift['description']}\n\n"
    text += "_Оцени подарок — покажем следующий!_"

    # Кнопки
    keyboard = [
        [
            InlineKeyboardButton("👍 Нравится", callback_data=f"rate_like_{gift['id']}"),
            InlineKeyboardButton("👎 Не подходит", callback_data=f"rate_dislike_{gift['id']}")
        ],
        [InlineKeyboardButton("⏭️ Пропустить", callback_data="rate_skip")],
        [InlineKeyboardButton("🏁 Завершить подбор", callback_data="rate_finish")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        try:
            await update.callback_query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        except:
            await update.callback_query.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def show_summary(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Показывает итоги подбора"""
    data = user_data[user_id]
    session_id = data["session_id"]
    
    liked = data["liked_gifts"]
    total_viewed = data["current_gift_index"]
    
    complete_session(session_id)
    save_event(session_id, "completed", {"liked": len(liked), "viewed": total_viewed})

    text = "🎉 *Подбор завершён!*\n\n"
    text += f"📊 Просмотрено: {total_viewed} подарков\n"
    text += f"❤️ Понравилось: {len(liked)}\n\n"

    if liked:
        text += "*Твои избранные:*\n\n"
        for i, gift in enumerate(liked[:10], 1):
            text += f"{i}. {gift['name']} — {gift['price']}\n"

    text += "\n🔄 Хочешь начать заново? Нажми /start"

    keyboard = [[InlineKeyboardButton("🔄 Начать заново", callback_data="restart")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    try:
        await query.answer()
    except:
        pass

    user_id = update.effective_user.id
    data_str = query.data

    if user_id not in user_data:
        init_user_data(user_id)
        await query.message.reply_text("⚠️ Сессия устарела. Начинаем заново!\n\nНажми /start")
        return

    data = user_data[user_id]
    session_id = data["session_id"]

    # === ОБРАБОТКА ОЦЕНОК ===
    if data_str.startswith("rate_"):
        action = data_str.replace("rate_", "")
        
        if action == "skip":
            save_event(session_id, "skip", {"index": data["current_gift_index"]})
            user_data[user_id]["current_gift_index"] += 1
            await show_single_gift(update, context, user_id)
            return
        
        if action == "finish":
            await show_summary(update, context, user_id)
            return
        
        if action.startswith("like_"):
            gift_id = int(action.replace("like_", ""))
            gift = data["all_results"][data["current_gift_index"]]
            
            save_rating(session_id, gift_id, gift["name"], rating=1)
            save_event(session_id, "like", {"gift_id": gift_id})
            
            user_data[user_id]["liked_gifts"].append(gift)
            user_data[user_id]["current_gift_index"] += 1
            await show_single_gift(update, context, user_id)
            return
        
        if action.startswith("dislike_"):
            gift_id = int(action.replace("dislike_", ""))
            gift = data["all_results"][data["current_gift_index"]]
            
            save_rating(session_id, gift_id, gift["name"], rating=-1)
            save_event(session_id, "dislike", {"gift_id": gift_id})
            
            user_data[user_id]["disliked_gifts"].append(gift)
            user_data[user_id]["current_gift_index"] += 1
            await show_single_gift(update, context, user_id)
            return

    # === RESTART ===
    if data_str == "restart":
        init_user_data(user_id)
        await send_question(update, context, user_id)
        return

    # === ИНТЕРЕСЫ ===
    if data_str.startswith("interest_"):
        interest_tag = data_str.replace("interest_", "")

        if interest_tag == "none":
            user_data[user_id]["selected_interests"] = []
            user_data[user_id]["interest_weights"] = {}
            user_data[user_id]["current_question"] = 11
            await show_single_gift(update, context, user_id)
            return

        # Защита от двойных нажатий
        if "processing_interest" in data and data["processing_interest"]:
            return
        user_data[user_id]["processing_interest"] = True

        selected = user_data[user_id].get("selected_interests", [])
        if interest_tag in selected:
            selected.remove(interest_tag)
        else:
            selected.append(interest_tag)
        user_data[user_id]["selected_interests"] = selected

        await send_interests_question(update, context, user_id)
        
        user_data[user_id]["processing_interest"] = False
        return

    # === ВОПРОСЫ 1-9 ===
    if data_str.startswith("q"):
        parts = data_str.split("_", 1)
        q_num = int(parts[0].replace("q", ""))
        answer = parts[1]

        question = QUESTIONS[q_num]

        if question["type"] == "primary":
            if question["tag"] == "budget":
                user_data[user_id]["filters"]["budget"] = get_budget_tags(answer)
            else:
                user_data[user_id]["filters"][question["tag"]] = answer

        elif question["type"] == "value":
            if question["tag"] == "gift_experience":
                val = float(answer.split("_")[1])
                user_data[user_id]["value_weights"]["gift_experience"] = val

            elif question["tag"] == "practical_emotional":
                if answer == "practical_1":
                    user_data[user_id]["value_weights"]["gift_practical"] = 1.0
                    user_data[user_id]["value_weights"]["gift_emotional"] = 0.0
                elif answer == "emotional_1":
                    user_data[user_id]["value_weights"]["gift_practical"] = 0.0
                    user_data[user_id]["value_weights"]["gift_emotional"] = 1.0
                else:
                    user_data[user_id]["value_weights"]["gift_practical"] = 0.5
                    user_data[user_id]["value_weights"]["gift_emotional"] = 0.5

            elif question["tag"] == "gift_daily_use":
                val = float(answer.split("_")[1])
                user_data[user_id]["value_weights"]["gift_daily_use"] = val

            elif question["tag"] == "gift_aesthetic":
                val = float(answer.split("_")[1])
                user_data[user_id]["value_weights"]["gift_aesthetic"] = val

        user_data[user_id]["current_question"] = q_num + 1
        await send_question(update, context, user_id)


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("terms", terms))
    app.add_handler(CommandHandler("support", support))
    app.add_handler(CommandHandler("paysupport", paysupport))
    app.add_handler(CallbackQueryHandler(handle_answer))

    print("🤖 Бот запущен! (v3.0 - с аналитикой и лайками)")
    app.run_polling()


if __name__ == "__main__":
    main()