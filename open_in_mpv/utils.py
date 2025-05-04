"""Utilities."""
from __future__ import annotations

import logging
import logging.config

from .constants import _LOG_DIR_PATH

log = logging.getLogger(__name__)


def setup_logging(*,
                  debug: bool = False,
                  force_color: bool = False,
                  no_color: bool = False) -> None:
    """Set up logging configuration."""
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': True,
        'root': {
            'level': 'DEBUG' if debug else 'INFO',
            'handlers': ['console', 'file'],
        },
        'formatters': {
            'default': {
                '()': 'colorlog.ColoredFormatter',
                'force_color': force_color,
                'format': (
                    '%(light_cyan)s%(asctime)s%(reset)s | %(log_color)s%(levelname)-8s%(reset)s | '
                    '%(light_green)s%(name)s%(reset)s:%(light_red)s%(funcName)s%(reset)s:'
                    '%(blue)s%(lineno)d%(reset)s - %(message)s'),
                'no_color': no_color,
            },
            'file': {
                'format': '%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - '
                          '%(message)s',
            }
        },
        'handlers': {
            'console': {
                'class': 'colorlog.StreamHandler',
                'formatter': 'default',
            },
            'file': {
                'backupCount': 1,
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': str(_LOG_DIR_PATH / 'main.log'),
                'formatter': 'file',
                'maxBytes': 1048576,
            },
        },
        'loggers': {
            'open_in_mpv': {
                'handlers': ['console', 'file'] if debug else ['file'],
                'propagate': False,
            },
        },
    })
