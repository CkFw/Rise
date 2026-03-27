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

# ui/dialogs/ai_chatt_module/chat_window.py
import logging
import json
from PySide6.QtCore import Qt, QPoint
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QWidget, QListWidget, QListWidgetItem, QMessageBox, QLineEdit
)

from .message_widget import MessageWidget
from .bridge import AIChatBridge

logger = logging.getLogger(__name__)

class AIChatWindow(QDialog):
    def __init__(self, api, parent=None):
        super().__init__(parent)
        self.api = api
        self.setWindowTitle("🤖 AI Чат")
        self.setGeometry(200, 200, 600, 700)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        self.drag_pos = None
        self.messages = []

        self.bridge = AIChatBridge(api, self)
        self.bridge.reply_ready.connect(self._on_reply)
        self.bridge.error_occurred.connect(self._on_error)
        self.bridge.speech_ready.connect(self._play_audio)
        self.bridge.loading_changed.connect(self._update_cancel_button)
        self.bridge.speaking_changed.connect(self._update_cancel_button)

        self._setup_ui()
        self._load_history()

        if not self.messages:
            self._add_message("Привет! Я ваш AI-помощник. Задавайте любые вопросы.", is_user=False)

        self.message_list.verticalScrollBar().rangeChanged.connect(
            lambda: self.message_list.verticalScrollBar().setValue(
                self.message_list.verticalScrollBar().maximum()
            )
        )

    # ------------------------ UI ------------------------
    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        title_bar = QWidget()
        title_bar.setStyleSheet("background-color: #252525; border-top-left-radius: 8px; border-top-right-radius: 8px;")
        title_bar.setFixedHeight(50)
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(15, 10, 15, 10)

        title_label = QLabel("🤖 AI Чат")
        title_label.setStyleSheet("color: #00a8ff; font-size: 18px; font-weight: bold;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()

        # Кнопка озвучивания (по умолчанию выключена)
        self.speech_btn = QPushButton("🔇")  # выключено
        self.speech_btn.setFixedSize(32, 32)
        self.speech_btn.setCheckable(True)
        self.speech_btn.setChecked(False)  # явно выключено
        self.speech_btn.setToolTip("Озвучивание ответов AI (выкл)")
        self.speech_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #aaa;
                font-size: 18px;
                border: none;
            }
            QPushButton:checked {
                color: #00a8ff;
            }
            QPushButton:hover {
                background-color: rgba(255,255,255,0.1);
                border-radius: 16px;
            }
        """)
        self.speech_btn.toggled.connect(self._on_speech_toggled)
        title_layout.addWidget(self.speech_btn)

        self.clear_btn = QPushButton("🗑 Очистить")
        self.clear_btn.setFixedSize(100, 30)
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #7f8c8d;
                color: #fff;
                border: none;
                border-radius: 5px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #95a5a6;
            }
        """)
        self.clear_btn.clicked.connect(self.clear_history)
        title_layout.addWidget(self.clear_btn)

        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.setStyleSheet("background-color: transparent; color: #aaa; font-size: 18px;")
        self.close_btn.clicked.connect(self.close)
        title_layout.addWidget(self.close_btn)

        main_layout.addWidget(title_bar)

        self.message_list = QListWidget()
        self.message_list.setStyleSheet("""
            QListWidget {
                background-color: #1a1a1a;
                border: none;
                outline: none;
            }
            QListWidget::item {
                padding: 5px;
                border: none;
            }
        """)
        self.message_list.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
        main_layout.addWidget(self.message_list, 1)

        self.typing_label = QLabel("🤖 AI печатает...")
        self.typing_label.setStyleSheet("color: #888; font-size: 12px; padding: 5px 15px; background-color: #252525;")
        self.typing_label.setVisible(False)
        main_layout.addWidget(self.typing_label)

        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(10, 10, 10, 10)
        input_layout.setSpacing(10)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Введите сообщение...")
        self.input_field.returnPressed.connect(self.send_message)
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #252525;
                color: #fff;
                border: 1px solid #444;
                border-radius: 20px;
                padding: 10px 15px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #00a8ff;
            }
        """)
        input_layout.addWidget(self.input_field, 1)

        self.send_btn = QPushButton("➤")
        self.send_btn.setFixedSize(40, 40)
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #00a8ff;
                color: #fff;
                border: none;
                border-radius: 20px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #0097e6;
            }
            QPushButton:disabled {
                background-color: #444;
            }
        """)
        self.send_btn.clicked.connect(self.send_message)

        self.cancel_btn = QPushButton("⏹️")
        self.cancel_btn.setFixedSize(40, 40)
        self.cancel_btn.setVisible(False)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: #fff;
                border: none;
                border-radius: 20px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        self.cancel_btn.clicked.connect(self.cancel_request)

        input_layout.addWidget(self.send_btn)
        input_layout.addWidget(self.cancel_btn)

        main_layout.addLayout(input_layout)

        self.title_bar = title_bar
        self.title_bar.mousePressEvent = self._mouse_press
        self.title_bar.mouseMoveEvent = self._mouse_move
        self.title_bar.mouseReleaseEvent = self._mouse_release

    def _mouse_press(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def _mouse_move(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_pos is not None:
            self.move(event.globalPos() - self.drag_pos)
            event.accept()

    def _mouse_release(self, event):
        self.drag_pos = None
        event.accept()

    # ------------------------ Озвучивание ------------------------
    def _on_speech_toggled(self, checked):
        self.bridge.toggle_speech(checked)
        self.speech_btn.setText("🔊" if checked else "🔇")
        self.speech_btn.setToolTip("Озвучивание ответов AI (вкл)" if checked else "Озвучивание ответов AI (выкл)")

    # ------------------------ Сообщения ------------------------
    def _load_history(self):
        history_json = self.api._get_setting('ai_chat_history', '[]')
        try:
            history = json.loads(history_json)
            for msg in history:
                role = msg.get('role', 'user')
                text = msg.get('content', '')
                if role == 'user':
                    self._add_message(text, is_user=True, save=False)
                else:
                    self._add_message(text, is_user=False, save=False)
            self.messages = history
        except Exception as e:
            logger.error(f"Error loading AI chat history: {e}")

    def _save_history(self):
        to_save = self.messages[-200:]
        self.api._save_setting('ai_chat_history', json.dumps(to_save, ensure_ascii=False))

    def _add_message(self, text, is_user, save=True):
        msg_widget = MessageWidget(text, is_user, self)
        item = QListWidgetItem(self.message_list)
        item.setSizeHint(msg_widget.sizeHint())
        self.message_list.addItem(item)
        self.message_list.setItemWidget(item, msg_widget)

        if not is_user and self.bridge.speech_enabled and save:
            self.bridge.speak_text(text)

        if save:
            role = 'user' if is_user else 'assistant'
            self.messages.append({'role': role, 'content': text})
            self._save_history()

    def clear_history(self):
        confirm = QMessageBox.question(
            self, "Очистить историю",
            "Вы уверены, что хотите удалить всю историю сообщений?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self.message_list.clear()
            self.messages = []
            self._save_history()
            self._add_message("Привет! Я ваш AI-помощник. Задавайте любые вопросы.", is_user=False)

    # ------------------------ Отправка сообщения ------------------------
    def send_message(self):
        if self.bridge.is_speaking or self.bridge.is_loading:
            return
        text = self.input_field.text().strip()
        if not text:
            return

        self._add_message(text, is_user=True)
        self.input_field.clear()
        self.input_field.setEnabled(False)
        self.send_btn.setVisible(False)
        self.typing_label.setVisible(True)

        self.bridge.set_history(self.messages)
        self.bridge.send_message(text)

    def cancel_request(self):
        self.bridge.cancel_request()
        self._finish_loading()

    def _on_reply(self, answer):
        self.typing_label.setVisible(False)
        self._add_message(answer, is_user=False)
        self._finish_loading()

    def _on_error(self, error_msg):
        self.typing_label.setVisible(False)
        if error_msg != "Отменено пользователем":
            self._add_message(error_msg, is_user=False, save=False)
        self._finish_loading()

    def _play_audio(self, file_path):
        self.bridge.play_audio(file_path)

    def _finish_loading(self):
        self.input_field.setEnabled(True)
        self.send_btn.setVisible(True)
        self.cancel_btn.setVisible(False)
        self.input_field.setFocus()

    def _update_cancel_button(self, _):
        visible = self.bridge.is_loading or self.bridge.is_speaking
        self.cancel_btn.setVisible(visible)
        self.send_btn.setVisible(not visible)