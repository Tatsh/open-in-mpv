"""Main command."""
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

from bascom import setup_logging
from open_in_mpv import __version__ as VERSION  # noqa: N812
from typing_extensions import override
import click

from .constants import (
    IS_WIN,
    LOG_PATH,
    MACPORTS_BIN_PATH,
    MPV_LOG_PATH,
    MPV_SOCKET,
    _LOG_DIR_PATH,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

logger = logging.getLogger(__name__)

__all__ = ('main',)


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


def get_mpv_path() -> str:
    """
    Get the path to the mpv executable.

    On Windows, if running from a PyInstaller bundle, use the bundled mpv.exe.
    Otherwise, use the system mpv.
    """
    if IS_WIN and getattr(sys, 'frozen', False):
        # Running in a PyInstaller bundle on Windows
        if (bundled_mpv := Path(sys.executable).parent / 'mpv.exe').exists():
            logger.debug('Using bundled mpv at: %s', bundled_mpv)
            return str(bundled_mpv)
        logger.warning('Bundled mpv.exe not found, falling back to system mpv.')
    return 'mpv'


def mpv_and_cleanup(url: str,
                    new_env: Mapping[str, str],
                    *,
                    debug: bool = False) -> Callable[[], None]:
    def callback() -> None:
        with Path(MPV_LOG_PATH).open('a', encoding='utf-8') as log:
            mpv_path = get_mpv_path()
            cmd_parts = [mpv_path]
            if not IS_WIN:
                cmd_parts.append('--gpu-api=opengl')
            cmd_parts.append('--player-operation-mode=pseudo-gui')
            if debug:
                cmd_parts.append('-v')
            else:
                cmd_parts.append('--quiet')
            cmd_parts.extend((f'--input-ipc-server={MPV_SOCKET}', url))
            if debug:
                cmd_parts.append(f'--log-file={MPV_LOG_PATH}')
            # On Windows with PyInstaller bundle, configure yt-dlp path
            if IS_WIN and getattr(sys, 'frozen', False):
                ytdlp_path = Path(sys.executable).parent / 'yt-dlp.exe'
                if ytdlp_path.exists():
                    logger.debug('Using bundled yt-dlp at: %s', ytdlp_path)
                    cmd_parts.extend(('--ytdl=yes',
                                     f'--script-opts=ytdl_hook-ytdl_path={ytdlp_path}'))
            logger.debug('Running: %s', ' '.join(quote(x) for x in cmd_parts))
            sp.run(cmd_parts, env=new_env, stderr=log, stdout=log, check=True)
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
@click.argument('chrome_url')
@click.argument('message', type=click.File('rb'), default=sys.stdin.buffer)
@click.option('-d', '--debug', help='Enable debug logging.', is_flag=True)
@click.version_option(VERSION, '-V', '--version', message='%(version)s')
def main(chrome_url: str, message: BinaryIO, *, debug: bool = False) -> None:  # noqa: ARG001
    """
    Open a URL in mpv.

    Standard input is read for a single unsigned integer (1 byte) that represents the length of the
    message. Then the message (encoded in JSON) is expected to be proceed.
    """  # noqa: DOC501
    input_json = request(message)
    debug = input_json.get('debug', debug)
    single: bool = input_json.get('single', True)
    setup_logging(
        debug=debug,
        formatters={
            'file': {
                'format': '%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - '
                          '%(message)s',
            }
        },
        handlers={
            'file': {
                'backupCount': 1,
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': str(_LOG_DIR_PATH / 'main.log'),
                'formatter': 'file',
                'maxBytes': 1048576,
            }
        },
        loggers={
            'open_in_mpv': {
                'handlers': ('console', 'file') if debug else ('file',),
                'propagate': False
            }
        },
        root={
            'handlers': ('console', 'file'),
        })
    logger.debug('Arguments: %s', ' '.join(quote(x) for x in sys.argv))
    logger.debug('Decoded message: %s', input_json)
    logger.info('Single instance mode %s.', 'enabled' if single else 'disabled')
    logger.info('Debug mode %s.', 'enabled' if debug else 'disabled')
    if input_json.get('init'):
        response({'logPath': str(LOG_PATH), 'socketPath': str(MPV_SOCKET), 'version': VERSION})
        return
    if (url := input_json.get('url')) is None:
        logger.error('No URL was given.')
        raise click.Abort
    if not re.match(r'^https?://', url):
        logger.error('Invalid URL: %s', url)
        raise click.Abort
    data_resp: dict[str, Any] = {
        'logPath': str(LOG_PATH),
        'message': 'About to spawn.',
        'version': VERSION
    }
    data_resp['env'] = environment(data_resp, debugging=debug)
    logger.debug('About to spawn.')
    response(data_resp)
    if MPV_SOCKET.exists() and single:
        logger.debug('Socket exists and single instance mode is enabled.')
        spawn(get_callback(cast('str', url), data_resp['env'], debug=debug))
    else:
        spawn_init(cast('str', url), data_resp['env'], debug=debug)
    logger.debug('mpv should open soon.')
    logger.debug('Exiting with status 0.')
