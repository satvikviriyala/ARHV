"""Small structured-logging helper used by Lambda handlers."""

from __future__ import annotations

import logging


def get_logger() -> logging.Logger:
    logger = logging.getLogger("pact")
    logger.setLevel(logging.INFO)
    return logger


logger = get_logger()


def log_event(name: str, **fields: object) -> None:
    logger.info(name, extra={"event": name, **fields})
