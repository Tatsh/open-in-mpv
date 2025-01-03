# SPDX-License-Identifier: MIT
from collections.abc import Sequence
from pathlib import Path
import logging

import click

from .constants import (
    IS_LINUX,
    IS_MAC,
    JSON_FILENAME,
    MAC_HOSTS_DIRS,
    SYSTEM_HOSTS_DIRS,
    USER_HOSTS_DIRS,
)

log = logging.getLogger(__name__)


def remove_from_all(directories: Sequence[str]) -> None:
    for directory in directories:
        path = Path(directory) / JSON_FILENAME
        log.debug('Deleting `%s`.', path)
        try:
            path.unlink()
        except FileNotFoundError:
            log.warning('Failed to delete %s because it does not exist.', path)


@click.command()
@click.option('-d', '--debug', is_flag=True, help='Enable debug logging.')
def main(*, debug: bool = False) -> None:
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO)
    if IS_LINUX:
        try:
            remove_from_all(SYSTEM_HOSTS_DIRS)
        except PermissionError:
            click.echo('To delete files installed in /etc, run this as root.', err=True)
        remove_from_all(USER_HOSTS_DIRS)
    if IS_MAC:
        remove_from_all(MAC_HOSTS_DIRS)
