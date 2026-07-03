# 部署说明（masterc.cn）

## 服务器目录

```text
/opt/dorm-power-guard-lite/
├── backend/          # FastAPI + NoneBot
│   ├── .env          # 仅保留在服务器，不被 CI 覆盖
│   └── venv/
├── frontend/dist/    # GitHub Actions 构建产物
└── deploy/           # nginx / systemd 模板
```

## 首次初始化

```bash
ssh root@47.108.202.199
bash /opt/dorm-power-guard-lite/deploy/bootstrap-server.sh
```

将现有 `/root/dorm-power-guard-lite/backend/.env` 复制到 `/opt/dorm-power-guard-lite/backend/.env`，并补充：

```env
ADMIN_USERNAME=root
ADMIN_PASSWORD=783688
ADMIN_JWT_SECRET=请改成随机长字符串
```

## GitHub Secrets

| Name | Value |
|------|-------|
| SSH_HOST | 47.108.202.199 |
| SSH_USER | root |
| SSH_PRIVATE_KEY | 部署专用私钥 |

## 登录

- 地址：https://masterc.cn
- 用户：`root`
- 密码：`783688`

## 内存优化

- 前端在 GitHub Actions 构建，服务器不安装 Node
- systemd `MemoryMax` 限制 backend 256M / nonebot 128M
- MySQL `innodb_buffer_pool_size=64M`
