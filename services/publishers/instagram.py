"""
Модуль для публикации постов в Instagram.
Использует Selenium для автоматизации браузера.
"""

import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.settings import INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD


class InstagramPublisher:
    """Публикатор постов в Instagram через Selenium."""

    def __init__(self, username: str = None, password: str = None, headless: bool = True):
        """
        Args:
            username: Логин Instagram. Если не указан, берётся из настроек.
            password: Пароль Instagram. Если не указан, берётся из настроек.
            headless: Запускать браузер без GUI (по умолчанию True).
        """
        self.driver = None
        self.username = username or INSTAGRAM_USERNAME
        self.password = password or INSTAGRAM_PASSWORD
        self.headless = headless
        self.logged_in = False

    def connect(self) -> bool:
        """Инициализация браузера и логин в Instagram."""
        try:
            if not self.username or not self.password:
                print("[ОШИБКА] INSTAGRAM_USERNAME или INSTAGRAM_PASSWORD не заданы в .env")
                return False

            # Настройка Chrome
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-notifications")
            chrome_options.add_argument("--lang=ru-RU")
            # User agent для мобильной версии (проще для постинга)
            chrome_options.add_argument(
                "--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
            )

            # Запуск браузера
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.implicitly_wait(10)

            print("[OK] Браузер запущен, выполняю вход в Instagram...")

            # Логин
            if not self._login():
                return False

            self.logged_in = True
            print("[OK] Instagram: успешный вход")
            return True

        except Exception as e:
            print(f"[ОШИБКА] Не удалось подключиться к Instagram: {e}")
            if self.driver:
                self.driver.quit()
            return False

    def _login(self) -> bool:
        """Авторизация в Instagram."""
        try:
            self.driver.get("https://www.instagram.com/accounts/login/")
            time.sleep(3)

            # Закрыть cookie popup если есть
            self._close_cookie_popup()

            # Ввод логина
            username_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            username_input.clear()
            username_input.send_keys(self.username)

            # Ввод пароля
            password_input = self.driver.find_element(By.NAME, "password")
            password_input.clear()
            password_input.send_keys(self.password)

            # Клик на кнопку входа
            password_input.send_keys(Keys.RETURN)
            time.sleep(5)

            # Проверка успешного входа
            if "login" in self.driver.current_url.lower():
                # Проверяем есть ли сообщение об ошибке
                try:
                    error_element = self.driver.find_element(By.ID, "slfErrorAlert")
                    print(f"[ОШИБКА] Неверный логин/пароль: {error_element.text}")
                    return False
                except:
                    pass

            # Закрыть popup "Сохранить данные входа"
            self._close_save_login_popup()

            # Закрыть popup "Включить уведомления"
            self._close_notifications_popup()

            return True

        except Exception as e:
            print(f"[ОШИБКА] Ошибка при входе: {e}")
            return False

    def _close_cookie_popup(self):
        """Закрыть popup с cookie."""
        try:
            # Разные варианты кнопок для cookie
            selectors = [
                "//button[contains(text(), 'Разрешить')]",
                "//button[contains(text(), 'Accept')]",
                "//button[contains(text(), 'Allow')]",
                "//button[contains(text(), 'Принять')]",
            ]
            for selector in selectors:
                try:
                    button = self.driver.find_element(By.XPATH, selector)
                    button.click()
                    time.sleep(1)
                    return
                except:
                    continue
        except:
            pass

    def _close_save_login_popup(self):
        """Закрыть popup сохранения данных входа."""
        try:
            time.sleep(2)
            # "Не сейчас" или "Not Now"
            selectors = [
                "//button[contains(text(), 'Не сейчас')]",
                "//button[contains(text(), 'Not Now')]",
                "//div[contains(text(), 'Не сейчас')]",
            ]
            for selector in selectors:
                try:
                    button = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    button.click()
                    time.sleep(1)
                    return
                except:
                    continue
        except:
            pass

    def _close_notifications_popup(self):
        """Закрыть popup уведомлений."""
        try:
            time.sleep(2)
            selectors = [
                "//button[contains(text(), 'Не сейчас')]",
                "//button[contains(text(), 'Not Now')]",
            ]
            for selector in selectors:
                try:
                    button = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    button.click()
                    time.sleep(1)
                    return
                except:
                    continue
        except:
            pass

    def publish(self, text: str, image_path: str) -> dict:
        """
        Публикация поста в Instagram.

        Args:
            text: Текст (подпись) поста
            image_path: Путь к изображению (ОБЯЗАТЕЛЬНО для Instagram)

        Returns:
            {'success': bool, 'post_id': str, 'error': str}
        """
        if not self.logged_in or not self.driver:
            return {'success': False, 'post_id': '', 'error': 'Не выполнен вход в Instagram'}

        if not image_path or not os.path.exists(image_path):
            return {'success': False, 'post_id': '', 'error': 'Instagram требует изображение для поста'}

        try:
            # Перейти на главную
            self.driver.get("https://www.instagram.com/")
            time.sleep(3)

            # Найти кнопку создания поста (иконка +)
            create_button = self._find_create_button()
            if not create_button:
                return {'success': False, 'post_id': '', 'error': 'Не найдена кнопка создания поста'}

            create_button.click()
            time.sleep(2)

            # Загрузить изображение
            # Ищем input для файла
            file_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
            )
            file_input.send_keys(os.path.abspath(image_path))
            time.sleep(3)

            # Нажать "Далее" (Next) - может быть несколько раз
            self._click_next_button()
            time.sleep(2)
            self._click_next_button()
            time.sleep(2)

            # Добавить подпись
            caption_area = self._find_caption_area()
            if caption_area:
                caption_area.click()
                # Instagram ограничение: 2200 символов
                truncated_text = text[:2200] if len(text) > 2200 else text
                caption_area.send_keys(truncated_text)
                time.sleep(1)

            # Нажать "Поделиться" (Share)
            if not self._click_share_button():
                return {'success': False, 'post_id': '', 'error': 'Не удалось нажать кнопку публикации'}

            time.sleep(5)

            # Проверить успешную публикацию
            # Instagram не возвращает ID поста при публикации через веб
            # Генерируем временную метку как идентификатор
            post_id = f"ig_{int(time.time())}"

            print(f"[OK] Опубликовано в Instagram, ID: {post_id}")
            return {'success': True, 'post_id': post_id, 'error': ''}

        except Exception as e:
            error_msg = str(e)
            print(f"[ОШИБКА] Не удалось опубликовать в Instagram: {error_msg}")
            return {'success': False, 'post_id': '', 'error': error_msg}

    def _find_create_button(self):
        """Найти кнопку создания поста."""
        selectors = [
            "//svg[@aria-label='Новая публикация']",
            "//svg[@aria-label='New post']",
            "//*[contains(@aria-label, 'New')]",
            "//*[contains(@aria-label, 'Create')]",
            "//*[contains(@aria-label, 'Создать')]",
        ]
        for selector in selectors:
            try:
                element = self.driver.find_element(By.XPATH, selector)
                # Кликаем на родительский элемент (обычно это ссылка или кнопка)
                parent = element.find_element(By.XPATH, "./..")
                return parent
            except:
                continue
        return None

    def _click_next_button(self):
        """Нажать кнопку Далее."""
        selectors = [
            "//button[contains(text(), 'Далее')]",
            "//button[contains(text(), 'Next')]",
            "//div[contains(text(), 'Далее')]",
            "//div[contains(text(), 'Next')]",
        ]
        for selector in selectors:
            try:
                button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                button.click()
                return True
            except:
                continue
        return False

    def _find_caption_area(self):
        """Найти поле для подписи."""
        selectors = [
            "//textarea[@aria-label='Добавьте подпись...']",
            "//textarea[@aria-label='Write a caption...']",
            "//textarea[contains(@placeholder, 'подпись')]",
            "//textarea[contains(@placeholder, 'caption')]",
            "//div[@aria-label='Добавьте подпись...']",
            "//div[@aria-label='Write a caption...']",
        ]
        for selector in selectors:
            try:
                element = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
                return element
            except:
                continue
        return None

    def _click_share_button(self):
        """Нажать кнопку Поделиться."""
        selectors = [
            "//button[contains(text(), 'Поделиться')]",
            "//button[contains(text(), 'Share')]",
            "//div[contains(text(), 'Поделиться')]",
            "//div[contains(text(), 'Share')]",
        ]
        for selector in selectors:
            try:
                button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                button.click()
                return True
            except:
                continue
        return False

    def disconnect(self):
        """Закрыть браузер."""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.logged_in = False
            print("[OK] Instagram: браузер закрыт")


# Для тестирования модуля напрямую
if __name__ == "__main__":
    publisher = InstagramPublisher(headless=False)  # headless=False для отладки
    if publisher.connect():
        result = publisher.publish(
            text="Тестовый пост от AutoPost\n\n#test #autopost",
            image_path="temp/test_image.jpg"
        )
        print(f"Результат: {result}")
        publisher.disconnect()
