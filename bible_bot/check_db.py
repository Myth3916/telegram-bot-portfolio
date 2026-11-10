import sqlite3

conn = sqlite3.connect('bible.db')
cursor = conn.cursor()

# Проверяем, есть ли данные
cursor.execute('SELECT COUNT(*) FROM verses')
count = cursor.fetchone()[0]
print(f"Всего стихов в базе: {count}")

# Смотрим первые 5 записей
cursor.execute('SELECT book, book_order, chapter FROM verses LIMIT 5')
rows = cursor.fetchall()
print("\nПервые 5 записей:")
for row in rows:
    print(f"  Книга: '{row[0]}', Порядок: {row[1]}, Глава: {row[2]}")

# Проверяем DISTINCT
cursor.execute('SELECT DISTINCT book, book_order FROM verses ORDER BY book_order LIMIT 5')
books = cursor.fetchall()
print("\nПервые 5 уникальных книг:")
for book in books:
    print(f"  '{book[0]}' (порядок: {book[1]})")

conn.close()