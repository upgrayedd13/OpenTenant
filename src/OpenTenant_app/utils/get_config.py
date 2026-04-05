from flask import current_app
from typing import Any

def get_config(config: str) -> Any:
    return current_app.config[config]