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
Миксин для управления флагами Chromium.
"""
import logging
from PySide6.QtWidgets import QCheckBox, QMessageBox

logger = logging.getLogger(__name__)


class FlagsMixin:
    """Миксин с методами для работы с флагами."""

    def save_flags(self):
        for row in range(self.flags_table.rowCount()):
            flag_item = self.flags_table.item(row, 0)
            if flag_item:
                flag = flag_item.text()
                cb = self.flags_table.cellWidget(row, 1).findChild(QCheckBox)
                if cb:
                    self.api.set_chromium_flag(flag, cb.isChecked())
        QMessageBox.information(
            self,
            "Сохранено",
            "Настройки флагов сохранены. Для применения изменений перезапустите браузер."
        )
        logger.info("Flags settings saved")

    def reset_flags(self):
        for row, (flag, desc, default) in enumerate(self.flags_list):
            cb = self.flags_table.cellWidget(row, 1).findChild(QCheckBox)
            if cb:
                cb.setChecked(default)
        QMessageBox.information(
            self,
            "Сброшено",
            "Флаги сброшены к значениям по умолчанию. Нажмите 'Сохранить', чтобы применить."
        )