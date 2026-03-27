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
Миксин для настроек VPN (PySide6)
Исправлено: использование единого экземпляра Database, логирование.
"""
import logging
from core.database import db
from core.config import (
    DEFAULT_VPN_ENABLED, DEFAULT_VPN_PROTOCOL, DEFAULT_VPN_HOST, DEFAULT_VPN_PORT,
    DEFAULT_VPN_USERNAME, DEFAULT_VPN_PASSWORD,
    DEFAULT_SS_METHOD, DEFAULT_SS_PASSWORD, DEFAULT_SS_LOCAL_PORT,
    DEFAULT_TROJAN_PASSWORD, DEFAULT_TROJAN_SNI, DEFAULT_TROJAN_LOCAL_PORT,
    DEFAULT_VMESS_UUID, DEFAULT_VMESS_ALTERID, DEFAULT_VMESS_SECURITY, DEFAULT_VMESS_LOCAL_PORT,
    DEFAULT_VLESS_UUID, DEFAULT_VLESS_LOCAL_PORT,
    DEFAULT_TUIC_TOKEN, DEFAULT_TUIC_LOCAL_PORT,
    DEFAULT_HYSTERIA_AUTH, DEFAULT_HYSTERIA_LOCAL_PORT,
    DEFAULT_JUICITY_UUID, DEFAULT_JUICITY_LOCAL_PORT
)

logger = logging.getLogger(__name__)

class VPNMixin:
    """Миксин для работы с настройками VPN и прокси"""

    def _get_setting(self, key, default):
        try:
            result = db.execute(
                "SELECT value FROM settings WHERE key = ?",
                (key,), fetchone=True
            )
            return result['value'] if result else default
        except Exception as e:
            logger.error(f"Error getting setting {key}: {e}")
            return default

    def _save_setting(self, key, value):
        try:
            db.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                (key, str(value))
            )
        except Exception as e:
            logger.error(f"Error saving setting {key}: {e}")

    def _get_bool(self, key, default):
        val = self._get_setting(key, '1' if default else '0')
        return val == '1'

    def _save_bool(self, key, value):
        self._save_setting(key, '1' if value else '0')

    def _get_int(self, key, default):
        try:
            return int(self._get_setting(key, str(default)))
        except:
            return default

    def _save_int(self, key, value):
        self._save_setting(key, str(value))

    # === Общие настройки VPN ===
    def get_vpn_enabled(self):
        return self._get_bool('vpn_enabled', DEFAULT_VPN_ENABLED)

    def save_vpn_enabled(self, enabled):
        self._save_bool('vpn_enabled', enabled)

    def get_vpn_protocol(self):
        return self._get_setting('vpn_protocol', DEFAULT_VPN_PROTOCOL)

    def save_vpn_protocol(self, protocol):
        self._save_setting('vpn_protocol', protocol)

    def get_vpn_host(self):
        return self._get_setting('vpn_host', DEFAULT_VPN_HOST)

    def save_vpn_host(self, host):
        self._save_setting('vpn_host', host)

    def get_vpn_port(self):
        return self._get_int('vpn_port', DEFAULT_VPN_PORT)

    def save_vpn_port(self, port):
        self._save_int('vpn_port', port)

    def get_vpn_username(self):
        return self._get_setting('vpn_username', DEFAULT_VPN_USERNAME)

    def save_vpn_username(self, username):
        self._save_setting('vpn_username', username)

    def get_vpn_password(self):
        return self._get_setting('vpn_password', DEFAULT_VPN_PASSWORD)

    def save_vpn_password(self, password):
        self._save_setting('vpn_password', password)

    # === SHADOWSOCKS ===
    def get_ss_method(self):
        return self._get_setting('ss_method', DEFAULT_SS_METHOD)

    def save_ss_method(self, method):
        self._save_setting('ss_method', method)

    def get_ss_password(self):
        return self._get_setting('ss_password', DEFAULT_SS_PASSWORD)

    def save_ss_password(self, password):
        self._save_setting('ss_password', password)

    def get_ss_local_port(self):
        return self._get_int('ss_local_port', DEFAULT_SS_LOCAL_PORT)

    def save_ss_local_port(self, port):
        self._save_int('ss_local_port', port)

    # === TROJAN ===
    def get_trojan_password(self):
        return self._get_setting('trojan_password', DEFAULT_TROJAN_PASSWORD)

    def save_trojan_password(self, password):
        self._save_setting('trojan_password', password)

    def get_trojan_sni(self):
        return self._get_setting('trojan_sni', DEFAULT_TROJAN_SNI)

    def save_trojan_sni(self, sni):
        self._save_setting('trojan_sni', sni)

    def get_trojan_local_port(self):
        return self._get_int('trojan_local_port', DEFAULT_TROJAN_LOCAL_PORT)

    def save_trojan_local_port(self, port):
        self._save_int('trojan_local_port', port)

    # === VMESS ===
    def get_vmess_uuid(self):
        return self._get_setting('vmess_uuid', DEFAULT_VMESS_UUID)

    def save_vmess_uuid(self, uuid):
        self._save_setting('vmess_uuid', uuid)

    def get_vmess_alterid(self):
        return self._get_int('vmess_alterid', DEFAULT_VMESS_ALTERID)

    def save_vmess_alterid(self, alterid):
        self._save_int('vmess_alterid', alterid)

    def get_vmess_security(self):
        return self._get_setting('vmess_security', DEFAULT_VMESS_SECURITY)

    def save_vmess_security(self, security):
        self._save_setting('vmess_security', security)

    def get_vmess_local_port(self):
        return self._get_int('vmess_local_port', DEFAULT_VMESS_LOCAL_PORT)

    def save_vmess_local_port(self, port):
        self._save_int('vmess_local_port', port)

    # === VLESS ===
    def get_vless_uuid(self):
        return self._get_setting('vless_uuid', DEFAULT_VLESS_UUID)

    def save_vless_uuid(self, uuid):
        self._save_setting('vless_uuid', uuid)

    def get_vless_local_port(self):
        return self._get_int('vless_local_port', DEFAULT_VLESS_LOCAL_PORT)

    def save_vless_local_port(self, port):
        self._save_int('vless_local_port', port)

    # === TUIC ===
    def get_tuic_token(self):
        return self._get_setting('tuic_token', DEFAULT_TUIC_TOKEN)

    def save_tuic_token(self, token):
        self._save_setting('tuic_token', token)

    def get_tuic_local_port(self):
        return self._get_int('tuic_local_port', DEFAULT_TUIC_LOCAL_PORT)

    def save_tuic_local_port(self, port):
        self._save_int('tuic_local_port', port)

    # === HYSTERIA ===
    def get_hysteria_auth(self):
        return self._get_setting('hysteria_auth', DEFAULT_HYSTERIA_AUTH)

    def save_hysteria_auth(self, auth):
        self._save_setting('hysteria_auth', auth)

    def get_hysteria_local_port(self):
        return self._get_int('hysteria_local_port', DEFAULT_HYSTERIA_LOCAL_PORT)

    def save_hysteria_local_port(self, port):
        self._save_int('hysteria_local_port', port)

    # === JUICITY ===
    def get_juicity_uuid(self):
        return self._get_setting('juicity_uuid', DEFAULT_JUICITY_UUID)

    def save_juicity_uuid(self, uuid):
        self._save_setting('juicity_uuid', uuid)

    def get_juicity_local_port(self):
        return self._get_int('juicity_local_port', DEFAULT_JUICITY_LOCAL_PORT)

    def save_juicity_local_port(self, port):
        self._save_int('juicity_local_port', port)