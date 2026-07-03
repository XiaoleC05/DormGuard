#!/usr/bin/env bash
# 在 ECS 上安装 GitHub Actions 自托管 Runner（解决 UFW 拦截 GitHub 云 Runner SSH 的问题）
set -euo pipefail

RUNNER_USER="github-runner"
RUNNER_DIR="/opt/actions-runner"
REPO_URL="https://github.com/XiaoleC05/dorm-power-guard-lite"
SUDOERS_FILE="/etc/sudoers.d/github-runner"

if [ -z "${1:-}" ]; then
  echo "用法: sudo bash $0 REGISTRATION_TOKEN"
  echo ""
  echo "获取 Token："
  echo "https://github.com/XiaoleC05/dorm-power-guard-lite/settings/actions/runners/new"
  echo "复制 --token 后面的字符串，不要加尖括号"
  exit 1
fi

if [ "$(id -u)" -ne 0 ]; then
  echo "请用 root 执行: sudo bash $0 <token>"
  exit 1
fi

TOKEN="$1"
RUNNER_VERSION="2.323.0"
ARCH="x64"

apt-get update -qq
apt-get install -y curl jq libicu70 2>/dev/null || apt-get install -y curl jq libicu66 2>/dev/null || apt-get install -y curl jq

if ! id "$RUNNER_USER" &>/dev/null; then
  useradd -m -s /bin/bash "$RUNNER_USER"
fi

install -d -o "$RUNNER_USER" -g "$RUNNER_USER" -m 755 "$RUNNER_DIR"

if [ ! -f "$RUNNER_DIR/config.sh" ]; then
  curl -fsSL -o /tmp/actions-runner.tar.gz \
    "https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-${ARCH}-${RUNNER_VERSION}.tar.gz"
  tar xzf /tmp/actions-runner.tar.gz -C "$RUNNER_DIR"
  rm -f /tmp/actions-runner.tar.gz
  chown -R "$RUNNER_USER:$RUNNER_USER" "$RUNNER_DIR"
fi

cat > "$SUDOERS_FILE" <<EOF
# 允许自托管 Runner 执行部署脚本（需要 systemctl / nginx 等）
$RUNNER_USER ALL=(ALL) NOPASSWD: /opt/dorm-power-guard-lite/deploy/apply-release.sh, /opt/dorm-power-guard-lite/deploy/fix-napcat.sh, /bin/systemctl, /usr/sbin/nginx, /bin/cp, /bin/ln, /usr/bin/rsync
EOF
chmod 440 "$SUDOERS_FILE"
visudo -cf "$SUDOERS_FILE"

if [ -f "$RUNNER_DIR/.runner" ]; then
  echo "Runner 已配置，重启服务..."
  (cd "$RUNNER_DIR" && ./svc.sh stop || true)
  (cd "$RUNNER_DIR" && ./svc.sh start)
  (cd "$RUNNER_DIR" && ./svc.sh status)
  exit 0
fi

sudo -u "$RUNNER_USER" bash -lc "cd '$RUNNER_DIR' && ./config.sh --url '$REPO_URL' --token '$TOKEN' --name oxelia51-ecs --unattended --replace"
(cd "$RUNNER_DIR" && ./svc.sh install "$RUNNER_USER")
(cd "$RUNNER_DIR" && ./svc.sh start)
(cd "$RUNNER_DIR" && ./svc.sh status)

echo "====== GitHub Actions 自托管 Runner 已启动 ======"
echo "在仓库 Actions 页应能看到 oxelia51-ecs (Idle)"
