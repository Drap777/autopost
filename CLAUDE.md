# AutoPost - Контекст проекта

## Что это
Софт для автоматического постинга в социальные сети (Telegram, Instagram, TikTok) с генерацией контента через OpenAI.

## Владелец
Проекты: RouteOfRest, NBot (АвтоМонейБот)

## Текущий статус
- [x] Структура проекта создана
- [x] Модуль Google Sheets написан
- [x] Модуль генерации контента (OpenAI) написан
- [x] Модуль постинга в Telegram написан
- [x] Telegram бот настроен и протестирован
- [x] Instagram модуль написан (Selenium)
- [ ] OpenAI API ключ - НЕ ПОДКЛЮЧЕН
- [ ] Google Sheets - НЕ НАСТРОЕН
- [ ] Instagram - НЕ НАСТРОЕН (нужен логин/пароль)
- [ ] TikTok модуль - НЕ НАПИСАН

## Настройки (.env)
- TELEGRAM_BOT_TOKEN: настроен (@soc_ap_bot)
- TELEGRAM_CHANNEL_ID: @green_candles_gang
- OPENAI_API_KEY: пусто (нужно добавить)
- GOOGLE_SHEETS_ID: пусто (нужно настроить)
- INSTAGRAM_USERNAME: пусто (нужно добавить)
- INSTAGRAM_PASSWORD: пусто (нужно добавить)

## Как запускать
```bash
cd /home/dev/autopost
source venv/bin/activate
python main.py --test

# Одиночный пост в Instagram
python main.py --single --topic "тема" --platform ig --test
```

## Следующие шаги
1. Получить и добавить OpenAI API ключ
2. Настроить Google Sheets для управления постами
3. Добавить Instagram логин/пароль для подключения
4. Написать TikTok модуль
5. Протестировать полный цикл генерации и постинга
