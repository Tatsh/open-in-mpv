# SPDX-License-Identifier: MIT
from struct import pack
import json
import subprocess as sp

from loguru import logger
from whichcraft import which
import click


@click.command()
@click.argument('url')
def main(url: str) -> None:
    full_path = which('open-in-mpv')
    if not full_path:
        raise click.Abort()
    logger.debug(f'open-in-mpv path: {full_path}')
    open_in_mpv_args = (full_path, 'chrome://nothing')
    data = json.dumps({'init': True})
    with sp.Popen(open_in_mpv_args, stdin=sp.PIPE, stdout=sp.PIPE) as proc0:
        proc0.communicate(input=pack('@i', len(data)) + data.encode('utf-8'))
        proc0.wait()
    data = json.dumps({'url': url})
    with sp.Popen(open_in_mpv_args, stdin=sp.PIPE, stdout=sp.PIPE) as proc:
        proc.communicate(input=pack('@i', len(data)) + data.encode('utf-8'))
        proc.wait()
    if proc0.returncode != 0 or proc.returncode != 0:
        raise click.Abort()
