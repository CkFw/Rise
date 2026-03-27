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
Вкладка "Профили" в диалоге настроек.
"""
import logging
from PySide6.QtCore import Qt, QRect, QSize
from PySide6.QtGui import QColor, QFontMetrics, QPainter
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QPushButton, QLineEdit, QListWidget, QListWidgetItem,
    QMessageBox, QAbstractItemDelegate, QStyle
)

logger = logging.getLogger(__name__)


class WordWrapDelegate(QAbstractItemDelegate):
    """Делегат для QListWidget, обеспечивающий перенос текста и правильный размер элементов."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

    def paint(self, painter, option, index):
        painter.save()
        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())
        elif option.state & QStyle.State_MouseOver:
            painter.fillRect(option.rect, option.palette.alternateBase())
        else:
            painter.fillRect(option.rect, option.palette.base())

        text = index.data(Qt.DisplayRole)
        if text:
            painter.setPen(option.palette.text().color())
            painter.setFont(option.font)
            rect = option.rect.adjusted(5, 5, -5, -5)
            painter.drawText(rect, Qt.TextWordWrap, text)
        painter.restore()

    def sizeHint(self, option, index):
        text = index.data(Qt.DisplayRole)
        if not text:
            return QSize(0, 0)
        width = self.parent.viewport().width() - 20
        fm = QFontMetrics(option.font)
        rect = fm.boundingRect(QRect(0, 0, width, 0), Qt.TextWordWrap, text)
        return QSize(width, rect.height() + 10)


def setup_profile_tab(self):
    """Создаёт и возвращает вкладку 'Профили'."""
    tab = QWidget()
    layout = QVBoxLayout(tab)
    layout.setSpacing(15)

    layout.addWidget(self._create_info_label(
        "👤 Управление профилями\n\n"
        "Каждый профиль имеет свои настройки, закладки, историю и пароли. "
        "Вы можете создать несколько профилей и переключаться между ними.\n\n"
        "⚠️ После смены профиля необходимо перезапустить браузер."
    ))

    # Создание нового профиля
    add_group = QGroupBox("Создать новый профиль")
    add_layout = QHBoxLayout()
    self.profile_name_edit = QLineEdit()
    self.profile_name_edit.setPlaceholderText("Введите имя профиля")
    add_layout.addWidget(self.profile_name_edit)
    add_btn = QPushButton("➕ Добавить")
    add_btn.clicked.connect(self.add_profile)
    add_layout.addWidget(add_btn)
    add_group.setLayout(add_layout)
    layout.addWidget(add_group)

    # Список профилей
    list_group = QGroupBox("Существующие профили")
    list_layout = QVBoxLayout()
    self.profile_list = QListWidget()
    self.profile_list.setUniformItemSizes(False)
    self.profile_list.setWordWrap(True)
    self.profile_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    self.profile_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
    self.profile_list.setItemDelegate(WordWrapDelegate(self.profile_list))
    list_layout.addWidget(self.profile_list)

    btn_layout = QHBoxLayout()
    select_btn = QPushButton("✅ Выбрать")
    select_btn.clicked.connect(self.select_profile)
    delete_btn = QPushButton("🗑️ Удалить")
    delete_btn.clicked.connect(self.delete_profile)
    btn_layout.addWidget(select_btn)
    btn_layout.addWidget(delete_btn)
    btn_layout.addStretch()
    list_layout.addLayout(btn_layout)

    list_group.setLayout(list_layout)
    layout.addWidget(list_group)

    layout.addStretch()
    self.refresh_profile_list()
    return tab