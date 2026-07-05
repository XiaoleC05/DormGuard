#!/usr/bin/env bash
set -euo pipefail

NB_DIR="/opt/DormGuard/backend/nonebot_bot"
NONEBOT_PORT="${NONEBOT_PORT:-8089}"
WS_URL="ws://127.0.0.1:${NONEBOT_PORT}/onebot/v11/ws"
COMPOSE_FILE="/opt/DormGuard/deploy/docker/napcat-compose.yml"
QQ_ACCOUNT="${QQ_BOT_ACCOUNT:-1270667498}"

echo "[1] NoneBot .env (仅本机监听)"
mkdir -p "$NB_DIR" /opt/napcat/QQ /opt/napcat/config
cat > "$NB_DIR/.env" <<EOF
HOST=127.0.0.1
PORT=${NONEBOT_PORT}
EOF

echo "[2] Restart NoneBot"
systemctl restart dormguard-nonebot
sleep 3

echo "[3] Update NapCat onebot configs -> $WS_URL"
python3 - "$WS_URL" <<'PY'
import glob, json, sys
ws_url = sys.argv[1]
for path in glob.glob("/opt/napcat/config/onebot11*.json"):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    clients = data.setdefault("network", {}).setdefault("websocketClients", [])
    if not clients:
        clients.append({"name": "NoneBot", "enable": True, "url": ws_url})
    for client in clients:
        client["url"] = ws_url
        client["enable"] = True
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"updated {path}")
PY

echo "[4] Ensure NapCat container (avoid recreate to keep QQ session)"
if docker ps -a --format '{{.Names}}' | grep -qx napcat; then
  echo "napcat exists, restart only"
  docker restart napcat
elif [ -f "$COMPOSE_FILE" ] && docker compose version >/dev/null 2>&1; then
  NAPCAT_QUICK_ACCOUNT="$QQ_ACCOUNT" docker compose -f "$COMPOSE_FILE" up -d
else
  docker run -d \
    --name napcat \
    --restart unless-stopped \
    --network host \
    --memory 256m \
    -e NAPCAT_QUICK_ACCOUNT="$QQ_ACCOUNT" \
    -v /opt/napcat/QQ:/root/.config/QQ \
    -v /opt/napcat/config:/app/napcat/config \
    ghcr.io/napneko/nodenapcat:latest
fi

sleep 12

echo "[5] Status"
ENV_FILE="/opt/DormGuard/backend/.env"
BOT_TOKEN=""
if [ -f "$ENV_FILE" ]; then
  BOT_TOKEN=$(grep -E '^QQ_BOT_API_TOKEN=' "$ENV_FILE" | cut -d= -f2- | tr -d '\r' || true)
fi
CURL_HEADERS=()
if [ -n "$BOT_TOKEN" ]; then
  CURL_HEADERS=(-H "Authorization: Bearer $BOT_TOKEN")
fi
STATUS=$(curl -s "${CURL_HEADERS[@]}" "http://127.0.0.1:${NONEBOT_PORT}/api/get_status" || true)
echo "$STATUS"
if echo "$STATUS" | grep -q '"status":"ok"'; then
  echo "NapCat connected"
  exit 0
fi

echo "NapCat not connected — login required"
docker logs napcat 2>&1 | grep -E 'txz.qq.com|WebUi User Panel Url' | tail -3 || true
echo "Scan QR via phone QQ, or SSH tunnel: ssh -L 6099:127.0.0.1:6099 aliyun then open http://localhost:6099/webui"
exit 0
