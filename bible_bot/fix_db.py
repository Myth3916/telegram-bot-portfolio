import sqlite3

conn = sqlite3.connect('bible.db')
cursor = conn.cursor()

# Словарь с правильными номерами для пропущенных книг
# (Канонический порядок Синодального перевода)
fixes = {
    '[Вторая книга Ездры]': 18,
    '[Книга Товита]': 19,
    '[Книга Иудифи]': 20,
    '[Книга Премудрости Соломона]': 21,
    '[Книга Премудрости Иисуса, сына Сирахова]': 22,
    '[Первая книга Маккавейская]': 23,
    '[Вторая книга Маккавейская]': 24,
    '[Третья книга Маккавейская]': 25,
    '[Послание Иеремии]': 34,
    '[Книга пророка Варуха]': 35,
}

print("🔧 Исправляем порядок книг в базе данных...\n")

for book_name, order in fixes.items():
    cursor.execute('''
        UPDATE verses 
        SET book_order = ? 
        WHERE book = ?
    ''', (order, book_name))
    
    # Проверяем, затронули ли мы строки
    if cursor.rowcount > 0:
        print(f"✅ Обновлено: '{book_name}' → порядок {order}")

conn.commit()

# Финальная проверка: остались ли книги с номером 999?
cursor.execute('SELECT DISTINCT book FROM verses WHERE book_order = 999')
remaining = cursor.fetchall()

print("\n" + "="*50)
if remaining:
    print("⚠️ Остались нераспознанные книги (порядок 999):")
    for r in remaining:
        print(f"  - {r[0]}")
else:
    print("🎉 Отлично! ВСЕ книги теперь имеют правильный канонический порядок!")
print("="*50)

conn.close()