# gunicorn.conf.py
import multiprocessing
import os

bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"

# 0.25 vCPU → do NOT trust the (2*cores)+1 formula, it rounds up to 2+ workers
workers = 1
threads = 2
worker_class = "gthread"

timeout = 120
graceful_timeout = 30
keepalive = 5

# Recycle workers to bound memory growth
max_requests = 500
max_requests_jitter = 50

# Logs to stdout/stderr so the platform captures them
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Load the app before forking → lower total memory on 256 MB
preload_app = True