#!/usr/bin/env bash

# This file is part of open-in-mpv.
#
# Copyright 2019 Andrew Udvare
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

_BIN_PATH=${_BIN_PATH:-/usr/local/bin}
_BROWSER=${_BROWSER:-chrome}
URI_PREFIX='https://raw.githubusercontent.com/Tatsh/open-in-mpv/master/src'
NATIVE_HOST_FILE_URI="${URI_PREFIX}/sh.tat.open_in_mpv.json.in"
OPEN_IN_MPV_FILE_URI="${URI_PREFIX}/open-in-mpv"
CHROME_HOSTS_DIR_LINUX="${HOME}/.config/google-chrome/NativeMessagingHosts"
CHROME_HOSTS_DIR_MAC="${HOME}/Library/Application Support/Google/Chrome/NativeMessagingHosts"
CHROMIUM_HOSTS_DIR_LINUX="${HOME}/.config/chromium/NativeMessagingHosts"
CHROMIUM_HOSTS_DIR_MAC="${HOME}/Library/Application Support/Chromium/NativeMessagingHosts"

NO_KILL_CHROME=${NO_KILL_CHROME:-false}

main() {
    local hosts_dir

    if ! command -v sudo &> /dev/null; then
        echo 'Please install sudo before using this script.' >&2
        return 1
    fi

    if [[ "$(uname)" == Linux ]]; then
        if [[ $_BROWSER == chrome ]]; then
            hosts_dir="$CHROME_HOSTS_DIR_LINUX"
        elif [[ $_BROWSER == chromium ]]; then
            hosts_dir="$CHROMIUM_HOSTS_DIR_LINUX"
        else
            echo 'Unknown browser.' >&2
            return 1
        fi
    elif command -v sw_vers &> /dev/null; then
        IS_MAC=true
        if [[ $_BROWSER == chrome ]]; then
            hosts_dir="$CHROME_HOSTS_DIR_MAC"
        elif [[ $_BROWSER == chromium ]]; then
            hosts_dir="$CHROMIUM_HOSTS_DIR_MAC"
        else
            echo 'Unknown browser.' >&2
            return 1
        fi
    else
        echo 'Unsupported OS.' >&2
        return 1
    fi

    sudo mkdir -p "$hosts_dir" "$_BIN_PATH"
    curl -q -o "${hosts_dir}/sh.tat.open_in_mpv.json" "$NATIVE_HOST_FILE_URI"
    sed -e "s|@BIN_PATH@|${_BIN_PATH}|" -i "${hosts_dir}/sh.tat.open_in_mpv.json"
    sudo curl -q -o "${_BIN_PATH}/open-in-mpv" "$OPEN_IN_MPV_FILE_URI"
    sudo chown -R "${USER}." "$hosts_dir"
    sudo chmod 0755 "${_BIN_PATH}/open-in-mpv"
    sudo chmod 0755 "${_BIN_PATH}"

    if ! [[ "$NO_KILL_CHROME" ]]; then
        if [[ "$IS_MAC" ]]; then
            if [[ $_BROWSER == chrome ]]; then
                killall 'Google Chrome'
            else
                killall 'Google Chromium'
            fi
        else
            killall chrome
        fi
    fi
}

main
