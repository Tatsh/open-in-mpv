# SPDX-License-Identifier: MIT
import os

import click
import xdg.BaseDirectory

URI_PREFIX = 'https://raw.githubusercontent.com/Tatsh/open-in-mpv/master/src'
NATIVE_HOST_FILE_URI = f'{URI_PREFIX}/sh.tat.open_in_mpv.json.in'

HOME = os.environ.get('HOME', '')
CHROME_BETA_HOSTS_DIR_MAC = (f'{HOME}/Library/Application Support/Google/Chrome Beta'
                             '/NativeMessagingHosts')
CHROME_CANARY_HOSTS_DIR_MAC = (f'{HOME}/Library/Application Support/Google/Chrome Canary'
                               '/NativeMessagingHosts')
CHROME_HOSTS_DIR_MAC = f'{HOME}/Library/Application Support/Google/Chrome/NativeMessagingHosts'
CHROMIUM_HOSTS_DIR_MAC = f'{HOME}/Library/Application Support/Chromium/NativeMessagingHosts'

USER_CHROME_HOSTS_DIR_LINUX = f'{HOME}/.config/google-chrome/NativeMessagingHosts'
USER_CHROME_BETA_HOSTS_DIR_LINUX = (f'{xdg.BaseDirectory.xdg_config_home}/google-chrome-beta/'
                                    'NativeMessagingHosts')
USER_CHROME_CANARY_HOSTS_DIR_LINUX = (f'{xdg.BaseDirectory.xdg_config_home}/google-chrome-canary/'
                                      'NativeMessagingHosts')
USER_CHROMIUM_HOSTS_DIR_LINUX = f'{xdg.BaseDirectory.xdg_config_home}/NativeMessagingHosts'

USER_CHROME_HOSTS_REG_PATH_WIN = 'HKCU:\\Software\\Google\\Chrome\\NativeMessagingHosts'


@click.command()
def main() -> None:
    pass
