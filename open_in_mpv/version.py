# SPDX-License-Identifier: MIT
from typing import Final

VERSION_MAJOR: Final[int] = 0
VERSION_MINOR: Final[int] = 2
VERSION_REVISION: Final[int] = 0
VERSION_NUMBER: Final[int] = (VERSION_MAJOR << 16 | VERSION_MINOR << 8 | VERSION_REVISION)
VERSION: Final[str] = f'v{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_REVISION}'
