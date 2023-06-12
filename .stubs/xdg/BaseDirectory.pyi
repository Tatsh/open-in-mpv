# SPDX-License-Identifier: MIT
from typing import Final

def save_state_path(*resource: str) -> str:
    ...


def get_runtime_dir(strict: bool = ...) -> str:
    ...


xdg_config_home: Final[str] = ...
