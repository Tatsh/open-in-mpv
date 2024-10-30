# SPDX-License-Identifier: MIT
from shutil import which
from struct import pack
import json
import subprocess as sp

import click


@click.command()
@click.argument('url')
def main(url: str) -> None:
    if not (full_path := which('open-in-mpv')):
        raise click.Abort
    click.echo(f'open-in-mpv path: {full_path}', err=True)
    open_in_mpv_args = (full_path, 'chrome://nothing')
    data = json.dumps({'init': True})
    with sp.Popen(open_in_mpv_args, stdin=sp.PIPE, stdout=sp.PIPE) as proc0:
        proc0.communicate(input=pack('@i', len(data)) + data.encode())
        proc0.wait()
    data = json.dumps({'url': url})
    with sp.Popen(open_in_mpv_args, stdin=sp.PIPE, stdout=sp.PIPE) as proc:
        proc.communicate(input=pack('@i', len(data)) + data.encode())
        proc.wait()
    if proc0.returncode != 0 or proc.returncode != 0:
        raise click.Abort
