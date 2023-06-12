# SPDX-License-Identifier: MIT
from copy import deepcopy
from pathlib import Path
from typing import Any, Sequence
import json
import os

from loguru import logger
from whichcraft import which
import click

from .constants import (HOST_DATA, IS_LINUX, IS_MAC, JSON_FILENAME, MAC_HOSTS_DIRS,
                        SYSTEM_HOSTS_DIRS, USER_HOSTS_DIRS)


def write_json(host_data: Any, directory: str) -> None:
    with open(Path(directory) / JSON_FILENAME, 'w+') as f:
        logger.debug(f'Writing to {f.name}')
        json.dump(host_data, f, indent=2, sort_keys=True, allow_nan=False)
        f.write('\n')


def write_json_files(host_data: Any, directories: Sequence[str], force: bool = False) -> None:
    for directory in directories:
        if os.path.exists(directory):
            write_json(host_data, directory)
        elif force:
            os.makedirs(directory, exist_ok=True)
            write_json(host_data, directory)


@click.command(epilog='Please fully exit your browser(s) to ensure successful installation.')
@click.option('-f',
              '--force',
              is_flag=True,
              help='Install user native host JSON files even if the path does not yet exist.')
@click.option('-s', '--system', is_flag=True, help='Install system native host JSON files.')
@click.option('-u', '--user', is_flag=True, help='Install user native host JSON files.')
def main(system: bool = False, user: bool = False, force: bool = False) -> None:
    if not system and not user:
        click.echo('Need an action.', err=True)
        raise click.Abort()
    host_data = deepcopy(HOST_DATA)
    full_path = which('open-in-mpv')
    if not full_path:
        click.echo('open-in-mpv not found in PATH.', err=True)
        raise click.Abort()
    host_data['path'] = full_path
    if IS_LINUX and system and os.geteuid() != 0:
        click.echo('Run this as root.', err=True)
        raise click.Abort()
    if IS_LINUX:
        if system:
            for directory in SYSTEM_HOSTS_DIRS:
                os.makedirs(directory, exist_ok=True)
                write_json(host_data, directory)
        if user:
            write_json_files(host_data, USER_HOSTS_DIRS, force)
    if IS_MAC:
        write_json_files(host_data, MAC_HOSTS_DIRS, force)
