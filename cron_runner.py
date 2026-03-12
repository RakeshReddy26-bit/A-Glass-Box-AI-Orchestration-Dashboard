#!/usr/bin/env python3
"""
Atlas cron runner — Python version of run_if_needed.sh
macOS TCC blocks /bin/bash from accessing ~/Desktop via cron,
but pyenv python3 works fine (same as the health ping).
Called by cron every 15 min between 8-10 AM.
"""
import os
import sys
import datetime
import subprocess

BASE = os.path.dirname(os.path.abspath(__file__))
MARKER = os.path.join(BASE, "logs", ".last_run_date")
LOG = os.path.join(BASE, "logs", "cron.log")
PYTHON = sys.executable

def log(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{ts} [CRON-PY] {msg}\n"
    with open(LOG, "a") as f:
        f.write(line)

def main():
    today = datetime.date.today().isoformat()
    log("cron_runner.py fired")

    # Check marker
    if os.path.exists(MARKER):
        with open(MARKER) as f:
            last = f.read().strip()
        if last == today:
            log("Already ran today, skipping")
            return

    # Write marker
    with open(MARKER, "w") as f:
        f.write(today)
    log(f"Starting pipeline for {today}")

    # Run pipeline
    os.chdir(BASE)
    result = subprocess.run(
        [PYTHON, "scheduler.py", "--run-now"],
        capture_output=True, text=True
    )
    # Log output
    if result.stdout:
        for line in result.stdout.strip().split("\n"):
            log(f"OUT: {line}")
    if result.stderr:
        for line in result.stderr.strip().split("\n"):
            log(f"ERR: {line}")
    log(f"Pipeline finished with exit code {result.returncode}")

if __name__ == "__main__":
    main()
