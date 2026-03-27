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
Управление загрузками: менеджер и диалог.
"""
import logging
from core.download_manager import DownloadManager

logger = logging.getLogger(__name__)

class DownloadMixin:
    """Управление загрузками файлов."""

    def _setup_download_manager(self):
        """Инициализирует менеджер загрузок (вызывается в __init__)."""
        self.download_manager = DownloadManager(self.api, self)
        self.download_manager.download_added.connect(self._on_download_added)
        self.download_manager.download_progress.connect(self._on_download_progress)
        self.download_manager.download_finished.connect(self._on_download_finished)
        self.download_manager.download_cancelled.connect(self._on_download_cancelled)

    def _on_download_added(self, item):
        pass

    def _on_download_progress(self, item_id, received, total):
        pass

    def _on_download_finished(self, item_id, filepath, size):
        if hasattr(self, 'downloads_dialog') and self.downloads_dialog and self.downloads_dialog.isVisible():
            self.downloads_dialog.load_downloads()

    def _on_download_cancelled(self, item_id):
        pass

    def _show_downloads_dialog(self):
        """Открывает диалог загрузок."""
        if hasattr(self, 'downloads_dialog') and self.downloads_dialog and self.downloads_dialog.isVisible():
            self.downloads_dialog.load_downloads()
            self.downloads_dialog.raise_()
            return
        from ui.dialogs.downloads import DownloadsDialog
        self.downloads_dialog = DownloadsDialog(self, self.api, self.download_manager)
        self.downloads_dialog.finished.connect(lambda: setattr(self, 'downloads_dialog', None))
        self.downloads_dialog.show()