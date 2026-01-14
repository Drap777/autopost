"""
Модуль для работы с Google Sheets.
Читает задания на постинг и обновляет статусы.
"""

from google.oauth2 import service_account
from googleapiclient.discovery import build
from typing import Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import GOOGLE_SHEETS_ID, GOOGLE_CREDENTIALS_FILE


class SheetsService:
    """Сервис для работы с Google Sheets."""

    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    # Названия колонок в таблице
    COLUMNS = {
        'project': 0,      # A - Название проекта (RouteOfRest, NBot)
        'topic': 1,        # B - Тема поста
        'platforms': 2,    # C - Платформы (tg, ig, tt)
        'datetime': 3,     # D - Дата и время публикации
        'status': 4,       # E - Статус (pending, done, error)
        'post_id': 5,      # F - ID поста после публикации
    }

    def __init__(self):
        self.service = None
        self.sheet_id = GOOGLE_SHEETS_ID

    def connect(self) -> bool:
        """Подключение к Google Sheets API."""
        try:
            credentials = service_account.Credentials.from_service_account_file(
                GOOGLE_CREDENTIALS_FILE,
                scopes=self.SCOPES
            )
            self.service = build('sheets', 'v4', credentials=credentials)
            print("[OK] Подключено к Google Sheets")
            return True
        except Exception as e:
            print(f"[ОШИБКА] Не удалось подключиться к Google Sheets: {e}")
            return False

    def get_pending_tasks(self) -> list[dict]:
        """Получить все задания со статусом 'pending'."""
        if not self.service:
            print("[ОШИБКА] Сначала вызовите connect()")
            return []

        try:
            # Читаем данные из листа (A2:F - пропускаем заголовок)
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id,
                range='A2:F'
            ).execute()

            rows = result.get('values', [])
            tasks = []

            for idx, row in enumerate(rows):
                # Пропускаем пустые строки
                if len(row) < 5:
                    continue

                status = row[self.COLUMNS['status']] if len(row) > self.COLUMNS['status'] else ''

                if status.lower() == 'pending':
                    tasks.append({
                        'row_number': idx + 2,  # +2 потому что начинаем с A2
                        'project': row[self.COLUMNS['project']],
                        'topic': row[self.COLUMNS['topic']],
                        'platforms': row[self.COLUMNS['platforms']].split(','),
                        'datetime': row[self.COLUMNS['datetime']],
                        'status': status,
                    })

            print(f"[OK] Найдено {len(tasks)} заданий для публикации")
            return tasks

        except Exception as e:
            print(f"[ОШИБКА] Не удалось прочитать данные: {e}")
            return []

    def update_status(self, row_number: int, status: str, post_id: Optional[str] = None) -> bool:
        """Обновить статус задания после публикации."""
        if not self.service:
            return False

        try:
            # Обновляем статус (колонка E)
            self.service.spreadsheets().values().update(
                spreadsheetId=self.sheet_id,
                range=f'E{row_number}',
                valueInputOption='RAW',
                body={'values': [[status]]}
            ).execute()

            # Если есть post_id, записываем его (колонка F)
            if post_id:
                self.service.spreadsheets().values().update(
                    spreadsheetId=self.sheet_id,
                    range=f'F{row_number}',
                    valueInputOption='RAW',
                    body={'values': [[post_id]]}
                ).execute()

            print(f"[OK] Строка {row_number}: статус обновлён на '{status}'")
            return True

        except Exception as e:
            print(f"[ОШИБКА] Не удалось обновить статус: {e}")
            return False


# Для тестирования модуля напрямую
if __name__ == "__main__":
    sheets = SheetsService()
    if sheets.connect():
        tasks = sheets.get_pending_tasks()
        for task in tasks:
            print(f"  - {task['project']}: {task['topic']}")
