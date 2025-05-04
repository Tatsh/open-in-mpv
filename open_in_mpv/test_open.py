# SPDX-License-Identifier: MIT
from __future__ import annotations

from shlex import quote
from shutil import which
from struct import pack
import json
import logging
import subprocess as sp

import click

from .utils import setup_logging

log = logging.getLogger(__name__)


@click.command(context_settings={'help_option_names': ('-h', '--help')})
@click.argument('url')
@click.option('-d', '--debug', help='Enable debug logging.', is_flag=True)
def main(url: str, *, debug: bool = False) -> None:
    """Test ``open-in-mpv`` command."""
    setup_logging(debug=debug)
    if not (full_path := which('open-in-mpv')):
        raise click.Abort
    log.debug('open-in-mpv path: %s', full_path)
    open_in_mpv_args = (full_path, 'chrome://nothing', *(('-d',) if debug else ()))
    log.debug('Running: %s', ' '.join(quote(x) for x in open_in_mpv_args))
    data = json.dumps({'init': True})
    with sp.Popen(open_in_mpv_args, stdin=sp.PIPE, stdout=sp.PIPE) as proc0:
        proc0.communicate(input=pack('@i', len(data)) + data.encode())
        proc0.wait()
    data = json.dumps({'url': url, 'debug': debug})
    with sp.Popen(open_in_mpv_args, stdin=sp.PIPE, stdout=sp.PIPE) as proc:
        proc.communicate(input=pack('@i', len(data)) + data.encode())
        proc.wait()
    if proc0.returncode != 0 or proc.returncode != 0:
        raise click.Abort
