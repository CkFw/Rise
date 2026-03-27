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
Мониторинг памяти: адаптация кэша, сборка мусора.
"""
import logging
import psutil
from PySide6.QtCore import QTimer
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile

logger = logging.getLogger(__name__)

class MemoryMonitoringMixin:
    """Управление памятью браузера."""

    def _init_timers(self):
        """Создаёт таймеры мониторинга памяти."""
        # Таймер выгрузки старых вкладок (определён в TabManagementMixin)
        self.discard_timer = QTimer(self)
        self.discard_timer.timeout.connect(self.discard_old_tabs)
        self.update_discard_interval()

        self.memory_timer = QTimer(self)
        self.memory_timer.timeout.connect(self._adapt_cache_to_memory_pressure)
        self.memory_timer.start(30000)

        self.video_monitor_timer = QTimer(self)
        self.video_monitor_timer.timeout.connect(self._monitor_video_memory)
        self.video_monitor_timer.start(60000)

    def _adapt_cache_to_memory_pressure(self):
        if not self.browsers:
            return
        current_tab = self.browsers[self.current_browser_index]
        js = """
        (function() {
            let videos = document.querySelectorAll('video');
            if (videos.length === 0) return {hasVideo: false};
            let v = videos[0];
            return {
                hasVideo: true,
                videoWidth: v.videoWidth,
                videoHeight: v.videoHeight,
                isPaused: v.paused
            };
        })();
        """
        current_tab.page().runJavaScript(js, self._apply_cache_policy)

    def _apply_cache_policy(self, video_info):
        profile = QWebEngineProfile.defaultProfile()
        mem = psutil.virtual_memory()
        free_mb = mem.available / (1024 * 1024)

        if video_info and video_info.get('hasVideo'):
            width = video_info.get('videoWidth', 0)
            height = video_info.get('videoHeight', 0)
            is_hd = width > 1900 or height > 1080

            if is_hd and free_mb < 1000:
                profile.setHttpCacheMaximumSize(20 * 1024 * 1024)  # 20 МБ
                profile.clearHttpCache()
                self.logger.info("Low memory + HD video: cache aggressively reduced")
            else:
                profile.setHttpCacheMaximumSize(50 * 1024 * 1024)  # 50 МБ
        else:
            profile.setHttpCacheMaximumSize(100 * 1024 * 1024)  # 100 МБ

    def _monitor_video_memory(self):
        for i, tab in enumerate(self.browsers):
            if tab.page().lifecycleState() == QWebEnginePage.LifecycleState.Active:
                js = """
                (function() {
                    if (performance.memory && performance.memory.usedJSHeapSize > 300 * 1024 * 1024) {
                        if (window.gc) window.gc();
                        return true;
                    }
                    return false;
                })();
                """
                tab.page().runJavaScript(js, lambda cleaned, idx=i: self._log_memory_clean(idx, cleaned))

    def _log_memory_clean(self, tab_index, cleaned):
        if cleaned:
            self.logger.info(f"Forced garbage collection on tab {tab_index}")