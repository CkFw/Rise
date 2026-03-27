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

# api_client.py
import logging
import json
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PySide6.QtCore import QUrl, Signal, QObject

logger = logging.getLogger(__name__)

class AIClient(QObject):
    response_received = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, api, parent=None):
        super().__init__(parent)
        self.api = api
        self.network_manager = QNetworkAccessManager()
        self.network_manager.finished.connect(self._on_reply)
        self.current_reply = None

    def send_message(self, prompt: str):
        # Отменяем предыдущий запрос, если есть
        self.cancel()

        # Получаем API-ключ из настроек пользователя
        api_key = self.api.get_ai_api_key()
        if not api_key:
            # Если ключ не задан, используем встроенный (по умолчанию)
            api_key = "sq-lRdAfPqeFRKKn18lYQgBmafeExBrD8Pr"
            logger.warning("No API key provided, using default key (may not work)")

        payload = {
            "model": "gpt-4o-mini",
            "request": {
                "messages": [
                    {"role": "system", "content": "Ты — дружелюбный AI-ассистент. Отвечай на русском языке."},
                    {"role": "user", "content": prompt}
                ]
            }
        }
        url = QUrl("https://api.onlysq.ru/ai/v2")
        request = QNetworkRequest(url)
        request.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")
        request.setRawHeader(b"Authorization", f"Bearer {api_key}".encode())
        request.setHeader(QNetworkRequest.UserAgentHeader, "RiseBrowser/1.0")

        data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        logger.debug(f"Sending request to {url.toString()}")
        self.current_reply = self.network_manager.post(request, data)

    def cancel(self):
        if self.current_reply and self.current_reply.isRunning():
            logger.debug("Cancelling current request")
            self.current_reply.abort()
            self.current_reply = None

    def _on_reply(self, reply: QNetworkReply):
        if reply != self.current_reply:
            # Игнорируем ответы от старых или отменённых запросов
            reply.deleteLater()
            return
        self.current_reply = None
        if reply.error() == QNetworkReply.NetworkError.NoError:
            data = reply.readAll().data().decode('utf-8')
            try:
                response = json.loads(data)
                answer = response.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
                if not answer:
                    answer = "⚠️ Пустой ответ от сервера."
                self.response_received.emit(answer)
            except json.JSONDecodeError:
                self.response_received.emit(data.strip() if data else "⚠️ Пустой ответ от сервера.")
        else:
            # Операция отмены не считается ошибкой
            if reply.error() != QNetworkReply.NetworkError.OperationCanceledError:
                error_msg = f"❌ Ошибка сети: {reply.errorString()}"
                self.error_occurred.emit(error_msg)
        reply.deleteLater()