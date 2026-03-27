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

import json
import logging
from PySide6.QtCore import QUrl
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

logger = logging.getLogger(__name__)


class NetworkHandler:
    def __init__(self, parent, api):
        self.parent = parent
        self.api = api
        self.network_manager = QNetworkAccessManager()
        self.network_manager.finished.connect(self._on_reply)

    def query_pollinations(self, prompt, context_limit=5):
        # Получаем API-ключ из настроек
        api_key = self.api.get_ai_api_key()
        if not api_key:
            from core.config import DEFAULT_AI_API_KEY
            api_key = DEFAULT_AI_API_KEY
            logger.warning("No API key in settings, using default key")

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
        self.network_manager.post(request, data)
        logger.debug(f"Request sent to {url.toString()}")

    def _on_reply(self, reply):
        if reply.error() == QNetworkReply.NetworkError.NoError:
            data = reply.readAll().data().decode('utf-8')
            try:
                response = json.loads(data)
                answer = response.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
                if not answer:
                    answer = "⚠️ Пустой ответ от сервера."
                self.parent._add_message(answer, is_user=False)
            except json.JSONDecodeError:
                self.parent._add_message(
                    data.strip() if data else "⚠️ Пустой ответ от сервера.",
                    is_user=False,
                    save=False
                )
        else:
            error_msg = f"❌ Ошибка сети: {reply.errorString()}"
            self.parent._add_message(error_msg, is_user=False, save=False)
        self.parent._finish_loading()