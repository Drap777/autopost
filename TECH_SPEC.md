# AutoPost - Техническое задание

## Цель
Автоматическая генерация и публикация контента в социальные сети на основе данных из Google Sheets.

## Платформы
- Telegram (каналы/группы)
- Instagram (посты, stories)
- TikTok (видео из изображений)

## Проекты для постинга
- RouteOfRest
- NBot (АвтоМонейБот)

---

## Архитектура (минимализм)

```
Google Sheets (темы/расписание)
        ↓
   Python скрипт
        ↓
   ┌────┴────┐
   ↓         ↓
OpenAI    DALL-E/Midjourney API
(текст)   (изображения)
   └────┬────┘
        ↓
   Постинг API
   ├── Telegram Bot API
   ├── Instagram Graph API
   └── TikTok API
```

---

## Структура проекта

```
autopost/
├── config/
│   └── settings.py          # API ключи, настройки
├── services/
│   ├── sheets.py            # Работа с Google Sheets
│   ├── generator.py         # Генерация текста (OpenAI)
│   ├── images.py            # Генерация изображений
│   └── publishers/
│       ├── telegram.py
│       ├── instagram.py
│       └── tiktok.py
├── scheduler.py             # Планировщик постов
├── main.py                  # Точка входа
└── requirements.txt
```

---

## Google Sheets структура

| Проект | Тема | Платформы | Дата/Время | Статус | Post ID |
|--------|------|-----------|------------|--------|---------|
| RouteOfRest | Лучшие пляжи Турции | tg,ig | 2024-01-15 10:00 | pending | - |
| NBot | Пассивный доход с ботами | tg,ig,tt | 2024-01-15 14:00 | done | 123 |

---

## Минимальный набор зависимостей

```
openai              # Генерация текста и изображений (DALL-E)
google-api-python-client  # Google Sheets
python-telegram-bot # Telegram
instagrapi          # Instagram (неофициальный, но рабочий)
schedule            # Планировщик
python-dotenv       # Переменные окружения
```

---

## Этапы реализации

### Фаза 1 - Базовый функционал
1. Подключение к Google Sheets (чтение тем)
2. Генерация текста через OpenAI
3. Генерация изображений через DALL-E
4. Постинг в Telegram

### Фаза 2 - Расширение
5. Постинг в Instagram
6. Планировщик по расписанию

### Фаза 3 - TikTok
7. Создание видео из изображений
8. Постинг в TikTok

---

## API которые понадобятся

| Сервис | Что нужно | Где получить |
|--------|-----------|--------------|
| OpenAI | API Key | platform.openai.com |
| Google Sheets | Service Account JSON | console.cloud.google.com |
| Telegram | Bot Token | @BotFather |
| Instagram | Login/Password | Аккаунт Instagram |
| TikTok | Session ID | Developer портал |

---

## Принцип работы

1. Скрипт читает Google Sheets
2. Находит строки со статусом "pending" и подходящим временем
3. Генерирует текст по теме через OpenAI
4. Генерирует изображение через DALL-E
5. Публикует в указанные платформы
6. Обновляет статус в таблице на "done"

---

## Запуск

Два варианта:
- **Cron/Scheduler** - запуск каждые 5-15 минут, проверка расписания
- **Демон** - постоянно работающий процесс с внутренним планировщиком
