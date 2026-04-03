from enum import unique, IntEnum

@unique
class UserRole(IntEnum):
    USER        = 1
    ADMIN       = 2
    SUPER_ADMIN = 3