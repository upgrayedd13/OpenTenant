from flask import abort, Response, jsonify
import logging

logger = logging.getLogger(__name__)

def log_and_abort(status: int, msg: str) -> None:
    logger.error(msg, stacklevel=2)
    abort(status, msg)


def log_and_jsonify(msg: str, status: int) -> tuple[Response, int]:
    logger.error(msg, stacklevel=2)
    return jsonify({'error': str(msg)}), status
