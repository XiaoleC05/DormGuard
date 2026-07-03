#!/usr/bin/env bash
# 服务器首次规范化脚本（仅需执行一次）
set -euo pipefail

APP_DIR="/opt/dorm-power-guard-lite"
REPO_URL="https://github.com/XiaoleC05/dorm-power-guard-lite.git"

echo "[1/8] 安装基础依赖..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq git python3 python3-pip python3-venv nginx mysql-server

echo "[2/8] 准备目录 ${APP_DIR}..."
mkdir -p "${APP_DIR}"
if [ ! -d "${APP_DIR}/.git" ]; then
  git clone "${REPO_URL}" "${APP_DIR}"
fi

echo "[3/8] 创建 Python 虚拟环境..."
cd "${APP_DIR}/backend"
python3 -m venv venv
./venv/bin/pip install --upgrade pip -q
./venv/bin/pip install -r requirements.txt -q

echo "[4/8] 安装 systemd 服务..."
cp "${APP_DIR}/deploy/systemd/dorm-backend.service" /etc/systemd/system/
cp "${APP_DIR}/deploy/systemd/dorm-nonebot.service" /etc/systemd/system/
systemctl daemon-reload

echo "[5/8] 配置 Nginx masterc.cn..."
cp "${APP_DIR}/deploy/nginx/masterc.cn.conf" /etc/nginx/sites-available/masterc.cn
ln -sf /etc/nginx/sites-available/masterc.cn /etc/nginx/sites-enabled/masterc.cn
nginx -t
systemctl enable nginx
systemctl reload nginx

echo "[6/8] 启用业务服务..."
systemctl enable dorm-backend dorm-nonebot
systemctl restart dorm-backend dorm-nonebot

echo "[7/8] 优化 MySQL 内存占用..."
cat > /etc/mysql/mysql.conf.d/99-dorm-low-memory.cnf <<'EOF'
[mysqld]
innodb_buffer_pool_size = 64M
performance_schema = OFF
EOF
systemctl restart mysql

echo "[8/8] 完成。请确认 ${APP_DIR}/backend/.env 已配置。"
