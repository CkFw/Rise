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
Диалог загрузок с отображением прогресса в колонке размера - PySide6
Исправлено: унификация импортов, логирование, улучшенная обработка ошибок.
"""
import os
import logging
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QWidget, QProgressBar
)

logger = logging.getLogger(__name__)

class DownloadsDialog(QDialog):
    """Диалог загрузок"""

    def __init__(self, parent_window, api, download_manager):
        super().__init__(parent_window)
        self.api = api
        self.download_manager = download_manager
        self.setWindowTitle("Загрузки")
        self.setGeometry(100, 100, 700, 450)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.drag_pos = None
        self._item_rows = {}
        self._size_widgets = {}
        self._cancel_buttons = {}
        self._path_to_item_id = {}

        # Таймер для автоматического обновления списка (каждые 2 секунды)
        self._refresh_timer = QTimer()
        self._refresh_timer.setInterval(2000)
        self._refresh_timer.timeout.connect(self.load_downloads)
        self._refresh_timer.start()

        self._setup_styles()
        self._setup_ui()
        self._connect_signals()
        self.load_downloads()
        logger.info("DownloadsDialog initialized")

    def _connect_signals(self):
        self.download_manager.download_added.connect(self._on_download_added)
        self.download_manager.download_progress.connect(self._on_progress)
        self.download_manager.download_cancelled.connect(self._on_cancelled)

    def closeEvent(self, event):
        self._refresh_timer.stop()
        if hasattr(self.parent(), 'downloads_dialog'):
            self.parent().downloads_dialog = None
        super().closeEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_pos is not None:
            self.move(event.globalPos() - self.drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_pos = None
        event.accept()

    def _setup_styles(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
                border: 1px solid #333;
            }
            QLabel {
                color: #fff;
                font-size: 18px;
                font-weight: bold;
                qproperty-alignment: AlignCenter;
                margin-top: 5px;
            }
            QTableWidget {
                background-color: #252525;
                color: #fff;
                border: none;
                border-radius: 5px;
                gridline-color: #333;
            }
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #333;
            }
            QTableWidget::item:hover {
                background-color: #333;
            }
            QHeaderView::section {
                background-color: #2a2a2a;
                color: #fff;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
            QPushButton {
                background-color: #00a8ff;
                color: #fff;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0097e6;
            }
            QPushButton#folderBtn {
                background-color: rgba(255, 193, 7, 200);
                min-width: 24px;
                max-width: 24px;
                min-height: 24px;
                max-height: 24px;
                padding: 0;
                border-radius: 12px;
                font-size: 14px;
            }
            QPushButton#folderBtn:hover {
                background-color: rgba(255, 193, 7, 230);
            }
            QPushButton#cancelBtn {
                background-color: rgba(232, 17, 35, 200);
                min-width: 24px;
                max-width: 24px;
                min-height: 24px;
                max-height: 24px;
                padding: 0;
                border-radius: 12px;
                font-size: 14px;
            }
            QPushButton#cancelBtn:hover {
                background-color: rgba(232, 17, 35, 230);
            }
            QProgressBar {
                border: none;
                background-color: #333;
                border-radius: 2px;
                height: 6px;
                margin: 2px 0;
            }
            QProgressBar::chunk {
                background-color: #00a8ff;
                border-radius: 2px;
            }
        """)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("📥 Загрузки"))

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Файл", "Путь", "Размер", "Действие"])

        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        self.table.setColumnWidth(1, 150)
        self.table.setColumnWidth(2, 100)

        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setDefaultSectionSize(85)
        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(QPushButton("Очистить список", clicked=self.clear_and_refresh))
        btn_layout.addWidget(QPushButton("Закрыть", clicked=self.close))
        layout.addLayout(btn_layout)

    def load_downloads(self):
        self.table.setRowCount(0)
        self._item_rows.clear()
        self._size_widgets.clear()
        self._cancel_buttons.clear()
        self._path_to_item_id.clear()

        active = self.download_manager.get_active_downloads()
        active_paths = {item.filepath for item in active}

        for item in active:
            self._add_active_row(item, insert_at_top=True)

        downloads = self.api.get_downloads()
        for download in reversed(downloads):
            filepath = download.get('filepath', '')
            if filepath not in active_paths:
                self._add_completed_row(download)

        self.table.resizeRowsToContents()
        self.table.viewport().update()
        logger.debug(f"Downloads loaded: {len(active)} active, {len(downloads)} total")

    def _add_completed_row(self, download):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setRowHeight(row, 60)

        filename = download.get('filename', 'Unknown')
        filepath = download.get('filepath', '')
        size = download.get('file_size', 0)

        if size <= 0 and os.path.exists(filepath):
            try:
                size = os.path.getsize(filepath)
                self.api.update_download_size(filepath, size)
            except Exception as e:
                logger.error(f"Error updating download size: {e}")

        file_widget = QWidget()
        file_layout = QHBoxLayout(file_widget)
        file_layout.setContentsMargins(5, 5, 5, 5)
        name_label = QLabel(f"✅ {filename}")
        name_label.setStyleSheet("color: #fff; font-size: 11px; font-weight: bold;")
        name_label.setWordWrap(True)
        file_layout.addWidget(name_label)
        self.table.setCellWidget(row, 0, file_widget)

        path_str = filepath[:60] + "..." if len(filepath) > 60 else filepath
        path_item = QTableWidgetItem(path_str)
        path_item.setToolTip(filepath)
        self.table.setItem(row, 1, path_item)

        size_widget = QWidget()
        size_layout = QVBoxLayout(size_widget)
        size_layout.setContentsMargins(5, 2, 5, 2)
        size_layout.setSpacing(0)

        completed_label = QLabel("Завершено")
        completed_label.setStyleSheet("color: #00ff88; font-size: 10px; font-weight: bold;")
        completed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        size_layout.addWidget(completed_label)

        size_str = self._format_size(size)
        size_label = QLabel(size_str)
        size_label.setStyleSheet("color: #fff; font-size: 11px;")
        size_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        size_layout.addWidget(size_label)

        self.table.setCellWidget(row, 2, size_widget)

        btn_widget = QWidget()
        btn_layout = QHBoxLayout(btn_widget)
        btn_layout.setContentsMargins(5, 0, 5, 0)
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        folder_btn = QPushButton("📁")
        folder_btn.setObjectName("folderBtn")
        folder_btn.setFixedSize(24, 24)
        folder_btn.setToolTip("Открыть папку с файлом")
        folder_btn.clicked.connect(lambda checked, p=filepath: self._open_folder(p))
        btn_layout.addWidget(folder_btn)

        self.table.setCellWidget(row, 3, btn_widget)

    def _add_active_row(self, item, insert_at_top=False):
        if item.filepath in self._path_to_item_id:
            old_id = self._path_to_item_id[item.filepath]
            self._remove_row_by_id(old_id)
            del self._path_to_item_id[item.filepath]

        if insert_at_top:
            self.table.insertRow(0)
            row = 0
            new_rows = {}
            for k, v in self._item_rows.items():
                new_rows[k] = v + 1
            self._item_rows = new_rows
        else:
            row = self.table.rowCount()
            self.table.insertRow(row)

        self.table.setRowHeight(row, 85)

        self._item_rows[item.id] = row
        self._path_to_item_id[item.filepath] = item.id

        file_widget = QWidget()
        file_layout = QHBoxLayout(file_widget)
        file_layout.setContentsMargins(5, 5, 5, 5)
        name_label = QLabel(f"📥 {item.filename}")
        name_label.setStyleSheet("color: #fff; font-size: 11px; font-weight: bold;")
        name_label.setWordWrap(True)
        file_layout.addWidget(name_label)
        self.table.setCellWidget(row, 0, file_widget)

        path_str = item.filepath[:60] + "..." if len(item.filepath) > 60 else item.filepath
        path_item = QTableWidgetItem(path_str)
        path_item.setToolTip(item.filepath)
        self.table.setItem(row, 1, path_item)

        size_widget = QWidget()
        size_layout = QVBoxLayout(size_widget)
        size_layout.setContentsMargins(5, 5, 5, 2)
        size_layout.setSpacing(2)

        recv_label = QLabel(self._format_size(item.received_bytes))
        recv_label.setStyleSheet("color: #00a8ff; font-size: 11px; font-weight: bold;")
        recv_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        recv_label.setWordWrap(True)
        size_layout.addWidget(recv_label)

        progress = QProgressBar()
        progress.setRange(0, 100)
        progress.setValue(item.progress)
        progress.setFixedHeight(6)
        progress.setTextVisible(False)
        size_layout.addWidget(progress)

        total_label = QLabel(self._format_size(item.total_bytes) if item.total_bytes > 0 else "? B")
        total_label.setStyleSheet("color: #fff; font-size: 11px;")
        total_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        total_label.setWordWrap(True)
        size_layout.addWidget(total_label)

        self.table.setCellWidget(row, 2, size_widget)
        self._size_widgets[item.id] = (progress, recv_label, total_label)

        btn_widget = QWidget()
        btn_layout = QHBoxLayout(btn_widget)
        btn_layout.setContentsMargins(5, 0, 5, 0)
        btn_layout.setSpacing(5)
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        folder_btn = QPushButton("📁")
        folder_btn.setObjectName("folderBtn")
        folder_btn.setFixedSize(24, 24)
        folder_btn.setToolTip("Открыть папку с файлом")
        folder_btn.clicked.connect(lambda checked, p=item.filepath: self._open_folder(p))
        btn_layout.addWidget(folder_btn)

        cancel_btn = QPushButton("✕")
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.setFixedSize(24, 24)
        cancel_btn.setToolTip("Отменить загрузку")
        cancel_btn.clicked.connect(lambda: self._cancel_download(item.id))
        btn_layout.addWidget(cancel_btn)

        self.table.setCellWidget(row, 3, btn_widget)
        self._cancel_buttons[item.id] = cancel_btn

        size_widget.update()

    def _open_folder(self, filepath):
        logger.info(f"Opening folder for {filepath}")
        self.api.open_file_location(filepath)

    def _remove_row_by_id(self, item_id):
        if item_id in self._item_rows:
            row = self._item_rows[item_id]
            self.table.removeRow(row)
            if item_id in self._size_widgets:
                del self._size_widgets[item_id]
            if item_id in self._cancel_buttons:
                del self._cancel_buttons[item_id]
            del self._item_rows[item_id]
            new_rows = {}
            for k, v in self._item_rows.items():
                if v > row:
                    new_rows[k] = v - 1
                else:
                    new_rows[k] = v
            self._item_rows = new_rows
            return True
        return False

    def _on_download_added(self, item):
        logger.info(f"DownloadsDialog: download added {item.id} - {item.filename}")
        self._add_active_row(item, insert_at_top=True)

    def _cancel_download(self, item_id):
        self.download_manager.cancel_download(item_id)

    def _on_progress(self, item_id, received, total):
        if item_id in self._size_widgets:
            progress, recv_label, total_label = self._size_widgets[item_id]
            percent = int(received * 100 / total) if total > 0 else 0
            progress.setValue(percent)
            recv_label.setText(self._format_size(received))
            total_label.setText(self._format_size(total) if total > 0 else "? B")
            progress.update()
        else:
            logger.debug(f"DownloadsDialog: item {item_id} not found in _size_widgets")

    def _on_cancelled(self, item_id):
        logger.info(f"DownloadsDialog: cancelled {item_id}")
        self._remove_row_by_id(item_id)
        to_del = None
        for path, iid in self._path_to_item_id.items():
            if iid == item_id:
                to_del = path
                break
        if to_del:
            del self._path_to_item_id[to_del]
        self.table.viewport().update()

    def _format_size(self, size):
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.1f} MB"
        else:
            return f"{size / (1024 * 1024 * 1024):.1f} GB"

    def clear_and_refresh(self):
        try:
            self.api.clear_downloads()
            self.load_downloads()
            logger.info("Downloads list cleared")
        except Exception as e:
            logger.error(f"Error clearing downloads: {e}", exc_info=True)