#!/usr/bin/env bash
# 在服务器上应用已构建的发布包（GitHub Actions self-hosted 或手动执行）
set -euo pipefail

APP_DIR=/opt/dorm-power-guard-lite
RELEASE_DIR="${1:-/tmp/dorm-release}"

if [ ! -d "$RELEASE_DIR/backend" ]; then
  echo "错误：未找到 $RELEASE_DIR/backend，请先解压 release.tar.gz"
  exit 1
fi

mkdir -p "$APP_DIR/backend" "$APP_DIR/frontend/dist" "$APP_DIR/deploy"
rsync -a "$RELEASE_DIR/backend/" "$APP_DIR/backend/"
rsync -a --delete "$RELEASE_DIR/frontend-dist/" "$APP_DIR/frontend/dist/"
rsync -a "$RELEASE_DIR/deploy/" "$APP_DIR/deploy/"
chmod +x "$APP_DIR/deploy/"*.sh "$APP_DIR/deploy/monitor/"*.sh 2>/dev/null || true

cd "$APP_DIR/backend"
if [ ! -d venv ]; then python3 -m venv venv; fi
./venv/bin/pip install --upgrade pip -q
./venv/bin/pip install -r requirements.txt -q
if [ -f requirements-nonebot.txt ]; then
  ./venv/bin/pip install -r requirements-nonebot.txt -q
fi

cp "$APP_DIR/deploy/systemd/dorm-backend.service" /etc/systemd/system/
cp "$APP_DIR/deploy/systemd/dorm-nonebot.service" /etc/systemd/system/
cp "$APP_DIR/deploy/systemd/dorm-healthcheck.service" /etc/systemd/system/
cp "$APP_DIR/deploy/systemd/dorm-healthcheck.timer" /etc/systemd/system/
cp "$APP_DIR/deploy/nginx/oxelia51.com.conf" /etc/nginx/sites-available/oxelia51.com
ln -sf /etc/nginx/sites-available/oxelia51.com /etc/nginx/sites-enabled/oxelia51.com
rm -f /etc/nginx/sites-enabled/masterc.cn

systemctl daemon-reload
systemctl enable --now dorm-healthcheck.timer
systemctl restart dorm-backend dorm-nonebot
bash "$APP_DIR/deploy/fix-napcat.sh" || true
nginx -t
systemctl reload nginx
"$APP_DIR/deploy/monitor/dorm-healthcheck.sh"
echo "Deploy success"
