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

# ui/main_window.py
"""
Главное окно браузера – собирает все миксины.
(Удалена функциональность Shift+колёсико)
Добавлена поддержка звуков клавиатуры.
"""
import os
import logging
from PySide6.QtWidgets import QMainWindow, QApplication, QMessageBox
from PySide6.QtCore import Qt, QTimer, QEvent, QUrl
from PySide6.QtGui import QKeyEvent
from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings
from PySide6.QtNetwork import QNetworkProxy

from core.api import BrowserAPI
from core.config import STYLES, DATA_DIR, DEFAULT_USER_AGENT
from core.cookie_manager import CookieManager
from core.adblock_manager import AdBlockManager
from core.download_manager import DownloadManager
from core.smart_buffer import SmartBufferManager
from core.event_filters import NavigationEventFilter
from core.utils import resource_path
from core.keyboard_sound import KeyboardSoundManager

from ui.window_mixins import (
    WindowManagementMixin,
    TabManagementMixin,
    NetworkMixin,
    DownloadMixin,
    HistoryFavoritesMixin,
    EventHandlingMixin,
    MemoryMonitoringMixin,
    HomePageMixin,
    UICustomizationMixin
)

# Импорт нового AI-чата
from ui.dialogs.ai_chatt_module.chat_window import AIChatWindow

logger = logging.getLogger(__name__)


class BrowserWindow(
    QMainWindow,
    WindowManagementMixin,
    TabManagementMixin,
    NetworkMixin,
    DownloadMixin,
    HistoryFavoritesMixin,
    EventHandlingMixin,
    MemoryMonitoringMixin,
    HomePageMixin,
    UICustomizationMixin
):
    def __init__(self):
        super().__init__()
        self.api = BrowserAPI()
        self.logger = logging.getLogger(f"{__name__}.BrowserWindow")

        # Общие атрибуты
        self.browsers = []
        self.browser_last_active = []
        self.tabs_audible = []
        self.current_browser_index = 0
        self.is_adding_tab = False
        self.home_page_path = None
        self.is_fullscreen = False
        self.tab_load_progress = []

        self.favorites_dialog = None
        self.history_dialog = None
        self.settings_dialog = None
        self.downloads_dialog = None
        self.ai_chat = None

        self.auto_hide_enabled = False
        self.auto_hide_delay = 5
        self.auto_hide_timer = None
        self.title_bar = None
        self.nav_bar = None
        self.tab_bar = None
        self.stack = None
        self.i2p_progress = None

        self.adblock_manager = AdBlockManager(self.api)
        self.adblock_manager.schedule_update()
        self.download_manager = DownloadManager(self.api, self)

        # Инициализация менеджера звуков клавиатуры
        self.keyboard_sound = KeyboardSoundManager(self.api)

        self._setup_webengine_profile()

        # Инициализация миксинов
        self._setup_network_mixins()
        self._setup_download_manager()

        self.nav_filter = NavigationEventFilter(self)
        QApplication.instance().installEventFilter(self.nav_filter)
        QApplication.instance().installEventFilter(self)

        self.setAcceptDrops(True)

        cookies_path = os.path.join(DATA_DIR, 'cookies.json')
        self.cookie_manager = CookieManager(QWebEngineProfile.defaultProfile(), cookies_path)
        self.cookie_manager.finished.connect(self._on_cookies_loaded)
        QTimer.singleShot(500, self._delayed_cookie_load)

        self._setup_ui()                # создаёт title_bar, nav_bar, tab_bar, stack
        self.restore_session()          # из HomePageMixin

        # Умный буфер
        self.smart_buffer = SmartBufferManager(self.api, QWebEngineProfile.defaultProfile(), self)

        self._init_auto_hide()          # из WindowManagementMixin
        self._start_services()          # из NetworkMixin (I2P, DPI)

        self._init_timers()             # из MemoryMonitoringMixin и TabManagementMixin
        self.apply_urlbar_customization()   # из UICustomizationMixin

        # Применяем стиль выделения ко всем вкладкам
        self.apply_selection_style()

        # Глобальные горячие клавиши (F5, F11, Shift+I)
        self._init_global_shortcuts()

        self.logger.info("BrowserWindow initialized")

    def _setup_webengine_profile(self):
        profile = QWebEngineProfile.defaultProfile()
        profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.DiskHttpCache)
        # Размер кэша из настроек
        cache_mb = self.api.get_cache_size_mb()
        profile.setHttpCacheMaximumSize(cache_mb * 1024 * 1024)
        profile.setSpellCheckEnabled(False)

        profile.setPersistentCookiesPolicy(QWebEngineProfile.ForcePersistentCookies)

        user_agent = self.api.get_user_agent()
        if not user_agent:
            user_agent = DEFAULT_USER_AGENT
        profile.setHttpUserAgent(user_agent)
        self.logger.info(f"User-Agent set to: {user_agent[:50]}...")

        settings = profile.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.ErrorPageEnabled, self.api.get_error_page_enabled())
        settings.setAttribute(QWebEngineSettings.WebAttribute.PrintElementBackgrounds, self.api.get_print_backgrounds_enabled())
        settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.HyperlinkAuditingEnabled, self.api.get_hyperlink_auditing_enabled())
        settings.setAttribute(QWebEngineSettings.WebAttribute.ScrollAnimatorEnabled, self.api.get_scroll_animator_enabled())
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, self.api.get_javascript_can_open_windows())
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, self.api.get_local_storage_enabled())
        settings.setAttribute(QWebEngineSettings.WebAttribute.PdfViewerEnabled, self.api.get_pdf_viewer_enabled())
        settings.setAttribute(QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, True)

        settings.setAttribute(QWebEngineSettings.WebAttribute.PlaybackRequiresUserGesture, False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, True)

        try:
            settings.setAttribute(QWebEngineSettings.WebAttribute.StorageAccessApiEnabled, True)
        except AttributeError:
            pass

        try:
            settings.setAttribute(QWebEngineSettings.WebAttribute.Accelerated2dCanvasEnabled, False)
        except AttributeError:
            pass
        try:
            settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, False)
        except AttributeError:
            pass

    def _delayed_cookie_load(self):
        if hasattr(self, 'cookie_manager'):
            self.logger.info("Попытка загрузить куки через 500 мс после запуска")
            self.cookie_manager.load_cookies()

    def _on_cookies_loaded(self):
        if not self.browsers:
            return
        current = self.browsers[self.current_browser_index]
        url = current.url().toString()
        if url and not url.startswith('file:') and url != 'about:blank':
            self.logger.info("Куки загружены, перезагружаем текущую страницу для применения.")
            current.reload()

    # ----- Методы, вызываемые из миксинов -----
    def show_ai_chat(self):
        if self.ai_chat and self.ai_chat.isVisible():
            self.ai_chat.raise_()
            return
        if not self.api.get_ai_chat_enabled():
            QMessageBox.information(self, "AI Чат", "AI-чат отключён в настройках.\nВключите его в Настройках → AI Чат.")
            return
        self.ai_chat = AIChatWindow(self.api, self)
        self.ai_chat.finished.connect(lambda: setattr(self, 'ai_chat', None))
        self.ai_chat.show()

    def apply_selection_style(self):
        """Применяет стиль выделения ко всем открытым вкладкам."""
        for tab in self.browsers:
            if hasattr(tab, 'inject_selection_style'):
                tab.inject_selection_style()

    def update_http_cache_size(self, cache_mb):
        """Обновляет размер кэша для всех вкладок и профиля."""
        size_bytes = cache_mb * 1024 * 1024
        profile = QWebEngineProfile.defaultProfile()
        profile.setHttpCacheMaximumSize(size_bytes)
        # Применяем ко всем уже созданным вкладкам (они используют тот же профиль)
        for tab in self.browsers:
            tab.page().profile().setHttpCacheMaximumSize(size_bytes)
        self.logger.info(f"HTTP cache size updated to {cache_mb} MB")

    def closeEvent(self, event):
        self.logger.info("Closing BrowserWindow")
        if hasattr(self, 'i2p_manager') and self.i2p_manager.enabled:
            self.i2p_manager.stop()
        if self.api.get_dpi_enabled():
            self._stop_dpi()
        if hasattr(self, 'ss_manager'):
            self.ss_manager.stop()
        if hasattr(self, 'trojan_manager'):
            self.trojan_manager.stop()

        urls = [b.url().toString() for b in self.browsers
                if b.url().toString() and not b.url().toString().startswith(('file:', 'rise:')) and b.url().toString() != "about:blank"]
        self.api.save_session_urls(urls)

        if self.api.get_clear_cache_on_exit():
            QWebEngineProfile.defaultProfile().clearHttpCache()

        if hasattr(self, 'cookie_manager'):
            self.cookie_manager._save_cookies_impl()

        if hasattr(self, 'HOME_TEMP_FILE') and os.path.exists(self.HOME_TEMP_FILE):
            try:
                os.remove(self.HOME_TEMP_FILE)
            except:
                pass

        super().closeEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            for url in urls:
                if url.isLocalFile() and url.toLocalFile().lower().endswith('.pdf'):
                    if self.api.get_pdf_separate_enabled():
                        try:
                            from ui.pdf_viewer import PDFViewerWindow
                            self.pdf_viewer = PDFViewerWindow(url.toLocalFile(), self)
                            self.pdf_viewer.show()
                            event.acceptProposedAction()
                            return
                        except Exception as e:
                            QMessageBox.warning(self, "Ошибка", f"PDF: {e}")
        event.ignore()

    # ----- Обработка событий клавиатуры для звуков -----
    def eventFilter(self, obj, event):
        # Сначала вызываем родительский фильтр
        result = super().eventFilter(obj, event)

        # Обрабатываем нажатия клавиш для звуков
        if event.type() == QEvent.Type.KeyPress:
            key = event.key()
            # Исключаем модификаторы
            if key not in (Qt.Key_Shift, Qt.Key_Control, Qt.Key_Alt, Qt.Key_Meta, Qt.Key_CapsLock, Qt.Key_NumLock):
                self.keyboard_sound.play_key_sound()
        return result