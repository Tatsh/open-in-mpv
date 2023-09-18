import os
import sys
import tempfile

from functools import lru_cache
from typing import Any, Final

from loguru import logger, Logger
from os.path import dirname, exists, expanduser, expandvars, join as path_join
import loguru
from xdg import BaseDirectory
from .constants import IS_LINUX, IS_MAC, IS_WIN

@lru_cache()
def get_log_path() -> str:
    if IS_MAC:
        return expanduser('~/Library/Logs')
    if IS_WIN:
        return expandvars(r'%LOCALDATA%\open-in-mpv')  # cspell:disable-line
    try:
        return BaseDirectory.save_state_path('open-in-mpv')
    except KeyError:
        return ""

@lru_cache()
def get_socket_path() -> str:
    if IS_MAC:
        return expanduser('~/Library/Caches/open-in-mpv.sock')
    if IS_WIN:
        return expandvars(r'\\.\pipe\open-in-mpv')
    try:
        return path_join(BaseDirectory.get_runtime_dir(), 'open-in-mpv.sock')
    except KeyError:
        return ""

MPV_SOCKET: Final[str] = get_socket_path()
MPV_LOG_PATH: Final[str] = get_log_path()

class Io:
    _logger: Logger
    _log_path: str
    _tmp: tempfile.TemporaryDirectory[str] | None
    _socket: tempfile._TemporaryFileWrapper[bytes] | None
    _socket_exists: bool
    _socket_path: str


    def __init__(self) -> None:
        self._logger = logger
        self._logger.add(sys.stderr, format="{time} {level} {message}", filter="open_in_mpv", level="ERROR")
        self._logger.add(sys.stdout, format="{time} {level} {message}", filter="open_in_mpv", level="INFO")
        self._tmp = (tempfile.TemporaryDirectory('open-in-mpv', ignore_cleanup_errors=True)
              if MPV_LOG_PATH == "" else None)
        self._log_path = path_join(MPV_LOG_PATH if not self._tmp else self._tmp.name, 'open-in-mpv.log')
        self._logger.add(self._log_path)
        self._socket = (tempfile.NamedTemporaryFile(prefix='open-in-mpv', suffix='.socket')
              if MPV_SOCKET == "" else None)
        self._socket_exists = self.create_socket()
        self._socket_path = MPV_SOCKET if not self._socket else self._socket.name


    @property
    def logging(self):
        return self._logger


    @property
    def log_path(self) -> str:
        return self._log_path


    @property
    def socket_exists(self) -> bool:
        return self._socket_exists


    @property
    def socket_path(self) -> str:
        return self._socket_path


    def create_log_path(self) -> bool:
        if exists(self.log_path) or self._tmp:
            return True
        try:
            os.makedirs(self.log_path, exist_ok=True)
        except OSError:
            return False
        return True


    def create_socket(self) -> bool:
        if self._socket:
            return True
        try:
            os.makedirs(dirname(MPV_SOCKET), exist_ok=True)
        except OSError:
            return False
        return True


    def remove_socket(self) -> bool:
        if self._socket:
            self._socket.close()
            return True
        try:
            os.remove(MPV_SOCKET)
        except OSError:
            return False
        return True
