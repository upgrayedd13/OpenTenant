from flask_login import current_user, login_required
from enum import unique, IntEnum
from typing import Callable, Any
from functools import wraps
from flask import abort


@unique
class UserRole(IntEnum):
    USER        = 1
    ADMIN       = 2
    SUPER_ADMIN = 3


# Function decorator to set that a given endpoint is only accessible
# if the user is logged in and has one these roles
def user_role_required(*roles: UserRole) -> Callable:
    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        @login_required
        def wrapped(*args, **kwargs) -> Any:
            if not current_user.role in roles:
                abort(403)  # forbidden
            return view_func(*args, **kwargs)
        return wrapped
    return decorator


# Function decorator to set that a user must be logged in and have
# the minimum user role necessary to access a given endpoint
def minimum_user_role(role : UserRole) -> Callable:
    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        @login_required
        def wrapped(*args, **kwargs) -> Any:
            if current_user.role < role.value:
                abort(403)  # forbidden
            return view_func(*args, **kwargs)
        return wrapped
    return decorator