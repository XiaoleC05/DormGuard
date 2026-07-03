#!/usr/bin/env bash
# 在 ECS 上安装 GitHub Actions 自托管 Runner（解决 UFW 拦截 GitHub 云 Runner SSH 的问题）
set -euo pipefail

RUNNER_DIR="/opt/actions-runner"
REPO_URL="https://github.com/XiaoleC05/dorm-power-guard-lite"

if [ -z "${1:-}" ]; then
  echo "用法: $0 <REGISTRATION_TOKEN>"
  echo ""
  echo "获取 Token 步骤："
  echo "1. 打开 https://github.com/XiaoleC05/dorm-power-guard-lite/settings/actions/runners/new"
  echo "2. 选择 Linux x64，复制配置命令中的 token（--token 后面的字符串）"
  echo "3. 在本机执行: bash $0 <token>"
  exit 1
fi

TOKEN="$1"
RUNNER_VERSION="2.323.0"
ARCH="x64"

apt-get update -qq
apt-get install -y curl jq libicu70 2>/dev/null || apt-get install -y curl jq libicu66 2>/dev/null || apt-get install -y curl jq

mkdir -p "$RUNNER_DIR"
cd "$RUNNER_DIR"

if [ ! -f ./config.sh ]; then
  curl -fsSL -o actions-runner.tar.gz \
    "https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-${ARCH}-${RUNNER_VERSION}.tar.gz"
  tar xzf actions-runner.tar.gz
  rm -f actions-runner.tar.gz
fi

if [ -f .runner ]; then
  echo "Runner 已配置，尝试重启服务..."
  ./svc.sh status || true
  exit 0
fi

./config.sh --url "$REPO_URL" --token "$TOKEN" --name "oxelia51-ecs" --unattended --replace

./svc.sh install
./svc.sh start
./svc.sh status

echo "====== GitHub Actions 自托管 Runner 已启动 ======"
echo "在仓库 Actions 页应能看到 oxelia51-ecs (Idle)"
