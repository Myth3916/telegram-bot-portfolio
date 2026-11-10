import sqlite3

conn = sqlite3.connect('bible.db')
cursor = conn.cursor()

# Ищем книги с номером 999 (не попавшие в словарь)
cursor.execute("""
    SELECT DISTINCT book, book_order 
    FROM verses 
    WHERE book_order = 999 
    ORDER BY book
""")
rows = cursor.fetchall()

print("📚 Книги с book_order=999 (не распознанные):")
for row in rows:
    # Показываем название с видимыми спецсимволами
    name = row[0]
    print(f"\n  '{name}'")
    print(f"  Длина: {len(name)}")
    # Показываем каждый символ и его код, чтобы найти скрытые различия
    for i, ch in enumerate(name):
        if ord(ch) > 127 or ch == ' ':
            print(f"    [{i}] '{ch}' (Unicode: {ord(ch)})")

conn.close()