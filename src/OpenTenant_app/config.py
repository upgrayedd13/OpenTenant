from datetime import timedelta
import os

class Config:
    '''
    Base configuration shared by all environments.
    Values come from environment variables.
    '''
    # database
    SQLALCHEMY_DATABASE_URI = os.getenv('FLASK_DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # flask login remember me
    REMEMBER_COOKIE_DURATION = timedelta(days=7)
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE   = False  # True in production with HTTPS

    # logging
    LOG_LEVEL = 'INFO'


# development override
class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


# production override
class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True