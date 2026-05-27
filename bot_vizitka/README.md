

```markdown
# 🤖 Бот-визитка для разработчика

> Профессиональный шаблон телеграм-бота для презентации услуг разработчика.  
> Цена проекта: **1500₽** | Время разработки: ~2 часа
```
![Логотип](logo.png)

## ✨ Возможности

- 🎯 Приветственное сообщение с описанием услуг
- 🔗 Inline-кнопки с ссылками на соцсети (Telegram, GitHub)
- 📩 Кнопка обратной связи с автоответом
- 🖼️ Поддержка логотипа/аватарки в приветствии
- 🔐 Безопасное хранение токена через `.env`
- 🌐 Поддержка SOCKS5-прокси для работы в РФ

## 🚀 Быстрый запуск

### 1. Клонировать репозиторий
```bash
git clone https://github.com/Myth3916/bot_vizitka.git
cd bot_vizitka
```

### 2. Создать виртуальное окружение
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# или
venv\Scripts\activate  # Windows
```

### 3. Установить зависимости
```bash
pip install -r requirements.txt
```

### 4. Настроить токен
Создай файл `.env` и добавь туда свой токен:
```env
BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
```
*Получи токен у @BotFather в Telegram*

### 5. Запустить бота
```bash
python main.py
```

## ⚙️ Настройка прокси (для РФ)

Если провайдер блокирует Telegram API, добавь в `main.py`:

```python
from telebot import apihelper
apihelper.proxy = {
    'https': 'socks5://127.0.0.1:12334',
    'http': 'socks5://127.0.0.1:12334'
}
```

## 📁 Структура проекта

```
bot_vizitka/
├── main.py          # Основной код бота
├── logo.png         # Логотип для приветствия
├── .env             # Токен (не коммитить!)
├── .gitignore       # Исключения для Git
├── requirements.txt # Зависимости Python
└── README.md        # Этот файл
```

## 🛠️ Технологии

- Python 3.12+
- [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI)
- python-dotenv для управления конфигурацией

## 📄 Лицензия

MIT. Используйте в личных и коммерческих проектах.

---

> 💡 **Заказать такого бота**: [@ConversAIonist](https://t.me/ConversAIonist)  
> 👨‍💻 **Мой профиль**: [GitHub](https://github.com/Myth3916)
```
