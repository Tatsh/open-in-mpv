# SPDX-License-Identifier: MIT
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from shutil import which
from typing import TYPE_CHECKING, Any
import json
import logging
import os

import click

from .constants import (
    HOST_DATA,
    IS_LINUX,
    IS_MAC,
    JSON_FILENAME,
    MAC_HOSTS_DIRS,
    SYSTEM_HOSTS_DIRS,
    USER_HOSTS_DIRS,
)
from .utils import setup_logging

if TYPE_CHECKING:
    from collections.abc import Sequence

log = logging.getLogger(__name__)


def write_json(host_data: Any, directory: str) -> None:
    with (Path(directory) / JSON_FILENAME).open('w+', encoding='utf-8') as f:
        log.debug('Writing to %s.', f.name)
        json.dump(host_data, f, indent=2, sort_keys=True, allow_nan=False)
        f.write('\n')


def write_json_files(host_data: Any, directories: Sequence[str], *, force: bool = False) -> None:
    for directory in directories:
        if force:
            Path(directory).mkdir(parents=True, exist_ok=True)
            write_json(host_data, directory)
        elif Path(directory).exists():
            write_json(host_data, directory)


@click.command(epilog='Please fully exit your browser(s) to ensure successful installation.',
               context_settings={'help_option_names': ('-h', '--help')})
@click.option('-d', '--debug', help='Enable debug logging.', is_flag=True)
@click.option('-f',
              '--force',
              is_flag=True,
              help='Install user native host JSON files even if the path does not yet exist.')
@click.option('-s', '--system', is_flag=True, help='Install system native host JSON files.')
@click.option('-u', '--user', is_flag=True, help='Install user native host JSON files.')
def main(*,
         system: bool = False,
         user: bool = False,
         force: bool = False,
         debug: bool = False) -> None:
    """Install open-in-mpv Chrome extension files."""
    setup_logging(debug=debug)
    if not system and not user:
        click.echo('Need an action.', err=True)
        raise click.Abort
    host_data = deepcopy(HOST_DATA)
    if not (full_path := which('open-in-mpv')):
        click.echo('open-in-mpv not found in PATH.', err=True)
        raise click.Abort
    host_data['path'] = full_path
    if IS_LINUX:
        if system:
            if os.geteuid() != 0:
                click.echo('Run this as root.', err=True)
                raise click.Abort
            for directory in SYSTEM_HOSTS_DIRS:
                Path(directory).mkdir(exist_ok=True, parents=True)
                write_json(host_data, directory)
        else:
            write_json_files(host_data, USER_HOSTS_DIRS, force=force)
    if IS_MAC:
        write_json_files(host_data, MAC_HOSTS_DIRS, force=force)
