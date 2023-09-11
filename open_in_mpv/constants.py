from typing import Final, Sequence
import os
import platform

import xdg.BaseDirectory

__all__ = ('HOST_DATA', 'HOST_DATA_FIREFOX', 'IS_LINUX', 'IS_MAC', 'IS_WIN', 'JSON_FILENAME',
           'MAC_HOSTS_DIRS', 'SYSTEM_HOSTS_DIRS', 'USER_CHROME_HOSTS_REG_PATH_WIN',
           'USER_HOSTS_DIRS')

IS_MAC: Final[bool] = bool(platform.mac_ver()[0])
IS_WIN: Final[bool] = bool(platform.win32_ver()[0])
IS_LINUX: Final[bool] = not IS_MAC and not IS_WIN

JSON_FILENAME: Final[str] = 'sh.tat.open_in_mpv.json'
HOME: Final[str] = os.environ.get('HOME', '')

USER_CHROME_HOSTS_REG_PATH_WIN: Final[str] = 'HKCU:\\Software\\Google\\Chrome\\NativeMessagingHosts'

MAC_HOSTS_DIRS: Final[tuple[str, ...]] = (
    f'{HOME}/Library/Application Support/Chromium/NativeMessagingHosts',
    f'{HOME}/Library/Application Support/Google/Chrome Beta/NativeMessagingHosts',
    f'{HOME}/Library/Application Support/Google/Chrome Canary/NativeMessagingHosts',
    f'{HOME}/Library/Application Support/Google/Chrome/NativeMessagingHosts',
    f'{HOME}/Library/Application Support/Mozilla/NativeMessagingHosts/')

MACPORTS_BIN_PATH: Final[str] = '/opt/local/bin'

SYSTEM_HOSTS_DIRS: Final[tuple[str, str, str]] = ('/etc/chromium/native-messaging-hosts',
                                                  '/etc/opt/chrome/native-messaging-hosts',
                                                  '/etc/opt/edge/native-messaging-hosts')
USER_HOSTS_DIRS: Final[tuple[str, ...]] = (
    f'{xdg.BaseDirectory.xdg_config_home}/BraveSoftware/Brave-Browser/NativeMessagingHosts',
    f'{xdg.BaseDirectory.xdg_config_home}/chromium/NativeMessagingHosts',
    f'{xdg.BaseDirectory.xdg_config_home}/google-chrome-beta/NativeMessagingHosts',
    f'{xdg.BaseDirectory.xdg_config_home}/google-chrome-canary/NativeMessagingHosts',
    f'{xdg.BaseDirectory.xdg_config_home}/google-chrome/NativeMessagingHosts',
    f'{xdg.BaseDirectory.xdg_config_home}/.mozilla/native-messaging-hosts/')

COMMON_HOST_DATA: Final[dict[str, str | None]] = {
    'description': 'Opens a URL in mpv (for use with extension).',
    'path': None,
    'type': 'stdio'
}
HOST_DATA: Final[dict[str, str | None | Sequence[str]]] = {
    **COMMON_HOST_DATA,
    # cspell:disable-next-line
    'allowed_origins': ['chrome-extension://ggijpepdpiehgbiknmfpfbhcalffjlbj/'],
    'name': 'sh.tat.open_in_mpv',
}
HOST_DATA_FIREFOX: Final[dict[str, str | None | Sequence[str]]] = {
    **COMMON_HOST_DATA,
    'allowed_extensions': ['{43e6f3ef-84a0-55f4-b9dd-d879106a24a9}'],
    'name': 'sh.tat.open-in-mpv',
}
