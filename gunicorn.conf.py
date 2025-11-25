import multiprocessing
import os

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = int(os.getenv("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))
worker_class = "gthread"
threads = int(os.getenv("GUNICORN_THREADS", 2))
max_requests = 1000
max_requests_jitter = 50

# Timeouts
timeout = 30
keepalive = 5
graceful_timeout = 30

# Application loading
preload_app = True
reload = os.getenv("GUNICORN_RELOAD", "false").lower() == "true"

# Logging
accesslog = "-"  # stdout
errorlog = "-"  # stderr
loglevel = os.getenv("LOG_LEVEL", "info")
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'


# Filter to exclude /health requests from access logs
class HealthCheckFilter:
    """Filter out /health requests from access logs"""

    def __call__(self, record):
        request_line = record.args.get("r", "")
        return "/health" not in request_line


# Process naming
proc_name = "flask-app"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None


# Server hooks
def on_starting(server):
    """Called just before the master process is initialized"""
    import logging

    # Apply filter to suppress health check logs
    gunicorn_logger = logging.getLogger("gunicorn.access")
    gunicorn_logger.addFilter(HealthCheckFilter())

    total_threads = server.cfg.workers * server.cfg.threads
    server.log.info(
        f"Starting Gunicorn: {server.cfg.workers} workers × "
        f"{server.cfg.threads} threads = {total_threads} max concurrent requests"
    )


def when_ready(server):
    """Called just after the server is started"""
    server.log.info("Gunicorn server is ready. Spawning workers")


def post_fork(server, worker):
    """Called just after a worker has been forked"""
    server.log.info(f"Worker spawned (pid: {worker.pid})")


def worker_int(worker):
    """Called when worker receives SIGINT or SIGQUIT"""
    worker.log.info(f"Worker received INT or QUIT signal (pid: {worker.pid})")
