from flask import abort
import logging

logger = logging.getLogger(__name__)

def log_and_abort(status: int, msg: str) -> None:
    logger.error(msg, stacklevel=2)
    abort(status, msg)
