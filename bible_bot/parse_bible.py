import xml.etree.ElementTree as ET

NS = '{http://www.gribuser.ru/xml/fictionbook/2.0}'

# Загружаем fb2 файл
tree = ET.parse('bible.fb2')
root = tree.getroot()

# Находим body
body = root.find(f'{NS}body')
if body is None:
    print("Тег body не найден!")
    exit()

print("Что находится внутри <body>:")
print(f"Всего дочерних элементов: {len(body)}")
print()

# Смотрим первые 10 элементов верхнего уровня в body
for i, child in enumerate(body[:10]):
    print(f"Элемент {i}: <{child.tag}>")
    
    # Если это title, показываем текст заголовка
    if 'title' in child.tag:
        title_text = ''.join(child.itertext()).strip()
        print(f"   Текст заголовка: {title_text[:100]}")
    
    # Если это section, показываем её содержимое
    elif 'section' in child.tag:
        print(f"   Внутри section: {len(child)} элементов")
        for sub in child[:3]:
            print(f"      - <{sub.tag}>")
    
    # Показываем первые параграфы, если есть
    paragraphs = child.findall(f'{NS}p')
    if not paragraphs:
        paragraphs = child.findall(f'.//{NS}p')
    
    if paragraphs:
        print(f"   Параграфов: {len(paragraphs)}")
        for j, p in enumerate(paragraphs[:3]):
            text = ''.join(p.itertext()).strip()
            print(f"      Параграф {j+1}: {text[:150]}...")
    
    print()

print("="*60)
print("Первые 2000 символов всего текста в body:")
print("="*60)
full_text = ''.join(body.itertext())
print(full_text[:2000])