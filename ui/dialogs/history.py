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
Диалог истории посещений - PySide6 (упрощённая версия без колонки названия)
Исправлено: унификация импортов, логирование, улучшенная обработка ошибок.
"""
import logging
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QMenu, QHeaderView, QTableWidget, QTableWidgetItem,
    QAbstractItemView, QApplication, QWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QClipboard

logger = logging.getLogger(__name__)

class HistoryDialog(QDialog):
    """Диалог истории посещений с двумя колонками: дата и URL"""

    def __init__(self, parent_window, browser_instance, history_data):
        super().__init__(parent_window)
        self.browser_instance = browser_instance
        self.history_data = history_data
        self.setWindowTitle("История")
        self.setGeometry(100, 100, 700, 500)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.drag_pos = None
        self._setup_styles()
        self._setup_ui()
        self.load_history()
        logger.info("HistoryDialog initialized")

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
                border-radius: 8px;
            }
            QLabel#titleLabel {
                color: #00a8ff;
                font-size: 20px;
                font-weight: bold;
                padding: 10px;
                background-color: #252525;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            QLineEdit {
                background-color: #252525;
                color: #fff;
                border: 1px solid #444;
                border-radius: 20px;
                padding: 8px 15px;
                font-size: 14px;
                margin: 5px 10px;
            }
            QLineEdit:focus {
                border-color: #00a8ff;
            }
            QTableWidget {
                background-color: #252525;
                color: #fff;
                border: none;
                gridline-color: #333;
                outline: none;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #333;
            }
            QTableWidget::item:hover {
                background-color: #333;
            }
            QTableWidget::item:selected {
                background-color: rgba(0, 168, 255, 100);
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
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #0097e6;
            }
            QPushButton#closeBtn {
                background-color: transparent;
                color: #aaa;
                font-size: 20px;
                padding: 5px 10px;
                min-width: 30px;
            }
            QPushButton#closeBtn:hover {
                color: #fff;
                background-color: rgba(255,255,255,0.1);
            }
            QMenu {
                background-color: #2a2a2a;
                color: #fff;
                border: 1px solid #444;
            }
            QMenu::item {
                padding: 8px 20px;
            }
            QMenu::item:selected {
                background-color: #00a8ff;
            }
        """)

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        title_bar = QWidget()
        title_bar.setStyleSheet("background-color: #252525; border-top-left-radius: 8px; border-top-right-radius: 8px;")
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(10, 5, 10, 5)

        title_label = QLabel("📜 История посещений")
        title_label.setObjectName("titleLabel")
        title_layout.addWidget(title_label)

        title_layout.addStretch()

        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("closeBtn")
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.clicked.connect(self.close)
        title_layout.addWidget(self.close_btn)

        main_layout.addWidget(title_bar)

        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(10, 10, 10, 5)
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("🔍 Поиск в истории...")
        self.search_edit.textChanged.connect(self.filter_history)
        search_layout.addWidget(self.search_edit)
        main_layout.addLayout(search_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Дата/время", "URL"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        self.table.itemDoubleClicked.connect(self.open_selected)
        main_layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(10, 5, 10, 10)

        self.clear_btn = QPushButton("Очистить историю")
        self.clear_btn.clicked.connect(self.clear_history)
        btn_layout.addWidget(self.clear_btn)

        btn_layout.addStretch()

        self.close_bottom_btn = QPushButton("Закрыть")
        self.close_bottom_btn.clicked.connect(self.close)
        btn_layout.addWidget(self.close_bottom_btn)

        main_layout.addLayout(btn_layout)

    def load_history(self):
        """Загружает данные истории в таблицу"""
        self.table.setRowCount(0)
        for item in self.history_data:
            self.add_history_row(item)
        logger.debug(f"Loaded {len(self.history_data)} history items")

    def add_history_row(self, item):
        row = self.table.rowCount()
        self.table.insertRow(row)

        datetime_item = QTableWidgetItem(item.get('visited_at', ''))
        datetime_item.setData(Qt.UserRole, item.get('url', ''))
        self.table.setItem(row, 0, datetime_item)

        url_text = item.get('url', '')
        title_text = item.get('title', '')
        url_item = QTableWidgetItem(url_text)
        if title_text:
            url_item.setToolTip(f"{title_text}\n{url_text}")
        else:
            url_item.setToolTip(url_text)
        self.table.setItem(row, 1, url_item)

    def filter_history(self, text):
        text = text.lower()
        for row in range(self.table.rowCount()):
            url_item = self.table.item(row, 1)
            if not url_item:
                continue
            match = (text in url_item.text().lower() or
                     (url_item.toolTip() and text in url_item.toolTip().lower()))
            self.table.setRowHidden(row, not match)

    def show_context_menu(self, position):
        item = self.table.itemAt(position)
        if not item:
            return
        row = item.row()
        url_item = self.table.item(row, 1)
        if not url_item:
            return
        url = url_item.text()

        menu = QMenu()
        open_action = menu.addAction("🔗 Открыть в текущей вкладке")
        open_action.triggered.connect(lambda: self.open_url(url))
        open_new_action = menu.addAction("➕ Открыть в новой вкладке")
        open_new_action.triggered.connect(lambda: self.open_url_new_tab(url))
        menu.addSeparator()
        copy_action = menu.addAction("📋 Копировать URL")
        copy_action.triggered.connect(lambda: self.copy_url(url))
        delete_action = menu.addAction("🗑 Удалить запись")
        delete_action.triggered.connect(lambda: self.delete_row(row))

        menu.exec_(self.table.viewport().mapToGlobal(position))

    def open_url(self, url):
        if url and self.browser_instance:
            self.browser_instance.navigate(url)
            self.close()

    def open_url_new_tab(self, url):
        if url and self.browser_instance:
            self.browser_instance.add_browser_tab(url=url, is_home=False)
            self.close()

    def copy_url(self, url):
        clipboard = QApplication.clipboard()
        clipboard.setText(url)
        logger.debug(f"URL copied to clipboard: {url}")

    def delete_row(self, row):
        self.table.removeRow(row)
        logger.debug(f"Row {row} removed from history display")

    def clear_history(self):
        self.browser_instance.api.clear_history()
        self.table.setRowCount(0)
        logger.info("History cleared")

    def open_selected(self, item):
        row = item.row()
        url_item = self.table.item(row, 1)
        if url_item:
            self.open_url(url_item.text())