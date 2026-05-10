from multiprocessing import cpu_count

bind = '127.0.0.1:8000'
workers = 4  # 2 * cpu_count + 1
limit_request_field_size = 0
limit_request_line = 0
# reload = True

# stops duplicate logging/weird formatting for access logger
access_log_format = (
    '%(h)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
)

logconfig_dict = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "default": {
            "format": "[%(asctime)s] [%(name)s:%(lineno)d] [%(process)d] [%(levelname)s] %(message)s",
        }
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stderr",
        }
    },

    "loggers": {
        "gunicorn.error": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },

        "gunicorn.access": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
    },
}