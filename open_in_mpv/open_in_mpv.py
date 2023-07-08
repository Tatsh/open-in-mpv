# SPDX-License-Identifier: MIT
from functools import lru_cache
from os.path import dirname, exists, expanduser, isdir, join as path_join
from typing import Any, Callable, Mapping, TextIO
import json
import os
import platform
import socket
import struct
import subprocess as sp
import sys
import tempfile

from loguru import logger
import click
import xdg.BaseDirectory


@lru_cache()
def get_log_path() -> str:
    if platform.mac_ver()[0]:
        return expanduser('~/Library/Logs')
    try:
        return xdg.BaseDirectory.save_state_path('open-in-mpv')
    except KeyError:
        with tempfile.TemporaryDirectory(prefix='open-in-mpv') as dir_:
            return dir_


@lru_cache()
def get_socket_path() -> str:
    if platform.mac_ver()[0]:
        return expanduser('~/Library/Caches/open-in-mpv.sock')
    try:
        return path_join(xdg.BaseDirectory.get_runtime_dir(), 'open-in-mpv.sock')
    except KeyError:
        with tempfile.NamedTemporaryFile(prefix='open-in-mpv', suffix='.sock') as socket_fp:
            return socket_fp.name


LOG_PATH = get_log_path()
MPV_SOCKET = get_socket_path()
VERSION = 'v0.0.6'


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


def mpv_and_cleanup(url: str,
                    new_env: Mapping[str, str],
                    log: TextIO,
                    debug: bool = False) -> Callable[[], None]:
    def callback() -> None:
        sp.check_call((
            'mpv',
            '--gpu-api=opengl',
            '--player-operation-mode=pseudo-gui',
            '--quiet',
            f'--input-ipc-server={MPV_SOCKET}',
            url,
        ) + ((f'--log-file={log.name}',) if debug else ()),
                      env=new_env,
                      stderr=log,
                      stdout=log)
        os.remove(MPV_SOCKET)

    return callback


def spawn_init(url: str, log: TextIO, new_env: Mapping[str, str], debug: bool = False) -> None:
    logger.debug('Spawning initial instance')
    spawn(mpv_and_cleanup(url, new_env, log, debug))


def get_callback(url: str,
                 log: TextIO,
                 new_env: Mapping[str, str],
                 debug: bool = False) -> Callable[[], None]:
    def callback() -> None:
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
            try:
                os.remove(MPV_SOCKET)
            except OSError:
                pass
            spawn_init(url, log, new_env, debug)

    return callback


def real_main(log: TextIO) -> int:
    """
    Actual entry point.

    Standard input is read for a single unsigned integer (1 byte) that represents the length of the
    message. Then the message is expected to be proceed.
    """
    os.makedirs(dirname(MPV_SOCKET), exist_ok=True)
    stdin_buffer = sys.stdin.buffer
    req_len = struct.unpack('@i', stdin_buffer.read(4))[0]
    message = json.loads(stdin_buffer.read(req_len).decode())
    logger.debug(f'Message contents ({req_len}): {message}')
    if 'init' in message:
        resp = json.dumps(dict(version=VERSION, logPath=log.name, socketPath=MPV_SOCKET)).encode()
        size = struct.pack('@i', len(resp))
        stdout_buffer = sys.stdout.buffer
        stdout_buffer.write(size)
        stdout_buffer.write(resp)
        log.close()
        return 0
    try:
        url: str = message['url']
    except KeyError:
        logger.exception('No URL was given')
        print(json.dumps(dict(message='Missing URL!')))
        return 1
    if (is_debug := message.get('debug', False)):
        logger.info('Debug mode enabled.')
    single: bool = message.get('single', True)
    # MacPorts
    new_env = os.environ.copy()
    data_resp: dict[str, Any] = dict(version=VERSION, log_path=log.name, message='About to spawn')
    if isdir('/opt/local/bin'):
        logger.info('Detected MacPorts. Setting PATH.')
        data_resp['macports'] = True
        old_path = os.environ.get('PATH')
        new_env['PATH'] = '/opt/local/bin' if not old_path else ':'.join(
            ('/opt/local/bin', old_path))
    data_resp['env'] = new_env
    if is_debug:
        logger.debug('Environment:')
        for k, value in new_env.items():
            logger.debug(f'  {k}={value}')
    logger.debug('About to spawn')
    resp = json.dumps(data_resp).encode()
    size = struct.pack('@i', len(resp))
    stdout_buffer = sys.stdout.buffer
    stdout_buffer.write(size)
    stdout_buffer.write(resp)
    if exists(MPV_SOCKET) and single:
        spawn(get_callback(url, log, new_env, is_debug))
    else:
        spawn_init(url, log, new_env, is_debug)
    logger.debug('mpv should open soon')
    logger.debug('Exiting with status 0')
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
