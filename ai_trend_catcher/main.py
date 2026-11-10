# Сначала нам нужно установить библиотеку в терминале:
# pip install feedparser

import feedparser

# Ссылка на RSS-ленту Hacker News (например, топ за день)
rss_url = "https://hnrss.org/frontpage"

# "Кормим" парсер ссылкой
feed = feedparser.parse(rss_url)

# Проходимся по первым 3 записям
print(f"Найдено новостей: {len(feed.entries)}\n")

for i in range(3):
    entry = feed.entries[i]
    print(f"Новость #{i+1}")
    print(f"Заголовок: {entry.title}")
    print(f"Ссылка: {entry.link}")
    print("-" * 40)