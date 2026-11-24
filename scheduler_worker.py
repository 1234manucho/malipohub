"""Standalone scheduler process.

In production, run this as a separate process/container so only one
scheduler fires jobs. On the web workers, set SCHEDULER_ENABLED=false
so they do not start their own scheduler.

Usage:
    python scheduler_worker.py

Deployment:
    web container:        SCHEDULER_ENABLED=false gunicorn -w 4 app:app
    scheduler container:  SCHEDULER_ENABLED=true  python scheduler_worker.py
"""
import os

# Force-enable the scheduler in this process even if the parent env has it
# disabled. Must be set BEFORE importing app, because config.py reads the
# env var at import time.
os.environ["SCHEDULER_ENABLED"] = "true"

import signal
import time
import logging

from app import app  # noqa: F401  -- triggers create_app() at import time
from extensions import scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)


def main():
    if not scheduler.running:
        logging.error("Scheduler did not start. Check SCHEDULER_ENABLED.")
        return

    job_count = len(scheduler.get_jobs())
    logging.info("Scheduler worker started. Jobs loaded: %d", job_count)

    stop = {"flag": False}

    def _shutdown(signum, frame):  # noqa: ARG001
        logging.info("Received signal %s, shutting down.", signum)
        stop["flag"] = True

    signal.signal(signal.SIGTERM, _shutdown)
    signal.signal(signal.SIGINT, _shutdown)

    while not stop["flag"]:
        time.sleep(2)

    logging.info("Stopping scheduler.")
    if scheduler.running:
        scheduler.shutdown(wait=False)
    logging.info("Bye.")


if __name__ == "__main__":
    main()