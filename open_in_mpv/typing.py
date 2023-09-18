# SPDX-License-Identifier: MIT
from typing import Callable, Mapping, Required, TypeAlias, TypedDict, Unpack

from .io import Io


class MpvParameters(TypedDict):
    url: Required[str]
    debug: Required[bool]
    io: Required[Io]
    environment: Required[Mapping[str, str]]


Mpv: TypeAlias = Callable[[Unpack[MpvParameters]], None]
