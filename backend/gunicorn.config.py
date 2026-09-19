# gunicorn.conf.py

# Server socket
bind = "0.0.0.0:8000"

# Worker processes
workers = 5
worker_class = "uvicorn.workers.UvicornWorker"

# Logging setup (shows requests in terminal like runserver)
accesslog = "-"          # Log access requests to standard output
errorlog = "-"           # Log errors to standard error
loglevel = "debug"        # Options: debug, info, warning, error, critical

# Custom log format (Optional: makes logs extra readable)
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

