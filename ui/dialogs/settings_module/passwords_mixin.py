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
Миксин для вкладки паролей.
"""
import logging
from PySide6.QtWidgets import (
    QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog, QMessageBox, QWidget
)

logger = logging.getLogger(__name__)

class PasswordsMixin:
    """Миксин для управления паролями"""

    def setup_passwords_tab(self):
        """Создаёт и возвращает вкладку паролей"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(QLabel("💾 Управление паролями (CSV)"))
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(QPushButton("📤 Экспорт", clicked=self.export_passwords))
        btn_layout.addWidget(QPushButton("📥 Импорт", clicked=self.import_passwords))
        btn_layout.addWidget(QPushButton("👁 Просмотр", clicked=self.view_passwords))
        layout.addLayout(btn_layout)
        return tab

    def export_passwords(self):
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Экспорт паролей", "passwords.csv", "CSV Files (*.csv)"
        )
        if filepath:
            if self.api.export_passwords(filepath):
                QMessageBox.information(self, "Успешно", "Пароли экспортированы!")
                logger.info(f"Passwords exported to {filepath}")
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось экспортировать!")

    def import_passwords(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Импорт паролей", "", "CSV Files (*.csv)"
        )
        if filepath:
            if self.api.import_passwords(filepath):
                QMessageBox.information(self, "Успешно", "Пароли импортированы!")
                logger.info(f"Passwords imported from {filepath}")
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось импортировать!")

    def view_passwords(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Пароли")
        dialog.setGeometry(100, 100, 600, 400)
        dialog.setStyleSheet(self.styleSheet())

        layout = QVBoxLayout(dialog)
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Сайт", "Логин", "Пароль"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setStyleSheet("border: none;")

        passwords = self.api.get_passwords()
        table.setRowCount(len(passwords))
        for i, pwd in enumerate(passwords):
            table.setItem(i, 0, QTableWidgetItem(pwd.get('site', '')))
            table.setItem(i, 1, QTableWidgetItem(pwd.get('username', '')))
            table.setItem(i, 2, QTableWidgetItem(pwd.get('password', '')))

        layout.addWidget(table)
        layout.addWidget(QPushButton("Закрыть", clicked=dialog.close))
        dialog.exec()