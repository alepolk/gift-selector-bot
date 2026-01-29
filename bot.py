from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from scoring import get_top_gifts

# === ТОКЕН БОТА ===
BOT_TOKEN = "8513351241:AAGmH0ANaZqC-Iook7KJN0Vbo0qT8sKqgTU"

# === ВОПРОСЫ (фиксированный порядок 1-9) ===
QUESTIONS = [
    None,  # индекс 0 не используем
    # 1. Бюджет
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
    # 2. Пол
    {
        "text": "👤 Кому выбираете подарок?",
        "options": [
            ("Мужчине", "gender_male"),
            ("Женщине", "gender_female"),
        ],
        "type": "primary",
        "tag": "gender"
    },
    # 3. Возраст
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
    # 4. Отношения
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
    # 5. Повод
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
    # 6. Вещь или впечатление
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
    # 7. Практичный или эмоциональный
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
    # 8. Ежедневное использование
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
    # 9. Эстетика
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

# Увлечения для мужчин
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

# Увлечения для женщин
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

# Увлечения для пожилых (65+)
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
    """Возвращает список бюджетных тегов до выбранного включительно"""
    all_budgets = ["budget_2000", "budget_5000", "budget_10000", "budget_15000",
                   "budget_20000", "budget_30000", "budget_50000", "budget_100000"]
    if selected_budget in all_budgets:
        index = all_budgets.index(selected_budget)
        return all_budgets[:index + 1]
    return all_budgets


def get_interests_for_user(gender: str, age: str) -> list:
    """Возвращает список увлечений в зависимости от пола и возраста"""
    if age == "age_65plus":
        return INTERESTS_ELDERLY
    if gender == "gender_female":
        return INTERESTS_FEMALE
    else:
        return INTERESTS_MALE


def init_user_data(user_id: int):
    """Инициализирует данные пользователя"""
    user_data[user_id] = {
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
        "current_offset": 0
    }


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало опроса"""
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
    """Условия использования"""
    await update.message.reply_text(
        "📜 *Условия использования*\n\n"
        "1. Бот предоставляет рекомендации подарков на основе ваших ответов.\n"
        "2. Мы не гарантируем наличие товаров в магазинах.\n"
        "3. Оплата за премиум-доступ не возвращается.\n"
        "4. Используя бота, вы соглашаетесь с этими условиями.\n\n"
        "По вопросам: @cfc_consult",
        parse_mode="Markdown"
    )


async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Поддержка"""
    await update.message.reply_text(
        "🆘 *Поддержка*\n\n"
        "Если у тебя возникли вопросы или проблемы, напиши: @cfc_consult\n\n"
        "Отвечаем в течение 24 часов.",
        parse_mode="Markdown"
    )


async def paysupport(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Поддержка по платежам"""
    await update.message.reply_text(
        "💳 *Поддержка по платежам*\n\n"
        "Проблемы с оплатой? Напиши: @cfc_consult\n\n"
        "Укажи:\n"
        "• Дату и время платежа\n"
        "• Сумму\n"
        "• Описание проблемы\n\n"
        "Разберёмся в течение 24 часов.",
        parse_mode="Markdown"
    )


async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Отправляет вопрос пользователю"""
    q_num = user_data[user_id]["current_question"]

    # Вопрос 10 — увлечения (множественный выбор)
    if q_num == 10:
        await send_interests_question(update, context, user_id)
        return

    # Вопросы закончились — показываем результат
    if q_num > 10:
        await show_results(update, context, user_id)
        return

    # Вопросы 1-9
    question = QUESTIONS[q_num]

    # Создаём кнопки
    keyboard = []
    for text, value in question["options"]:
        keyboard.append([InlineKeyboardButton(text, callback_data=f"q{q_num}_{value}")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    text = f"*Вопрос {q_num} из 10*\n\n{question['text']}"

    # Если это callback (ответ на кнопку) — редактируем сообщение
    if update.callback_query:
        try:
            await update.callback_query.message.edit_text(
                text,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
        except:
            await update.callback_query.message.reply_text(
                text,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def send_interests_question(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Отправляет вопрос про увлечения с множественным выбором"""
    data = user_data[user_id]
    gender = data["filters"].get("gender", "gender_male")
    age = data["filters"].get("age", "age_26_35")

    interests = get_interests_for_user(gender, age)
    selected = data.get("selected_interests", [])

    # Создаём кнопки с галочками
    keyboard = []
    for text, tag in interests:
        checkmark = "✅ " if tag in selected else ""
        keyboard.append([InlineKeyboardButton(
            f"{checkmark}{text}",
            callback_data=f"interest_{tag}"
        )])

    # Кнопка "Не знаю увлечений"
    keyboard.append([InlineKeyboardButton(
        "🤷 Не знаю увлечений",
        callback_data="interest_none"
    )])

    # Кнопка "Готово"
    keyboard.append([InlineKeyboardButton(
        "✅ Готово — показать подарки",
        callback_data="interests_done"
    )])

    reply_markup = InlineKeyboardMarkup(keyboard)

    selected_count = len(selected)
    text = f"*Вопрос 10 из 10*\n\n"
    text += "🎯 *Какие увлечения есть у получателя?*\n"
    text += "_Выбери все подходящие и нажми «Готово»_\n\n"
    if selected_count > 0:
        text += f"Выбрано: {selected_count}"

    if update.callback_query:
        try:
            await update.callback_query.message.edit_text(
                text,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
        except:
            await update.callback_query.message.reply_text(
                text,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает ответ пользователя"""
    query = update.callback_query

    try:
        await query.answer()
    except Exception:
        pass

    user_id = update.effective_user.id
    data_str = query.data

    # Проверяем есть ли пользователь
    if user_id not in user_data:
        init_user_data(user_id)
        await query.message.reply_text("⚠️ Сессия устарела. Начинаем заново!\n\nНажми /start")
        return

    # Обработка кнопки "Показать ещё"
    if data_str.startswith("more_"):
        offset = int(data_str.split("_")[1])
        await show_results(update, context, user_id, offset)
        return

    # Обработка кнопки "Начать заново"
    if data_str == "restart":
        init_user_data(user_id)
        await send_question(update, context, user_id)
        return

    # Обработка выбора увлечений
    if data_str.startswith("interest_"):
        interest_tag = data_str.replace("interest_", "")

        if interest_tag == "none":
            user_data[user_id]["selected_interests"] = []
            user_data[user_id]["current_question"] = 11
            await show_results(update, context, user_id)
            return

        # Переключаем выбор увлечения
        selected = user_data[user_id].get("selected_interests", [])
        if interest_tag in selected:
            selected.remove(interest_tag)
        else:
            selected.append(interest_tag)
        user_data[user_id]["selected_interests"] = selected

        await send_interests_question(update, context, user_id)
        return

    # Обработка "Готово" по увлечениям
    if data_str == "interests_done":
        selected = user_data[user_id].get("selected_interests", [])
        for tag in selected:
            user_data[user_id]["interest_weights"][tag] = 1.0

        user_data[user_id]["current_question"] = 11
        await show_results(update, context, user_id)
        return

    # Обработка ответов на вопросы 1-9
    if data_str.startswith("q"):
        parts = data_str.split("_", 1)
        q_num = int(parts[0].replace("q", ""))
        answer = parts[1]

        question = QUESTIONS[q_num]

        # PRIMARY вопросы
        if question["type"] == "primary":
            if question["tag"] == "budget":
                user_data[user_id]["filters"]["budget"] = get_budget_tags(answer)
            else:
                user_data[user_id]["filters"][question["tag"]] = answer

        # VALUE вопросы
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

        # Следующий вопрос
        user_data[user_id]["current_question"] = q_num + 1
        await send_question(update, context, user_id)


async def show_results(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, offset: int = 0):
    """Показывает результаты подбора"""
    data = user_data[user_id]

    if offset == 0:
        all_gifts = get_top_gifts(
            filters=data["filters"],
            value_weights=data["value_weights"],
            interest_weights=data["interest_weights"],
            limit=100
        )
        user_data[user_id]["all_results"] = all_gifts
    else:
        all_gifts = user_data[user_id]["all_results"]

    if not all_gifts:
        await update.callback_query.message.reply_text(
            "😔 К сожалению, не нашлось подходящих подарков.\n\n"
            "Попробуй изменить параметры: /start"
        )
        return

    user_data[user_id]["current_offset"] = offset

    gifts_to_show = all_gifts[offset:offset + 5]

    if not gifts_to_show:
        await update.callback_query.message.reply_text(
            "📭 Больше подходящих подарков нет.\n\n🔄 Начать заново: /start"
        )
        return

    text = f"🎁 *ПОДАРКИ {offset + 1}–{offset + len(gifts_to_show)} из {len(all_gifts)}:*\n\n"

    for i, gift in enumerate(gifts_to_show, offset + 1):
        text += f"*{i}. {gift['name']}*\n"
        text += f"💰 {gift['price']}\n"
        if gift['description']:
            text += f"📝 {gift['description']}\n"
        text += "\n"

    keyboard = []

    if offset + 5 < len(all_gifts):
        keyboard.append([InlineKeyboardButton("➡️ Показать ещё 5", callback_data=f"more_{offset + 5}")])

    keyboard.append([InlineKeyboardButton("🔄 Начать заново", callback_data="restart")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)


def main():
    """Запуск бота"""
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("terms", terms))
    app.add_handler(CommandHandler("support", support))
    app.add_handler(CommandHandler("paysupport", paysupport))
    app.add_handler(CallbackQueryHandler(handle_answer))

    print("🤖 Бот запущен! (v2.3 - с командами поддержки)")
    app.run_polling()


if __name__ == "__main__":
    main()