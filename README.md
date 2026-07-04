# DormGuard

Xihua University dormitory electricity balance monitor. Sends automated QQ bot alerts when balance drops below the threshold.

## Features

- Scheduled automatic electricity balance queries
- QQ bot push alerts when balance falls below the configured threshold
- Group notification for roommate sync
- Historical balance record query

## Architecture

```text
Python + FastAPI (backend)
  ↓
MySQL (balance history)
  ↓
QQ Bot (go-cqhttp, alert push)
```

Vue 3 frontend provides a data dashboard. FastAPI backend handles scheduled queries and alert logic.

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

Configure the following parameters in `.env`:

- `DATABASE_URL`: MySQL connection string
- `QQ_BOT_URL`: go-cqhttp WebSocket address
- `ALERT_THRESHOLD`: alert threshold (default 10 CNY)
- `CHECK_INTERVAL`: check interval in minutes

## Usage

- QQ bot: 1270667498
- Alert group: 6011223303

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/xxx`)
3. Commit your changes (`git commit -m 'Add xxx'`)
4. Push the branch (`git push origin feature/xxx`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.
