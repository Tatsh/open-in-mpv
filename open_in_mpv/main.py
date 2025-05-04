from __future__ import annotations

from pathlib import Path
from shlex import quote
from typing import TYPE_CHECKING, Any, BinaryIO, cast
import json
import logging
import os
import re
import socket
import struct
import subprocess as sp
import sys

from open_in_mpv import __version__ as VERSION  # noqa: N812
from open_in_mpv.constants import (
    LOG_PATH,
    MACPORTS_BIN_PATH,
    MPV_LOG_PATH,
    MPV_SOCKET,
)
from typing_extensions import override
import click

from .utils import setup_logging

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

logger = logging.getLogger(__name__)


def environment(data_resp: dict[str, Any], *, debugging: bool) -> dict[str, Any]:
    env: dict[str, Any] = os.environ.copy()
    if Path(MACPORTS_BIN_PATH).is_dir():
        logger.info('Detected MacPorts. Setting PATH.')
        data_resp['macports'] = True
        old_path = os.environ.get('PATH')
        env['PATH'] = MACPORTS_BIN_PATH if not old_path else f'{MACPORTS_BIN_PATH}:{old_path}'
    if debugging:  # pragma: no cover
        logger.debug('Environment:')
        for k, value in env.items():
            logger.debug('  %s=%s', k, value)
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
        'single': message.get('single', True),
    }


def remove_socket() -> bool:
    try:
        Path(MPV_SOCKET).unlink(missing_ok=True)
    except OSError:  # pragma: no cover
        return False
    return True


def spawn(func: Callable[[], Any]) -> None:
    """
    See Stevens' "Advanced Programming in the UNIX Environment" for details (ISBN 0201563177).

    Credit: https://stackoverflow.com/a/6011298/374110.

    Takes a callable which will be called in the fork.
    """
    try:
        if os.fork() > 0:
            # parent process, return and keep running
            return
    except OSError as exc:
        logger.exception('Fork #1 failed: %s (%s).', exc.errno, exc.strerror)
        sys.exit(1)
    os.setsid()
    # do second fork
    logger.debug('Second fork.')
    try:
        if os.fork() > 0:
            # exit from second parent
            sys.exit(0)
    except OSError as exc:
        logger.exception('Fork #2 failed: %s (%s).', exc.errno, exc.strerror)
        sys.exit(1)
    logger.debug('Calling callback.')
    func()
    logger.debug('Callback returned.')
    # Exit without calling cleanup handlers
    os._exit(os.EX_OK)


def mpv_and_cleanup(url: str,
                    new_env: Mapping[str, str],
                    *,
                    debug: bool = False) -> Callable[[], None]:
    def callback() -> None:
        with Path(MPV_LOG_PATH).open('a', encoding='utf-8') as log:
            cmd = (
                'mpv',
                '--gpu-api=opengl',
                '--player-operation-mode=pseudo-gui',
                *(('--quiet',) if not debug else ('-v',)),
                f'--input-ipc-server={MPV_SOCKET}',
                url,
            ) + ((f'--log-file={MPV_LOG_PATH}',) if debug else ())
            logger.debug('Running: %s', ' '.join(quote(x) for x in cmd))
            sp.run(cmd, env=new_env, stderr=log, stdout=log, check=True)
        if not remove_socket():  # pragma: no cover
            logger.warning('Failed to remove socket file.')

    return callback


def spawn_init(url: str, new_env: Mapping[str, str], *, debug: bool = False) -> None:
    logger.debug('Spawning initial instance.')
    spawn(mpv_and_cleanup(url, new_env, debug=debug))


def get_callback(url: str,
                 new_env: Mapping[str, str],
                 *,
                 debug: bool = False) -> Callable[[], None]:
    def callback() -> None:
        logger.debug('Sending loadfile command.')
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(2)
        try:
            sock.connect(str(MPV_SOCKET))
            sock.settimeout(None)
            logger.debug('Connected to socket.')
            sock.send(json.dumps({'command': ['loadfile', url]}).encode(errors='strict') + b'\n')
        except OSError:
            logger.exception('Connection refused.')
            if not remove_socket():  # pragma: no cover
                logger.exception('Failed to remove socket file.')
            spawn_init(url, new_env, debug=debug)

    return callback


def real_main(*, debug: bool = False) -> int:
    """
    Actual entry point.

    Standard input is read for a single unsigned integer (1 byte) that represents the length of the
    message. Then the message is expected to be proceed.
    """
    message: dict[str, Any] = request(sys.stdin.buffer)
    if message['init']:
        response({'version': VERSION, 'logPath': str(LOG_PATH), 'socketPath': str(MPV_SOCKET)})
        return 0
    if (url := message.get('url')) is None:
        logger.error('No URL was given.')
        return 1
    if not re.match(r'^https?://', url):
        return 1
    if (is_debug := message.get('debug', False)):  # pragma: no cover
        logger.info('Debug mode enabled.')
    single: bool = message.get('single', True)
    # MacPorts
    data_resp: dict[str, Any] = {
        'version': VERSION,
        'log_path': str(LOG_PATH),
        'message': 'About to spawn.'
    }
    data_resp['env'] = environment(data_resp, debugging=is_debug or debug)
    logger.debug('About to spawn.')
    response(data_resp)
    if MPV_SOCKET.exists() and single:
        logger.debug('Socket exists and single instance mode is enabled.')
        spawn(get_callback(cast('str', url), data_resp['env'], debug=is_debug or debug))
    else:
        spawn_init(cast('str', url), data_resp['env'], debug=is_debug or debug)
    logger.debug('mpv should open soon.')
    logger.debug('Exiting with status 0.')
    return 0


class CustomHelp(click.Command):
    @override
    def format_help(self, ctx: click.Context, formatter: click.formatting.HelpFormatter) -> None:
        click.echo('This script is intended to be used with the '
                   'Chrome extension. There is no CLI interface for general use.')
        super().format_help(ctx, formatter)


@click.command(cls=CustomHelp,
               context_settings={
                   'allow_extra_args': True,
                   'help_option_names': ('-h', '--help')
               })
@click.option('-V', '--version', help='Display version.', is_flag=True)
@click.option('-d', '--debug', help='Enable debug logging.', is_flag=True)
def main(*, debug: bool = False, version: bool = False) -> None:
    """Open a URL in mpv."""
    setup_logging(debug=debug)
    if version:
        click.echo(VERSION)
        return
    if real_main(debug=debug) != 0:
        raise click.Abort
