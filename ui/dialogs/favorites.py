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
Упрощённый диалог избранного (быстрые закладки) с удалением по ПКМ - PySide6
Исправлено: унификация импортов, логирование, улучшенная обработка ошибок.
"""
import logging
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QInputDialog, QMessageBox, QMenu
)
from PySide6.QtCore import Qt

logger = logging.getLogger(__name__)

class FavoritesDialog(QDialog):
    """Диалог для быстрого управления закладками"""

    def __init__(self, parent_window, api, current_url="", current_title=""):
        super().__init__(parent_window)
        self.api = api
        self.parent_window = parent_window
        self.current_url = current_url
        self.current_title = current_title
        self.setWindowTitle("Избранное")
        self.setGeometry(100, 100, 500, 400)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.drag_pos = None
        self._setup_styles()
        self._setup_ui()
        self.load_favorites()
        logger.info("FavoritesDialog initialized")

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
            QListWidget {
                background-color: #252525;
                color: #fff;
                border: none;
                border-radius: 5px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #333;
            }
            QListWidget::item:hover {
                background-color: #333;
            }
            QPushButton {
                background-color: #00a8ff;
                color: #fff;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0097e6;
            }
            QMenu {
                background-color: #2a2a2a;
                color: #fff;
                border: none;
                margin: 0px;
                padding: 4px 0px;
            }
            QMenu::item {
                padding: 8px 20px;
                background-color: transparent;
            }
            QMenu::item:selected {
                background-color: #00a8ff;
            }
        """)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("⭐ Избранное"))

        self.list = QListWidget()
        self.list.itemDoubleClicked.connect(self.open_selected)
        self.list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.list)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("➕ Добавить текущую страницу")
        self.add_btn.clicked.connect(self.add_current)
        btn_layout.addWidget(self.add_btn)

        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

    def show_context_menu(self, position):
        item = self.list.itemAt(position)
        if not item:
            return
        menu = QMenu()
        delete_action = menu.addAction("🗑 Удалить")
        bm_id = item.data(Qt.UserRole)
        delete_action.triggered.connect(lambda: self.delete_item(bm_id))
        menu.exec_(self.list.viewport().mapToGlobal(position))

    def delete_item(self, bm_id):
        self.api.delete_bookmark(bm_id)
        self.load_favorites()
        logger.debug(f"Bookmark {bm_id} deleted")

    def load_favorites(self):
        self.list.clear()
        bookmarks = self.api.get_bookmarks()
        for bm in bookmarks:
            if bm['type'] == 'bookmark':
                item = QListWidgetItem(f"🔖 {bm['name']}")
                item.setData(Qt.UserRole, bm['id'])
                item.setData(Qt.UserRole + 1, bm['url'])
                self.list.addItem(item)
        logger.debug(f"Loaded {self.list.count()} favorites")

    def add_current(self):
        if not self.current_url:
            QMessageBox.warning(self, "Ошибка", "Нет активной страницы для добавления.")
            return

        name, ok = QInputDialog.getText(self, "Добавить в избранное",
                                         "Введите название:",
                                         text=self.current_title if self.current_title else self.current_url)
        if ok and name:
            self.api.add_bookmark(name, self.current_url, 'bookmark')
            self.load_favorites()
            logger.info(f"Added bookmark: {name} - {self.current_url}")

    def open_selected(self, item):
        url = item.data(Qt.UserRole + 1)
        if url and self.parent_window:
            self.parent_window.navigate(url)
            self.close()