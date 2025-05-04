# SPDX-License-Identifier: MIT
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
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
from .utils import setup_logging

if TYPE_CHECKING:
    from collections.abc import Iterable

log = logging.getLogger(__name__)


def remove_from_all(directories: Iterable[str]) -> None:
    for directory in directories:
        path = Path(directory) / JSON_FILENAME
        log.debug('Deleting `%s`.', path)
        path.unlink(missing_ok=True)


@click.command(context_settings={'help_option_names': ('-h', '--help')})
@click.option('-d', '--debug', is_flag=True, help='Enable debug logging.')
def main(*, debug: bool = False) -> None:
    """Uninstall open-in-mpv Chrome extension files."""
    setup_logging(debug=debug)
    if IS_LINUX:
        try:
            remove_from_all(SYSTEM_HOSTS_DIRS)
        except PermissionError:
            click.echo('To delete files installed in /etc, run this as root.', err=True)
        remove_from_all(USER_HOSTS_DIRS)
    if IS_MAC:
        remove_from_all(MAC_HOSTS_DIRS)
