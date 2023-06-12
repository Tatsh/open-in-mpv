import os
import platform

import xdg.BaseDirectory

__all__ = ('HOST_DATA', 'HOST_DATA_FIREFOX', 'IS_LINUX', 'IS_MAC', 'IS_WIN', 'JSON_FILENAME',
           'MAC_HOSTS_DIRS', 'SYSTEM_HOSTS_DIRS', 'USER_CHROME_HOSTS_REG_PATH_WIN',
           'USER_HOSTS_DIRS')

IS_MAC = bool(platform.mac_ver()[0])
IS_WIN = bool(platform.win32_ver()[0])
IS_LINUX = not IS_MAC and not IS_WIN

JSON_FILENAME = 'sh.tat.open_in_mpv.json'
HOME = os.environ.get('HOME', '')

USER_CHROME_HOSTS_REG_PATH_WIN = 'HKCU:\\Software\\Google\\Chrome\\NativeMessagingHosts'

MAC_HOSTS_DIRS = (f'{HOME}/Library/Application Support/Chromium/NativeMessagingHosts',
                  f'{HOME}/Library/Application Support/Google/Chrome Beta/NativeMessagingHosts',
                  f'{HOME}/Library/Application Support/Google/Chrome Canary/NativeMessagingHosts',
                  f'{HOME}/Library/Application Support/Google/Chrome/NativeMessagingHosts')

SYSTEM_HOSTS_DIRS = ('/etc/chromium/native-messaging-hosts',
                     '/etc/opt/chrome/native-messaging-hosts',
                     '/etc/opt/edge/native-messaging-hosts')
USER_HOSTS_DIRS = (
    f'{xdg.BaseDirectory.xdg_config_home}/BraveSoftware/Brave-Browser/NativeMessagingHosts',
    f'{xdg.BaseDirectory.xdg_config_home}/chromium/NativeMessagingHosts',
    f'{xdg.BaseDirectory.xdg_config_home}/google-chrome-beta/NativeMessagingHosts',
    f'{xdg.BaseDirectory.xdg_config_home}/google-chrome-canary/NativeMessagingHosts',
    f'{xdg.BaseDirectory.xdg_config_home}/google-chrome/NativeMessagingHosts')

COMMON_HOST_DATA = {
    'description': 'Opens a URL in mpv (for use with extension).',
    'path': None,
    'type': 'stdio'
}
HOST_DATA = {
    **COMMON_HOST_DATA,
    # cspell:disable-next-line
    'allowed_origins': ['chrome-extension://ggijpepdpiehgbiknmfpfbhcalffjlbj/'],
    'name': 'sh.tat.open_in_mpv',
}
HOST_DATA_FIREFOX = {
    **COMMON_HOST_DATA,
    'allowed_extensions': ['{43e6f3ef-84a0-55f4-b9dd-d879106a24a9}'],
    'name': 'sh.tat.open-in-mpv',
}
