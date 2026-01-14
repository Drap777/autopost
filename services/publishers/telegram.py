"""
Модуль для публикации постов в Telegram.
Использует python-telegram-bot для отправки сообщений в каналы/группы.
"""

import asyncio
import os
import sys
from telegram import Bot
from telegram.constants import ParseMode

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID


class TelegramPublisher:
    """Публикатор постов в Telegram."""

    def __init__(self, channel_id: str = None):
        """
        Args:
            channel_id: ID канала/группы. Если не указан, берётся из настроек.
        """
        self.bot = None
        self.channel_id = channel_id or TELEGRAM_CHANNEL_ID

    def connect(self) -> bool:
        """Инициализация бота."""
        try:
            if not TELEGRAM_BOT_TOKEN:
                print("[ОШИБКА] TELEGRAM_BOT_TOKEN не задан в .env")
                return False

            self.bot = Bot(token=TELEGRAM_BOT_TOKEN)
            print("[OK] Telegram бот инициализирован")
            return True
        except Exception as e:
            print(f"[ОШИБКА] Не удалось инициализировать бота: {e}")
            return False

    async def _send_photo_async(self, image_path: str, caption: str) -> str:
        """Асинхронная отправка фото с подписью."""
        with open(image_path, 'rb') as photo:
            message = await self.bot.send_photo(
                chat_id=self.channel_id,
                photo=photo,
                caption=caption,
                parse_mode=ParseMode.HTML,
            )
        return str(message.message_id)

    async def _send_text_async(self, text: str) -> str:
        """Асинхронная отправка текстового сообщения."""
        message = await self.bot.send_message(
            chat_id=self.channel_id,
            text=text,
            parse_mode=ParseMode.HTML,
        )
        return str(message.message_id)

    def publish(self, text: str, image_path: str = None) -> dict:
        """
        Публикация поста в Telegram.

        Args:
            text: Текст поста
            image_path: Путь к изображению (опционально)

        Returns:
            {'success': bool, 'post_id': str, 'error': str}
        """
        if not self.bot:
            return {'success': False, 'post_id': '', 'error': 'Бот не инициализирован'}

        try:
            # Telegram ограничение: подпись к фото - 1024 символа
            if image_path and os.path.exists(image_path):
                # Если текст слишком длинный для подписи
                if len(text) > 1024:
                    # Отправляем фото с коротким текстом
                    short_caption = text[:1000] + "..."
                    post_id = asyncio.run(self._send_photo_async(image_path, short_caption))

                    # Затем отправляем полный текст отдельным сообщением
                    asyncio.run(self._send_text_async(text))
                else:
                    post_id = asyncio.run(self._send_photo_async(image_path, text))
            else:
                post_id = asyncio.run(self._send_text_async(text))

            print(f"[OK] Опубликовано в Telegram, ID: {post_id}")
            return {'success': True, 'post_id': post_id, 'error': ''}

        except Exception as e:
            error_msg = str(e)
            print(f"[ОШИБКА] Не удалось опубликовать в Telegram: {error_msg}")
            return {'success': False, 'post_id': '', 'error': error_msg}

    def set_channel(self, channel_id: str):
        """Сменить канал для публикации."""
        self.channel_id = channel_id
        print(f"[OK] Канал изменён на: {channel_id}")


# Для тестирования модуля напрямую
if __name__ == "__main__":
    publisher = TelegramPublisher()
    if publisher.connect():
        result = publisher.publish(
            text="Тестовый пост от AutoPost 🚀\n\nЭто автоматическое сообщение.",
            image_path=None
        )
        print(f"Результат: {result}")
