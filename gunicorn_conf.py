from multiprocessing import cpu_count

bind = '127.0.0.1:8000'
workers = 4
accesslog = '-'
errorlog = '-'
loglevel = 'info'
limit_request_field_size = 0
limit_request_line = 0