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

# ui/dialogs/settings.py
"""
Диалог настроек браузера (PySide6) – финальная версия.
Разделен на модули. Вкладка звуков клавиатуры добавлена.
"""
import os
import logging
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QWidget, QCheckBox, QLineEdit, QTextEdit, QMessageBox,
    QGroupBox, QScrollArea, QSpinBox, QComboBox, QFileDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QGridLayout, QListWidget, QListWidgetItem,
    QSlider, QAbstractItemView, QStyleOptionViewItem, QAbstractItemDelegate, QStyle
)
from PySide6.QtCore import Qt, QEvent, QUrl, QSize, QRect
from PySide6.QtGui import QMouseEvent, QDesktopServices, QColor, QFont, QPainter, QFontMetrics
from PySide6.QtWebEngineCore import QWebEngineProfile
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput, QSoundEffect

from core.config import DATA_DIR, ADBLOCK_MODE_NAMES
from core.utils import resource_path
from core.profile_manager import ProfileManager

from ui.dialogs.settings_module.base_mixin import BaseMixin
from ui.dialogs.settings_module.search_mixin import SearchMixin
from ui.dialogs.settings_module.passwords_mixin import PasswordsMixin
from ui.dialogs.settings_module.performance_mixin import PerformanceMixin
from ui.dialogs.settings_module.i2p_mixin import I2PMixin
from ui.dialogs.settings_module.vpn_mixin import VPNMixin
from ui.dialogs.settings_module.dpi_mixin import DPIMixin
from ui.dialogs.settings_module.internet_tab import setup_internet_tab
from ui.dialogs.settings_module.ai_chat_tab import setup_ai_chat_tab
from ui.dialogs.settings_module.customization_tab import setup_customization_tab
from ui.dialogs.settings_module.functions_tab import setup_functions_tab
from ui.dialogs.settings_module.profile_tab import setup_profile_tab
from ui.dialogs.settings_module.flags_tab import setup_flags_tab
from ui.dialogs.settings_module.keyboard_sounds_tab import setup_keyboard_sounds_tab

from ui.dialogs.customize_titlebar import CustomizeTitleBarWindow
from ui.dialogs.customize_titlebar_bg import CustomizeTitleBarBgWindow
from ui.dialogs.customize_urlbar import CustomizeUrlBarWindow
from ui.dialogs.customize_home_bg import CustomizeHomeBackgroundWindow
from ui.dialogs.customize_center import CustomizeCenterWindow
from ui.dialogs.customize_selection import CustomizeSelectionWindow

logger = logging.getLogger(__name__)


class SettingsDialog(
    QDialog,
    BaseMixin,
    SearchMixin,
    PasswordsMixin,
    PerformanceMixin,
    I2PMixin,
    VPNMixin,
    DPIMixin
):
    """Диалог настроек браузера – объединение всех миксинов"""

    def __init__(self, parent_window, api):
        super().__init__(parent_window)
        self.api = api
        self.parent_window = parent_window
        self.setWindowTitle("Настройки")
        self.setGeometry(100, 100, 700, 950)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.drag_pos = None
        self.window_pos = None

        self.profile_manager = ProfileManager()  # для работы с профилями

        self._setup_ui()
        self._load_config()
        logger.info("SettingsDialog initialized")

    def eventFilter(self, obj, event):
        if obj == self.title_bar:
            if event.type() == QEvent.Type.MouseButtonPress:
                mouse_event = QMouseEvent(event)
                if mouse_event.button() == Qt.MouseButton.LeftButton:
                    self.drag_pos = mouse_event.globalPos() - self.frameGeometry().topLeft()
                    self.window_pos = self.pos()
                    return True
            elif event.type() == QEvent.Type.MouseMove:
                if event.buttons() == Qt.MouseButton.LeftButton and self.drag_pos is not None:
                    self.move(event.globalPos() - self.drag_pos)
                    return True
            elif event.type() == QEvent.Type.MouseButtonRelease:
                if event.button() == Qt.MouseButton.LeftButton:
                    self.drag_pos = None
                    self.window_pos = None
                    return True
        return super().eventFilter(obj, event)

    def _setup_styles(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
                border: 1px solid #333;
                border-radius: 12px;
            }
            QLabel#titleLabel {
                color: #00a8ff;
                font-size: 22px;
                font-weight: bold;
                padding: 5px 10px;
                background-color: transparent;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 14px;
            }
            QLabel.info-label {
                color: #aaa;
                font-size: 13px;
                padding: 12px;
                background-color: #252525;
                border-radius: 8px;
                border-left: 4px solid #00a8ff;
                margin-bottom: 15px;
                line-height: 1.5;
            }
            QLabel.section-title {
                color: #00a8ff;
                font-size: 16px;
                font-weight: bold;
                padding: 5px 0;
            }
            QLabel.note-label {
                color: #f39c12;
                font-size: 12px;
                padding: 5px;
                background-color: #2a2a2a;
                border-radius: 4px;
                margin-top: 5px;
            }
            QComboBox, QSpinBox, QCheckBox, QLineEdit, QTextEdit, QSlider {
                background-color: #252525;
                color: #fff;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
            }
            QComboBox {
                min-height: 30px;
                padding: 4px 8px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 20px;
                border-left: 1px solid #444;
                border-top-right-radius: 5px;
                border-bottom-right-radius: 5px;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
                background-color: #aaa;
            }
            QComboBox QAbstractItemView {
                background-color: #252525;
                color: #fff;
                border: 1px solid #444;
                selection-background-color: #00a8ff;
                selection-color: #fff;
                outline: none;
                min-width: 150px;
            }
            QComboBox QAbstractItemView::item {
                padding: 8px 12px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #333;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #00a8ff;
            }
            QLineEdit {
                min-width: 300px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #444;
                height: 6px;
                background: #252525;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #00a8ff;
                width: 14px;
                height: 14px;
                margin: -4px 0;
                border-radius: 7px;
            }
            QGroupBox {
                color: #00a8ff;
                border: 1px solid #444;
                border-radius: 8px;
                margin-top: 15px;
                font-weight: bold;
                font-size: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                background-color: #1a1a1a;
            }
            QPushButton {
                background-color: #00a8ff;
                color: #fff;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                transition: background-color 0.2s ease, transform 0.05s linear;
                transform-origin: center;
                overflow: visible;
            }
            QPushButton:hover {
                background-color: #0097e6;
            }
            QPushButton:active {
                transform: scale(0.98);
            }
            QPushButton:disabled {
                background-color: #444;
                color: #888;
                transform: none;
            }
            QPushButton.save-btn {
                background-color: #27ae60;
                font-size: 15px;
                padding: 12px 30px;
                min-width: 220px;
                border-radius: 25px;
            }
            QPushButton.save-btn:hover {
                background-color: #2ecc71;
            }
            QPushButton.save-btn:active {
                transform: scale(0.98);
            }
            QPushButton.secondary-btn {
                background-color: #7f8c8d;
            }
            QPushButton.secondary-btn:hover {
                background-color: #95a5a6;
            }
            QPushButton.secondary-btn:active {
                transform: scale(0.98);
            }
            QPushButton#closeBtn {
                background-color: transparent;
                color: #aaa;
                font-size: 22px;
                padding: 5px 10px;
                min-width: 40px;
                border-radius: 20px;
                transition: background-color 0.2s ease;
            }
            QPushButton#closeBtn:hover {
                color: #fff;
                background-color: rgba(255,255,255,0.1);
            }
            QTabWidget::pane {
                border: none;
                background-color: #1a1a1a;
                border-radius: 10px;
            }
            QTabBar::tab {
                background-color: #252525;
                color: #fff;
                padding: 12px 20px;
                border: 1px solid #333;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-size: 14px;
                min-width: 80px;
            }
            QTabBar::tab:selected {
                background-color: #00a8ff;
                border-bottom: none;
            }
            QTabBar::tab:hover:!selected {
                background-color: #333;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollArea > QWidget {
                background-color: transparent;
            }
            QStackedWidget {
                background-color: transparent;
            }
            QTableWidget {
                background-color: #252525;
                color: #fff;
                border: 1px solid #444;
                border-radius: 8px;
                gridline-color: #333;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #333;
                color: #fff;
            }
            QTableWidget::item:selected {
                background-color: #00a8ff;
            }
            QHeaderView::section {
                background-color: #2a2a2a;
                color: #fff;
                padding: 8px;
                border: none;
                font-weight: bold;
                font-size: 14px;
            }
            QFrame.separator {
                background-color: #333;
                max-height: 1px;
                min-height: 1px;
                margin: 15px 0;
            }
            QGridLayout {
                spacing: 10px;
            }
            QListWidget {
                background-color: #252525;
                color: #fff;
                border: 1px solid #444;
                border-radius: 8px;
                outline: none;
                min-height: 200px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #333;
                white-space: normal;
                word-wrap: break-word;
            }
            QListWidget::item:selected {
                background-color: #00a8ff;
            }
        """)

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.title_bar = QWidget()
        self.title_bar.setStyleSheet("background-color: #252525; border-top-left-radius: 12px; border-top-right-radius: 12px;")
        self.title_bar.setFixedHeight(70)
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(20, 10, 20, 10)

        title_icon = QLabel("⚙️")
        title_icon.setStyleSheet("font-size: 28px; margin-right: 5px;")
        title_layout.addWidget(title_icon)

        title_label = QLabel("Настройки")
        title_label.setObjectName("titleLabel")
        title_layout.addWidget(title_label)

        title_layout.addStretch()

        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("closeBtn")
        self.close_btn.setFixedSize(40, 40)
        self.close_btn.clicked.connect(self.reject)
        title_layout.addWidget(self.close_btn)

        main_layout.addWidget(self.title_bar)
        self.title_bar.installEventFilter(self)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(15, 15, 15, 15)
        self._setup_styles()

        tabs = QTabWidget()
        tabs.addTab(self.setup_search_tab(), "🔍 Поиск")
        tabs.addTab(self.setup_passwords_tab(), "🔑 Пароли")
        tabs.addTab(self.setup_performance_tab(), "⚡ Производительность")
        tabs.addTab(setup_functions_tab(self), "⚙️ Функции")
        tabs.addTab(setup_profile_tab(self), "👤 Профиль")
        tabs.addTab(self.setup_i2p_tab(), "🧅 I2P")
        tabs.addTab(self.setup_vpn_tab(), "🔐 VPN")
        tabs.addTab(self.setup_dpi_tab(), "🛡️ DPI")
        tabs.addTab(setup_customization_tab(self), "🎨 Кастомизация")
        tabs.addTab(setup_flags_tab(self), "🚩 Флаги")
        tabs.addTab(setup_internet_tab(self), "🌐 Интернет")
        tabs.addTab(setup_ai_chat_tab(self), "🤖 AI Чат")
        tabs.addTab(setup_keyboard_sounds_tab(self), "🔊 Звук клавиатуры")

        content_layout.addWidget(tabs)
        main_layout.addWidget(content_widget)

    # ---------- Вспомогательные методы ----------
    def _create_info_label(self, text):
        label = QLabel(text)
        label.setProperty("class", "info-label")
        label.setWordWrap(True)
        return label

    def _create_note_label(self, text):
        label = QLabel(text)
        label.setProperty("class", "note-label")
        label.setWordWrap(True)
        return label

    # ---------- Методы профиля ----------
    def refresh_profile_list(self):
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

    # ---------- Методы флагов ----------
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

    # ---------- Вкладка поиска (SearchMixin) ----------
    def setup_search_tab(self):
        return super().setup_search_tab()

    # ---------- Вкладка паролей (PasswordsMixin) ----------
    def setup_passwords_tab(self):
        return super().setup_passwords_tab()

    # ---------- Вкладка производительности (PerformanceMixin) ----------
    def setup_performance_tab(self):
        return super().setup_performance_tab()

    # ---------- Вкладка I2P (I2PMixin) ----------
    def setup_i2p_tab(self):
        return super().setup_i2p_tab()

    # ---------- Вкладка VPN (VPNMixin) ----------
    def setup_vpn_tab(self):
        return super().setup_vpn_tab()

    # ---------- Вкладка DPI (DPIMixin) ----------
    def setup_dpi_tab(self):
        return super().setup_dpi_tab()

    # ---------- Методы сохранения для вкладок Интернет и AI ----------
    def save_internet_settings(self):
        self.api.set_doh_enabled(self.doh_check.isChecked())
        self.api.set_doh_provider(self.doh_combo.currentText())
        self.api.set_quic_enabled(self.quic_check.isChecked())
        self.api.set_webrtc_enabled(self.webrtc_check.isChecked())
        self.api.set_ipv6_enabled(self.ipv6_check.isChecked())
        self.api.set_tcp_buffer_size(self.tcp_spin.value())
        QMessageBox.information(self, "Готово", "Настройки сети сохранены.")
        logger.info("Internet settings saved")

    def save_ai_settings(self):
        self.api.set_ai_chat_enabled(self.ai_chat_check.isChecked())
        provider_map = {
            "Бесплатный GPT (Free GPT API)": "free_gpt",
        }
        selected = self.ai_provider_combo.currentText()
        self.api.set_ai_provider(provider_map.get(selected, "free_gpt"))
        self.api.set_ai_api_key(self.ai_api_key_edit.text().strip())

        lang_display = self.ai_lang_combo.currentText()
        lang_code = self.voice_map[lang_display]["code"]
        self.api.set_ai_voice_language(lang_code)
        voice_code = self.ai_voice_combo.currentData()
        if voice_code:
            self.api.set_ai_voice_name(voice_code)

        logger.info("AI chat settings saved")

    def _update_ai_voices(self, lang_name):
        self.ai_voice_combo.clear()
        voices = self.voice_map[lang_name]["voices"]
        for display_name, voice_code in voices.items():
            self.ai_voice_combo.addItem(display_name, voice_code)

    # ---------- Методы сохранения для вкладки Функции ----------
    def save_functions_settings(self):
        self.api.save_pdf_separate_enabled(self.pdf_separate_check.isChecked())
        self.api.save_pdf_viewer_enabled(self.pdf_viewer_check.isChecked())
        self.api.save_adblock_enabled(self.adblock_check.isChecked())
        mode_index = self.adblock_mode_combo.currentIndex()
        mode_map = ["simple", "advanced", "smart"]
        self.api.save_adblock_mode(mode_map[mode_index])
        self.api.save_translate_enabled(self.translate_check.isChecked())
        self.api.save_fullscreen_support_enabled(self.fullscreen_check.isChecked())
        QMessageBox.information(self, "Готово", "Настройки функций сохранены.")
        logger.info("Functions settings saved")

    # ---------- Методы для открытия диалогов кастомизации ----------
    def _open_titlebar_customization(self):
        dlg = CustomizeTitleBarWindow(self.api, self)
        dlg.applied.connect(self._on_titlebar_applied)
        dlg.exec()

    def _open_titlebar_bg_customization(self):
        dlg = CustomizeTitleBarBgWindow(self.api, self)
        dlg.applied.connect(self._on_titlebar_applied)
        dlg.exec()

    def _open_urlbar_customization(self):
        dlg = CustomizeUrlBarWindow(self.api, self)
        dlg.applied.connect(self._on_urlbar_applied)
        dlg.exec()

    def _open_home_bg_customization(self):
        dlg = CustomizeHomeBackgroundWindow(self.api, self)
        dlg.applied.connect(self._on_home_bg_applied)
        dlg.exec()

    def _open_center_customization(self):
        dlg = CustomizeCenterWindow(self.api, self)
        dlg.applied.connect(self._on_center_applied)
        dlg.exec()

    def _open_selection_customization(self):
        dlg = CustomizeSelectionWindow(self.api, self)
        dlg.applied.connect(self._on_selection_applied)
        dlg.exec()

    def _on_titlebar_applied(self):
        if self.parent_window and hasattr(self.parent_window, 'apply_titlebar_customization'):
            self.parent_window.apply_titlebar_customization()

    def _on_urlbar_applied(self):
        if self.parent_window and hasattr(self.parent_window, 'apply_urlbar_customization'):
            self.parent_window.apply_urlbar_customization()

    def _on_home_bg_applied(self):
        if self.parent_window and hasattr(self.parent_window, 'update_current_home_page'):
            self.parent_window.update_current_home_page()

    def _on_center_applied(self):
        if self.parent_window and hasattr(self.parent_window, 'update_current_home_page'):
            self.parent_window.update_current_home_page()

    def _on_selection_applied(self):
        if self.parent_window and hasattr(self.parent_window, 'apply_selection_style'):
            self.parent_window.apply_selection_style()

    # ---------- Методы для вкладки "Звук клавиатуры" ----------
    def _browse_keyboard_sound(self):
        """Открывает диалог выбора звукового файла для клавиатуры."""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Выберите звуковой файл", "",
            "Audio files (*.wav *.mp3 *.ogg);;All files (*)"
        )
        if filepath:
            self.keyboard_sound_path_edit.setText(filepath)

    def save_keyboard_sounds_settings(self):
        """Сохраняет настройки звуков клавиатуры."""
        self.api.set_keyboard_sounds_enabled(self.keyboard_sounds_check.isChecked())
        self.api.set_keyboard_sound_path(self.keyboard_sound_path_edit.text())
        self.api.set_keyboard_sound_volume(self.keyboard_sound_volume_slider.value())
        # Обновляем менеджер звука в главном окне
        if hasattr(self.parent_window, 'keyboard_sound'):
            self.parent_window.keyboard_sound.update_settings(
                enabled=self.keyboard_sounds_check.isChecked(),
                path=self.keyboard_sound_path_edit.text(),
                volume=self.keyboard_sound_volume_slider.value()
            )
        QMessageBox.information(self, "Готово", "Настройки звука клавиатуры сохранены.")
        logger.info("Keyboard sounds settings saved")

    # ---------- Сохранение всех настроек ----------
    def save_all_settings(self):
        self.save_performance_settings()
        self.save_i2p_settings()
        self.save_vpn_settings()
        self.save_dpi_settings()
        self.save_internet_settings()
        self.save_ai_settings()
        self.save_flags()
        self._save_config()
        QMessageBox.information(
            self,
            "Готово",
            "Настройки сохранены. Для некоторых изменений может потребоваться перезапуск браузера."
        )
        logger.info("All settings saved")
        self.accept()