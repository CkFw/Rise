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
Вкладка "Флаги" в диалоге настроек.
"""
import logging
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QCheckBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QPushButton
)

logger = logging.getLogger(__name__)


def setup_flags_tab(self):
    """Создаёт и возвращает вкладку флагов."""
    tab = QWidget()
    layout = QVBoxLayout(tab)
    layout.setSpacing(15)

    layout.addWidget(self._create_info_label(
        "🚩 Флаги Chromium — экспериментальные функции. Включение/отключение флагов требует перезапуска браузера."
    ))

    self.flags_table = QTableWidget()
    self.flags_table.setColumnCount(2)
    self.flags_table.setHorizontalHeaderLabels(["Флаг", "Включён"])
    self.flags_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
    self.flags_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
    self.flags_table.verticalHeader().setVisible(False)
    self.flags_table.setShowGrid(False)
    self.flags_table.setAlternatingRowColors(True)

    self.flags_table.setStyleSheet("""
        QTableWidget {
            background-color: #252525;
            color: #ffffff;
            border: 1px solid #444;
            border-radius: 5px;
        }
        QTableWidget::item {
            background-color: #252525;
            color: #ffffff;
            padding: 8px;
            border-bottom: 1px solid #333;
        }
        QTableWidget::item:selected {
            background-color: #00a8ff;
        }
        QTableWidget::item:alternate {
            background-color: #1e1e1e;
        }
        QHeaderView::section {
            background-color: #2a2a2a;
            color: #ffffff;
            padding: 8px;
            border: none;
            font-weight: bold;
        }
    """)

    self.flags_list = self.api.get_all_flags_with_descriptions()
    self.flags_table.setRowCount(len(self.flags_list))

    for row, (flag, desc, default) in enumerate(self.flags_list):
        flag_item = QTableWidgetItem(flag)
        flag_item.setToolTip(desc)
        flag_item.setForeground(QColor("#ffffff"))
        flag_item.setFlags(flag_item.flags() & ~Qt.ItemIsEditable)
        self.flags_table.setItem(row, 0, flag_item)

        cb_widget = QWidget()
        cb_layout = QHBoxLayout(cb_widget)
        cb_layout.setContentsMargins(0, 0, 0, 0)
        cb_layout.setAlignment(Qt.AlignCenter)
        cb = QCheckBox()
        cb.setChecked(self.api.get_chromium_flag(flag, default))
        cb.setStyleSheet("background-color: transparent;")
        cb_layout.addWidget(cb)
        self.flags_table.setCellWidget(row, 1, cb_widget)

    layout.addWidget(self.flags_table)

    btn_layout = QHBoxLayout()
    btn_layout.addStretch()
    save_btn = QPushButton("💾 Сохранить флаги")
    save_btn.setProperty("class", "save-btn")
    save_btn.clicked.connect(self.save_flags)
    reset_btn = QPushButton("🔄 Сбросить")
    reset_btn.setProperty("class", "secondary-btn")
    reset_btn.clicked.connect(self.reset_flags)
    btn_layout.addWidget(save_btn)
    btn_layout.addWidget(reset_btn)
    btn_layout.addStretch()
    layout.addLayout(btn_layout)

    return tab