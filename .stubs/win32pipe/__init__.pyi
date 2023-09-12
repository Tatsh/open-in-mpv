# SPDX-License-Identifier: MIT
# Author: movrsi
from typing import Final

from pywintypes import PyHANDLE

PIPE_READMODE_MESSAGE: Final[int] = ...

def SetNamedPipeHandleState(handle: PyHANDLE, mode: int=0, maxCollectionCount: None | int = 0, # pylint: disable=C0103, W0613
                            CollectDataTimeout: None| int=0) -> int: # pylint: disable=C0103, W0613
    ...
