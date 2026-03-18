#!/usr/bin/env python3
"""
Atlas cron runner — Python version of run_if_needed.sh
macOS TCC blocks /bin/bash from accessing ~/Desktop via cron,
but pyenv python3 works fine (same as the health ping).
Called by cron every 15 min between 8-10 AM.
"""
import argparse
import asyncio
import os
import sys
import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
MARKER = os.path.join(BASE, "logs", ".last_run_date")
LOG = os.path.join(BASE, "logs", "cron.log")


def _status(value):
    if isinstance(value, dict):
        return value.get("status", "unknown")
    return "unknown"

def log(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{ts} [CRON-PY] {msg}\n"
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line)


def read_marker():
    if not os.path.exists(MARKER):
        return ""
    with open(MARKER, "r", encoding="utf-8") as f:
        return f.read().strip()


def write_marker(today):
    with open(MARKER, "w", encoding="utf-8") as f:
        f.write(today)


def run_pipeline_once():
    """Run the pipeline and return its result dict."""
    os.chdir(BASE)
    if BASE not in sys.path:
        sys.path.insert(0, BASE)
    from integrations.daily_pipeline import run_daily_pipeline

    return asyncio.run(run_daily_pipeline())

def main():
    parser = argparse.ArgumentParser(description="Run Atlas daily pipeline from cron")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Ignore today's marker and run immediately",
    )
    args = parser.parse_args()

    today = datetime.date.today().isoformat()
    log(f"cron_runner.py fired (force={args.force})")

    # Check marker before running.
    last = read_marker()
    if last == today and not args.force:
        log("Already ran today, skipping")
        return 0

    log(f"Starting pipeline for {today}")

    try:
        result = run_pipeline_once()
    except Exception as e:
        log(f"Pipeline crashed before completion: {e}")
        return 1

    email_status = _status(result.get("email")) if isinstance(result, dict) else "unknown"
    confidence = result.get("confidence", 0) if isinstance(result, dict) else 0
    log(f"Pipeline summary: email={email_status}, confidence={confidence}%")

    # Mark success only after email succeeds so cron can retry failures.
    if email_status == "success":
        write_marker(today)
        log("Marker updated: daily run successful")
        return 0

    log("Daily run incomplete (email not successful); marker NOT updated so cron can retry")
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
