# SPDX-License-Identifier: MIT
from pathlib import Path
from typing import Sequence
import os

from loguru import logger
import click

from .constants import (IS_LINUX, IS_MAC, JSON_FILENAME, MAC_HOSTS_DIRS, SYSTEM_HOSTS_DIRS,
                        USER_HOSTS_DIRS)


def remove_from_all(directories: Sequence[str]):
    for directory in directories:
        path = Path(directory) / JSON_FILENAME
        logger.debug(f'Deleting {path}')
        try:
            os.remove(Path(directory) / JSON_FILENAME)
        except FileNotFoundError:
            logger.warning(f'Failed to delete {path} because it does not exist')


@click.command()
def main() -> None:
    if IS_LINUX:
        try:
            remove_from_all(SYSTEM_HOSTS_DIRS)
        except PermissionError:
            click.echo('To delete files installed in /etc, run this as root.', err=True)
        remove_from_all(USER_HOSTS_DIRS)
    if IS_MAC:
        remove_from_all(MAC_HOSTS_DIRS)
