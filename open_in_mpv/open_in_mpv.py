# SPDX-License-Identifier: MIT
import functools
from os.path import isdir
from typing import Any, BinaryIO, Callable, Unpack
import json
import os
import random
import socket
import struct
import subprocess as sp
import sys
import time

from loguru import logger
import click

from .constants import IS_WIN, MACPORTS_BIN_PATH, MPV_EXEC
from .io import Io
from .typing import Mpv, MpvParameters
from .version import VERSION

try:
    from win32file import GENERIC_READ, GENERIC_WRITE, OPEN_EXISTING, CreateFile, WriteFile
    from win32pipe import PIPE_READMODE_MESSAGE, SetNamedPipeHandleState  # cspell:disable-line
    import pywintypes
except ImportError:
    if IS_WIN:
        logger.error('Failed to resolve pywin32. Exiting...')
        sys.exit(os.EX_SOFTWARE)


def callback(func: Mpv) -> Callable[[], Any]:
    @functools.wraps
    def wrapper(**kwargs: MpvParameters) -> Callable[[], Any]:
        return func(**kwargs)

    return wrapper


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


@callback
def mpv_launch(**kwargs: Unpack[MpvParameters]) -> None:
    kwargs['io'].logging.debug('Spawning initial instance')
    sp.check_call((
        MPV_EXEC,
        '--gpu-api=opengl',
        '--player-operation-mode=pseudo-gui',
        '--quiet',
        f'--input-ipc-server={kwargs["io"].socket_path}',
        kwargs['url'],
    ) + ((f'--log-file={kwargs["io"].log_path}',) if kwargs['debug'] else ()),
                    env=kwargs['environment'],
                    stderr=sys.stderr,
                    stdout=sys.stdout)
    if not kwargs['io'].remove_socket():
        kwargs['io'].logging.error('Failed to remove socket file.')


@callback
def mpv_launch_socket(**kwargs: Unpack[MpvParameters]) -> None:
    kwargs['io'].logging.debug('Sending loadfile command')
    if IS_WIN:
        try:
            logger.debug('open-in-mpv running on Windows.')
            handle = CreateFile(kwargs['io'].socket_path, GENERIC_READ | GENERIC_WRITE,
                                0, None, OPEN_EXISTING, 0, None)
            #cspell:disable-next-line
            if (res :=  SetNamedPipeHandleState(handle, PIPE_READMODE_MESSAGE, None, None)) == 0:
                kwargs['io'].logging.debug(f'SetNamedPipeHandleState return code: {res}')
                spawn(mpv_launch(**kwargs), kwargs['io'])
                return
            WriteFile(handle, json.dumps(dict(command=['loadfile', kwargs['url']],
                                              request_id=random.randint(0x01, 0x7fffffff))
                                              ).encode(errors='strict') + b'\n')
        except pywintypes.error as e:
            match e.args[0]:
                case 2:
                    kwargs['io'].logging.debug('Pipe not found, retrying in a second')
                    time.sleep(1)
                    spawn(mpv_launch_socket(**kwargs), kwargs['io'])
                case 109:
                    kwargs['io'].logging.debug('Broken pipe')
                    spawn(mpv_launch(**kwargs), kwargs['io'])
    else:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(2)
        try:
            sock.connect(kwargs['io'].socket_path)
            sock.settimeout(None)
            kwargs['io'].logging.debug('Connected to socket')
            sock.send(json.dumps(dict(command=['loadfile', kwargs['url']])).encode(errors='strict') + b'\n')
        except socket.error:
            logger.exception('Connection refused')
            if not kwargs['io'].remove_socket():
                kwargs['io'].logging.error('Failed to remove socket file')
            spawn(mpv_launch(**kwargs), kwargs['io'])


def spawn(func: Callable[[], Any], io: Io) -> None:
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
        io.logging.exception(f'Fork #1 failed: {exc.errno} ({exc.strerror})')
        sys.exit(1)
    os.setsid()
    # do second fork
    io.logging.debug('Second fork')
    try:
        if os.fork() > 0:
            # exit from second parent
            sys.exit(0)
    except OSError as exc:
        io.logging.exception(f'Fork #2 failed: {exc.errno} ({exc.strerror})')
        sys.exit(1)
    io.logging.debug('Calling callback')
    func()
    io.logging.debug('Callback returned')
    # Exit without calling cleanup handlers
    os._exit(os.EX_OK)  # pylint: disable=protected-access


class CustomHelp(click.Command):
    def format_help(self, ctx: click.Context, formatter: click.formatting.HelpFormatter) -> None:
        click.echo('This script is intended to be used with the '
                   'Chrome extension. There is no CLI interface for general use.')
        super().format_help(ctx, formatter)


@click.command(cls=CustomHelp, context_settings=dict(allow_extra_args=True))
@click.option('-V', '--version', help='Display version.', is_flag=True)
def main(version: bool = False) -> int:
    io: Io = Io()
    if version:
        click.echo(VERSION)
        return 1
    if not io.socket_exists:
        io.logging.error('Failed to create socket file!')
        return 1
    message: dict[str, Any] = request(sys.stdin.buffer)
    if message['init']:
        response(dict(version=VERSION, logPath=io.log_path, socketPath=io.socket_path))
        return 0
    if (url := message.get('url', None) is None):
        io.logging.exception('No URL was given')
        print(json.dumps(dict(message='Missing URL!')))
        return 1
    if (is_debug := message.get('debug', False)):
        io.logging.info('Debug mode enabled.')
    single: bool = message.get('single', True)
    # MacPorts
    data_resp: dict[str, Any] = dict(version=VERSION, log_path=io.log_path, message='About to spawn')
    data_resp['env'] = environment(data_resp, is_debug)
    io.logging.debug('About to spawn')
    response(data_resp)
    if io.socket_exists and single:
        spawn(mpv_launch_socket(**MpvParameters(url=url, io=io, debug=is_debug, environment=data_resp['env'])), io)
    else:
        spawn(mpv_launch(**MpvParameters(url=url, io=io, debug=is_debug, environment=data_resp['env'])), io)
    io.logging.debug('mpv should open soon')
    io.logging.debug('Exiting with status 0')
    return 0
