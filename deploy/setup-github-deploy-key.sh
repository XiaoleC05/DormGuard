#!/usr/bin/env bash
# 在服务器上生成 GitHub Actions 部署专用密钥
set -euo pipefail

KEY_PATH="/root/.ssh/github_actions_deploy"
mkdir -p /root/.ssh
chmod 700 /root/.ssh

if [ ! -f "$KEY_PATH" ]; then
  ssh-keygen -t ed25519 -N "" -C "github-actions-deploy" -f "$KEY_PATH"
fi

cat "$KEY_PATH.pub" >> /root/.ssh/authorized_keys
chmod 600 /root/.ssh/authorized_keys

echo "====== 将下面私钥完整复制到 GitHub Secret: SSH_PRIVATE_KEY ======"
cat "$KEY_PATH"
echo "====== 公钥已写入 authorized_keys ======"
