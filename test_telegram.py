#!/usr/bin/env python3
"""Быстрый тест отправки сообщения в Telegram."""

import asyncio
from telegram import Bot
from dotenv import load_dotenv
import os

load_dotenv()

async def test_send():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    channel = os.getenv("TELEGRAM_CHANNEL_ID")

    print(f"Токен: {token[:20]}...")
    print(f"Канал: {channel}")

    bot = Bot(token=token)

    message = await bot.send_message(
        chat_id=channel,
        text="Тестовое сообщение от AutoPost\n\nЕсли ты видишь это - бот работает!"
    )

    print(f"\n[OK] Сообщение отправлено! ID: {message.message_id}")

if __name__ == "__main__":
    asyncio.run(test_send())
