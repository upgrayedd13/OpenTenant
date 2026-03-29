from multiprocessing import cpu_count

bind = '127.0.0.1:8000'
workers = cpu_count() * 2 + 1
accesslog = '-'
errorlog = '-'
loglevel = 'info'
