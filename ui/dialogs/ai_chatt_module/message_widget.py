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

# message_widget.py
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
import re

def markdown_to_html(text):
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    text = text.replace('&', '&amp;')
    return text

class MessageWidget(QWidget):
    def __init__(self, text, is_user, parent=None):
        super().__init__(parent)
        self.original_text = text
        self.is_user = is_user
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        avatar = QLabel()
        avatar.setFixedSize(32, 32)
        avatar.setStyleSheet("border-radius: 16px; background-color: #333;")
        if self.is_user:
            avatar.setText("👤")
            avatar.setAlignment(Qt.AlignCenter)
        else:
            avatar.setText("🤖")
            avatar.setAlignment(Qt.AlignCenter)

        msg_container = QWidget()
        msg_layout = QVBoxLayout(msg_container)
        msg_layout.setContentsMargins(10, 8, 10, 8)
        msg_layout.setSpacing(0)

        msg_label = QLabel()
        msg_label.setWordWrap(True)
        msg_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        msg_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                color: #ffffff;
                font-size: 14px;
            }
        """)
        html_text = markdown_to_html(self.original_text)
        msg_label.setText(html_text)
        msg_layout.addWidget(msg_label)

        if self.is_user:
            msg_container.setStyleSheet("""
                QWidget {
                    background-color: #00a8ff;
                    border-radius: 15px;
                    margin: 2px;
                }
            """)
            layout.addStretch()
            layout.addWidget(msg_container)
            layout.addWidget(avatar)
        else:
            msg_container.setStyleSheet("""
                QWidget {
                    background-color: #2a2a2a;
                    border-radius: 15px;
                    margin: 2px;
                }
            """)
            layout.addWidget(avatar)
            layout.addWidget(msg_container)
            layout.addStretch()

        self.setFixedHeight(msg_label.sizeHint().height() + 30)