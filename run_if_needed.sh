#!/bin/bash
# Atlas catch-up scheduler — runs the daily pipeline if it hasn't run today.
# macOS cron skips jobs when the Mac is asleep, so we run this every 15 min
# between 8-10 AM. If today's pipeline already ran, this exits silently.

export PATH="/Users/kalamakuntlarakeshreddy/.pyenv/versions/3.11.9/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

PROJ_DIR="/Users/kalamakuntlarakeshreddy/Desktop/A-Glass-Box-AI-Orchestration-Dashboard"
PYTHON="/Users/kalamakuntlarakeshreddy/.pyenv/versions/3.11.9/bin/python3"
LOG="$PROJ_DIR/logs/cron.log"
MARKER="$PROJ_DIR/logs/.last_run_date"

TODAY=$(date +%Y-%m-%d)

# Log every invocation for debugging
echo "$(date '+%Y-%m-%d %H:%M:%S') [CRON] run_if_needed.sh fired" >> "$LOG"

# Check if pipeline already ran today
if [ -f "$MARKER" ] && [ "$(cat "$MARKER")" = "$TODAY" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') [CRON] Already ran today, skipping" >> "$LOG"
    exit 0
fi

# Mark today so we don't run again
echo "$TODAY" > "$MARKER"
echo "$(date '+%Y-%m-%d %H:%M:%S') [CRON] Starting pipeline for $TODAY" >> "$LOG"

# Run the pipeline
cd "$PROJ_DIR" || exit 1
"$PYTHON" scheduler.py --run-now >> "$LOG" 2>&1
