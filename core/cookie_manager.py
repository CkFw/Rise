# Этот файл является частью Rise Browser.
# Copyright (C) 2026 Clark Flow (Егор)
# 
# Rise Browser is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Rise Browser is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Менеджер для ручного сохранения и загрузки кук (обход проблем с профилем WebEngine).
Загрузка происходит постепенно, чтобы избежать краша.
"""
import json
import logging
import os
from PySide6.QtCore import QObject, Signal, QTimer, QDateTime, QUrl
from PySide6.QtNetwork import QNetworkCookie
from PySide6.QtWebEngineCore import QWebEngineProfile

logger = logging.getLogger(__name__)


class CookieManager(QObject):
    """Менеджер для ручного сохранения и загрузки кук."""
    finished = Signal()  # новый сигнал, излучается после завершения загрузки всех кук

    def __init__(self, profile: QWebEngineProfile, storage_path: str):
        super().__init__()
        self.profile = profile
        self.storage_path = storage_path
        self.cookie_store = profile.cookieStore()
        self._cookies = []  # список всех текущих кук (объекты QNetworkCookie)
        self._save_timer = QTimer()
        self._save_timer.setInterval(2000)  # сохранять не чаще чем раз в 2 секунды
        self._save_timer.setSingleShot(True)
        self._save_timer.timeout.connect(self._save_cookies_impl)

        # Подключаем сигналы
        self.cookie_store.cookieAdded.connect(self._on_cookie_added)
        self.cookie_store.cookieRemoved.connect(self._on_cookie_removed)

        logger.info("CookieManager инициализирован, загрузка отложена")

    def load_cookies(self):
        """Загружает куки из файла и добавляет их в хранилище (безопасно)."""
        if not os.path.exists(self.storage_path):
            logger.info("Файл с куками не найден, загрузка пропущена")
            return

        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                cookies_data = json.load(f)

            if not cookies_data:
                return

            logger.info(f"Начинаем загрузку {len(cookies_data)} кук...")
            # Устанавливаем куки с задержкой между ними, чтобы не перегружать WebEngine
            self._set_cookies_gradually(cookies_data)

        except Exception as e:
            logger.error(f"Ошибка загрузки кук: {e}")

    def _set_cookies_gradually(self, cookies_data, index=0):
        """Устанавливает куки по одной с интервалом 10 мс для избежания краша."""
        if index >= len(cookies_data):
            logger.info("Загрузка кук завершена")
            self.finished.emit()  # сигнал о завершении
            return

        cookie_dict = cookies_data[index]
        try:
            cookie = self._dict_to_cookie(cookie_dict)
            if cookie:
                domain = cookie.domain().lstrip('.')
                if domain and domain not in ('localhost', '127.0.0.1'):
                    scheme = "https" if cookie.isSecure() else "http"
                    url = QUrl(f"{scheme}://{domain}")
                    if url.isValid():
                        self.cookie_store.setCookie(cookie, url)
                        logger.debug(f"Установлена кука {index+1}/{len(cookies_data)}: {cookie.name()}")
        except Exception as e:
            logger.error(f"Ошибка при установке куки {index}: {e}")

        # Следующая кука через 10 мс (было 50 мс)
        QTimer.singleShot(10, lambda: self._set_cookies_gradually(cookies_data, index + 1))

    def _on_cookie_added(self, cookie):
        """Обработчик добавления куки."""
        self._cookies.append(cookie)
        self._schedule_save()

    def _on_cookie_removed(self, cookie):
        """Обработчик удаления куки."""
        self._cookies = [c for c in self._cookies if not self._cookies_equal(c, cookie)]
        self._schedule_save()

    def _schedule_save(self):
        """Запланировать сохранение кук через небольшой промежуток."""
        self._save_timer.start()

    def _save_cookies_impl(self):
        """Непосредственно сохраняет куки в файл."""
        try:
            cookies_data = []
            seen = set()
            for cookie in self._cookies:
                key = (cookie.domain(), bytes(cookie.name()), cookie.path())
                if key in seen:
                    continue
                seen.add(key)
                cookie_dict = self._cookie_to_dict(cookie)
                if cookie_dict:
                    cookies_data.append(cookie_dict)

            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(cookies_data, f, indent=2, ensure_ascii=False)

            logger.debug(f"Сохранено {len(cookies_data)} кук в {self.storage_path}")
        except Exception as e:
            logger.error(f"Ошибка сохранения кук: {e}")

    def _cookie_to_dict(self, cookie: QNetworkCookie):
        """Преобразует QNetworkCookie в словарь для JSON."""
        try:
            name = bytes(cookie.name()).decode('utf-8', errors='ignore')
            value = bytes(cookie.value()).decode('utf-8', errors='ignore')
            domain = cookie.domain()
            path = cookie.path()
            secure = cookie.isSecure()
            httponly = cookie.isHttpOnly()
            expires = cookie.expirationDate()

            data = {
                'name': name,
                'value': value,
                'domain': domain,
                'path': path,
                'secure': secure,
                'httponly': httponly,
            }
            if expires.isValid():
                data['expires'] = expires.toSecsSinceEpoch()
            return data
        except Exception as e:
            logger.error(f"Ошибка преобразования куки в dict: {e}")
            return None

    def _dict_to_cookie(self, data: dict):
        """Восстанавливает QNetworkCookie из словаря."""
        try:
            cookie = QNetworkCookie(
                data['name'].encode('utf-8'),
                data['value'].encode('utf-8')
            )
            cookie.setDomain(data['domain'])
            cookie.setPath(data.get('path', '/'))
            if data.get('secure'):
                cookie.setSecure(True)
            if data.get('httponly'):
                cookie.setHttpOnly(True)
            if 'expires' in data:
                dt = QDateTime.fromSecsSinceEpoch(data['expires'])
                cookie.setExpirationDate(dt)
            return cookie
        except Exception as e:
            logger.error(f"Ошибка восстановления куки из dict: {e}")
            return None

    def _cookies_equal(self, c1: QNetworkCookie, c2: QNetworkCookie) -> bool:
        """Сравнивает две куки по основным полям."""
        return (c1.domain() == c2.domain() and
                c1.name() == c2.name() and
                c1.path() == c2.path())