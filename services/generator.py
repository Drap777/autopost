"""
Модуль для генерации контента через OpenAI.
Генерирует текст (GPT) и изображения (DALL-E).
"""

import openai
import requests
import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import OPENAI_API_KEY


class ContentGenerator:
    """Генератор контента через OpenAI API."""

    # Промпты для разных проектов
    PROJECT_PROMPTS = {
        'RouteOfRest': {
            'style': 'туристический блог, вдохновляющий на путешествия',
            'tone': 'дружелюбный, информативный, с эмодзи',
            'hashtags': '#путешествия #отдых #travel #RouteOfRest',
        },
        'NBot': {
            'style': 'финансовый/технический блог о заработке',
            'tone': 'экспертный, мотивирующий, с конкретными примерами',
            'hashtags': '#заработок #боты #пассивныйдоход #NBot',
        },
    }

    def __init__(self):
        self.client = None
        self.temp_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'temp'
        )

    def connect(self) -> bool:
        """Инициализация клиента OpenAI."""
        try:
            if not OPENAI_API_KEY:
                print("[ОШИБКА] OPENAI_API_KEY не задан в .env")
                return False

            self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
            print("[OK] OpenAI клиент инициализирован")
            return True
        except Exception as e:
            print(f"[ОШИБКА] Не удалось подключиться к OpenAI: {e}")
            return False

    def generate_text(self, project: str, topic: str, platform: str = 'tg') -> str:
        """
        Генерация текста поста.

        Args:
            project: Название проекта (RouteOfRest, NBot)
            topic: Тема поста
            platform: Платформа (tg, ig, tt)

        Returns:
            Готовый текст поста
        """
        if not self.client:
            print("[ОШИБКА] Сначала вызовите connect()")
            return ""

        # Получаем настройки проекта
        project_config = self.PROJECT_PROMPTS.get(project, {
            'style': 'информационный блог',
            'tone': 'нейтральный',
            'hashtags': '',
        })

        # Ограничения по платформам
        length_limits = {
            'tg': '1500-2000 символов',
            'ig': '1800-2200 символов',
            'tt': '150-300 символов (короткое описание для видео)',
        }

        prompt = f"""Напиши пост для социальной сети на тему: "{topic}"

Проект: {project}
Стиль: {project_config['style']}
Тон: {project_config['tone']}
Длина: {length_limits.get(platform, '1500 символов')}

Требования:
- Пост должен быть на русском языке
- Начни с цепляющего заголовка или вопроса
- Добавь полезную информацию по теме
- Используй абзацы для читаемости
- В конце добавь призыв к действию
- Добавь релевантные хэштеги: {project_config['hashtags']}

Напиши только текст поста, без пояснений."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Ты - опытный SMM-специалист. Пишешь вовлекающие посты для социальных сетей."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7,
            )

            text = response.choices[0].message.content.strip()
            print(f"[OK] Текст сгенерирован ({len(text)} символов)")
            return text

        except Exception as e:
            print(f"[ОШИБКА] Не удалось сгенерировать текст: {e}")
            return ""

    def generate_image(self, project: str, topic: str) -> str:
        """
        Генерация изображения через DALL-E.

        Args:
            project: Название проекта
            topic: Тема для изображения

        Returns:
            Путь к сохранённому изображению
        """
        if not self.client:
            print("[ОШИБКА] Сначала вызовите connect()")
            return ""

        # Стили изображений для проектов
        image_styles = {
            'RouteOfRest': 'красивое фото природы, путешествия, яркие цвета, профессиональная фотография',
            'NBot': 'современный минималистичный дизайн, технологии, финансы, синие и зелёные тона',
        }

        style = image_styles.get(project, 'профессиональный стиль')

        prompt = f"{topic}. Стиль: {style}. Без текста на изображении."

        try:
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )

            image_url = response.data[0].url

            # Скачиваем изображение
            image_response = requests.get(image_url)
            if image_response.status_code == 200:
                # Создаём уникальное имя файла
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{project}_{timestamp}.png"
                filepath = os.path.join(self.temp_dir, filename)

                with open(filepath, 'wb') as f:
                    f.write(image_response.content)

                print(f"[OK] Изображение сохранено: {filepath}")
                return filepath

            print("[ОШИБКА] Не удалось скачать изображение")
            return ""

        except Exception as e:
            print(f"[ОШИБКА] Не удалось сгенерировать изображение: {e}")
            return ""

    def generate_content(self, project: str, topic: str, platform: str = 'tg') -> dict:
        """
        Полная генерация контента: текст + изображение.

        Returns:
            {'text': str, 'image_path': str}
        """
        print(f"\n[ГЕНЕРАЦИЯ] Проект: {project}, Тема: {topic}")

        text = self.generate_text(project, topic, platform)
        image_path = self.generate_image(project, topic)

        return {
            'text': text,
            'image_path': image_path,
        }


# Для тестирования модуля напрямую
if __name__ == "__main__":
    generator = ContentGenerator()
    if generator.connect():
        content = generator.generate_content(
            project="RouteOfRest",
            topic="Топ-5 мест для отдыха в Турции",
            platform="tg"
        )
        print("\n--- РЕЗУЛЬТАТ ---")
        print(f"Текст:\n{content['text'][:200]}...")
        print(f"\nИзображение: {content['image_path']}")
