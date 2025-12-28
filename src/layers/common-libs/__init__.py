"""
Common libraries layer for Python Lambda functions.

This layer provides essential utilities including structured logging
and secret management with caching.
"""

from common_libs.logger import logger
from common_libs.secretManager import get_secret

__all__ = [
    "logger",
    "get_secret"
]

