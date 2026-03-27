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
Менеджер для управления загрузками с поддержкой прогресса и отмены (PySide6)
Исправлено: логирование, обработка дубликатов, корректное завершение.
"""
import os
import time
import logging
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QFileDialog

logger = logging.getLogger(__name__)

class DownloadItem:
    """Элемент загрузки"""
    def __init__(self, id, download, filepath, url):
        self.id = id
        self.download = download
        self.filepath = filepath
        self.url = url
        self.filename = os.path.basename(filepath)
        self.progress = 0
        self.total_bytes = 0
        self.received_bytes = 0
        self.is_finished = False
        self.is_cancelled = False

class DownloadManager(QObject):
    download_added = Signal(object)
    download_progress = Signal(int, int, int)  # id, received, total
    download_finished = Signal(int, str, int)  # id, filepath, size
    download_cancelled = Signal(int)

    def __init__(self, api, parent=None):
        super().__init__(parent)
        self.api = api
        self.dialog_open = False
        self.active_downloads = {}
        self.next_id = 0
        self._processing_urls = set()
        self.logger = logging.getLogger(f"{__name__}.DownloadManager")

    def handle_download_requested(self, download):
        url = download.url().toString()
        self.logger.info(f"Download requested: {url}")

        if url in self._processing_urls:
            self.logger.warning(f"Duplicate download request for {url}, cancelling")
            download.cancel()
            return

        self._processing_urls.add(url)

        if self.dialog_open:
            self.logger.warning("Download dialog already open, cancelling")
            download.cancel()
            self._processing_urls.discard(url)
            return

        self.dialog_open = True
        try:
            suggested_filename = download.downloadFileName()
            filepath, _ = QFileDialog.getSaveFileName(
                self.parent(), "Сохранить файл",
                suggested_filename,
                "All Files (*)"
            )
            if filepath:
                dir_path = os.path.dirname(filepath)
                filename = os.path.basename(filepath)
                download.setDownloadDirectory(dir_path)
                download.setDownloadFileName(filename)
                download.accept()

                # Удаляем предыдущую запись с таким же путём
                self.api.remove_download_by_path(filepath)

                item = DownloadItem(self.next_id, download, filepath, url)
                self.active_downloads[self.next_id] = item
                self.next_id += 1

                self.api.add_download(item.filename, filepath, url, 0)

                download.downloadProgress.connect(
                    lambda received, total: self._on_progress(download, received, total))
                download.finished.connect(lambda: self._on_finished(download))

                self.logger.info(f"Download added: {item.id} - {item.filename}")
                self.download_added.emit(item)

                if download.isFinished():
                    self._on_finished(download)
            else:
                download.cancel()
                self._processing_urls.discard(url)
        except Exception as e:
            self.logger.error(f"Error handling download: {e}", exc_info=True)
            self._processing_urls.discard(url)
        finally:
            self.dialog_open = False

    def _on_progress(self, download, received, total):
        for item_id, item in self.active_downloads.items():
            if item.download == download:
                if item.is_cancelled:
                    return
                item.received_bytes = received
                item.total_bytes = total
                if total > 0:
                    item.progress = int(received * 100 / total)
                else:
                    item.progress = 0
                self.logger.debug(f"Progress {item_id}: {received}/{total} ({item.progress}%)")
                self.download_progress.emit(item_id, received, total)
                break

    def _on_finished(self, download):
        self.logger.debug("Download finished callback entered")
        for item_id, item in list(self.active_downloads.items()):
            if item.download == download:
                self.logger.debug(f"Found item {item_id}")
                if item.is_cancelled:
                    return
                item.is_finished = True

                real_size = download.totalBytes()
                self.logger.debug(f"totalBytes returned {real_size}")

                if real_size <= 0:
                    time.sleep(0.5)
                    if os.path.exists(item.filepath):
                        try:
                            real_size = os.path.getsize(item.filepath)
                            self.logger.debug(f"Got size from filesystem: {real_size}")
                        except Exception as e:
                            self.logger.error(f"Error getting file size: {e}")

                if real_size > 0:
                    self.api.update_download_size(item.filepath, real_size)
                    item.total_bytes = real_size

                self.logger.info(f"Download finished: {item_id} - {item.filename}, size={real_size}")
                self.download_finished.emit(item_id, item.filepath, real_size)

                self._processing_urls.discard(item.url)
                del self.active_downloads[item_id]
                break
        else:
            self.logger.warning("Finished download not found in active downloads")

    def cancel_download(self, item_id):
        if item_id in self.active_downloads:
            item = self.active_downloads[item_id]
            if not item.is_finished and not item.is_cancelled:
                item.download.cancel()
                item.is_cancelled = True
                self._delete_file(item.filepath)
                del self.active_downloads[item_id]
                self.logger.info(f"Download cancelled: {item_id}")
            else:
                if item_id in self.active_downloads:
                    del self.active_downloads[item_id]
            self.download_cancelled.emit(item_id)
        else:
            self.download_cancelled.emit(item_id)

    def _delete_file(self, filepath):
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                self.logger.debug(f"Deleted partial file: {filepath}")
            except Exception as e:
                self.logger.error(f"Could not delete file {filepath}: {e}")

    def get_active_downloads(self):
        return list(self.active_downloads.values())