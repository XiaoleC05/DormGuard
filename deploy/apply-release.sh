#!/usr/bin/env bash
# 在服务器上应用已构建的发布包（GitHub Actions self-hosted 或手动执行）
set -euo pipefail

APP_DIR=/opt/DormGuard
OLD_APP_DIR=/opt/dorm-power-guard-lite
RELEASE_DIR="${1:-/tmp/dormguard-release}"

if [ ! -d "$RELEASE_DIR/backend" ]; then
  echo "错误：未找到 $RELEASE_DIR/backend，请先解压 dormguard-release.tar.gz"
  exit 1
fi

# 兼容旧部署路径：仅迁移 .env（不复制 venv，避免 shebang 指向旧路径）
if [ -d "$OLD_APP_DIR" ]; then
  mkdir -p "$APP_DIR/backend"
  if [ -f "$OLD_APP_DIR/backend/.env" ] && [ ! -f "$APP_DIR/backend/.env" ]; then
    cp -a "$OLD_APP_DIR/backend/.env" "$APP_DIR/backend/.env"
  fi
fi

mkdir -p "$APP_DIR/backend" "$APP_DIR/frontend/dist" "$APP_DIR/deploy"
rsync -a "$RELEASE_DIR/backend/" "$APP_DIR/backend/"
rsync -a --delete "$RELEASE_DIR/frontend-dist/" "$APP_DIR/frontend/dist/"
rsync -a "$RELEASE_DIR/deploy/" "$APP_DIR/deploy/"
chmod +x "$APP_DIR/deploy/"*.sh "$APP_DIR/deploy/monitor/"*.sh 2>/dev/null || true

ensure_backend_venv() {
  cd "$APP_DIR/backend"
  local recreate=0
  if [ ! -x "venv/bin/python" ] && [ ! -x "venv/bin/python3" ]; then
    recreate=1
  elif head -1 venv/bin/pip 2>/dev/null | grep -q 'dorm-power-guard-lite'; then
    recreate=1
  fi
  if [ "$recreate" -eq 1 ]; then
    echo "重建 Python 虚拟环境（修复旧路径 shebang）..."
    rm -rf venv
  fi
  if [ ! -d venv ]; then
    python3 -m venv venv
  fi
  venv/bin/python -m pip install --upgrade pip -q
  venv/bin/python -m pip install -r requirements.txt -q
  if [ -f requirements-nonebot.txt ]; then
    venv/bin/python -m pip install -r requirements-nonebot.txt -q
  fi
}

ensure_backend_venv

cp "$APP_DIR/deploy/systemd/dormguard-backend.service" /etc/systemd/system/
cp "$APP_DIR/deploy/systemd/dormguard-nonebot.service" /etc/systemd/system/
cp "$APP_DIR/deploy/systemd/dormguard-healthcheck.service" /etc/systemd/system/
cp "$APP_DIR/deploy/systemd/dormguard-healthcheck.timer" /etc/systemd/system/
cp "$APP_DIR/deploy/nginx/oxelia51.com.conf" /etc/nginx/sites-available/oxelia51.com
ln -sf /etc/nginx/sites-available/oxelia51.com /etc/nginx/sites-enabled/oxelia51.com
cp "$APP_DIR/deploy/nginx/default-ip.conf" /etc/nginx/sites-available/default-ip
ln -sf /etc/nginx/sites-available/default-ip /etc/nginx/sites-enabled/default-ip
rm -f /etc/nginx/sites-enabled/masterc.cn

systemctl stop dorm-backend dorm-nonebot 2>/dev/null || true
systemctl disable dorm-backend dorm-nonebot dorm-healthcheck.timer 2>/dev/null || true
rm -f /etc/systemd/system/dorm-backend.service /etc/systemd/system/dorm-nonebot.service
rm -f /etc/systemd/system/dorm-healthcheck.service /etc/systemd/system/dorm-healthcheck.timer

systemctl daemon-reload
systemctl enable --now dormguard-healthcheck.timer
systemctl restart dormguard-backend dormguard-nonebot

bash "$APP_DIR/deploy/fix-napcat.sh" || true

nginx -t
systemctl reload nginx

if "$APP_DIR/deploy/monitor/dormguard-healthcheck.sh"; then
  echo "Deploy success"
else
  echo "Deploy finished with health warnings (see above)" >&2
  exit 1
fi
