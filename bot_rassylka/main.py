# main.py — Бот с рассылкой (шаг 2: старт, БД, админка)
import os
import telebot
from telebot import types, apihelper
from dotenv import load_dotenv
import db  # Подключаем наш модуль базы данных
import time

# Загружаем переменные из .env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))  # Если не указан, будет 0

# === НАСТРОЙКА ПРОКСИ (как в визитке) ===
apihelper.proxy = {
    'https': 'socks5://127.0.0.1:12334',
    'http': 'socks5://127.0.0.1:12334'
}
# ========================================

bot = telebot.TeleBot(TOKEN)

# Инициализируем БД при запуске
db.init_db()

def is_admin(message):
    """Проверяет, является ли пользователь админом"""
    return message.from_user.id == ADMIN_ID

@bot.message_handler(commands=["start"])
def handle_start(message):
    # Сохраняем пользователя в БД
    db.add_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
    bot.reply_to(message, "👋 Привет! Ты успешно подписан на рассылку. Жди новости!")

@bot.message_handler(commands=["stats"])
def handle_stats(message):
    if not is_admin(message):
        bot.reply_to(message, "🔒 Доступ запрещён. Эта команда только для админа.")
        return
    
    total_users = db.get_stats()
    bot.reply_to(message, f"📊 Всего подписчиков в базе: {total_users}")


@bot.message_handler(commands=["send"])
def ask_for_broadcast(message):
    """Шаг 1: Админ запускает команду, бот просит текст"""
    if not is_admin(message):
        return
    
    msg = bot.send_message(message.chat.id, "✍️ Введи текст для рассылки:")
    # Регистрируем следующий шаг: ждем текст от этого же админа
    bot.register_next_step_handler(msg, process_broadcast)

def process_broadcast(message):
    """Шаг 2: Бот получает текст и начинает рассылать"""
    text = message.text
    
    # Получаем всех пользователей
    users = db.get_all_users()
    
    if not users:
        bot.send_message(message.chat.id, " В базе нет пользователей для рассылки.")
        return

    sent_count = 0
    failed_count = 0
    
    # Отправляем сообщение о начале
    bot.send_message(message.chat.id, f"📢 Начало рассылки на {len(users)} пользователей...")
    
    for user_id in users:
        try:
            bot.send_message(user_id, text)
            sent_count += 1
            time.sleep(0.05) # ⚠️ ВАЖНО: Задержка 0.05 сек, чтобы Telegram не забанил бота
        except Exception as e:
            failed_count += 1
            # В реальном проекте тут можно удалить юзера из базы, если он заблокировал бота
            
    # Финальный отчет
    report = f"✅ Рассылка завершена!\n\n" \
             f"📤 Доставлено: {sent_count}\n" \
             f"❌ Ошибок: {failed_count}"
    
    bot.send_message(message.chat.id, report)


if __name__ == "__main__":
    if ADMIN_ID == 0:
        print("️ Внимание: ADMIN_ID не указан в .env! Команда /stats не будет работать.")
    print("✅ Бот с рассылкой запущен...")
    bot.infinity_polling()