import os
from typing import Final

from loguru import logger

from .core import Graph, Node

logger.add(
    "polysophia.log",
    format="{time} {level} {message}",
    level=os.getenv("LOG_LEVEL", "DEBUG"),
)

TZ: Final = "utc"
