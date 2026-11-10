import xml.etree.ElementTree as ET
import re

NS = '{http://www.gribuser.ru/xml/fictionbook/2.0}'

def get_text(elem):
    """Собирает весь текст из элемента, включая вложенные теги"""
    return ''.join(elem.itertext()).strip()

# Загружаем файл
tree = ET.parse('bible.fb2')
root = tree.getroot()
body = root.find(f'{NS}body')

current_book = "Неизвестно"
current_chapter = 1
verses_found = 0

print("🔍 Тестируем парсинг первых 20 стихов:\n")

# Проходим по всем параграфам <p> в теле документа
for p in body.iter(f'{NS}p'):
    text = get_text(p)
    if not text:
        continue

    # 1. Проверяем, не является ли это названием книги
    # (ищем ключевые слова или текст полностью в верхнем регистре)
    if ("книга" in text.lower() or "благовествование" in text.lower() or 
        "послание" in text.lower() or (text.isupper() and len(text) < 50)):
        current_book = text
        print(f"\n📖 НАЧАЛО КНИГИ: {current_book}")
        continue

    # 2. Проверяем, не является ли это номером главы
    if text.lower().startswith("глава"):
        match = re.search(r'Глава\s+(\d+)', text, re.IGNORECASE)
        if match:
            current_chapter = int(match.group(1))
            print(f"  ➖➖➖ Глава {current_chapter} ➖➖➖")
        continue

    # 3. Проверяем, является ли это стихом
    # ^(\d+) - начинается с цифры
    # [\s\xa0]+ - затем пробел или неразрывный пробел (частая штука в FB2)
    # (.*) - остальной текст стиха
    verse_match = re.match(r'^(\d+)[\s\xa0]+(.*)', text)
    
    if verse_match:
        verse_num = int(verse_match.group(1))
        verse_text = verse_match.group(2).strip()
        
        # Выводим в удобном формате, обрезая длинный текст для читаемости
        print(f"[{current_book} {current_chapter}:{verse_num}] {verse_text[:70]}...")
        
        verses_found += 1
        if verses_found >= 20:
            print("\n✅ Тест завершён. Найдено 20 стихов.")
            break