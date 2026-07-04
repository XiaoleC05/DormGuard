# DormGuard

西华大学宿舍电费余额实时监控工具。余额低于阈值时通过 QQ 机器人自动告警。

## Features

- 定时自动查询宿舍电费余额
- 余额低于设定阈值时 QQ 机器人推送告警
- 群通知，室友同步接收提醒
- 历史电费查询与记录

## Architecture

```text
Python + FastAPI (backend)
  ↓
MySQL (balance history)
  ↓
QQ Bot (go-cqhttp, alert push)
```

Vue 3 前端提供数据查看面板，FastAPI 后端负责定时查询和告警逻辑。

## Requirements

- Python 3.10+
- MySQL 8.0
- go-cqhttp

## Installation

```bash
git clone https://github.com/XiaoleC05/DormGuard.git
cd DormGuard

pip install -r requirements.txt

# configure database and QQ bot credentials
cp .env.example .env
# edit .env with your settings

python main.py
```

## Configuration

在 `.env` 中配置以下参数：

- `DATABASE_URL`: MySQL 连接字符串
- `QQ_BOT_URL`: go-cqhttp WebSocket 地址
- `ALERT_THRESHOLD`: 告警阈值（默认 10 元）
- `CHECK_INTERVAL`: 查询间隔（分钟）

## Usage

- QQ 机器人号：1270667498
- 告警群：6011223303

## Contributing

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/xxx`)
3. 提交变更 (`git commit -m 'Add xxx'`)
4. 推送分支 (`git push origin feature/xxx`)
5. 提交 Pull Request

## License

This project is licensed under the MIT License.
