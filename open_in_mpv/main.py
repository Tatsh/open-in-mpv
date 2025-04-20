from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any, BinaryIO, TextIO, cast
import json
import logging
import os
import socket
import struct
import subprocess as sp
import sys

from typing_extensions import override
import click

from open_in_mpv import __version__ as VERSION  # noqa: N812
from open_in_mpv.constants import LOG_PATH, MACPORTS_BIN_PATH, MPV_SOCKET

fallbacks: dict[str, Any] = {'log': None, 'socket': None}
logger = logging.getLogger(__name__)


def environment(data_resp: dict[str, Any], *, debugging: bool) -> dict[str, Any]:
    env: dict[str, Any] = os.environ.copy()
    if Path(MACPORTS_BIN_PATH).is_dir():
        logger.info('Detected MacPorts. Setting PATH.')
        data_resp['macports'] = True
        old_path = os.environ.get('PATH')
        env['PATH'] = MACPORTS_BIN_PATH if not old_path else f'{MACPORTS_BIN_PATH}:{old_path}'
    if debugging:
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
    logger.debug('Message contents (%d): %s.', req_len, message)
    return {
        'init': 'init' in message,
        'url': message.get('url', None),
        'debug': message.get('debug', False),
        'single': message.get('single')
    }


def remove_socket() -> bool:
    if fallbacks['socket']:
        fallbacks['socket'].close()
        return True
    try:
        Path(MPV_SOCKET).unlink()
    except OSError:
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
                    log: TextIO,
                    *,
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
        if not remove_socket():
            logger.error('Failed to remove socket file.')

    return callback


def spawn_init(url: str, log: TextIO, new_env: Mapping[str, str], *, debug: bool = False) -> None:
    logger.debug('Spawning initial instance.')
    spawn(mpv_and_cleanup(url, new_env, log, debug=debug))


def get_callback(url: str,
                 log: TextIO,
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
            if not remove_socket():
                logger.exception('Failed to remove socket file.')
            spawn_init(url, log, new_env, debug=debug)

    return callback


def real_main(log: TextIO) -> int:
    """
    Actual entry point.

    Standard input is read for a single unsigned integer (1 byte) that represents the length of the
    message. Then the message is expected to be proceed.
    """
    Path(MPV_SOCKET).parent.mkdir(parents=True, exist_ok=True)
    message: dict[str, Any] = request(sys.stdin.buffer)
    if message['init']:
        response({'version': VERSION, 'logPath': log.name, 'socketPath': MPV_SOCKET})
        log.close()
        return 0
    if (url := message.get('url')) is None:
        logger.error('No URL was given.')
        return 1
    if 'https' not in url:
        return 1
    if (is_debug := message.get('debug', False)):
        logger.info('Debug mode enabled.')
    single: bool = message.get('single', True)
    # MacPorts
    data_resp: dict[str, Any] = {
        'version': VERSION,
        'log_path': log.name,
        'message': 'About to spawn.'
    }
    data_resp['env'] = environment(data_resp, debugging=is_debug)
    logger.debug('About to spawn.')
    response(data_resp)
    if Path(MPV_SOCKET).exists() and single:
        spawn(get_callback(cast('str', url), log, data_resp['env'], debug=is_debug))
    else:
        spawn_init(cast('str', url), log, data_resp['env'], debug=is_debug)
    logger.debug('mpv should open soon.')
    logger.debug('Exiting with status 0.')
    if fallbacks['log']:
        fallbacks['log'].cleanup()
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
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO)
    if version:
        click.echo(VERSION)
        return
    LOG_PATH.mkdir(exist_ok=True)
    out_log_path = LOG_PATH / 'open-in-mpv.log'
    with Path(out_log_path).open('a+', encoding='utf-8') as log:
        real_main(log)
