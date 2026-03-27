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
Отдельное окно для просмотра PDF в браузере - PySide6
Исправлено: добавлено логирование.
"""
import os
import logging
from PySide6.QtCore import Qt, QUrl
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings

logger = logging.getLogger(__name__)

class PDFViewerWindow(QMainWindow):
    """
    Отдельное окно для отображения PDF-файла с использованием QWebEngineView.
    """
    def __init__(self, filepath, parent=None):
        super().__init__(parent)
        self.filepath = filepath
        self.setWindowTitle(f"PDF: {os.path.basename(filepath)}")
        self.setGeometry(200, 200, 800, 600)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self.web_view = QWebEngineView()
        settings = self.web_view.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.PdfViewerEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)

        self.web_view.load(QUrl.fromLocalFile(filepath))
        layout.addWidget(self.web_view)

        btn_layout = QHBoxLayout()
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.close)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

        logger.info(f"PDFViewerWindow opened for {filepath}")