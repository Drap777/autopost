# AutoPost

Автоматический постинг в социальные сети с генерацией контента через OpenAI.

## Возможности

- Генерация текста через GPT-4o-mini
- Генерация изображений через DALL-E 3
- Постинг в Telegram (готово)
- Постинг в Instagram (готово)
- Управление заданиями через Google Sheets (опционально)

## Быстрый старт

### 1. Установка зависимостей

```bash
cd /home/dev/autopost
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Настройка

Открой файл `.env` и заполни:

```env
# ОБЯЗАТЕЛЬНО
OPENAI_API_KEY=sk-твой-ключ-от-openai

# Для Telegram (уже настроено)
TELEGRAM_BOT_TOKEN=уже-заполнено
TELEGRAM_CHANNEL_ID=@green_candles_gang

# Для Instagram
INSTAGRAM_USERNAME=твой_логин
INSTAGRAM_PASSWORD=твой_пароль

# Для Google Sheets (опционально)
GOOGLE_SHEETS_ID=id-таблицы
```

#### Где взять OpenAI API ключ:
1. Зайди на https://platform.openai.com/
2. Зарегистрируйся / войди
3. Перейди в API Keys
4. Создай новый ключ
5. Пополни баланс (минимум $5)

### 3. Тестовый запуск

```bash
source venv/bin/activate

# Тест генерации (без реальной публикации)
python main.py --single --topic "Лучшие пляжи Турции" --platform tg --test
```

Если всё работает, увидишь сгенерированный текст и путь к картинке.

### 4. Реальная публикация

```bash
# Пост в Telegram
python main.py --single --topic "Лучшие пляжи Турции" --platform tg

# Пост в Instagram
python main.py --single --topic "Красивые закаты" --platform ig
```

## Команды

| Команда | Описание |
|---------|----------|
| `python main.py --test` | Обработать задания из Google Sheets (тест) |
| `python main.py` | Обработать задания из Google Sheets (боевой) |
| `python main.py --single --topic "тема" --platform tg` | Одиночный пост в Telegram |
| `python main.py --single --topic "тема" --platform ig` | Одиночный пост в Instagram |
| `python main.py --single --topic "тема" --platform tg --test` | Тест без публикации |

## Параметры

- `--test` - тестовый режим (генерирует контент, но не публикует)
- `--single` - режим одиночного поста (без Google Sheets)
- `--topic "тема"` - тема для генерации контента
- `--platform tg|ig` - платформа (tg = Telegram, ig = Instagram)
- `--project RouteOfRest|NBot` - проект (влияет на стиль контента)

## Проекты

Есть два предустановленных стиля:

**RouteOfRest** (по умолчанию):
- Туристический блог
- Дружелюбный тон с эмодзи
- Хэштеги: #путешествия #отдых #travel

**NBot**:
- Финансовый/технический блог
- Экспертный тон
- Хэштеги: #заработок #боты #пассивныйдоход

Пример:
```bash
python main.py --single --topic "Как начать инвестировать" --project NBot --platform tg
```

## Структура файлов

```
autopost/
├── main.py                 # Главный файл
├── .env                    # Настройки (ЗАПОЛНИ!)
├── .env.example            # Пример настроек
├── requirements.txt        # Зависимости Python
├── config/
│   └── settings.py         # Загрузка настроек
├── services/
│   ├── generator.py        # Генератор контента (OpenAI)
│   ├── sheets.py           # Google Sheets интеграция
│   └── publishers/
│       ├── telegram.py     # Публикация в Telegram
│       └── instagram.py    # Публикация в Instagram
└── temp/                   # Временные файлы (картинки)
```

## Возможные проблемы

### "OPENAI_API_KEY не задан"
Заполни ключ в файле `.env`

### "Недостаточно средств на балансе OpenAI"
Пополни баланс на https://platform.openai.com/account/billing

### Instagram не работает
- Проверь логин/пароль
- Возможно нужно подтвердить вход через приложение (2FA)
- Попробуй запустить с `headless=False` для отладки:
  ```python
  # В main.py измени:
  self.instagram = InstagramPublisher(headless=False)
  ```

### Telegram не отправляет
- Проверь что бот добавлен в канал как администратор
- Проверь TELEGRAM_CHANNEL_ID (должен начинаться с @ или быть числом)

## Google Sheets (опционально)

Если хочешь управлять постами через таблицу:

1. Создай Google Cloud проект
2. Включи Google Sheets API
3. Создай Service Account и скачай JSON ключ
4. Положи ключ в `config/google_credentials.json`
5. Заполни GOOGLE_SHEETS_ID в `.env`

Формат таблицы:
| Project | Topic | Platforms | DateTime | Status | PostID |
|---------|-------|-----------|----------|--------|--------|
| RouteOfRest | Пляжи Турции | tg,ig | 2024-01-15 10:00 | pending | |

## Контакты

По вопросам пиши владельцу проекта.
