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

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from ui.dialogs.customize_titlebar import CustomizeTitleBarWindow
from ui.dialogs.customize_titlebar_bg import CustomizeTitleBarBgWindow
from ui.dialogs.customize_urlbar import CustomizeUrlBarWindow
from ui.dialogs.customize_home_bg import CustomizeHomeBackgroundWindow
from ui.dialogs.customize_center import CustomizeCenterWindow
from ui.dialogs.customize_selection import CustomizeSelectionWindow

def setup_customization_tab(self):
    tab = QWidget()
    layout = QVBoxLayout(tab)
    layout.setSpacing(15)

    layout.addWidget(self._create_info_label(
        "🎨 Настройка внешнего вида интерфейса: верхняя панель, фон панели, адресная строка, фон домашней страницы, центр, выделение текста."
    ))

    btn1 = QPushButton("🖌️ Верхняя панель")
    btn1.clicked.connect(self._open_titlebar_customization)
    layout.addWidget(btn1)

    btn2 = QPushButton("🖼️ Фон верхней панели")
    btn2.clicked.connect(self._open_titlebar_bg_customization)
    layout.addWidget(btn2)

    btn3 = QPushButton("🔍 Адресная строка")
    btn3.clicked.connect(self._open_urlbar_customization)
    layout.addWidget(btn3)

    btn4 = QPushButton("🏠 Фон домашней страницы")
    btn4.clicked.connect(self._open_home_bg_customization)
    layout.addWidget(btn4)

    btn5 = QPushButton("🎯 Центр")
    btn5.clicked.connect(self._open_center_customization)
    layout.addWidget(btn5)

    btn6 = QPushButton("✏️ Выделение текста")
    btn6.clicked.connect(self._open_selection_customization)
    layout.addWidget(btn6)

    layout.addStretch()
    return tab