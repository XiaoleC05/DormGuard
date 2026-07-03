#!/usr/bin/env bash
# 一次性：从 /root/dorm-power-guard-lite 迁移到 /opt，并停掉重复进程
set -euo pipefail

OLD_DIR="/root/dorm-power-guard-lite"
APP_DIR="/opt/dorm-power-guard-lite"

echo "[1] 停止手动启动的重复进程..."
pkill -f "${OLD_DIR}/backend/venv/bin/python run.py" 2>/dev/null || true
pkill -f "${OLD_DIR}/backend/nonebot_bot" 2>/dev/null || true
sleep 2

echo "[2] 迁移代码到 ${APP_DIR}..."
mkdir -p /opt
if [ -d "$OLD_DIR" ]; then
  rsync -a --delete --exclude venv --exclude node_modules "$OLD_DIR/" "$APP_DIR/"
else
  mkdir -p "$APP_DIR"
fi

echo "[3] 保留 .env..."
if [ -f "$OLD_DIR/backend/.env" ] && [ ! -f "$APP_DIR/backend/.env" ]; then
  cp "$OLD_DIR/backend/.env" "$APP_DIR/backend/.env"
fi

if ! grep -q '^ADMIN_USERNAME=' "$APP_DIR/backend/.env" 2>/dev/null; then
  cat >> "$APP_DIR/backend/.env" <<'EOF'
ADMIN_USERNAME=root
ADMIN_PASSWORD=783688
ADMIN_JWT_SECRET=please-change-this-secret
ADMIN_TOKEN_EXPIRE_HOURS=168
EOF
fi

echo "[4] 创建虚拟环境..."
cd "$APP_DIR/backend"
python3 -m venv venv
./venv/bin/pip install --upgrade pip -q
./venv/bin/pip install -r requirements.txt -q

echo "[5] 安装 systemd + nginx..."
cp "$APP_DIR/deploy/systemd/dorm-backend.service" /etc/systemd/system/
cp "$APP_DIR/deploy/systemd/dorm-nonebot.service" /etc/systemd/system/
cp "$APP_DIR/deploy/nginx/masterc.cn.conf" /etc/nginx/sites-available/masterc.cn
ln -sf /etc/nginx/sites-available/masterc.cn /etc/nginx/sites-enabled/masterc.cn
systemctl daemon-reload

echo "[6] 限制 MySQL 内存..."
cat > /etc/mysql/mysql.conf.d/99-dorm-low-memory.cnf <<'EOF'
[mysqld]
innodb_buffer_pool_size = 64M
performance_schema = OFF
EOF
systemctl restart mysql

echo "[7] 启动业务服务..."
systemctl enable dorm-backend dorm-nonebot
systemctl restart dorm-backend dorm-nonebot
nginx -t
systemctl reload nginx

echo "[8] 清理旧目录（保留 .env 备份）..."
if [ -d "$OLD_DIR" ]; then
  mv "$OLD_DIR" "/root/dorm-power-guard-lite.bak.$(date +%Y%m%d)"
fi

echo "迁移完成：${APP_DIR}"
