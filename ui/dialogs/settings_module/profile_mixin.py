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
Миксин для управления профилями.
"""
import logging
from PySide6.QtWidgets import QListWidgetItem, QMessageBox
from PySide6.QtGui import QColor

logger = logging.getLogger(__name__)


class ProfileMixin:
    """Миксин с методами для работы с профилями."""

    def refresh_profile_list(self):
        """Обновляет список профилей с правильным отображением."""
        self.profile_list.clear()
        for name in self.profile_manager.get_profiles():
            item = QListWidgetItem(name)
            if name == self.profile_manager.get_current():
                item.setForeground(QColor("#00a8ff"))
                item.setToolTip("Текущий профиль")
            self.profile_list.addItem(item)
        self.profile_list.doItemsLayout()

    def add_profile(self):
        name = self.profile_name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите имя профиля")
            return
        if name in self.profile_manager.get_profiles():
            QMessageBox.warning(self, "Ошибка", "Профиль с таким именем уже существует")
            return
        if self.profile_manager.add_profile(name):
            QMessageBox.information(self, "Успешно", f"Профиль '{name}' создан")
            self.profile_name_edit.clear()
            self.refresh_profile_list()
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось создать профиль")

    def select_profile(self):
        current_item = self.profile_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Ошибка", "Выберите профиль")
            return
        name = current_item.text()
        if name == self.profile_manager.get_current():
            QMessageBox.information(self, "Информация", "Этот профиль уже выбран")
            return
        if QMessageBox.question(self, "Смена профиля",
                                f"Выбрать профиль '{name}'?\n\nДля применения изменений необходимо перезапустить браузер.",
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            self.profile_manager.set_current(name)
            QMessageBox.information(self, "Готово", "Профиль изменён. Перезапустите браузер.")
            self.accept()

    def delete_profile(self):
        current_item = self.profile_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Ошибка", "Выберите профиль")
            return
        name = current_item.text()
        if name == self.profile_manager.get_current():
            QMessageBox.warning(self, "Ошибка", "Нельзя удалить текущий профиль")
            return
        if name == "Основной":
            QMessageBox.warning(self, "Ошибка", "Нельзя удалить основной профиль")
            return
        if QMessageBox.question(self, "Удаление профиля",
                                f"Удалить профиль '{name}'?\n\nВсе данные профиля будут безвозвратно удалены.",
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            if self.profile_manager.delete_profile(name):
                QMessageBox.information(self, "Готово", f"Профиль '{name}' удалён")
                self.refresh_profile_list()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось удалить профиль")