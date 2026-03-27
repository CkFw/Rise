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
Диалог управления закладками (без Drag-and-Drop) - PySide6
Исправлено: унификация импортов, логирование, улучшенная обработка ошибок.
"""
import logging
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTreeWidget, QTreeWidgetItem, QInputDialog, QMessageBox,
    QListWidget, QListWidgetItem, QMenu
)
from PySide6.QtCore import Qt

logger = logging.getLogger(__name__)

class BookmarksDialog(QDialog):
    """Диалог управления закладками"""

    def __init__(self, parent_window, api):
        super().__init__(parent_window)
        self.api = api
        self.parent_window = parent_window
        self.setWindowTitle("Закладки")
        self.setGeometry(100, 100, 700, 550)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.drag_pos = None
        self._setup_styles()
        self._setup_ui()
        self.load_bookmarks()
        logger.info("BookmarksDialog initialized")

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
        }
        QLabel {
            color: #fff;
            font-size: 18px;
            font-weight: bold;
            qproperty-alignment: AlignCenter;
            margin-top: 15px;
        }
        QTreeWidget {
            background-color: #252525;
            color: #fff;
            border: none;
            border-radius: 5px;
        }
        QTreeWidget::item {
            padding: 8px;
            border-bottom: 1px solid #333;
        }
        QTreeWidget::item:hover {
            background-color: #333;
        }
        QTreeWidget::item:selected {
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
            padding: 10px 20px;
            border-radius: 5px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #0097e6;
        }
        QPushButton:disabled {
            background-color: #444;
            color: #888;
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
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("🔖 Закладки и папки"))

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Название", "Тип"])

        self.tree.setDragEnabled(False)
        self.tree.setAcceptDrops(False)
        self.tree.setDropIndicatorShown(False)

        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        self.tree.itemDoubleClicked.connect(self.open_bookmark)

        layout.addWidget(self.tree)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(QPushButton("📁 Папка", clicked=self.add_folder))
        btn_layout.addWidget(QPushButton("🔖 Ярлык", clicked=self.add_bookmark))
        btn_layout.addWidget(QPushButton("🗑 Удалить", clicked=self.delete_selected))
        btn_layout.addWidget(QPushButton("Закрыть", clicked=self.close))
        layout.addLayout(btn_layout)

        hint_label = QLabel("💡 Добавляйте ярлыки через кнопку + на домашней странице")
        hint_label.setStyleSheet("color: #888; font-size: 12px; padding: 5px;")
        layout.addWidget(hint_label)

        self.load_bookmarks()

    def show_context_menu(self, position):
        item = self.tree.itemAt(position)
        if not item:
            return

        item_type = item.data(1, Qt.UserRole)

        menu = QMenu()

        if item_type == 'folder':
            menu.addAction("📂 Открыть папку", lambda: self.open_folder_contents(item.data(0, Qt.UserRole), item.text(0)))
            menu.addSeparator()
            menu.addAction("✏️ Переименовать", lambda: self.rename_folder(item))
            menu.addAction("🗑️ Удалить папку", lambda: self.delete_folder(item))
        else:
            menu.addAction("🔗 Открыть ярлык", lambda: self.open_bookmark(item, 0))
            menu.addSeparator()
            menu.addAction("✏️ Переименовать", lambda: self.rename_bookmark(item))
            menu.addAction("🗑️ Удалить ярлык", lambda: self.delete_bookmark(item))

        menu.exec_(self.tree.viewport().mapToGlobal(position))

    def rename_folder(self, item):
        new_name, ok = QInputDialog.getText(self, "Переименовать папку", "Новое название:", text=item.text(0))
        if ok and new_name:
            folder_id = item.data(0, Qt.UserRole)
            # Удаляем старую и создаём новую? Или обновляем через API?
            # В API должна быть функция обновления, но пока реализуем через удаление/создание
            self.api.delete_bookmark(folder_id)
            self.api.add_bookmark(new_name, '', 'folder')
            self.load_bookmarks()
            logger.info(f"Folder renamed to {new_name}")

    def rename_bookmark(self, item):
        new_name, ok = QInputDialog.getText(self, "Переименовать ярлык", "Новое название:", text=item.text(0))
        if ok and new_name:
            bookmark_id = item.data(0, Qt.UserRole)
            url = item.data(2, Qt.UserRole)
            self.api.delete_bookmark(bookmark_id)
            self.api.add_bookmark(new_name, url, 'bookmark')
            self.load_bookmarks()
            logger.info(f"Bookmark renamed to {new_name}")

    def delete_folder(self, item):
        if QMessageBox.warning(
                self, 'Удаление папки',
                'Вместе с папкой будут удалены все ярлыки внутри неё.\n\nПродолжить?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
        ) != QMessageBox.StandardButton.Yes:
            return
        self.api.delete_bookmark(item.data(0, Qt.UserRole))
        self.load_bookmarks()
        logger.info("Folder deleted")

    def delete_bookmark(self, item):
        self.api.delete_bookmark(item.data(0, Qt.UserRole))
        self.load_bookmarks()
        logger.debug("Bookmark deleted")

    def load_bookmarks(self):
        self.tree.clear()
        bookmarks = self.api.get_bookmarks()
        folders = {}
        root_items = []

        for bm in bookmarks:
            if bm['type'] == 'folder':
                item = QTreeWidgetItem([bm['name'], '📁 Папка'])
                item.setData(0, Qt.UserRole, bm['id'])
                item.setData(1, Qt.UserRole, 'folder')
                folders[bm['id']] = item
                if bm['parent_id'] is None:
                    root_items.append(item)

        for item in root_items:
            self.tree.addTopLevelItem(item)

        for bm in bookmarks:
            if bm['type'] == 'bookmark':
                item = QTreeWidgetItem([bm['name'], '🔖 Ярлык'])
                item.setData(0, Qt.UserRole, bm['id'])
                item.setData(1, Qt.UserRole, 'bookmark')
                item.setData(2, Qt.UserRole, bm['url'])
                if bm['parent_id'] and bm['parent_id'] in folders:
                    folders[bm['parent_id']].addChild(item)
                else:
                    self.tree.addTopLevelItem(item)

        self.tree.expandAll()
        logger.debug(f"Loaded {len(bookmarks)} bookmarks")

    def open_bookmark(self, item, column):
        if item.data(1, Qt.UserRole) == 'bookmark':
            url = item.data(2, Qt.UserRole)
            if url and self.parent_window:
                self.parent_window.navigate(url)
                self.close()
        elif item.data(1, Qt.UserRole) == 'folder':
            self.open_folder_contents(item.data(0, Qt.UserRole), item.text(0))

    def open_folder_contents(self, folder_id, folder_name):
        bookmarks = self.api.get_bookmarks_by_parent(folder_id)

        dialog = QDialog(self)
        dialog.setWindowTitle(f"📁 {folder_name}")
        dialog.setGeometry(100, 100, 500, 400)
        dialog.setStyleSheet(self.styleSheet())

        layout = QVBoxLayout(dialog)

        list_widget = QListWidget()
        for bm in bookmarks:
            if bm['type'] == 'bookmark':
                li = QListWidgetItem(f"🔖 {bm['name']}")
                li.setData(Qt.UserRole, bm['url'])
                list_widget.addItem(li)

        def on_item_double_click(item):
            url = item.data(Qt.UserRole)
            if url:
                self.parent_window.navigate(url)
                dialog.close()

        list_widget.itemDoubleClicked.connect(on_item_double_click)
        layout.addWidget(list_widget)

        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)

        dialog.exec()

    def add_folder(self):
        name, ok = QInputDialog.getText(self, "Новая папка", "Название папки:")
        if ok and name:
            self.api.add_bookmark(name, '', 'folder')
            self.load_bookmarks()
            logger.info(f"Folder added: {name}")

    def add_bookmark(self):
        name, ok = QInputDialog.getText(self, "Новый ярлык", "Название:")
        if not ok or not name:
            return
        url, ok = QInputDialog.getText(self, "Новый ярлык", "URL:")
        if ok and url:
            self.api.add_bookmark(name, url, 'bookmark')
            self.load_bookmarks()
            logger.info(f"Bookmark added: {name} - {url}")

    def delete_selected(self):
        item = self.tree.currentItem()
        if item:
            if item.data(1, Qt.UserRole) == 'folder':
                if QMessageBox.warning(
                        self, 'Удаление папки',
                        'Вместе с папкой будут удалены все ярлыки внутри неё.\n\nПродолжить?',
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No
                ) != QMessageBox.StandardButton.Yes:
                    return
            self.api.delete_bookmark(item.data(0, Qt.UserRole))
            self.load_bookmarks()
            logger.info("Selected item deleted")