from collections.abc import Sequence
from typing import Final
import os
import platform

from platformdirs import user_config_dir

__all__ = ('HOST_DATA', 'HOST_DATA_FIREFOX', 'IS_LINUX', 'IS_MAC', 'IS_WIN', 'JSON_FILENAME',
           'MAC_HOSTS_DIRS', 'SYSTEM_HOSTS_DIRS', 'USER_CHROME_HOSTS_REG_PATH_WIN',
           'USER_HOSTS_DIRS')

IS_MAC: Final[bool] = bool(platform.mac_ver()[0])
IS_WIN: Final[bool] = bool(platform.win32_ver()[0])
IS_LINUX: Final[bool] = not IS_MAC and not IS_WIN

JSON_FILENAME: Final[str] = 'sh.tat.open_in_mpv.json'
HOME: Final[str] = os.environ.get('HOME', '')

USER_CHROME_HOSTS_REG_PATH_WIN: Final[str] = r'HKCU:\Software\Google\Chrome\NativeMessagingHosts'

MAC_HOSTS_DIRS: Final[tuple[str, ...]] = (
    f'{HOME}/Library/Application Support/Chromium/NativeMessagingHosts',
    f'{HOME}/Library/Application Support/Google/Chrome Beta/NativeMessagingHosts',
    f'{HOME}/Library/Application Support/Google/Chrome Canary/NativeMessagingHosts',
    f'{HOME}/Library/Application Support/Google/Chrome/NativeMessagingHosts',
    f'{HOME}/Library/Application Support/Mozilla/NativeMessagingHosts')

MACPORTS_BIN_PATH: Final[str] = '/opt/local/bin'

SYSTEM_HOSTS_DIRS: Final[tuple[str, str, str]] = ('/etc/chromium/native-messaging-hosts',
                                                  '/etc/opt/chrome/native-messaging-hosts',
                                                  '/etc/opt/edge/native-messaging-hosts')
USER_HOSTS_DIRS: Final[tuple[str, ...]] = (
    f'{user_config_dir()}/BraveSoftware/Brave-Browser/NativeMessagingHosts',
    f'{user_config_dir()}/chromium/NativeMessagingHosts',
    f'{user_config_dir()}/google-chrome-beta/NativeMessagingHosts',
    f'{user_config_dir()}/google-chrome-canary/NativeMessagingHosts',
    f'{user_config_dir()}/google-chrome/NativeMessagingHosts',
    f'{user_config_dir()}/.mozilla/native-messaging-hosts')

COMMON_HOST_DATA: Final[dict[str, str | None]] = {
    'description': 'Opens a URL in mpv (for use with extension).',
    'path': None,
    'type': 'stdio'
}
HOST_DATA: Final[dict[str, str | None | Sequence[str]]] = {
    **COMMON_HOST_DATA,
    'allowed_origins': ['chrome-extension://ggijpepdpiehgbiknmfpfbhcalffjlbj/'],
    'name': 'sh.tat.open_in_mpv',
}
HOST_DATA_FIREFOX: Final[dict[str, str | None | Sequence[str]]] = {
    **COMMON_HOST_DATA,
    'allowed_extensions': ['{43e6f3ef-84a0-55f4-b9dd-d879106a24a9}'],
    'name': 'sh.tat.open-in-mpv',
}
