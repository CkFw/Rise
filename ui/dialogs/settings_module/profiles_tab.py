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
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QInputDialog, QMessageBox, QApplication
)
from PySide6.QtCore import Qt, QTimer

def setup_profiles_tab(self):
    """Создаёт и возвращает вкладку 'Профили'."""
    tab = QWidget()
    layout = QVBoxLayout(tab)
    layout.setSpacing(15)

    layout.addWidget(self._create_info_label(
        "👤 Профили позволяют хранить разные наборы закладок, истории, паролей и настроек.\n"
        "При переключении профиля браузер будет перезапущен."
    ))

    # Список профилей
    self.profiles_list = QListWidget()
    self.profiles_list.setStyleSheet("""
        QListWidget {
            background-color: #252525;
            color: #fff;
            border: 1px solid #444;
            border-radius: 5px;
            outline: none;
        }
        QListWidget::item {
            padding: 10px;
            border-bottom: 1px solid #333;
        }
        QListWidget::item:selected {
            background-color: #00a8ff;
        }
    """)
    layout.addWidget(self.profiles_list)

    # Кнопки управления
    btn_layout = QHBoxLayout()
    self.add_btn = QPushButton("➕ Добавить профиль")
    self.add_btn.clicked.connect(self._add_profile)
    self.select_btn = QPushButton("✅ Выбрать")
    self.select_btn.clicked.connect(self._select_profile)
    self.delete_btn = QPushButton("🗑️ Удалить")
    self.delete_btn.clicked.connect(self._delete_profile)
    btn_layout.addWidget(self.add_btn)
    btn_layout.addWidget(self.select_btn)
    btn_layout.addWidget(self.delete_btn)
    btn_layout.addStretch()
    layout.addLayout(btn_layout)

    layout.addStretch()
    self._load_profiles()
    return tab

def _load_profiles(self):
    """Загружает список профилей."""
    self.profiles_list.clear()
    profiles = self.api.get_profiles()
    active = self.api.get_active_profile()
    for p in profiles:
        item = QListWidgetItem(p['name'])
        if active and active['id'] == p['id']:
            item.setBackground(Qt.green)
            item.setToolTip("Активный профиль")
        self.profiles_list.addItem(item)
        item.setData(Qt.UserRole, p['id'])

def _add_profile(self):
    name, ok = QInputDialog.getText(self, "Добавить профиль", "Введите имя профиля:")
    if ok and name:
        if self.api.add_profile(name):
            self._load_profiles()
            QMessageBox.information(self, "Готово", f"Профиль '{name}' добавлен.")
        else:
            QMessageBox.warning(self, "Ошибка", "Профиль с таким именем уже существует.")

def _select_profile(self):
    current = self.profiles_list.currentItem()
    if not current:
        QMessageBox.warning(self, "Ошибка", "Выберите профиль.")
        return
    profile_id = current.data(Qt.UserRole)
    active = self.api.get_active_profile()
    if active and active['id'] == profile_id:
        QMessageBox.information(self, "Информация", "Этот профиль уже активен.")
        return
    reply = QMessageBox.question(
        self, "Переключение профиля",
        "Для применения профиля браузер будет перезапущен. Продолжить?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    if reply == QMessageBox.StandardButton.Yes:
        self.api.set_active_profile(profile_id)
        QMessageBox.information(self, "Перезапуск", "Браузер будет перезапущен.")
        QTimer.singleShot(100, lambda: QApplication.quit())
        # После завершения приложение будет перезапущено (можно использовать QProcess)

def _delete_profile(self):
    current = self.profiles_list.currentItem()
    if not current:
        QMessageBox.warning(self, "Ошибка", "Выберите профиль.")
        return
    profile_id = current.data(Qt.UserRole)
    active = self.api.get_active_profile()
    if active and active['id'] == profile_id:
        QMessageBox.warning(self, "Ошибка", "Нельзя удалить активный профиль.")
        return
    reply = QMessageBox.question(
        self, "Удаление профиля",
        "Все данные профиля будут удалены без возможности восстановления. Продолжить?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    if reply == QMessageBox.StandardButton.Yes:
        self.api.delete_profile(profile_id)
        self._load_profiles()