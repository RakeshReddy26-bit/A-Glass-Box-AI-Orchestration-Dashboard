#!/usr/bin/env bash

set -u

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
ENV_FILE="$BACKEND_DIR/.env"
SERVER_PID=""
PASS_COUNT=0
FAIL_COUNT=0

log() {
  printf "%s\n" "$1"
}

pass() {
  PASS_COUNT=$((PASS_COUNT + 1))
  log "PASS: $1"
}

fail() {
  FAIL_COUNT=$((FAIL_COUNT + 1))
  log "FAIL: $1"
}

warn() {
  log "WARN: $1"
}

cleanup() {
  if [ -n "$SERVER_PID" ] && kill -0 "$SERVER_PID" >/dev/null 2>&1; then
    kill "$SERVER_PID" >/dev/null 2>&1 || true
  fi
}

trap cleanup EXIT

if [ ! -d "$BACKEND_DIR" ]; then
  log "FAIL: backend directory not found at $BACKEND_DIR"
  exit 1
fi

if command -v /Users/kalamakuntlarakeshreddy/.pyenv/versions/3.11.9/bin/python >/dev/null 2>&1; then
  PYTHON_BIN="/Users/kalamakuntlarakeshreddy/.pyenv/versions/3.11.9/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python)"
else
  log "FAIL: No Python interpreter found"
  exit 1
fi

if [ -f "$ENV_FILE" ]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
else
  warn "No backend/.env found; key checks may fail"
fi

log "Starting backend server for verification..."
(
  cd "$BACKEND_DIR" || exit 1
  "$PYTHON_BIN" server.py >/tmp/glassbox-healthcheck.log 2>&1
) &
SERVER_PID=$!

HEALTH_JSON=""
for _ in $(seq 1 25); do
  HEALTH_JSON="$(curl -sS http://127.0.0.1:8000/api/health 2>/dev/null || true)"
  if [ -n "$HEALTH_JSON" ]; then
    break
  fi
  sleep 1
done

if [ -z "$HEALTH_JSON" ]; then
  fail "Backend did not become healthy in time"
  log "See /tmp/glassbox-healthcheck.log for details"
  log ""
  log "Summary: $PASS_COUNT passed, $FAIL_COUNT failed"
  exit 1
fi

if printf "%s" "$HEALTH_JSON" | grep -q '"status":"ok"'; then
  pass "Backend health endpoint reachable"
else
  fail "Backend health endpoint did not return status=ok"
fi

if printf "%s" "$HEALTH_JSON" | grep -q '"claude_api":true'; then
  pass "Anthropic API key recognized by backend"
else
  fail "Anthropic API key not recognized by backend (claude_api=false)"
fi

APPROVALS_JSON="$(curl -sS http://127.0.0.1:8000/api/approvals 2>/dev/null || true)"
if printf "%s" "$APPROVALS_JSON" | grep -q '"pending"'; then
  pass "Approvals endpoint returned data"
else
  fail "Approvals endpoint failed"
fi

CHAT_JSON="$(curl -sS -X POST http://127.0.0.1:8000/api/chat -H 'Content-Type: application/json' -d '{"agent":"atlas","message":"Healthcheck ping: reply in one sentence."}' 2>/dev/null || true)"
if printf "%s" "$CHAT_JSON" | grep -q '"response"' && ! printf "%s" "$CHAT_JSON" | grep -qi 'API key not configured\|API error'; then
  pass "Live agent chat returned a valid response"
else
  fail "Live agent chat failed (check Anthropic key/network)"
fi

TOKEN_PLACEHOLDER="PASTE_YOUR_BOT_TOKEN_HERE"
CHAT_PLACEHOLDER="PASTE_YOUR_CHAT_ID_HERE"

if [ -n "${TELEGRAM_BOT_TOKEN:-}" ] && [ "${TELEGRAM_BOT_TOKEN}" != "$TOKEN_PLACEHOLDER" ]; then
  TELEGRAM_ME="$(curl -sS "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe" 2>/dev/null || true)"
  if printf "%s" "$TELEGRAM_ME" | grep -q '"ok":true'; then
    pass "Telegram bot token is valid"
  else
    fail "Telegram bot token check failed"
  fi

  if [ -n "${TELEGRAM_CHAT_ID:-}" ] && [ "${TELEGRAM_CHAT_ID}" != "$CHAT_PLACEHOLDER" ]; then
    TELEGRAM_CHAT="$(curl -sS "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getChat?chat_id=${TELEGRAM_CHAT_ID}" 2>/dev/null || true)"
    if printf "%s" "$TELEGRAM_CHAT" | grep -q '"ok":true'; then
      pass "Telegram chat ID is valid/reachable"
    else
      fail "Telegram chat ID check failed"
    fi
  else
    warn "TELEGRAM_CHAT_ID missing or placeholder; skipped chat check"
  fi
else
  warn "TELEGRAM_BOT_TOKEN missing or placeholder; skipped Telegram checks"
fi

log ""
log "Summary: $PASS_COUNT passed, $FAIL_COUNT failed"

if [ "$FAIL_COUNT" -gt 0 ]; then
  exit 1
fi

exit 0
