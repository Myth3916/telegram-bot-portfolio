import telebot
import sqlite3
import re

# ВСТАВЬ СЮДА СВОЙ ТОКЕН ОТ @BotFather
BOT_TOKEN = '8210368809:AAErNbEfeHyE9B0DWB8ylLNgaiNIGDNEbP4'

bot = telebot.TeleBot(BOT_TOKEN)

# Словарь для хранения прогресса чтения каждого пользователя
# Формат: {chat_id: {"book": "Бытие", "chapter": 1}}
user_progress = {}

def get_db_connection():
    conn = sqlite3.connect('bible.db')
    conn.row_factory = sqlite3.Row
    return conn

def send_long_message(chat_id, text):
    """Функция для отправки длинных текстов, разбивая их на части до 4000 символов"""
    max_len = 4000
    if len(text) <= max_len:
        bot.send_message(chat_id, text, parse_mode='Markdown')
    else:
        chunks = [text[i:i + max_len] for i in range(0, len(text), max_len)]
        for i, chunk in enumerate(chunks):
            # Добавляем номер части, если их несколько
            prefix = f"(Часть {i+1}/{len(chunks)})\n" if len(chunks) > 1 else ""
            bot.send_message(chat_id, prefix + chunk, parse_mode='Markdown')

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "👋 Привет! Я Библейский Бот.\n\n"
        "📖 **Чтение:** `/read Бытие 1` (или просто `/read`, чтобы продолжить)\n"
        "⏭ **Продолжить:** `/next` (прочитает следующую главу)\n"
        "🔍 **Поиск:** `/search свет` (найдет стихи со словом 'свет')\n\n"
        "Напиши команду или просто слово для поиска!"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode='Markdown')

@bot.message_handler(commands=['read'])
def read_chapter(message):
    chat_id = message.chat.id
    parts = message.text.split()

    # Если пользователь написал просто /read, пытаемся продолжить чтение
    if len(parts) == 1:
        if chat_id in user_progress:
            book_name = user_progress[chat_id]['book']
            chapter_num = user_progress[chat_id]['chapter']
        else:
            bot.send_message(chat_id, "⚠️ Укажи книгу и главу. Пример: `/read Бытие 1`", parse_mode='Markdown')
            return
    else:
        # Пользователь указал книгу и главу: /read Бытие 1
        if len(parts) < 3:
            bot.send_message(chat_id, "⚠️ Формат: `/read <Книга> <Глава>`\nПример: `/read Бытие 1`", parse_mode='Markdown')
            return
        
        book_name = parts[1]
        try:
            chapter_num = int(parts[2])
        except ValueError:
            bot.send_message(chat_id, "⚠️ Номер главы должен быть числом!")
            return
        
        # Сохраняем прогресс
        user_progress[chat_id] = {'book': book_name, 'chapter': chapter_num}

    conn = get_db_connection()
    cursor = conn.cursor()

    # Ищем книгу по частичному совпадению (например, "Бытие" найдет "Первая книга Моисеева. БЫТИЕ")
    query = '''
        SELECT book, chapter, verse_num, text FROM verses 
        WHERE book LIKE ? AND chapter = ? 
        ORDER BY verse_num ASC
    '''
    cursor.execute(query, (f'%{book_name}%', chapter_num))
    verses = cursor.fetchall()
    conn.close()

    if not verses:
        bot.send_message(chat_id, f"❌ Не найдено: '{book_name}', глава {chapter_num}. Проверь название (например, 'Иоанна' вместо 'Иоанн').")
        return

    # Формируем текст для отправки
    real_book_name = verses[0]['book']
    full_text = f"📖 *{real_book_name}, Глава {chapter_num}*\n\n"
    
    for v in verses:
        full_text += f"*{v['verse_num']}.* {v['text']}\n"

    send_long_message(chat_id, full_text)

@bot.message_handler(commands=['next'])
def next_chapter(message):
    chat_id = message.chat.id
    
    if chat_id not in user_progress:
        bot.send_message(chat_id, "⚠️ Ты еще ничего не читал. Начни с команды: `/read Бытие 1`", parse_mode='Markdown')
        return

    current_book = user_progress[chat_id]['book']
    current_chapter = user_progress[chat_id]['chapter']
    next_chapter_num = current_chapter + 1

    # Просто меняем номер главы в прогрессе и вызываем логику чтения
    # (Если следующей главы нет, бот напишет "Не найдено", и пользователь поймет, что нужно сменить книгу)
    user_progress[chat_id]['chapter'] = next_chapter_num
    
    # Имитируем команду /read
    message.text = f"/read {current_book} {next_chapter_num}"
    read_chapter(message)

@bot.message_handler(commands=['search'])
def search_verses(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(message.chat.id, "⚠️ Формат: `/search <слово>`\nПример: `/search любовь`", parse_mode='Markdown')
        return

    search_word = parts[1]
    
    conn = get_db_connection()
    cursor = conn.cursor()

    # Ищем слово в тексте. LIMIT 10, чтобы не спамить
    query = '''
        SELECT book, chapter, verse_num, text FROM verses 
        WHERE text LIKE ? 
        LIMIT 10
    '''
    cursor.execute(query, (f'%{search_word}%',))
    results = cursor.fetchall()
    conn.close()

    if not results:
        bot.send_message(message.chat.id, f"🔍 По запросу '{search_word}' ничего не найдено. Попробуй другое слово или его часть.")
        return

    response = f"🔍 Найдено по запросу '{search_word}' (первые 10):\n\n"
    for r in results:
        text_preview = r['text'][:150] + "..." if len(r['text']) > 150 else r['text']
        response += f"📜 *{r['book']} {r['chapter']}:{r['verse_num']}*\n{text_preview}\n\n"

    send_long_message(message.chat.id, response)

print("🤖 Бот запущен и готов к работе!")
bot.polling(none_stop=True)