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
Миксин для настроек производительности и WebEngine (PySide6)
Добавлены настройки для пользовательского User-Agent, размера кэша HTTP и видеооптимизаций.
"""
import logging
import json
from core.database import db
from core.config import (
    DEFAULT_PLUGINS_ENABLED, DEFAULT_HYPERLINK_AUDITING_ENABLED, DEFAULT_SCROLL_ANIMATOR_ENABLED,
    DEFAULT_BACKGROUND_MEDIA_ENABLED, DEFAULT_AGGRESSIVE_DISCARD, DEFAULT_CLEAR_CACHE_ON_EXIT,
    DEFAULT_ADBLOCK_ENABLED, DEFAULT_ADBLOCK_MODE, ADBLOCK_MODES,
    DEFAULT_RESTORE_SESSION,
    DEFAULT_JAVASCRIPT_CAN_OPEN_WINDOWS, DEFAULT_LOCAL_STORAGE_ENABLED,
    DEFAULT_ERROR_PAGE_ENABLED, DEFAULT_PDF_VIEWER_ENABLED,
    DEFAULT_PREDICTIVE_NETWORK_ACTIONS, DEFAULT_FULLSCREEN_SUPPORT_ENABLED,
    DEFAULT_TRANSLATE_ENABLED,
    DEFAULT_MOBILE_SUGGESTION_ENABLED, DEFAULT_MOBILE_SUGGESTION_DOMAINS,
    DEFAULT_USER_AGENT,
    DEFAULT_HTTP_CACHE_SIZE_MB,
    DEFAULT_VIDEO_OPTIMIZATIONS_ENABLED,
    DEFAULT_CONTENT_VISIBILITY_ENABLED
)

logger = logging.getLogger(__name__)

class PerformanceMixin:
    """Миксин для работы с настройками производительности"""

    # === Вспомогательные методы ===
    def _get_setting(self, key, default):
        try:
            result = db.execute(
                "SELECT value FROM settings WHERE key = ?",
                (key,), fetchone=True
            )
            if result:
                return result['value']
            return default
        except Exception as e:
            logger.error(f"Error getting setting {key}: {e}")
            return default

    def _save_setting(self, key, value):
        try:
            db.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                (key, str(value))
            )
        except Exception as e:
            logger.error(f"Error saving setting {key}: {e}")

    def _get_bool(self, key, default):
        val = self._get_setting(key, '1' if default else '0')
        return val == '1'

    def _save_bool(self, key, value):
        self._save_setting(key, '1' if value else '0')

    def _get_int(self, key, default):
        try:
            return int(self._get_setting(key, str(default)))
        except:
            return default

    def _save_int(self, key, value):
        self._save_setting(key, str(value))

    # === Плагины ===
    def get_plugins_enabled(self):
        return self._get_bool('plugins_enabled', DEFAULT_PLUGINS_ENABLED)

    def save_plugins_enabled(self, enabled):
        self._save_bool('plugins_enabled', enabled)

    # === Гиперссылки аудит ===
    def get_hyperlink_auditing_enabled(self):
        return self._get_bool('hyperlink_auditing', DEFAULT_HYPERLINK_AUDITING_ENABLED)

    def save_hyperlink_auditing_enabled(self, enabled):
        self._save_bool('hyperlink_auditing', enabled)

    # === Анимация прокрутки ===
    def get_scroll_animator_enabled(self):
        return self._get_bool('scroll_animator', DEFAULT_SCROLL_ANIMATOR_ENABLED)

    def save_scroll_animator_enabled(self, enabled):
        self._save_bool('scroll_animator', enabled)

    # === Интервал выгрузки вкладок ===
    def get_discard_interval(self):
        return self._get_int('discard_interval', 300)

    def save_discard_interval(self, seconds):
        self._save_int('discard_interval', seconds)

    # === Фоновое медиа ===
    def get_background_media_enabled(self):
        return self._get_bool('background_media_enabled', DEFAULT_BACKGROUND_MEDIA_ENABLED)

    def save_background_media_enabled(self, enabled):
        self._save_bool('background_media_enabled', enabled)

    # === Очистка кэша при выходе ===
    def get_clear_cache_on_exit(self):
        return self._get_bool('clear_cache_on_exit', DEFAULT_CLEAR_CACHE_ON_EXIT)

    def save_clear_cache_on_exit(self, enabled):
        self._save_bool('clear_cache_on_exit', enabled)

    # === Агрессивная выгрузка (не используется) ===
    def get_aggressive_discard(self):
        return self._get_bool('aggressive_discard', DEFAULT_AGGRESSIVE_DISCARD)

    def save_aggressive_discard(self, enabled):
        self._save_bool('aggressive_discard', enabled)

    # === Блокировщик рекламы ===
    def get_adblock_enabled(self):
        return self._get_bool('adblock_enabled', DEFAULT_ADBLOCK_ENABLED)

    def save_adblock_enabled(self, enabled):
        self._save_bool('adblock_enabled', enabled)

    def get_adblock_mode(self):
        mode = self._get_setting('adblock_mode', DEFAULT_ADBLOCK_MODE)
        if mode not in ADBLOCK_MODES:
            mode = DEFAULT_ADBLOCK_MODE
        return mode

    def save_adblock_mode(self, mode):
        if mode not in ADBLOCK_MODES:
            mode = DEFAULT_ADBLOCK_MODE
        self._save_setting('adblock_mode', mode)

    # === Восстановление сессии ===
    def get_restore_session(self):
        return self._get_bool('restore_session', DEFAULT_RESTORE_SESSION)

    def save_restore_session(self, enabled):
        self._save_bool('restore_session', enabled)

    def get_session_urls(self):
        try:
            val = self._get_setting('session_urls', '[]')
            return json.loads(val)
        except Exception as e:
            logger.error(f"Error parsing session urls: {e}")
            return []

    def save_session_urls(self, urls_list):
        try:
            self._save_setting('session_urls', json.dumps(urls_list))
        except Exception as e:
            logger.error(f"Error saving session urls: {e}")

    # === Настройки WebEngine ===
    def get_javascript_can_open_windows(self):
        return self._get_bool('javascript_can_open_windows', DEFAULT_JAVASCRIPT_CAN_OPEN_WINDOWS)

    def save_javascript_can_open_windows(self, enabled):
        self._save_bool('javascript_can_open_windows', enabled)

    def get_local_storage_enabled(self):
        return self._get_bool('local_storage_enabled', DEFAULT_LOCAL_STORAGE_ENABLED)

    def save_local_storage_enabled(self, enabled):
        self._save_bool('local_storage_enabled', enabled)

    def get_error_page_enabled(self):
        return self._get_bool('error_page_enabled', DEFAULT_ERROR_PAGE_ENABLED)

    def save_error_page_enabled(self, enabled):
        self._save_bool('error_page_enabled', enabled)

    def get_pdf_viewer_enabled(self):
        return self._get_bool('pdf_viewer_enabled', DEFAULT_PDF_VIEWER_ENABLED)

    def save_pdf_viewer_enabled(self, enabled):
        self._save_bool('pdf_viewer_enabled', enabled)

    def get_predictive_network_actions_enabled(self):
        return self._get_bool('predictive_network_actions', DEFAULT_PREDICTIVE_NETWORK_ACTIONS)

    def save_predictive_network_actions_enabled(self, enabled):
        self._save_bool('predictive_network_actions', enabled)

    def get_fullscreen_support_enabled(self):
        return self._get_bool('fullscreen_support_enabled', DEFAULT_FULLSCREEN_SUPPORT_ENABLED)

    def save_fullscreen_support_enabled(self, enabled):
        self._save_bool('fullscreen_support_enabled', enabled)

    # === Настройка перевода выделенного текста ===
    def get_translate_enabled(self):
        return self._get_bool('translate_enabled', DEFAULT_TRANSLATE_ENABLED)

    def save_translate_enabled(self, enabled):
        self._save_bool('translate_enabled', enabled)

    # === Настройки предложения мобильной версии (устарело, оставлено для совместимости) ===
    def get_mobile_suggestion_enabled(self):
        return self._get_bool('mobile_suggestion_enabled', DEFAULT_MOBILE_SUGGESTION_ENABLED)

    def save_mobile_suggestion_enabled(self, enabled):
        self._save_bool('mobile_suggestion_enabled', enabled)

    def get_mobile_suggestion_domains(self):
        domains_str = self._get_setting('mobile_suggestion_domains', '')
        if domains_str:
            return [d.strip() for d in domains_str.split(',') if d.strip()]
        return DEFAULT_MOBILE_SUGGESTION_DOMAINS

    def save_mobile_suggestion_domains(self, domains_list):
        self._save_setting('mobile_suggestion_domains', ','.join(domains_list))

    # === Пользовательский User-Agent ===
    def get_user_agent(self):
        return self._get_setting('user_agent', DEFAULT_USER_AGENT)

    def save_user_agent(self, user_agent):
        self._save_setting('user_agent', user_agent)

    # === Размер кэша HTTP ===
    def get_cache_size_mb(self):
        return self._get_int('http_cache_size_mb', DEFAULT_HTTP_CACHE_SIZE_MB)

    def save_cache_size_mb(self, size_mb):
        self._save_int('http_cache_size_mb', size_mb)
        logger.info(f"HTTP cache size set to {size_mb} MB")

    # === Видеооптимизации ===
    def get_video_optimizations_enabled(self):
        return self._get_bool('video_optimizations_enabled', DEFAULT_VIDEO_OPTIMIZATIONS_ENABLED)

    def save_video_optimizations_enabled(self, enabled):
        self._save_bool('video_optimizations_enabled', enabled)
        logger.info(f"Video optimizations enabled set to {enabled}")

    # === CSS content-visibility ===
    def get_content_visibility_enabled(self):
        return self._get_bool('content_visibility_enabled', DEFAULT_CONTENT_VISIBILITY_ENABLED)

    def save_content_visibility_enabled(self, enabled):
        self._save_bool('content_visibility_enabled', enabled)
        logger.info(f"Content visibility enabled set to {enabled}")