from multiprocessing import cpu_count

from OpenTenant_app.logging_config import LOGGING_CONFIG

bind = '0.0.0.0:8000'
workers = cpu_count() - 1
limit_request_field_size = 0
limit_request_line = 0
# reload = True

# stops duplicate logging/weird formatting for access logger
access_log_format = '%(h)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

logconfig_dict = LOGGING_CONFIG