from datetime import timedelta
import os

class Config:
    # helper function to nicely parse out bools
    def env_bool(name: str, default=False) -> bool:
        return os.getenv(name, str(int(default))).lower() in ('1', 'true', 'yes')

    # helper function to nicely parse out ints
    def env_int(name: str, default=0) -> int:
        return int(os.getenv(name, default))

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


# development override
class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


# production override
class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
