import os
import sqlite3                # <-- для работы с базой данных
from datetime import datetime  # <-- для времени
import telebot
from dotenv import load_dotenv
from telebot import apihelper  # <-- для прокси 

# Фиксируем путь к базе относительно расположения main.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "leads.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            text TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_to_db(user_id, username, text):
    """Сохраняет заявку в базу данных"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO leads (user_id, username, text, created_at) VALUES (?, ?, ?, ?)",
        (user_id, username, text, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# === НАСТРОЙКА ПРОКСИ ДЛЯ TELEBOT ===
from telebot import apihelper

apihelper.proxy = {
    'https': 'socks5://127.0.0.1:12334',
    'http': 'socks5://127.0.0.1:12334'
}
# === КОНЕЦ НАСТРОЙКИ ===

@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message, "👋 Привет! Я бот для сбора заявок.\nНажми кнопку ниже 👇", 
                 reply_markup=keyboard())

def keyboard():
    from telebot import types
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📩 Оставить заявку", callback_data="lead"))
    return markup

@bot.callback_query_handler(func=lambda call: call.data == "lead")
def handle_lead(call):
    bot.send_message(call.message.chat.id, "✍️ Напиши своё имя и телефон:")
    bot.register_next_step_handler(call.message, save_lead)

def save_lead(message):
    """Обрабатывает ввод пользователя и сохраняет заявку"""
    # Сохраняем в базу
    save_to_db(
        message.from_user.id,
        message.from_user.username,
        message.text
    )
    # отправим данные админу (мне)
    bot.send_message(message.from_user.id, f"✅ Принято: {message.text}")
   

# === АДМИНКА ===

# Твой Telegram chat_id (узнай у бота @userinfobot или напиши боту /start и посмотри в логи)
ADMIN_CHAT_ID = 1539534866  # ← ЗАМЕНИ НА СВОЙ!

@bot.message_handler(commands=["admin"])
def admin_panel(message):
    """Панель администратора — показывает статистику"""
    if message.chat.id != ADMIN_CHAT_ID:
        bot.reply_to(message, "❌ Доступ запрещён")
        return
    
    # Получаем статистику из БД
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Всего заявок
    cur.execute("SELECT COUNT(*) FROM leads")
    total = cur.fetchone()[0]
    
    # Заявок за сегодня
    cur.execute("SELECT COUNT(*) FROM leads WHERE DATE(created_at) = DATE('now')")
    today = cur.fetchone()[0]
    
    # Последние 5 заявок
    cur.execute("SELECT username, text, created_at FROM leads ORDER BY id DESC LIMIT 5")
    recent = cur.fetchall()
    
    conn.close()
    
    # Формируем сообщение
    msg = f"📊 **Статистика заявок**\n\n"
    msg += f"📈 Всего: {total}\n"
    msg += f"📅 Сегодня: {today}\n\n"
    
    if recent:
        msg += f"🕐 **Последние 5 заявок:**\n"
        for i, (username, text, created_at) in enumerate(recent, 1):
            user = f"@{username}" if username else "❌ нет username"
            msg += f"\n{i}. {user}\n   📝 {text}\n   ⏰ {created_at[:16]}"
    else:
        msg += "📭 Пока нет заявок"
    
    # Добавляем кнопку экспорта
    from telebot import types
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📥 Экспорт CSV", callback_data="export_csv"))

    bot.send_message(message.chat.id, msg, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "export_csv")
def export_csv(call):
    """Экспортирует все заявки в CSV файл"""
    if call.message.chat.id != ADMIN_CHAT_ID:
        bot.answer_callback_query(call.id, "❌ Доступ запрещён")
        return
    
    # Получаем все заявки из БД
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, user_id, username, text, created_at FROM leads ORDER BY id")
    rows = cur.fetchall()
    conn.close()
    
    if not rows:
        bot.answer_callback_query(call.id, "📭 Нет данных для экспорта")
        return
    
    # Создаём CSV файл
    import csv
    csv_path = os.path.join(BASE_DIR, "leads_export.csv")
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['ID', 'User ID', 'Username', 'Заявка', 'Дата'])
        writer.writerows(rows)
    
    # Отправляем файл админу
    with open(csv_path, 'rb') as f:
        bot.send_document(
            call.message.chat.id, 
            f, 
            visible_file_name=f"leads_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        )
    
    bot.answer_callback_query(call.id, "✅ Файл отправлен!")
# === КОНЕЦ АДМИНКИ ===

if __name__ == "__main__":
    init_db()  # ← Создаём таблицу при старте
    print("🤖 Бот запущен...")
    bot.infinity_polling()