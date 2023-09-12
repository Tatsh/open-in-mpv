# SPDX-License-Identifier: MIT
from functools import lru_cache
from os.path import dirname, exists, expanduser, expandvars, isdir, join as path_join
from typing import Any, BinaryIO, Callable, Final, Mapping, TextIO, cast
import json
import os
import random
import socket
import struct
import subprocess as sp
import sys
import tempfile
import time

from loguru import logger
import click
import xdg.BaseDirectory

from .constants import IS_MAC, IS_WIN, MACPORTS_BIN_PATH

try:
    from win32file import GENERIC_READ, GENERIC_WRITE, OPEN_EXISTING, CreateFile, WriteFile
    from win32pipe import PIPE_READMODE_MESSAGE, SetNamedPipeHandleState  # cspell:disable-line
    import pywintypes  # cspell:disable-line
except ImportError:
    if IS_WIN:
        logger.error('Failed to resolve pywin32. Exiting...') # cspell:disable-line
        os._exit(os.EX_SOFTWARE) # pylint: disable=protected-access


FALLBACKS: Final[dict[str, Any]] = {'log': None, 'socket': None}
CALLBACKS: dict[str, Callable[[str, bool, TextIO, Mapping[str, str]], Any]] = {}


def callback(f: Callable[[str, bool, TextIO, Mapping[str, str]], Any]) -> None:
    CALLBACKS[f.__name__] = f


@lru_cache()
def get_log_path() -> str:
    if IS_MAC:
        return expanduser('~/Library/Logs')
    if IS_WIN:
        return expandvars(r'%LOCALDATA%\open-in-mpv')  # cspell:disable-line
    try:
        return xdg.BaseDirectory.save_state_path('open-in-mpv')
    except KeyError:
        FALLBACKS['log'] = tempfile.TemporaryDirectory(prefix='open-in-mpv')  # pylint: disable=R1732
        return str(FALLBACKS['log'].name)


@lru_cache()
def get_socket_path() -> str:
    if IS_MAC:
        return expanduser('~/Library/Caches/open-in-mpv.sock')
    if IS_WIN:
        return expandvars(r'\\.\pipe\open-in-mpv')
    try:
        return path_join(xdg.BaseDirectory.get_runtime_dir(), 'open-in-mpv.sock')
    except KeyError:
        FALLBACKS['socket'] = tempfile.NamedTemporaryFile(prefix='open-in-mpv', suffix='.sock')  # pylint: disable=R1732
        return str(FALLBACKS['socket'].name)


LOG_PATH = get_log_path()
MPV_SOCKET = get_socket_path()
VERSION = 'v0.1.7'


def environment(data_resp: dict[str, Any], debugging: bool) -> dict[str, Any]:
    env: dict[str, Any] = os.environ.copy()
    if isdir(MACPORTS_BIN_PATH):
        logger.info('Detected MacPorts. Setting PATH.')
        data_resp['macports'] = True
        old_path = os.environ.get('PATH')
        env['PATH'] = MACPORTS_BIN_PATH if not old_path else ':'.join((MACPORTS_BIN_PATH, old_path))
    if debugging:
        logger.debug('Environment:')
        for k, value in env.items():
            logger.debug(f'  {k}={value}')
    return env


def response(data: dict[str, Any]) -> None:
    resp = json.dumps(data).encode()
    size = struct.pack('@i', len(resp))
    stdout_buffer: BinaryIO = sys.stdout.buffer
    stdout_buffer.write(size)
    stdout_buffer.write(resp)


def request(buffer: BinaryIO) -> dict[str, Any]:
    req_len = struct.unpack('@i', buffer.read(4))[0]
    message = json.loads(buffer.read(req_len).decode())
    logger.debug('Message contents (%d): %s', req_len, message)
    return {
        'init': 'init' in message,
        'url': message.get('url', None),
        'debug': message.get('debug', False),
        'single': message.get('single')
    }


def remove_socket() -> bool:
    if FALLBACKS['socket']:
        FALLBACKS['socket'].close()
        return True
    try:
        os.remove(MPV_SOCKET)
    except OSError:
        return False
    return True


def mpv_executable() -> str:
    return 'mpv.exe' if IS_WIN else 'mpv'


@callback
def mpv_launch(url: str, debug: bool, log: TextIO, new_env: Mapping[str, str]) -> None:
    sp.check_call((
        mpv_executable(),
        '--gpu-api=opengl',
        '--player-operation-mode=pseudo-gui',
        '--quiet',
        f'--input-ipc-server={MPV_SOCKET}',
        url,
    ) + ((f'--log-file={log.name}',) if debug else ()),
                    env=new_env,
                    stderr=log,
                    stdout=log)
    if not remove_socket():
        logger.error('Failed to remove socket file.')


@callback
def mpv_launch_socket(url: str, debug: bool, log: TextIO, new_env: Mapping[str, str]) -> None:
    if IS_WIN:
        try:
            handle = CreateFile(MPV_SOCKET, GENERIC_READ | GENERIC_WRITE,
                                0, None, OPEN_EXISTING, 0, None)

            #cspell:disable-next-line
            if (res :=  SetNamedPipeHandleState(handle, PIPE_READMODE_MESSAGE, None, None)) == 0:
                logger.debug(f'SetNamedPipeHandleState return code: {res}')
                CALLBACKS['mpv_and_cleanup'](url, debug, log, new_env)
                return

            WriteFile(handle, json.dumps(dict(command=['loadfile', url],
                                              request_id=random.randint(0x01, 0x7fffffff))
                                              ).encode(errors='strict') + b'\n')
        except pywintypes.error as e: # cspell:disable-line
            match e.args[0]:
                case 2:
                    logger.debug('Pipe not found, retrying in a second')
                    time.sleep(1)
                    CALLBACKS['mpv_launch_socket'](url, debug, log, new_env)
                case 109:
                    logger.debug('Broken pipe')
                    CALLBACKS['mpv_and_cleanup'](url, debug, log, new_env)
    else:
        logger.debug('Sending loadfile command')
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(2)
        try:
            sock.connect(MPV_SOCKET)
            sock.settimeout(None)
            logger.debug('Connected to socket')
            sock.send(json.dumps(dict(command=['loadfile', url])).encode(errors='strict') + b'\n')
        except socket.error:
            logger.exception('Connection refused')
            if not remove_socket():
                logger.error('Failed to remove socket file')
            CALLBACKS['mpv_and_cleanup'](url, debug, log, new_env)


def spawn(func: Callable[[], Any]) -> None:
    """See Stevens' "Advanced Programming in the UNIX Environment" for details
    (ISBN 0201563177).

    Credit: https://stackoverflow.com/a/6011298/374110.

    Takes a callable which will be called in the fork.
    """
    try:
        if os.fork() > 0:
            # parent process, return and keep running
            return
    except OSError as exc:
        logger.exception('Fork #1 failed: %s (%s)', exc.errno, exc.strerror)
        sys.exit(1)
    os.setsid()
    # do second fork
    logger.debug('Second fork')
    try:
        if os.fork() > 0:
            # exit from second parent
            sys.exit(0)
    except OSError as exc:
        logger.exception('Fork #2 failed: %s (%s)', exc.errno, exc.strerror)
        sys.exit(1)
    logger.debug('Calling callback')
    func()
    logger.debug('Callback returned')
    # Exit without calling cleanup handlers
    os._exit(os.EX_OK)  # pylint: disable=protected-access



def real_main(log: TextIO) -> int:
    """
    Actual entry point.

    Standard input is read for a single unsigned integer (1 byte) that represents the length of the
    message. Then the message is expected to be proceed.
    """
    os.makedirs(dirname(MPV_SOCKET), exist_ok=True)
    message: dict[str, Any] = request(sys.stdin.buffer)
    if message['init']:
        response(dict(version=VERSION, logPath=log.name, socketPath=MPV_SOCKET))
        log.close()
        return 0
    if (url := message.get('url', None) is None):
        logger.exception('No URL was given')
        print(json.dumps(dict(message='Missing URL!')))
        return 1
    if (is_debug := message.get('debug', False)):
        logger.info('Debug mode enabled.')
    single: bool = message.get('single', True)
    # MacPorts
    data_resp: dict[str, Any] = dict(version=VERSION, log_path=log.name, message='About to spawn')
    data_resp['env'] = environment(data_resp, is_debug)
    logger.debug('About to spawn')
    response(data_resp)
    if exists(MPV_SOCKET) and single:
        spawn(CALLBACKS['mpv_launch_socket'](cast(str, url), is_debug, log, data_resp['env']))
    else:
        logger.debug('Spawning initial instance')
        spawn(CALLBACKS['mpv_and_cleanup'](cast(str, url), is_debug, log, data_resp['env']))
    logger.debug('mpv should open soon')
    logger.debug('Exiting with status 0')
    if FALLBACKS['log']:
        FALLBACKS['log'].cleanup()
    return 0


class CustomHelp(click.Command):
    def format_help(self, ctx: click.Context, formatter: click.formatting.HelpFormatter) -> None:
        click.echo('This script is intended to be used with the '
                   'Chrome extension. There is no CLI interface for general use.')
        super().format_help(ctx, formatter)


@click.command(cls=CustomHelp, context_settings=dict(allow_extra_args=True))
@click.option('-V', '--version', help='Display version.', is_flag=True)
def main(version: bool = False) -> None:
    if version:
        click.echo(VERSION)
        return
    os.makedirs(LOG_PATH, exist_ok=True)
    out_log_path = path_join(LOG_PATH, 'open-in-mpv.log')
    with open(out_log_path, 'a+') as log:
        real_main(log)
