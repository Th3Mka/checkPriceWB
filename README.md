🐍 CheckPriceWB

📋 Функциональные возможности
🔍 Проверка цен товаров:
Пользователь может запросить информацию о товаре и получить его название, бренд, цену и ссылку на Wildberries.
💬 Отправка отзывов:
Пользователи могут оставить отзыв, который сохраняется в базе данных.
🔖 Интерактивное меню:
Бот предоставляет удобные кнопки для навигации по функциональности (помощь, настройки, ответы на вопросы и т. д.).
📊 Сохранение данных пользователей:
Имя и возраст пользователя сохраняются в базе данных при регистрации.


⚙️ Технологии
Python 3.10+
Aiogram 3 — фреймворк для создания Telegram-ботов
SQLite — база данных для хранения отзывов и пользовательских данных
SQLAlchemy — ORM для работы с базой данных
Environs — для безопасной загрузки конфигураций через .env файл

🛠️ Структура проекта

telegramPriceBotWB/
├── handlers/
│ ├── callbacks.py
│ ├── commands.py
│ └── user_handler.py
├── keyboard/
│ └── main_menu.py
├── config_data/
│ └── config.py
├── lexicon/
│ └── lexicon_ru.py
├── database/
│ └── database.py
├── requirements.txt
├── main.py
└── README.md

## Установка

🚀 Как запустить проект
1. Клонируйте репозиторий

git clone https://github.com/Th3Mka/checkPriceWB.git
cd checkPriceWB
2. Создайте виртуальное окружение и установите зависимости

python -m venv venv
source venv/bin/activate  # Для Linux/Mac
venv\Scripts\activate     # Для Windows

pip install -r requirements.txt
3. Настройте переменные окружения
Создайте файл .env в корне проекта и добавьте туда ваш Telegram токен и ID администраторов:


BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
ADMIN_IDS=123456789,987654321
BOT_TOKEN — токен вашего бота, полученный через BotFather.
ADMIN_IDS — ID администраторов (список через запятую).
4. Запустите базу данных
Проект использует SQLite. Таблицы создаются автоматически при первом запуске.

5. Запустите бота

python main.py

📦 Установка зависимостей
Все необходимые библиотеки перечислены в requirements.txt:

pip install -r requirements.txt

✅ Примеры команд бота
/start — начало работы с ботом
/help — информация о функционале
/check_price — проверка цены товара
/feedback — отправка отзыва
/settings — настройки бота
