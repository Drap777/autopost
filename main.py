#!/usr/bin/env python3
"""
AutoPost - Автоматический постинг в социальные сети.

Читает задания из Google Sheets, генерирует контент через OpenAI,
и публикует в указанные платформы.

Использование:
    python main.py              # Обработать все pending задания
    python main.py --test       # Тестовый режим (без публикации)
    python main.py --schedule   # Запуск по расписанию (каждые 5 минут)
"""

import argparse
import os
import sys
from datetime import datetime

# Добавляем корневую директорию в путь
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)

from services.sheets import SheetsService
from services.generator import ContentGenerator
from services.publishers.telegram import TelegramPublisher
from services.publishers.instagram import InstagramPublisher


class AutoPost:
    """Главный класс приложения."""

    def __init__(self):
        self.sheets = SheetsService()
        self.generator = ContentGenerator()
        self.telegram = TelegramPublisher()
        self.instagram = InstagramPublisher()

    def connect_all(self) -> bool:
        """Подключение ко всем сервисам."""
        print("\n=== Подключение к сервисам ===\n")

        # Google Sheets
        if not self.sheets.connect():
            print("[!] Google Sheets недоступен, продолжаем без него")

        # OpenAI
        if not self.generator.connect():
            print("[!] OpenAI недоступен")
            return False

        # Telegram
        if not self.telegram.connect():
            print("[!] Telegram недоступен")
            return False

        # Instagram (опционально - если настроен)
        if not self.instagram.connect():
            print("[!] Instagram недоступен, продолжаем без него")

        print("\n=== Все сервисы подключены ===\n")
        return True

    def process_task(self, task: dict, test_mode: bool = False) -> bool:
        """
        Обработка одного задания.

        Args:
            task: Задание из Google Sheets
            test_mode: Если True, не публикуем и не обновляем статус
        """
        project = task['project']
        topic = task['topic']
        platforms = task['platforms']
        row_number = task.get('row_number')

        print(f"\n--- Обработка задания ---")
        print(f"Проект: {project}")
        print(f"Тема: {topic}")
        print(f"Платформы: {', '.join(platforms)}")

        # Генерируем контент
        for platform in platforms:
            platform = platform.strip().lower()

            if platform == 'tg':
                content = self.generator.generate_content(project, topic, 'tg')

                if test_mode:
                    print(f"\n[ТЕСТ] Текст ({len(content['text'])} символов):")
                    print(content['text'][:300] + "..." if len(content['text']) > 300 else content['text'])
                    print(f"[ТЕСТ] Изображение: {content['image_path']}")
                else:
                    # Публикуем в Telegram
                    result = self.telegram.publish(
                        text=content['text'],
                        image_path=content['image_path']
                    )

                    if result['success'] and row_number:
                        self.sheets.update_status(row_number, 'done', result['post_id'])
                    elif row_number:
                        self.sheets.update_status(row_number, 'error')

            elif platform == 'ig':
                content = self.generator.generate_content(project, topic, 'ig')

                if test_mode:
                    print(f"\n[ТЕСТ] Текст для Instagram ({len(content['text'])} символов):")
                    print(content['text'][:300] + "..." if len(content['text']) > 300 else content['text'])
                    print(f"[ТЕСТ] Изображение: {content['image_path']}")
                else:
                    if not self.instagram.logged_in:
                        print("[ОШИБКА] Instagram не подключен, пропускаем")
                        continue

                    # Публикуем в Instagram
                    result = self.instagram.publish(
                        text=content['text'],
                        image_path=content['image_path']
                    )

                    if result['success'] and row_number:
                        self.sheets.update_status(row_number, 'done', result['post_id'])
                    elif row_number:
                        self.sheets.update_status(row_number, 'error')

            # TODO: Добавить обработку 'tt' (TikTok) в следующих фазах

        return True

    def run(self, test_mode: bool = False):
        """Запуск обработки всех pending заданий."""
        print("\n" + "=" * 50)
        print("   AutoPost - Автоматический постинг")
        print("=" * 50)
        print(f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        if test_mode:
            print("Режим: ТЕСТОВЫЙ (без публикации)")

        if not self.connect_all():
            print("\n[ОШИБКА] Не удалось подключиться к сервисам")
            return

        # Получаем задания из таблицы
        tasks = self.sheets.get_pending_tasks()

        if not tasks:
            print("\n[INFO] Нет заданий для обработки")
            return

        # Обрабатываем каждое задание
        for task in tasks:
            self.process_task(task, test_mode)

        # Закрываем браузер Instagram
        self.instagram.disconnect()

        print("\n" + "=" * 50)
        print("   Обработка завершена")
        print("=" * 50 + "\n")

    def run_single(self, project: str, topic: str, platform: str = 'tg', test_mode: bool = False):
        """
        Запуск для одного поста без Google Sheets.
        Удобно для быстрого тестирования.
        """
        print("\n" + "=" * 50)
        print("   AutoPost - Одиночный пост")
        print("=" * 50)

        if not self.generator.connect():
            return

        # Подключаем нужную платформу
        if not test_mode:
            if platform == 'tg' and not self.telegram.connect():
                return
            elif platform == 'ig' and not self.instagram.connect():
                return

        task = {
            'project': project,
            'topic': topic,
            'platforms': [platform],
        }

        self.process_task(task, test_mode)

        # Закрываем браузер Instagram если использовался
        if platform == 'ig':
            self.instagram.disconnect()


def main():
    parser = argparse.ArgumentParser(description='AutoPost - Автоматический постинг')
    parser.add_argument('--test', action='store_true', help='Тестовый режим (без публикации)')
    parser.add_argument('--single', action='store_true', help='Одиночный пост')
    parser.add_argument('--project', type=str, default='RouteOfRest', help='Проект для --single')
    parser.add_argument('--topic', type=str, help='Тема для --single')
    parser.add_argument('--platform', type=str, default='tg', choices=['tg', 'ig', 'tt'],
                        help='Платформа для --single: tg (Telegram), ig (Instagram), tt (TikTok)')

    args = parser.parse_args()

    app = AutoPost()

    if args.single:
        if not args.topic:
            print("[ОШИБКА] Укажите --topic для режима --single")
            return
        app.run_single(args.project, args.topic, platform=args.platform, test_mode=args.test)
    else:
        app.run(test_mode=args.test)


if __name__ == "__main__":
    main()
