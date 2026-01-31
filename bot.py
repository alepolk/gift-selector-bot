from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from scoring import get_top_gifts
from analytics import (
    create_session, save_answers, save_rating, 
    save_event, complete_session
)
import asyncio

# === ТОКЕН БОТА ===
BOT_TOKEN = "8513351241:AAGmH0ANaZqC-Iook7KJN0Vbo0qT8sKqgTU"

# === DEBUG MODE ===
DEBUG = True

def debug_print(msg):
    if DEBUG:
        print(f"[DEBUG] {msg}")

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

# Увлечения - ФИКСИРОВАННЫЙ ПОРЯДОК (не меняется!)
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
    """Возвращает КОПИЮ списка интересов (чтобы не мутировать оригинал)"""
    if age == "age_65plus":
        return list(INTERESTS_ELDERLY)
    if gender == "gender_female":
        return list(INTERESTS_FEMALE)
    return list(INTERESTS_MALE)


def init_user_data(user_id: int):
    session_id = create_session(source="bot", user_id=str(user_id))
    save_event(session_id, "start")
    
    user_data[user_id] = {
        "session_id": session_id,
        "current_question": 1,
        "state": "questions",  # questions | interests | gifts | finished
        "filters": {},
        "value_weights": {
            "gift_practical": 0.5,
            "gift_emotional": 0.5,
            "gift_experience": 0.5,
            "gift_daily_use": 0.5,
            "gift_aesthetic": 0.5,
        },
        "interest_weights": {},
        "selected_interests": [],  # Список, не set!
        "interests_list": None,  # Кэшируем список интересов
        "all_results": [],
        "current_gift_index": 0,
        "liked_gifts": [],
        "disliked_gifts": [],
        "is_processing": False,  # Блокировка от двойных нажатий
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
    data = user_data[user_id]
    q_num = data["current_question"]
    session_id = data["session_id"]

    question = QUESTIONS[q_num]
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
            pass
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def send_interests_question(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Показывает вопрос с интересами - порядок кнопок НЕ меняется"""
    data = user_data[user_id]
    
    # Кэшируем список интересов при первом показе
    if data["interests_list"] is None:
        gender = data["filters"].get("gender", "gender_male")
        age = data["filters"].get("age", "age_26_35")
        data["interests_list"] = get_interests_for_user(gender, age)
    
    interests = data["interests_list"]
    selected = data["selected_interests"]

    # Строим клавиатуру - порядок ВСЕГДА одинаковый
    keyboard = []
    for text, tag in interests:
        if tag in selected:
            btn_text = f"✅ {text}"
        else:
            btn_text = text
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"int_{tag}")])

    keyboard.append([InlineKeyboardButton("🤷 Не знаю увлечений", callback_data="int_skip")])
    keyboard.append([InlineKeyboardButton("✅ Готово — показать подарки", callback_data="int_done")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    selected_count = len(selected)
    text = f"*Вопрос 10 из 10*\n\n"
    text += "🎯 *Какие увлечения есть у получателя?*\n"
    text += "_Выбери все подходящие и нажми «Готово»_\n\n"
    text += f"Выбрано: {selected_count}"

    if update.callback_query:
        try:
            await update.callback_query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        except:
            pass


async def show_gift(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Показывает текущий подарок"""
    data = user_data[user_id]
    
    all_gifts = data["all_results"]
    current_index = data["current_gift_index"]
    total = len(all_gifts)

    debug_print(f"show_gift: user={user_id}, total={total}, current_index={current_index}")

    # Если подарки закончились
    if current_index >= total:
        debug_print(f"show_gift: Подарки закончились, показываем summary")
        await show_summary(update, context, user_id)
        return

    gift = all_gifts[current_index]

    text = f"🎁 *Подарок {current_index + 1} из {total}*\n\n"
    text += f"*{gift['name']}*\n"
    text += f"💰 {gift['price']}\n\n"
    if gift.get('description'):
        text += f"📝 {gift['description']}\n\n"
    text += "_Оцени подарок — покажем следующий!_"

    keyboard = [
        [
            InlineKeyboardButton("👍 Нравится", callback_data="gift_like"),
            InlineKeyboardButton("👎 Не подходит", callback_data="gift_dislike")
        ],
        [InlineKeyboardButton("⏭️ Пропустить", callback_data="gift_skip")],
        [InlineKeyboardButton("🏁 Завершить подбор", callback_data="gift_finish")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        try:
            await update.callback_query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        except Exception as e:
            debug_print(f"show_gift edit_text error: {e}")
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def show_summary(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Показывает итоги подбора"""
    data = user_data[user_id]
    session_id = data["session_id"]
    
    data["state"] = "finished"
    
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
        try:
            await update.callback_query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        except:
            pass


async def load_and_show_gifts(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, interest_weights: dict):
    """Загружает подарки и показывает первый"""
    data = user_data[user_id]
    session_id = data["session_id"]
    
    debug_print(f"load_and_show_gifts: user={user_id}")
    debug_print(f"  filters: {data['filters']}")
    debug_print(f"  value_weights: {data['value_weights']}")
    debug_print(f"  interest_weights: {interest_weights}")
    
    try:
        # Загружаем подарки
        all_gifts = get_top_gifts(
            filters=data["filters"],
            value_weights=data["value_weights"],
            interest_weights=interest_weights,
            limit=100
        )
        
        debug_print(f"  get_top_gifts returned: {len(all_gifts) if all_gifts else 'None'} gifts")
        
        if all_gifts is None:
            all_gifts = []
            debug_print("  WARNING: get_top_gifts returned None!")
        
        data["all_results"] = all_gifts
        data["current_gift_index"] = 0
        
        # Сохраняем в аналитику
        save_answers(
            session_id=session_id,
            filters=data["filters"],
            value_weights=data["value_weights"],
            interests=data["selected_interests"]
        )
        save_event(session_id, "results_loaded", {"count": len(all_gifts)})
        
        if len(all_gifts) == 0:
            debug_print("  No gifts found! Showing 'no results' message")
            # Показываем сообщение что подарков не найдено
            text = "😔 *К сожалению, подарков по вашим критериям не найдено*\n\n"
            text += "Попробуйте:\n"
            text += "• Увеличить бюджет\n"
            text += "• Выбрать меньше фильтров\n\n"
            text += "Нажмите /start чтобы начать заново"
            
            keyboard = [[InlineKeyboardButton("🔄 Начать заново", callback_data="restart")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if update.callback_query:
                try:
                    await update.callback_query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
                except Exception as e:
                    debug_print(f"  edit_text error: {e}")
            return
        
        await show_gift(update, context, user_id)
        
    except Exception as e:
        debug_print(f"  EXCEPTION in load_and_show_gifts: {e}")
        import traceback
        traceback.print_exc()
        
        # Показываем ошибку пользователю
        text = f"⚠️ *Произошла ошибка при загрузке подарков*\n\nПопробуйте /start"
        keyboard = [[InlineKeyboardButton("🔄 Начать заново", callback_data="restart")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            try:
                await update.callback_query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
            except:
                pass


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    callback_data = query.data
    
    debug_print(f"handle_callback: user={user_id}, data={callback_data}")
    
    # Отвечаем на callback сразу
    try:
        await query.answer()
    except:
        pass

    # Проверяем есть ли данные пользователя
    if user_id not in user_data:
        init_user_data(user_id)
        await query.message.reply_text("⚠️ Сессия устарела. Начинаем заново!\n\nНажми /start")
        return

    data = user_data[user_id]
    
    # === БЛОКИРОВКА ОТ ДВОЙНЫХ НАЖАТИЙ ===
    if data["is_processing"]:
        debug_print(f"  Blocked: already processing")
        return
    data["is_processing"] = True
    
    try:
        session_id = data["session_id"]
        state = data["state"]
        
        debug_print(f"  state={state}")

        # === RESTART ===
        if callback_data == "restart":
            init_user_data(user_id)
            await send_question(update, context, user_id)
            return

        # === ВОПРОСЫ 1-9 ===
        if callback_data.startswith("q") and state == "questions":
            parts = callback_data.split("_", 1)
            if len(parts) != 2:
                return
                
            try:
                q_num = int(parts[0].replace("q", ""))
            except ValueError:
                return
                
            answer = parts[1]
            
            debug_print(f"  Question {q_num}, answer={answer}")
            
            # Проверяем что это текущий вопрос
            if q_num != data["current_question"]:
                debug_print(f"  Skipped: not current question (current={data['current_question']})")
                return
            
            question = QUESTIONS[q_num]

            if question["type"] == "primary":
                if question["tag"] == "budget":
                    data["filters"]["budget"] = get_budget_tags(answer)
                else:
                    data["filters"][question["tag"]] = answer

            elif question["type"] == "value":
                if question["tag"] == "gift_experience":
                    val = float(answer.split("_")[1])
                    data["value_weights"]["gift_experience"] = val

                elif question["tag"] == "practical_emotional":
                    if answer == "practical_1":
                        data["value_weights"]["gift_practical"] = 1.0
                        data["value_weights"]["gift_emotional"] = 0.0
                    elif answer == "emotional_1":
                        data["value_weights"]["gift_practical"] = 0.0
                        data["value_weights"]["gift_emotional"] = 1.0
                    else:
                        data["value_weights"]["gift_practical"] = 0.5
                        data["value_weights"]["gift_emotional"] = 0.5

                elif question["tag"] == "gift_daily_use":
                    val = float(answer.split("_")[1])
                    data["value_weights"]["gift_daily_use"] = val

                elif question["tag"] == "gift_aesthetic":
                    val = float(answer.split("_")[1])
                    data["value_weights"]["gift_aesthetic"] = val

            # Переход к следующему вопросу
            next_q = q_num + 1
            data["current_question"] = next_q
            
            debug_print(f"  Moving to question {next_q}")
            
            if next_q <= 9:
                await send_question(update, context, user_id)
            else:
                # Переходим к интересам
                data["state"] = "interests"
                save_event(session_id, "question_10_interests")
                debug_print(f"  Switching to interests state")
                await send_interests_question(update, context, user_id)
            return

        # === ИНТЕРЕСЫ ===
        if callback_data.startswith("int_") and state == "interests":
            action = callback_data[4:]  # Убираем "int_"
            
            debug_print(f"  Interest action: {action}")
            
            if action == "done":
                # Готово - загружаем подарки
                debug_print(f"  Interest DONE - loading gifts")
                data["state"] = "gifts"
                
                # Формируем веса интересов
                interest_weights = {}
                for tag in data["selected_interests"]:
                    interest_weights[tag] = 1.0
                data["interest_weights"] = interest_weights
                
                await load_and_show_gifts(update, context, user_id, interest_weights)
                return
            
            if action == "skip":
                # Пропустить интересы
                debug_print(f"  Interest SKIP - loading gifts without interests")
                data["state"] = "gifts"
                data["selected_interests"] = []
                data["interest_weights"] = {}
                
                await load_and_show_gifts(update, context, user_id, {})
                return
            
            # Toggle интереса (action = "interest_tech" и т.д.)
            interest_tag = action
            selected = data["selected_interests"]
            
            if interest_tag in selected:
                selected.remove(interest_tag)
                debug_print(f"  Removed interest: {interest_tag}")
            else:
                selected.append(interest_tag)
                debug_print(f"  Added interest: {interest_tag}")
            
            await send_interests_question(update, context, user_id)
            return

        # === ПОДАРКИ ===
        if callback_data.startswith("gift_") and state == "gifts":
            action = callback_data[5:]  # Убираем "gift_"
            
            debug_print(f"  Gift action: {action}")
            
            current_index = data["current_gift_index"]
            all_gifts = data["all_results"]
            
            if current_index >= len(all_gifts):
                await show_summary(update, context, user_id)
                return
            
            gift = all_gifts[current_index]
            
            if action == "like":
                save_rating(session_id, gift['id'], gift["name"], rating=1)
                save_event(session_id, "like", {"gift_id": gift['id']})
                data["liked_gifts"].append(gift)
                data["current_gift_index"] += 1
                await show_gift(update, context, user_id)
                
            elif action == "dislike":
                save_rating(session_id, gift['id'], gift["name"], rating=-1)
                save_event(session_id, "dislike", {"gift_id": gift['id']})
                data["disliked_gifts"].append(gift)
                data["current_gift_index"] += 1
                await show_gift(update, context, user_id)
                
            elif action == "skip":
                save_event(session_id, "skip", {"index": current_index})
                data["current_gift_index"] += 1
                await show_gift(update, context, user_id)
                
            elif action == "finish":
                await show_summary(update, context, user_id)
            
            return

    except Exception as e:
        debug_print(f"  EXCEPTION in handle_callback: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Снимаем блокировку
        if user_id in user_data:
            user_data[user_id]["is_processing"] = False


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("terms", terms))
    app.add_handler(CommandHandler("support", support))
    app.add_handler(CommandHandler("paysupport", paysupport))
    app.add_handler(CallbackQueryHandler(handle_callback))

    print("🤖 Бот запущен! (v6.0 - с отладкой)")
    print(f"DEBUG mode: {DEBUG}")
    app.run_polling()


if __name__ == "__main__":
    main()