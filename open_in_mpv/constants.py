from __future__ import annotations

import os
import platform

from platformdirs import user_config_dir, user_log_path, user_runtime_path

__all__ = ('HOST_DATA', 'HOST_DATA_FIREFOX', 'IS_LINUX', 'IS_MAC', 'IS_WIN', 'JSON_FILENAME',
           'LOG_PATH', 'MAC_HOSTS_DIRS', 'MPV_LOG_PATH', 'MPV_SOCKET', 'SYSTEM_HOSTS_DIRS',
           'USER_CHROME_HOSTS_REG_PATH_WIN', 'USER_HOSTS_DIRS')

IS_MAC = bool(platform.mac_ver()[0])
IS_WIN = bool(platform.win32_ver()[0])
IS_LINUX = not IS_MAC and not IS_WIN

JSON_FILENAME = 'sh.tat.open_in_mpv.json'
HOME = os.environ.get('HOME', '')

USER_CHROME_HOSTS_REG_PATH_WIN = r'HKCU:\Software\Google\Chrome\NativeMessagingHosts'

MAC_HOSTS_DIRS = (f'{HOME}/Library/Application Support/Chromium/NativeMessagingHosts',
                  f'{HOME}/Library/Application Support/Google/Chrome Beta/NativeMessagingHosts',
                  f'{HOME}/Library/Application Support/Google/Chrome Canary/NativeMessagingHosts',
                  f'{HOME}/Library/Application Support/Google/Chrome/NativeMessagingHosts',
                  f'{HOME}/Library/Application Support/Mozilla/NativeMessagingHosts')

MACPORTS_BIN_PATH = '/opt/local/bin'

SYSTEM_HOSTS_DIRS = ('/etc/chromium/native-messaging-hosts',
                     '/etc/opt/chrome/native-messaging-hosts',
                     '/etc/opt/edge/native-messaging-hosts')
USER_HOSTS_DIRS = (f'{user_config_dir()}/BraveSoftware/Brave-Browser/NativeMessagingHosts',
                   f'{user_config_dir()}/chromium/NativeMessagingHosts',
                   f'{user_config_dir()}/google-chrome-beta/NativeMessagingHosts',
                   f'{user_config_dir()}/google-chrome-canary/NativeMessagingHosts',
                   f'{user_config_dir()}/google-chrome/NativeMessagingHosts',
                   f'{user_config_dir()}/.mozilla/native-messaging-hosts')

COMMON_HOST_DATA = {
    'description': 'Opens a URL in mpv (for use with extension).',
    'path': None,
    'type': 'stdio'
}
HOST_DATA = COMMON_HOST_DATA | {
    'allowed_origins': ['chrome-extension://jlhcojdohadhkchjpjefbmagpiaedpgc/'],
    'name': 'sh.tat.open_in_mpv',
}
HOST_DATA_FIREFOX = COMMON_HOST_DATA | {
    'allowed_extensions': ['{43e6f3ef-84a0-55f4-b9dd-d879106a24a9}'],
    'name': 'sh.tat.open-in-mpv',
}

try:
    _LOG_DIR_PATH = user_log_path('open-in-mpv', ensure_exists=True)
    MPV_SOCKET = user_runtime_path('open-in-mpv', ensure_exists=True) / 'open-in-mpv.sock'
except PermissionError:  # pragma: no cover
    _LOG_DIR_PATH = user_log_path('open-in-mpv')
    MPV_SOCKET = user_runtime_path('open-in-mpv') / 'open-in-mpv.sock'
LOG_PATH = _LOG_DIR_PATH / 'main.log'
MPV_LOG_PATH = _LOG_DIR_PATH / 'mpv.log'
