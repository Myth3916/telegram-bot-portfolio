import xml.etree.ElementTree as ET
import re
import sqlite3

NS = '{http://www.gribuser.ru/xml/fictionbook/2.0}'

def get_text(elem):
    """Собирает весь текст из элемента, включая вложенные теги"""
    return ''.join(elem.itertext()).strip()

# 1. Подключаемся к базе данных (файл создастся автоматически)
conn = sqlite3.connect('bible.db')
cursor = conn.cursor()

# 2. Создаём таблицу для стихов
cursor.execute('''
    CREATE TABLE IF NOT EXISTS verses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book TEXT,
        chapter INTEGER,
        verse INTEGER,
        text TEXT
    )
''')

# Создаём индексы для быстрого поиска
cursor.execute('CREATE INDEX IF NOT EXISTS idx_book_chapter ON verses (book, chapter)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_text ON verses (text)')

# Очищаем таблицу перед новой записью (на случай повторного запуска)
cursor.execute('DELETE FROM verses')

# 3. Загружаем FB2 файл
print("Загрузка FB2 файла...")
tree = ET.parse('bible.fb2')
root = tree.getroot()
body = root.find(f'{NS}body')

current_book = "Неизвестно"
current_chapter = 0
batch = []
total_verses = 0

print("Начинаем парсинг и сохранение в базу данных...")

# 4. Проходим по всем параграфам
for p in body.iter(f'{NS}p'):
    text = get_text(p)
    if not text:
        continue

    # Определяем название книги по ключевым словам
    if any(keyword in text.lower() for keyword in ["книга", "благовествование", "послание", "откровение", "псалтирь", "плач иеремии", "песнь песней"]):
        current_book = text
        current_chapter = 0
        continue

    # Определяем номер главы
    if text.lower().startswith("глава"):
        match = re.search(r'Глава\s+(\d+)', text, re.IGNORECASE)
        if match:
            current_chapter = int(match.group(1))
        continue

    # Определяем стих
    verse_match = re.match(r'^(\d+)[\s\xa0]+(.*)', text)
    if verse_match and current_chapter > 0:
        verse_num = int(verse_match.group(1))
        verse_text = verse_match.group(2).strip()
        
        # Добавляем в пакет для массовой вставки
        batch.append((current_book, current_chapter, verse_num, verse_text))
        total_verses += 1

        # Сохраняем в базу каждые 1000 стихов (для экономии памяти и скорости)
        if len(batch) >= 1000:
            cursor.executemany('''
                INSERT INTO verses (book, chapter, verse, text) 
                VALUES (?, ?, ?, ?)
            ''', batch)
            conn.commit()
            print(f"  Сохранено стихов: {total_verses}")
            batch = []

# 5. Сохраняем оставшиеся стихи
if batch:
    cursor.executemany('''
        INSERT INTO verses (book, chapter, verse, text) 
        VALUES (?, ?, ?, ?)
    ''', batch)
    conn.commit()

print(f"\n✅ Готово! Всего сохранено стихов: {total_verses}")

# 6. Делаем тестовый запрос, чтобы проверить базу
print("\n🔍 Тестовый запрос из базы данных (Иоанна 3:16):")
cursor.execute('''
    SELECT book, chapter, verse, text FROM verses 
    WHERE book LIKE '%Иоанна%' AND chapter = 3 AND verse = 16
''')
result = cursor.fetchone()
if result:
    print(f"[{result[0]} {result[1]}:{result[2]}] {result[3]}")
else:
    print("Стих не найден (возможно, книга называется иначе, проверим позже).")

conn.close()