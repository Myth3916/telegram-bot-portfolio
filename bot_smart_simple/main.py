# main.py — Умный бот-консультант для бизнеса (с сохранением в JSON)
import os
import json
import telebot
from telebot import apihelper
from telebot import types  # Для создания кнопок
from dotenv import load_dotenv
import random

# Загружаем токен из файла .env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Настройка прокси (если нужна)
apihelper.proxy = {
    'https': 'socks5://127.0.0.1:12334',
    'http': 'socks5://127.0.0.1:12334'
}

bot = telebot.TeleBot(TOKEN)

# === НАСТРОЙКИ АДМИНИСТРАТОРА ===
# ⚠️ ЗАМЕНИТЕ это число на ваш реальный Telegram ID (узнайте у @userinfobot)
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

def is_admin(message):
    return message.from_user.id == ADMIN_ID

# === БАЗА ЗНАНИЙ ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KNOWLEDGE_FILE = os.path.join(BASE_DIR, "knowledge.json")

# Начальная база под бизнес-задачи (FAQ)
DEFAULT_KNOWLEDGE = {
    "сколько стоит": "💰 Стоимость зависит от услуги. Базовый пакет — от 1500₽. Для точного расчета напишите менеджеру: @ConversAIonist",
    "сроки": "⏳ Стандартные сроки выполнения — 2–3 рабочих дня. Срочные заказы обсуждаются индивидуально.",
    "доставка": "🚚 Да, мы осуществляем доставку по всей России! СДЭК, Почта России, курьером по Москве.",
    "как записаться": "📝 Чтобы записаться, напишите нам в личные сообщения: @ConversAIonist",
    "оплата": "💳 Принимаем оплату банковской картой, переводом по СБП или на расчетный счет для юр. лиц.",
    "контакты": "📩 Telegram: @ConversAIonist\n📞 Телефон: +7 (999) 000-00-00",
    "гарантия": "🛡️ Мы даем гарантию 7 дней на все виды работ. Если что-то пойдет не так — исправим бесплатно!",
    "спасибо": "Пожалуйста! 😊 Рады были помочь!",
}

# Словарь синонимов для умного поиска
KEYWORDS = {
    "сколько стоит": ["цена", "стоимость", "прайс", "сколько", "рублей", "денег", "дорого"],
    "сроки": ["когда", "долго", "быстро", "время", "срочно", "дни"],
    "доставка": ["доставить", "привезти", "курьер", "почта", "сдэк", "доставляете"],
    "как записаться": ["запись", "записаться", "забронировать", "регистрация"],
    "оплата": ["оплатить", "платить", "карта", "перевод", "сбп"],
    "контакты": ["телефон", "связь", "позвонить", "написать"],
    "гарантия": ["гарантия", "возврат", "исправить", "поломка"],
}

DEFAULT_RESPONSES = [
    "Интересный вопрос! Пока я не знаю точного ответа, но вы можете уточнить его у нашего менеджера: @ConversAIonist 😊",
    "Хм, не уверен, что понял. Попробуйте перефразировать или выберите вопрос из меню.",
    "Я ещё учусь! Попробуйте спросить о цене, сроках или доставке.",
]

# === РАБОТА С ФАЙЛОМ ===
def load_knowledge():
    if os.path.exists(KNOWLEDGE_FILE):
        with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        save_knowledge(DEFAULT_KNOWLEDGE)
        return DEFAULT_KNOWLEDGE.copy()

def save_knowledge(data):
    with open(KNOWLEDGE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

KNOWLEDGE_BASE = load_knowledge()

# === КЛАВИАТУРА ===
def create_main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    keyboard.add(
        types.KeyboardButton("💰 Сколько стоит?"),
        types.KeyboardButton("⏳ Какие сроки?")
    )
    keyboard.add(
        types.KeyboardButton("🚚 Есть доставка?"),
        types.KeyboardButton("📝 Как записаться?")
    )
    keyboard.add(
        types.KeyboardButton("💳 Как оплатить?"),
        types.KeyboardButton("📩 Контакты")
    )
    return keyboard

# === УМНЫЙ ПОИСК ===
def find_answer(user_text):
    user_text = user_text.lower().strip()
    
    # 1. Ищем точное совпадение ключа
    for key, answer in KNOWLEDGE_BASE.items():
        if key in user_text:
            return answer
    
    # 2. Ищем по синонимам
    for key, synonyms in KEYWORDS.items():
        for synonym in synonyms:
            if synonym in user_text:
                return KNOWLEDGE_BASE.get(key, random.choice(DEFAULT_RESPONSES))
    
    # 3. Если ничего не нашли
    return random.choice(DEFAULT_RESPONSES)

# === ОБРАБОТЧИКИ КОМАНД ===
@bot.message_handler(commands=["start"])
def handle_start(message):
    keyboard = create_main_keyboard()
    bot.send_message(
        message.chat.id,
        "👋 Здравствуйте! Я бот-консультант компании.\n\n"
        "Я работаю 24/7 и готов ответить на самые частые вопросы.\n"
        "Нажмите на кнопку ниже или напишите свой вопрос текстом:",
        reply_markup=keyboard
    )

@bot.message_handler(commands=["help"])
def handle_help(message):
    keyboard = create_main_keyboard()
    bot.send_message(
        message.chat.id,
        "📖 **Как пользоваться ботом:**\n\n"
        "1. Нажмите на кнопку с нужным вопросом\n"
        "2. Или напишите вопрос текстом\n"
        "3. Бот автоматически найдёт ответ\n\n"
        "Выберите вопрос из списка:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

@bot.message_handler(commands=["admin_help"])
def handle_admin_help(message):
    if not is_admin(message):
        return bot.reply_to(message, "❌ Эта команда доступна только администратору.")
    
    help_text = (
        "🛠️ **Панель управления администратора:**\n\n"
        "➕ **Добавить ответ:**\n`/add ключ|ответ`\n"
        "*(Пример: `/add акция|Скидка 10% до конца месяца`)*\n\n"
        "➖ **Удалить ответ:**\n`/delete ключ`\n"
        "*(Пример: `/delete акция`)*\n\n"
        "📋 **Посмотреть всю базу:**\n`/list`\n\n"
        "💡 *Совет: ключи пишите в нижнем регистре (маленькими буквами).*"
    )
    bot.send_message(message.chat.id, help_text, parse_mode="Markdown")

@bot.message_handler(commands=["add"])
def handle_add(message):
    if not is_admin(message):
        return bot.reply_to(message, "❌ Эта команда доступна только администратору.")
    
    text = message.text[4:].strip()
    parts = text.split("|")
    
    if len(parts) == 2:
        key = parts[0].strip().lower()
        answer = parts[1].strip()
        KNOWLEDGE_BASE[key] = answer
        save_knowledge(KNOWLEDGE_BASE)
        bot.reply_to(message, f"✅ Успешно добавлено!\n\n🔑 Ключ: `{key}`\n💬 Ответ: {answer}", parse_mode="Markdown")
    else:
        bot.reply_to(message, "❌ Ошибка формата! Используй:\n`/add ключ|ответ`\n\nПример: `/add цена|Наш прайс от 1500₽`", parse_mode="Markdown")

@bot.message_handler(commands=["delete"])
def handle_delete(message):
    if not is_admin(message):
        return bot.reply_to(message, "❌ Эта команда доступна только администратору.")
    
    key_to_delete = message.text[8:].strip().lower()
    
    if key_to_delete in KNOWLEDGE_BASE:
        del KNOWLEDGE_BASE[key_to_delete]
        save_knowledge(KNOWLEDGE_BASE)
        bot.reply_to(message, f"🗑️ Запись `{key_to_delete}` успешно удалена из базы.", parse_mode="Markdown")
    else:
        bot.reply_to(message, f"❌ Запись `{key_to_delete}` не найдена в базе.", parse_mode="Markdown")

@bot.message_handler(commands=["list"])
def handle_list(message):
    if not is_admin(message):
        return bot.reply_to(message, "❌ Эта команда доступна только администратору.")
    
    if not KNOWLEDGE_BASE:
        return bot.reply_to(message, "📭 База знаний пуста.")
        
    items = "\n".join([f"🔹 `{k}`: {v[:40]}..." if len(v) > 40 else f"🔹 `{k}`: {v}" 
                       for k, v in KNOWLEDGE_BASE.items()])
    bot.reply_to(message, f"📚 База знаний ({len(KNOWLEDGE_BASE)} записей):\n\n{items}", parse_mode="Markdown")

@bot.message_handler(content_types=["text"])
def handle_message(message):
    # Игнорируем команды, чтобы они не обрабатывались как обычный текст
    if message.text.startswith("/"):
        return
    
    answer = find_answer(message.text)
    bot.reply_to(message, answer)

if __name__ == "__main__":
    print("✅ Умный бизнес-бот запущен...")
    print(f"📚 В базе знаний: {len(KNOWLEDGE_BASE)} ответов")
    print(f"👤 ID Администратора: {ADMIN_ID}")
    bot.infinity_polling()