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
Глобальные фильтры событий для мыши и клавиатуры (PySide6)
"""
from PySide6.QtCore import Qt, QEvent, QObject
from PySide6.QtGui import QMouseEvent

class NavigationEventFilter(QObject):
    """
    Перехватывает боковые кнопки мыши (XButton1, XButton2) для навигации назад/вперёд.
    """
    def __init__(self, parent_window):
        super().__init__(parent_window)
        self.window = parent_window

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.MouseButtonPress and isinstance(event, QMouseEvent):
            if event.button() == Qt.MouseButton.XButton1:
                self.window.go_back()
                return True
            elif event.button() == Qt.MouseButton.XButton2:
                self.window.go_forward()
                return True
        return super().eventFilter(obj, event)