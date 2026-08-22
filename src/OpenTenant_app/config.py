from datetime import timedelta
from flask import Flask
import re
import os


def env_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(int(default))).lower() in ('1', 'true', 'yes')


def env_int(name: str, default: int = 0) -> int:    return int(os.getenv(name, str(default)))


def env_bytes(name: str, default: int | str = 0) -> int:
    var = os.getenv(name, str(default)).strip().upper()

    match = re.fullmatch(r'(\d+|\d+\.\d+)([A-Z]{0,2})', var)
    if not match:
        raise ValueError(f'Invalid byte value: {var}')

    number, suffix = match.groups()
    number = float(number)

    multipliers = {
        '':   1,
        'B':  1,
        'K':  1024,
        'KB': 1024,
        'M':  1024 ** 2,
        'MB': 1024 ** 2,
        'G':  1024 ** 3,
        'GB': 1024 ** 3,
        'T':  1024 ** 4,
        'TB': 1024 ** 4,
    }

    if suffix not in multipliers:
        raise ValueError(f'Unknown size suffix: {suffix}')

    return int(number * multipliers[suffix])


class Config:
    ENV = os.getenv('ENV', 'development').lower()

    # --------------------------------------------------
    # Security
    # --------------------------------------------------
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-fallback-key')

    # --------------------------------------------------
    # Database
    # --------------------------------------------------
    DB_USER = os.getenv('POSTGRES_USER')
    DB_PASS = os.getenv('POSTGRES_PASSWORD')
    DB_NAME = os.getenv('POSTGRES_DB')
    DB_HOST = os.getenv('POSTGRES_HOST', 'db')
    DB_PORT = env_int('POSTGRES_PORT', 5432)

    SQLALCHEMY_DATABASE_URI = f'postgresql+psycopg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = env_bool('SQLALCHEMY_TRACK_MODIFICATIONS', False)

    # --------------------------------------------------
    # Cookies (safe defaults overridden per environment)
    # --------------------------------------------------
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = False

    REMEMBER_COOKIE_DURATION = timedelta(days=env_int('REMEMBER_COOKIE_DURATION_DAYS', 7))
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = False

    # --------------------------------------------------
    # Logging
    # --------------------------------------------------
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    # --------------------------------------------------
    # File storage
    # --------------------------------------------------
    TMP_DIR               = os.getenv('TMP_DIR',               '/tmp/OpenTenant')
    LEASES_DIR            = os.getenv('LEASES_DIR',            '/tmp/leases')
    FILE_REPOSITORY_DIR   = os.getenv('FILE_REPOSITORY_DIR',   '/tmp/files')
    MAX_CONTENT_LENGTH    = env_bytes('MAX_CONTENT_LENGTH',    '10M')  # largest request size
    MAX_TMP_DIR_SIZE      = env_bytes('MAX_TMP_DIR_SIZE',      '1G')
    MAX_LEASES_DIR_SIZE   = env_bytes('MAX_LEASES_DIR_SIZE',   '10G')
    MAX_FILE_REP_DIR_SIZE = env_bytes('MAX_FILE_REP_DIR_SIZE', '10G')

    # --------------------------------------------------
    # Email
    # --------------------------------------------------
    BOT_EMAIL             = os.getenv('BOT_EMAIL',      'no-reply@example.com')
    CONTACT_EMAIL         = os.getenv('CONTACT_EMAIL',  'contact@example.com')
    FEEDBACK_EMAIL        = os.getenv('FEEDBACK_EMAIL', 'feedback@exmample.com')


class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True


def validate_config(app: Flask) -> None:
    env = app.config.get('ENV')

    if env == 'production':
        errors = []

        if not app.config.get('SECRET_KEY'):
            errors.append('SECRET_KEY must be set in production')

        if app.config.get('DEBUG'):
            errors.append('DEBUG must be False in production')

        if not app.config.get('SESSION_COOKIE_SECURE'):
            errors.append('SESSION_COOKIE_SECURE must be True in production')

        if not app.config.get('REMEMBER_COOKIE_SECURE'):
            errors.append('REMEMBER_COOKIE_SECURE must be True in production')

        if app.config.get('SECRET_KEY') == 'dev-fallback-key':
            errors.append('SECRET_KEY is using the development fallback value')

        if errors:
            raise RuntimeError('Invalid production configuration:\n- ' + '\n- '.join(errors))