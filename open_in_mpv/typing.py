# SPDX-License-Identifier: MIT
from typing import Callable, Mapping, Required, TypeAlias, TypedDict, Unpack

from .io import Io


class MpvParameters(TypedDict):
    url: Required[str]
    debug: Required[bool]
    io: Required[Io]
    environment: Required[Mapping[str, str]]


class ResponseError(TypedDict):
    message: str


class ResponseInit(TypedDict):
    version: str
    logPath: str
    socketPath: str

# dict(version=VERSION, log_path=io.log_path, message='About to spawn')
class ResponseSpawn(TypedDict):
    version: str
    log_path: str
    message: str = 'About to spawn'


Mpv: TypeAlias = Callable[[Unpack[MpvParameters]], None]
