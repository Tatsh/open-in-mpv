# SPDX-License-Identifier: MIT
from .install import main as install
from .open_in_mpv import main as open_in_mpv
from .test_open import main as test_open
from .uninstall import main as uninstall

__all__ = ('install', 'open_in_mpv', 'test_open', 'uninstall')
