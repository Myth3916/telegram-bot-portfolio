import pdfplumber

# Открываем PDF
with pdfplumber.open('bible.pdf') as pdf:
    print(f"Всего страниц: {len(pdf.pages)}")
    
    # Смотрим первые 3 страницы
    for i in range(min(3, len(pdf.pages))):
        page = pdf.pages[i]
        text = page.extract_text()
        
        print(f"\n{'='*50}")
        print(f"Страница {i + 1}")
        print(f"{'='*50}")
        print(text[:1500] if text else "(пустая страница)")