#!/usr/bin/env bash

set -u

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$ROOT_DIR/logs"
CRON_LOG="$LOG_DIR/cron.log"
ATLAS_LOG="$LOG_DIR/atlas.log"
MARKER_FILE="$LOG_DIR/.last_run_date"
HEALTH_URL="https://api.skill-vector.com/health"
TODAY="$(date +%Y-%m-%d)"

print_line() {
  printf '%s\n' "$1"
}

safe_tail_match() {
  local file="$1"
  local pattern="$2"
  if [ -f "$file" ]; then
    grep "$pattern" "$file" | tail -n 1 || true
  fi
}

extract_email_status() {
  local line="$1"
  printf '%s' "$line" | sed -n 's/.*email=\([^, ]*\).*/\1/p'
}

extract_confidence() {
  local line="$1"
  printf '%s' "$line" | sed -n 's/.*confidence=\([^ ]*\).*/\1/p'
}

api_code="000"
api_state="DOWN"
if api_code="$(curl -sS -m 8 -o /tmp/atlas_health_status.json -w "%{http_code}" "$HEALTH_URL" 2>/dev/null)"; then
  if [ "$api_code" = "200" ]; then
    api_state="UP"
  fi
fi

marker="missing"
if [ -f "$MARKER_FILE" ]; then
  marker="$(cat "$MARKER_FILE" 2>/dev/null || echo "read-error")"
fi

last_summary="$(safe_tail_match "$CRON_LOG" "Pipeline summary:")"
email_status="unknown"
confidence="unknown"
if [ -n "$last_summary" ]; then
  parsed_email="$(extract_email_status "$last_summary")"
  parsed_confidence="$(extract_confidence "$last_summary")"
  if [ -n "$parsed_email" ]; then
    email_status="$parsed_email"
  fi
  if [ -n "$parsed_confidence" ]; then
    confidence="$parsed_confidence"
  fi
fi

if [ -f "$CRON_LOG" ] && grep -q "$TODAY .*Pipeline summary: email=success" "$CRON_LOG"; then
  today_run="success"
else
  today_run="not-success"
fi

last_email_line="$(safe_tail_match "$ATLAS_LOG" "\[EMAIL\]")"
last_pipeline_line="$(safe_tail_match "$ATLAS_LOG" "PIPELINE COMPLETE")"

overall="ATTENTION"
if [ "$api_state" = "UP" ] && [ "$email_status" = "success" ] && [ "$today_run" = "success" ]; then
  overall="OK"
fi

print_line "========================================"
print_line "ATLAS Morning Status ($TODAY)"
print_line "========================================"
print_line "Overall:            $overall"
print_line "API:                $api_state (HTTP $api_code)"
print_line "Last Email Status:  $email_status"
print_line "Last Confidence:    $confidence"
print_line "Marker Date:        $marker"
print_line "Today's Run:        $today_run"
print_line ""

if [ -n "$last_summary" ]; then
  print_line "Last Cron Summary:"
  print_line "  $last_summary"
fi

if [ -n "$last_pipeline_line" ]; then
  print_line "Last Pipeline Line:"
  print_line "  $last_pipeline_line"
fi

if [ -n "$last_email_line" ]; then
  print_line "Last Email Log Line:"
  print_line "  $last_email_line"
fi

if [ "$overall" != "OK" ]; then
  print_line ""
  print_line "Action Hint: check logs/cron.log and logs/atlas.log"
fi
