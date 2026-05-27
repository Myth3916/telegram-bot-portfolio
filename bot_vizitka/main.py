# main.py — Бот-визитка на pyTelegramBotAPI 
import os
import telebot
from telebot import types, apihelper  # ← Добавили apihelper для прокси
from dotenv import load_dotenv

# Загружаем токен из .env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# === НАСТРОЙКА ПРОКСИ (как в рабочем лид-боте) ===
apihelper.proxy = {
    'https': 'socks5://127.0.0.1:12334',
    'http': 'socks5://127.0.0.1:12334'
}
# === КОНЕЦ НАСТРОЙКИ ПРОКСИ ===

# Путь к логотипу (используем os.path.join для надёжности)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(BASE_DIR, "logo.png")

# Инициализируем бота
bot = telebot.TeleBot(TOKEN)

# Обработчик команды /start
@bot.message_handler(commands=["start"])
def send_welcome(message):
    # Создаём inline-кнопки
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_telegram = types.InlineKeyboardButton("Telegram", url="https://t.me/ConversAIonist")
    btn_github = types.InlineKeyboardButton("GitHub", url="https://github.com/Myth3916")
    btn_contact = types.InlineKeyboardButton("📩 Связаться", callback_data="contact")
    markup.add(btn_telegram, btn_github)
    markup.add(btn_contact)

    # Текст визитки
    text = (
        "👋 Привет! Я — Олег, разработчик чат-ботов на Python.\n\n"
        "🔹 Создаю ботов для бизнеса и личных задач\n"
        "🔹 Работаю с Telegram API, базами данных, внешними сервисами\n"
        "🔹 Готов взять ваш проект в работу!\n\n"
        "🔗 Мои контакты:"
    )
    
    # Отправляем фото с подписью
    try:
        with open(LOGO_PATH, 'rb') as photo:
            bot.send_photo(
                message.chat.id,
                photo,
                caption=text,
                reply_markup=markup,
                disable_notification=False
            )
    except FileNotFoundError:
        # Если фото не найдено, отправляем только текст
        bot.send_message(
            message.chat.id,
            text + "\n\n⚠️ Логотип не найден",
            reply_markup=markup
        )

    

# Обработчик нажатия на кнопку "Связаться"
@bot.callback_query_handler(func=lambda call: call.data == "contact")
def handle_contact(call):
    bot.answer_callback_query(call.id, "✍️ Напишите мне в ЛС: @ConversAIonist")
    bot.send_message(call.message.chat.id, "📬 Напишите мне напрямую: @ConversAIonist")

# Запуск бота
if __name__ == "__main__":
    print("✅ Бот-визитка запущен...")
    print(f"📁 Путь к логотипу: {LOGO_PATH}")
    if os.path.exists(LOGO_PATH):
        print("✅ Логотип найден")
    else:
        print("⚠️ Логотип не найден по указанному пути")
    bot.infinity_polling()