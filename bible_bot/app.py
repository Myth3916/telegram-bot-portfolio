from flask import Flask, render_template,request
import sqlite3

app = Flask(__name__)
DATABASE = 'bible.db'

# Словарь: как называть главы в разных книгах
CHAPTER_NAMES = {
    'Псалтирь': 'Псалом',
    'Книга Плач Иеремии': 'Плач',
    'Книга Песни песней Соломона': 'Песнь',
    'Книга Притчей Соломоновых': 'Притча',
}

def get_chapter_name(book_name):
    """Возвращает правильное название для глав книги"""
    return CHAPTER_NAMES.get(book_name, 'Глава')

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT DISTINCT book, book_order FROM verses ORDER BY book_order')
    rows = cursor.fetchall()
    
    books = [{'name': row['book'], 'order': row['book_order']} for row in rows]
    
    # Разделяем на Ветхий и Новый Завет (книги 1-49 — ВЗ, 50+ — НЗ)
    old_testament = [b for b in books if b['order'] <= 48]
    new_testament = [b for b in books if b['order'] >= 49]
    
    conn.close()
    return render_template('index.html', 
                         old_testament=old_testament, 
                         new_testament=new_testament)

@app.route('/book/<int:book_order>')
def book_page(book_order):
    """Страница отдельной книги — показывает список глав"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Получаем название книги по её номеру
    cursor.execute('SELECT DISTINCT book FROM verses WHERE book_order = ?', (book_order,))
    book_row = cursor.fetchone()
    
    if not book_row:
        conn.close()
        return 'Книга не найдена', 404
    
    book_name = book_row['book']
    
    # Получаем список глав и количество стихов в каждой
    cursor.execute('''
        SELECT chapter, COUNT(*) as verse_count 
        FROM verses 
        WHERE book_order = ? 
        GROUP BY chapter 
        ORDER BY chapter
    ''', (book_order,))
    chapters = cursor.fetchall()
    
    conn.close()
    
    return render_template('book.html', 
                         book_name=book_name, 
                         book_order=book_order,
                         chapter_name=get_chapter_name(book_name),
                         chapters=chapters)

@app.route('/book/<int:book_order>/chapter/<int:chapter_num>')
def chapter_page(book_order, chapter_num):
    """Страница чтения главы — показывает все стихи"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Получаем название книги
    cursor.execute('SELECT DISTINCT book FROM verses WHERE book_order = ?', (book_order,))
    book_row = cursor.fetchone()
    
    if not book_row:
        conn.close()
        return 'Книга не найдена', 404
    
    book_name = book_row['book']
    
    # Получаем все стихи главы
    cursor.execute('''
        SELECT verse_num, text 
        FROM verses 
        WHERE book_order = ? AND chapter = ? 
        ORDER BY verse_num
    ''', (book_order, chapter_num))
    verses = cursor.fetchall()
    
    if not verses:
        conn.close()
        return 'Глава не найдена', 404
    
    # Проверяем, есть ли следующая глава (для кнопки навигации)
    cursor.execute('''
        SELECT DISTINCT chapter 
        FROM verses 
        WHERE book_order = ? AND chapter > ? 
        ORDER BY chapter 
        LIMIT 1
    ''', (book_order, chapter_num))
    next_chapter = cursor.fetchone()
    
    # Проверяем, есть ли предыдущая глава
    cursor.execute('''
        SELECT DISTINCT chapter 
        FROM verses 
        WHERE book_order = ? AND chapter < ? 
        ORDER BY chapter DESC 
        LIMIT 1
    ''', (book_order, chapter_num))
    prev_chapter = cursor.fetchone()
    
    conn.close()
    
    return render_template('chapter.html',
                         book_name=book_name,
                         book_order=book_order,
                         chapter_name=get_chapter_name(book_name),
                         chapter_num=chapter_num,
                         verses=verses,
                         next_chapter=next_chapter['chapter'] if next_chapter else None,
                         prev_chapter=prev_chapter['chapter'] if prev_chapter else None)

@app.route('/search')
def search():
    """Страница поиска по тексту Библии"""
    query = request.args.get('q', '').strip()
    
    if not query:
        return render_template('search.html', query='', results=[])
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Разбиваем запрос на отдельные слова
    words = query.split()
    
    # Строим SQL-запрос с условием LIKE для каждого слова
    # Например: WHERE text LIKE '%Бог%' AND text LIKE '%свет%'
    conditions = []
    params = []
    for word in words:
        conditions.append("text LIKE ?")
        params.append(f'%{word}%')
    
    where_clause = " AND ".join(conditions)
    
    # Ищем стихи, содержащие ВСЕ слова
    sql = f'''
        SELECT book, book_order, chapter, verse_num, text 
        FROM verses 
        WHERE {where_clause}
        ORDER BY book_order, chapter, verse_num
        LIMIT 50
    '''
    
    cursor.execute(sql, params)
    results = cursor.fetchall()
    conn.close()
    
    return render_template('search.html', 
                         query=query, 
                         results=results,
                         chapter_names=CHAPTER_NAMES)  # ← передаём весь словарь


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)