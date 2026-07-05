#!/usr/bin/env bash
# 健康检查：后端、NoneBot、Nginx
set -euo pipefail

LOG_TAG="dormguard-healthcheck"
ENV_FILE="/opt/DormGuard/backend/.env"
FAIL=0
MSG=""

check() {
  local name="$1"
  shift
  if "$@"; then
    MSG+="[OK] $name "
  else
    MSG+="[FAIL] $name "
    FAIL=1
  fi
}

load_bot_token() {
  if [ -f "$ENV_FILE" ]; then
    grep -E '^QQ_BOT_API_TOKEN=' "$ENV_FILE" | cut -d= -f2- | tr -d '\r' || true
  fi
}

check_nonebot() {
  local token="$1"
  local body
  local nonebot_port="${NONEBOT_PORT:-8089}"
  local curl_args=(-fsS --max-time 10)
  if [ -n "$token" ]; then
    curl_args+=(-H "Authorization: Bearer $token")
  fi
  body=$(curl "${curl_args[@]}" "http://127.0.0.1:${nonebot_port}/api/get_status") || return 1
  python3 -c "import json,sys; d=json.loads(sys.argv[1]); sys.exit(0 if d.get('status')=='ok' else 1)" "$body"
}

BOT_TOKEN="$(load_bot_token)"

check "backend" curl -fsS --max-time 10 http://127.0.0.1:8000/health
check "nonebot" check_nonebot "$BOT_TOKEN"
check "nginx" systemctl is-active --quiet nginx

if [ "$FAIL" -ne 0 ]; then
  logger -t "$LOG_TAG" "$MSG"
  echo "UNHEALTHY: $MSG" >&2
  exit 1
fi

echo "HEALTHY: $MSG"
