# main.py — Умный бот с базой знаний (с сохранением в JSON)
import os
import json  # ← НОВОЕ: для работы с JSON-файлом
import telebot
from telebot import apihelper
from dotenv import load_dotenv
import random

# Загружаем токен
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Настройка прокси
apihelper.proxy = {
    'https': 'socks5://127.0.0.1:12334',
    'http': 'socks5://127.0.0.1:12334'
}

bot = telebot.TeleBot(TOKEN)

# === БАЗА ЗНАНИЙ ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KNOWLEDGE_FILE = os.path.join(BASE_DIR, "knowledge.json")  # ← НОВОЕ

# Начальная база (если файла ещё нет)
DEFAULT_KNOWLEDGE = {
    "привет": "👋 Привет! Я умный бот. Задай мне вопрос!",
    "как дела": "Отлично! Спасибо, что спросил. А у тебя как?",
    "что ты умеешь": "Я умею отвечать на вопросы! Попробуй спросить что-нибудь.",
    "кто тебя создал": "Меня создал Олег — разработчик Telegram-ботов на Python.",
    "сколько стоит": "Разработка ботов от 1500₽. Подробности: @ConversAIonist",
    "контакты": "📩 Telegram: @ConversAIonist\nGitHub: github.com/Myth3916",
    "спасибо": "Пожалуйста! 😊 Всегда рад помочь!",
    "пока": "До свидания! Заходи ещё! 👋",
}

# ← НОВОЕ: Загружаем базу из файла или создаём новую
def load_knowledge():
    if os.path.exists(KNOWLEDGE_FILE):
        with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        save_knowledge(DEFAULT_KNOWLEDGE)
        return DEFAULT_KNOWLEDGE.copy()

# ← НОВОЕ: Сохраняем базу в файл
def save_knowledge(data):
    with open(KNOWLEDGE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Загружаем базу при старте
KNOWLEDGE_BASE = load_knowledge()

DEFAULT_RESPONSES = [
    "Интересный вопрос! Пока я не знаю ответа, но учусь. 😊",
    "Хм, не уверен, что понял. Попробуй перефразировать.",
    "Я ещё учусь! Попробуй спросить что-то другое.",
]

def find_answer(user_text):
    user_text = user_text.lower().strip()
    for key, answer in KNOWLEDGE_BASE.items():
        if key in user_text:
            return answer
    return random.choice(DEFAULT_RESPONSES)

@bot.message_handler(commands=["start"])
def handle_start(message):
    bot.reply_to(
        message,
        "👋 Привет! Я умный бот с базой знаний.\n\n"
        "Задай мне вопрос или напиши /help для справки."
    )

@bot.message_handler(commands=["help"])
def handle_help(message):
    bot.reply_to(
        message,
        " **Как пользоваться:**\n\n"
        "Просто напиши вопрос, например:\n"
        "• Привет\n"
        "• Как дела\n"
        "• Что ты умеешь\n"
        "• Сколько стоит\n"
        "• Контакты\n\n"
        "Я постараюсь ответить! 😊"
    )

@bot.message_handler(commands=["add"])
def handle_add(message):
    text = message.text[4:].strip()
    parts = text.split("|")
    
    if len(parts) == 2:
        key = parts[0].strip().lower()
        answer = parts[1].strip()
        KNOWLEDGE_BASE[key] = answer
        save_knowledge(KNOWLEDGE_BASE)  # ← НОВОЕ: сохраняем сразу!
        bot.reply_to(message, f"✅ Добавлено в базу!\n\n🔑 Ключ: {key}\n💬 Ответ: {answer}")
    else:
        bot.reply_to(message, "❌ Ошибка! Используй: /add ключ|ответ")

# ← НОВОЕ: Команда для просмотра всей базы
@bot.message_handler(commands=["list"])
def handle_list(message):
    items = "\n".join([f"• {k}: {v[:30]}..." if len(v) > 30 else f"• {k}: {v}" 
                       for k, v in KNOWLEDGE_BASE.items()])
    bot.reply_to(message, f" База знаний ({len(KNOWLEDGE_BASE)} записей):\n\n{items}")

@bot.message_handler(content_types=["text"])
def handle_message(message):
    answer = find_answer(message.text)
    bot.reply_to(message, answer)

if __name__ == "__main__":
    print("✅ Умный бот запущен...")
    print(f"📚 В базе знаний: {len(KNOWLEDGE_BASE)} ответов")
    bot.infinity_polling()