from datetime import timedelta
import re
import os

class Config:
    # helper function to nicely parse out bools
    def env_bool(name: str, default: bool=False) -> bool:
        return os.getenv(name, str(int(default))).lower() in ('1', 'true', 'yes')

    # helper function to nicely parse out ints
    def env_int(name: str, default: int=0) -> int:
        return int(os.getenv(name, str(default)))

    # helper function to nicely parse out byte valus
    def env_bytes(name: str, default: int|str=0) -> int:
        var = os.getenv(name, str(default)).strip().upper()

        match = re.fullmatch(r'(\d+|\d+\.\d+)([A-Z]{0,2})', var)
        if not match:
            raise ValueError(f'Invalid byte value: {var}')

        number, suffix = match.groups()
        number = float(number)

        multipliers = {
            "":   1,
            "B":  1,
            "K":  1024,
            "KB": 1024,
            "M":  1024 ** 2,
            "MB": 1024 ** 2,
            "G":  1024 ** 3,
            "GB": 1024 ** 3,
            "T":  1024 ** 4,
            "TB": 1024 ** 4,
        }

        if suffix not in multipliers:
            raise ValueError(f'Unknown size suffix: {suffix}')

        return int(number * multipliers[suffix])

    # security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-fallback-key')

    # database
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI') 
    SQLALCHEMY_TRACK_MODIFICATIONS = env_bool('SQLALCHEMY_TRACK_MODIFICATIONS', False)

    # flask login remember me cookie
    REMEMBER_COOKIE_DURATION = timedelta(days=env_int('REMEMEBER_COOKIE_DURATION_DAYS', 7))
    REMEMBER_COOKIE_HTTPONLY = env_bool('REMEMBER_COOKIE_HTTPONLY', True)
    REMEMBER_COOKIE_SECURE   = env_bool('REMEMBER_COOKIE_SECURE', False)

    # flask session cookie
    SESSION_COOKIE_SECURE   = env_bool('SESSION_COOKIE_SECURE', False)
    SESSION_COOKIE_HTTPONLY = env_bool('SESSION_COOKIE_HTTPONLY', True)
    SESSION_COOKIE_SAMESITE = os.getenv('SESSION_COOKIE_SAMESITE', 'Lax')

    # logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    # file and path stuff
    TMP_DIR               = os.getenv('TMP_DIR',               '/tmp/OpenTenant')
    LEASES_DIR            = os.getenv('LEASES_DIR',            '/tmp/leases')
    FILE_REPOSITORY_DIR   = os.getenv('FILE_REPOSITORY_DIR',   '/tmp/files')
    MAX_CONTENT_LENGTH    = env_bytes('MAX_CONTENT_LENGTH',    '10M')  # largest request size
    MAX_LEASES_DIR_SIZE   = env_bytes('MAX_LEASES_DIR_SIZE',   '10G')
    MAX_FILE_REP_DIR_SIZE = env_bytes('MAX_FILE_REP_DIR_SIZE', '10G')


# development override
class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


# production override
class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
