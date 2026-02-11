# DormPowerGuard-Lite

西华大学宿舍电费监控系统 - MVP快速验证方案

**管理员QQ：714085964**

> 本项目专门为西华大学学生设计，用于监控宿舍电费使用情况，避免因电费不足导致停电。

---

## 📋 目录

- [项目简介](#项目简介)
- [项目特点](#项目特点)
- [技术栈](#技术栈)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
- [详细配置](#详细配置)
- [功能说明](#功能说明)
- [API接口](#api接口)
- [数据库设计](#数据库设计)
- [部署指南](#部署指南)
- [代码更新和维护](#代码更新和维护)
- [常见问题](#常见问题)
- [相关文档](#相关文档)
- [联系与支持](#联系与支持)

---

## 项目简介

这是一个针对**西华大学一卡通宿舍用电小程序**的轻量级电费监控系统，通过Python爬虫定时抓取电费数据，当余额低于设定阈值时自动发送邮件或QQ消息告警。

### 数据来源

- **系统名称**：西华大学一卡通宿舍用电小程序
- **访问地址**：https://ecard.xhu.edu.cn
- **数据接口**：通过抓包分析微信小程序API获取

### 核心功能

1. **定时爬虫** - 每小时自动抓取电费数据
2. **数据存储** - 将电费记录存入MySQL数据库，支持历史查询
3. **告警通知** - 余额低于阈值时自动发送邮件或QQ消息
4. **监控面板** - Web界面查看电费状态、趋势图和用电量统计，支持告警规则配置
5. **手动刷新** - 支持手动触发数据获取
6. **单一宿舍监控** - 针对配置文件中设置的openid用户的宿舍号进行监控

---

## 项目特点

- ✅ **专门针对西华大学**：适配西华大学一卡通系统（https://ecard.xhu.edu.cn）
- ✅ **自动监控**：定时抓取电费数据，无需手动查询
- ✅ **智能告警**：电费低于阈值时自动发送邮件/QQ通知
- ✅ **数据可视化**：Web界面展示电费趋势和用电量统计
- ✅ **易于部署**：支持本地部署和云服务器部署
- ✅ **分类监控**：支持空调和照明分别设置阈值和告警
- ✅ **防频繁告警**：1小时内不重复告警（手动触发除外）
- ✅ **单一宿舍监控**：针对配置文件中设置的openid用户的宿舍号进行监控，告警规则最多存在一个
- ✅ **简洁界面**：监控面板整合告警规则配置，页面整洁简约

---

## 技术栈

### 后端技术

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.8+ | 编程语言 |
| FastAPI | 0.104+ | Web框架，提供REST API |
| Uvicorn | 0.24+ | ASGI服务器，运行FastAPI应用 |
| SQLAlchemy | 2.0+ | ORM框架，数据库操作 |
| PyMySQL | 1.1+ | MySQL数据库驱动 |
| APScheduler | 3.10+ | 定时任务调度 |
| Pydantic | 2.5+ | 数据验证和序列化 |
| Requests | 2.31+ | HTTP请求库，用于爬虫 |
| python-dotenv | 1.0+ | 环境变量管理 |
| email-validator | 2.1+ | 邮箱格式验证 |

### 前端技术

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue | 3.3+ | 前端框架 |
| Vue Router | 4.2+ | 路由管理（前端页面导航） |
| Pinia | 2.1+ | 状态管理（电费数据状态） |
| Element Plus | 2.4+ | UI组件库 |
| ECharts | 5.4+ | 数据可视化图表 |
| Axios | 1.6+ | HTTP客户端 |
| Vite | 5.0+ | 构建工具和开发服务器 |
| Day.js | 1.11+ | 日期时间处理 |

### 数据库

- **MySQL** 5.7+ - 关系型数据库

---

## 项目结构

```
dorm-power-guard-lite/
├── backend/                 # 后端代码
│   ├── app/
│   │   ├── api/            # API路由
│   │   │   ├── power.py   # 电费记录API
│   │   │   ├── alert.py   # 告警API
│   │   │   ├── system.py  # 系统管理API
│   │   ├── models.py       # 数据库模型（SQLAlchemy）
│   │   ├── schemas.py      # Pydantic模型（数据验证）
│   │   ├── services.py     # 业务逻辑层
│   │   ├── crawler.py      # 爬虫模块
│   │   ├── auth_manager.py # 认证管理模块（爬虫认证）
│   │   ├── alert.py        # 告警模块
│   │   ├── scheduler.py    # 定时任务模块
│   │   ├── templates.py    # 邮件模板
│   │   ├── database.py     # 数据库连接
│   │   ├── config.py       # 配置管理
│   │   └── main.py         # FastAPI应用入口
│   ├── requirements.txt    # Python依赖
│   ├── .env.example        # 环境变量示例
│   ├── scripts/            # 脚本目录
│   │   ├── db/            # 数据库脚本
│   │   ├── migrations/    # 迁移脚本
│   │   ├── start/         # 启动脚本
│   │   └── install/       # 安装脚本
│   ├── run.py              # 应用启动入口
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── api/           # API调用
│   │   │   ├── index.js   # Axios配置
│   │   │   ├── power.js   # 电费记录API
│   │   │   ├── alert.js   # 告警API
│   │   │   └── system.js  # 系统管理API
│   │   ├── components/    # 可复用组件
│   │   ├── views/         # 页面组件
│   │   │   ├── Dashboard.vue  # 监控面板
│   │   │   ├── Records.vue    # 电费记录
│   │   │   ├── AlertRules.vue # 告警规则
│   │   │   └── AlertLogs.vue  # 告警日志
│   │   ├── stores/        # 状态管理（Pinia）
│   │   │   └── power.js
│   │   ├── router/        # 路由配置
│   │   │   └── index.js
│   │   ├── App.vue        # 根组件
│   │   └── main.js        # 入口文件
│   ├── package.json       # 前端依赖
│   └── vite.config.js     # Vite配置
└── README.md              # 项目说明
```

---

## 快速开始

### 1. 环境要求

- **Python 3.8+**
- **Node.js 16+** 和 npm
- **MySQL 5.7+**
- **Git**（可选，用于代码更新）

### 2. 克隆项目

```bash
git clone https://gitee.com/ak-god/dorm-power-guard-lite.git
cd dorm-power-guard-lite
```

### 3. 后端部署

#### 3.1 安装Python依赖

```bash
cd backend
pip install -r requirements.txt
```

#### 3.2 配置数据库

**方式一：使用SQL脚本（推荐）**

```bash
mysql -u root -p < backend/scripts/db/init_db.sql
```

**方式二：手动创建**

```bash
mysql -u root -p
```

```sql
CREATE DATABASE dorm_power_guard CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

#### 3.2 配置环境变量

复制 `.env.example` 为 `.env`：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入实际配置（详见[详细配置](#详细配置)章节）。

#### 3.3 启动服务

**方式一：一键启动所有服务（推荐）**

Windows系统提供了完整的一键启动脚本，会自动启动后端、前端、NoneBot和NapCatQQ：

```powershell
# 批处理版本（推荐）
.\start-all-complete.bat

# PowerShell版本（功能更强大）
.\start-all-complete.ps1
```

此脚本会：
- ✅ 自动检查并停止已运行的服务
- ✅ 检查并安装依赖
- ✅ 按顺序启动所有服务（后端 → NoneBot → NapCatQQ → 前端）
- ✅ 显示服务状态和访问地址
- ✅ 提示用户进行NapCatQQ登录操作（扫码或账号密码）

**停止所有服务：**

```powershell
.\stop-all.bat
```

**方式二：手动启动各个服务**

**启动后端：**

```powershell
cd backend
python run.py
```

**Linux/Mac系统：**

```bash
cd backend
python3 run.py
```

后端将在 `http://localhost:8000` 启动。

**访问API文档：**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**启动NoneBot QQ机器人：**

```powershell
cd backend\nonebot_bot
python bot.py
```

**启动NapCatQQ：**

```powershell
# 手动启动NapCatQQ（如果使用一键启动脚本则不需要）
# 确保NapCatQQ.exe在桌面，配置文件在 %USERPROFILE%\Desktop\config\onebot11.json
# 直接运行 NapCatQQ.exe 并登录QQ即可
```

### 4. 前端部署

#### 4.1 安装依赖

```bash
cd frontend
npm install
```

#### 4.2 启动开发服务器

```bash
npm run dev
```

前端将在 `http://localhost:3000` 启动。

#### 5.3 构建生产版本

```bash
npm run build
```

构建产物在 `dist/` 目录。

### 4. QQ机器人配置（可选）

如果需要使用QQ告警功能，需要配置QQ机器人：

1. **安装NoneBot**（已包含在项目中）
2. **安装NapCatQQ**（OneBot实现）
3. **配置连接**（详见[QQ机器人配置](#qq机器人配置)章节）

**快速启动QQ机器人：**

```powershell
# 启动NoneBot
cd backend\nonebot_bot
python bot.py

# 启动NapCatQQ（需要先安装）
# 参考：backend/nonebot_bot/README.md
```

---

## 详细配置

### 1. 数据库配置

编辑 `backend/.env` 文件：

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=dorm_power_guard
```

### 2. 爬虫配置（西华大学一卡通）

编辑 `backend/.env` 文件：

```env
# 系统地址
CRAWLER_BASE_URL=https://ecard.xhu.edu.cn
CRAWLER_API_BASE_URL=https://ecard.xhu.edu.cn/api

# 宿舍信息
CRAWLER_DORM_NUMBER=320  # 您的宿舍号
CRAWLER_ROOM_ID=5699     # 房间ID（通过抓包获取）

# 区域和楼栋信息（根据实际情况修改）
CRAWLER_AREA_ID=1        # 区域ID（1=郫都校区）
CRAWLER_YQ_ID=3          # 园区ID（3=德馨苑）
CRAWLER_BUILDING_ID=40-1 # 楼栋ID
CRAWLER_FLOOR_ID=3       # 楼层ID
CRAWLER_FACTORY_CODE=E014
CRAWLER_SIGN=qt
CRAWLER_ORG_ID=2

# 认证信息（通过抓包获取，详见抓包教程）
CRAWLER_OPENID=your_openid
CRAWLER_JSESSIONID=your_jsessionid
```

**重要**：认证信息需要通过抓包工具获取，详见[抓包获取认证信息](#抓包获取认证信息)章节。

### 3. 定时任务配置

定时任务已固定为**每小时执行一次**，无需在 `.env` 中配置 `SCHEDULER_HOURS`。

### 4. 邮件告警配置

#### 4.1 获取QQ邮箱授权码

1. **登录QQ邮箱**
   - 访问：https://mail.qq.com
   - 使用QQ账号登录

2. **开启SMTP服务**
   - 点击右上角"设置" → "账户"
   - 找到"POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务"部分
   - 开启"POP3/SMTP服务"或"IMAP/SMTP服务"
   - 如果之前未开启，系统会要求进行身份验证（手机验证）

3. **生成授权码**
   - 在"POP3/SMTP服务"或"IMAP/SMTP服务"开启后
   - 点击"生成授权码"按钮
   - 按提示发送短信到指定号码
   - 获取16位授权码（例如：`abcdefghijklmnop`）

#### 4.2 配置邮件发送

编辑 `backend/.env` 文件：

```env
# 启用邮件告警
EMAIL_ENABLED=true

# QQ邮箱SMTP配置
EMAIL_SMTP_HOST=smtp.qq.com
EMAIL_SMTP_PORT=465
EMAIL_SMTP_USER=1270667498@qq.com
EMAIL_SMTP_PASSWORD=your_auth_code  # 替换为你的授权码
EMAIL_FROM=1270667498@qq.com

# 默认接收邮箱（可选，告警规则中配置的邮箱优先级更高）
EMAIL_TO=

# 应用基础URL（用于生成邮件中的链接）
BASE_URL=http://localhost:3000  # 开发环境
# 或
BASE_URL=https://yourdomain.com  # 生产环境
```

#### 4.3 配置告警规则

在前端页面：
1. 进入"告警规则"页面
2. 点击"编辑"
3. 开启"邮件告警"
4. 设置告警阈值（空调和照明，单位：度）
5. 输入接收邮箱地址（多个用逗号分隔）
6. 保存

**注意**：告警规则中配置的邮箱优先级高于全局配置的 `EMAIL_TO`。

### 5. QQ机器人配置（可选，使用 NoneBot）

```env
# QQ机器人配置（NoneBot）
QQ_BOT_ENABLED=true
QQ_BOT_API_URL=http://localhost:8080
QQ_BOT_GROUP_ID=123456789
QQ_BOT_USER_ID=
QQ_BOT_ACCESS_TOKEN=
```

**详细配置指南：**
- `backend/QQ_BOT_SETUP.md` - QQ机器人完整配置指南
- `backend/NONEBOT_SETUP.md` - NoneBot详细配置指南
- `backend/nonebot_bot/README.md` - NoneBot项目说明和快速开始

**文档索引：** 查看 `backend/DOCUMENTATION_INDEX.md` 了解所有文档位置

---

## 抓包获取认证信息

### 方法一：使用Charles抓包（推荐新手）

#### 1. 安装Charles抓包工具

下载地址：https://www.charlesproxy.com/download/

#### 2. 配置手机代理

1. **查看电脑IP地址**
   - Windows: `ipconfig` 查看 IPv4 地址
   - Mac/Linux: `ifconfig` 查看 IP 地址

2. **配置Charles**
   - 打开Charles
   - Proxy → Proxy Settings → 设置端口（默认8888）
   - Proxy → SSL Proxying Settings → 启用SSL Proxying
   - 添加 `ecard.xhu.edu.cn`

3. **配置手机代理**
   - 手机连接与电脑相同的WiFi
   - 设置 → WLAN → 长按当前WiFi → 修改网络
   - 代理：手动
   - 主机名：电脑IP地址
   - 端口：8888

4. **安装Charles证书**
   - 手机浏览器访问：http://chls.pro/ssl
   - 下载并安装证书
   - Android：设置 → 安全 → 安装证书
   - iOS：设置 → 通用 → 关于本机 → 证书信任设置

#### 3. 抓取认证信息

1. **打开西华大学一卡通小程序**
2. **进入宿舍电费查询页面**
3. **在Charles中查看请求**
   - 找到 `ecard.xhu.edu.cn` 的请求
   - 查看请求URL，找到 `openid` 参数
   - 查看请求头，找到 `Cookie` 中的 `JSESSIONID`

#### 4. 配置认证信息

将获取的 `openid` 和 `JSESSIONID` 填入 `backend/.env` 文件：

```env
CRAWLER_OPENID=F461BA806676CD7ADB6AF5AD55C05FF0763F214F010389C27ED18FA6796EA068
CRAWLER_JSESSIONID=9E90FB4FBCAD9700B6FBA66311403CA9
```

### 方法二：使用Fiddler抓包

1. **下载安装Fiddler**
   - 访问：https://www.telerik.com/fiddler
   - 下载并安装

2. **配置Fiddler**
   - Tools → Options → HTTPS
   - 启用"Capture HTTPS CONNECTs"
   - 启用"Decrypt HTTPS traffic"

3. **配置手机代理**（同Charles方法）

4. **抓取请求**
   - 打开小程序
   - 在Fiddler中查看请求
   - 找到包含`openid`和`JSESSIONID`的请求

### 方法三：使用mitmproxy抓包（命令行工具）

```bash
# 安装
pip install mitmproxy

# 启动代理
mitmproxy -p 8888

# 配置手机代理后，在终端中查看请求
```

### 认证信息说明

- **openid**：用户唯一标识，通过URL参数传递
- **JSESSIONID**：会话ID，通过Cookie传递
- **有效期**：通常不会过期，小程序会保持登录状态
- **自动获取**：系统支持自动获取认证信息（方案一）

### 常见问题

**问题1：无法抓取HTTPS请求**
- 解决：安装并信任证书

**问题2：手机无法连接代理**
- 解决：确保手机和电脑在同一WiFi网络

**问题3：找不到openid和JSESSIONID**
- 解决：查看请求URL和请求头，仔细查找

---

## 功能说明

### 1. 监控面板

- **功能**：查看当前电费余量、历史趋势图
- **操作**：点击"重新获取"按钮手动刷新数据
- **显示内容**：
  - 空调余量（度）
  - 照明余量（度）
  - 用电量趋势图（ECharts图表）

### 2. 电费记录

- **功能**：查看历史电费记录
- **显示内容**：
  - 记录时间
  - 空调余量和用电量（度）
  - 照明余量和用电量（度）

### 3. 告警规则

- **功能**：配置告警阈值和接收邮箱
- **配置项**：
  - 空调告警阈值（度）
  - 照明告警阈值（度）
  - 邮件告警开关
  - 接收邮箱地址（多个用逗号分隔）
  - QQ告警开关（可选）

### 4. 告警日志

- **功能**：查看历史告警记录
- **显示内容**：
  - 告警时间
  - 告警类别（空调/照明）
  - 告警状态（成功/失败）
  - 告警消息

### 5. 定时任务

系统**每小时自动执行一次**爬虫，获取电费数据并检查告警阈值。无需在 `.env` 中配置执行时间。

### 6. 告警功能

- **邮件告警**：使用QQ邮箱发送告警邮件到指定邮箱
- **QQ机器人告警**：支持 NoneBot QQ机器人
- **防频繁告警**：1小时内不重复告警（手动触发除外）
- **分类告警**：支持空调和照明分别设置阈值
- **失败重试**：上次告警失败时，下次触发立即重试

---

## API接口

### RESTful API规范

- **GET**：查询数据
- **POST**：创建数据
- **PUT**：更新数据
- **DELETE**：删除数据

### 主要API端点

#### 1. 电费记录API

- `GET /api/power/records/{dorm_number}/latest` - 获取最新电费记录
- `GET /api/power/records/{dorm_number}?limit=100` - 获取电费记录列表

**请求示例：**

```bash
curl http://localhost:8000/api/power/records/320/latest
```

**响应示例：**

```json
{
  "id": 1,
  "dorm_number": "320",
  "kbalance": 45.5,
  "zbalance": 38.2,
  "kpower_consumption": 2.3,
  "zpower_consumption": 1.8,
  "record_time": "2024-01-01T12:00:00",
  "created_at": "2024-01-01T12:00:00"
}
```

#### 2. 告警规则API

- `GET /api/alert/rules` - 获取所有告警规则
- `POST /api/alert/rules` - 创建告警规则
- `PUT /api/alert/rules/{dorm_number}` - 更新告警规则
- `DELETE /api/alert/rules/{dorm_number}` - 删除告警规则

**创建告警规则示例：**

```bash
curl -X POST http://localhost:8000/api/alert/rules \
  -H "Content-Type: application/json" \
  -d '{
    "dorm_number": "320",
    "kthreshold": 20.0,
    "zthreshold": 20.0,
    "email_enabled": true,
    "email_address": "user@example.com"
  }'
```

#### 3. 系统管理API

- `POST /api/system/crawl` - 手动触发爬虫任务
- `GET /api/system/qq-config` - 获取QQ机器人全局配置

**请求示例：**

```bash
# 手动触发爬虫
curl -X POST http://localhost:8000/api/system/crawl

# 获取QQ配置
curl http://localhost:8000/api/system/qq-config
```

---

## 数据库设计

### 表结构

#### 1. `power_records` - 电费记录表

存储从西华大学电费系统抓取的电费数据，包括余量和用电量信息。本项目针对单一宿舍监控，宿舍号从配置文件读取。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键ID，自增 |
| dorm_number | VARCHAR(50) | 宿舍号（如：320、324），用于标识不同的宿舍 |
| balance | FLOAT | 电费余量（度），主要监控项，通常是空调余量，用于判断是否需要告警 |
| kbalance | FLOAT | 空调余量（度），从API获取的空调专用电费余量 |
| zbalance | FLOAT | 照明余量（度），从API获取的照明专用电费余量 |
| kpower_consumption | FLOAT | 空调用电量（度），与上次记录的差值，表示本次记录周期内的空调用电量 |
| zpower_consumption | FLOAT | 照明用电量（度），与上次记录的差值，表示本次记录周期内的照明用电量 |
| power_consumption | FLOAT | 用电量（度），已废弃，保留用于兼容性，请使用kpower_consumption和zpower_consumption |
| record_time | DATETIME | 记录时间，数据抓取的时间点 |
| created_at | DATETIME | 创建时间，记录插入数据库的时间 |

**索引建议：**

```sql
CREATE INDEX idx_dorm_number ON power_records(dorm_number);
CREATE INDEX idx_record_time ON power_records(record_time);
```

#### 2. `alert_rules` - 告警规则表

存储单一宿舍的告警配置，包括阈值设置和告警方式（邮件/QQ）。本项目仅支持单一宿舍监控，最多存在一条规则，宿舍号从配置文件读取。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键ID，自增 |
| dorm_number | VARCHAR(50) | 宿舍号（如：320、324），从配置文件读取，唯一标识监控的宿舍 |
| room_id | VARCHAR(50) | 房间ID（roomid），从西华大学电费系统API获取，用于查询该宿舍的电费数据 |
| kthreshold | FLOAT | 空调告警阈值（度），当空调余量低于此值时触发告警 |
| zthreshold | FLOAT | 照明告警阈值（度），当照明余量低于此值时触发告警 |
| threshold | FLOAT | 告警阈值（度），已废弃，保留用于兼容性，请使用kthreshold和zthreshold |
| enabled | BOOLEAN | 是否启用告警规则，False时不会触发任何告警 |
| email_enabled | BOOLEAN | 是否启用邮件告警，True时当余量低于阈值会发送邮件 |
| email_address | VARCHAR(255) | 邮件告警接收邮箱地址，启用邮件告警时必须填写 |
| qq_enabled | BOOLEAN | 是否启用QQ告警，True时当余量低于阈值会发送QQ消息 |
| qq_receiver_id | VARCHAR(50) | QQ告警接收者ID，可以是QQ号（私聊）或群号（群聊，通常>=1000000000），启用QQ告警时必须填写 |
| last_alert_time | DATETIME | 最后告警时间，用于防止频繁告警，记录最近一次成功发送告警的时间 |
| created_at | DATETIME | 创建时间，规则创建的时间 |
| updated_at | DATETIME | 更新时间，规则最后修改的时间 |

**唯一约束：**

```sql
ALTER TABLE alert_rules ADD UNIQUE KEY uk_dorm_number (dorm_number);
```

#### 3. `alert_logs` - 告警日志表

记录所有告警发送的历史记录，包括成功和失败的告警，用于审计和问题排查。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键ID，自增 |
| dorm_number | VARCHAR(50) | 宿舍号（如：320、324），标识触发告警的宿舍 |
| alert_category | VARCHAR(20) | 告警类别：ac（空调）/light（照明），标识是哪个类型的电费余量触发了告警 |
| balance | FLOAT | 触发告警时的余量（度），记录告警触发时的实际电费余量 |
| threshold | FLOAT | 告警阈值（度），记录触发告警时使用的阈值 |
| alert_type | VARCHAR(20) | 告警类型：email（邮件告警）/qq（QQ告警），标识使用的告警方式 |
| alert_status | VARCHAR(20) | 告警状态：success（发送成功）/failed（发送失败），标识告警是否成功发送 |
| alert_message | TEXT | 告警消息内容，记录实际发送的告警消息文本 |
| created_at | DATETIME | 创建时间，告警发送的时间 |

---

## 部署指南

### Windows 本地运行

使用项目根目录的一键启动脚本（推荐）：

```bash
.\start-all-complete.bat
```

或分别启动：

```bash
# 后端（新开终端）
cd backend
python run.py

# 前端（新开终端）
cd frontend
npm run dev

# NoneBot（可选，新开终端）
cd backend\nonebot_bot
python bot.py
```

### Linux/Mac 本地运行

```bash
# 后端
cd backend && python3 run.py

# 前端（新终端）
cd frontend && npm run dev

# NoneBot（可选）
cd backend/nonebot_bot && python3 bot.py
```

---

### 云服务器部署（24 小时运行）

要让程序在电脑关闭后仍能运行，需要部署到一台**长期在线的服务器**（如云服务器）。

#### 一、准备云服务器

1. **购买云服务器**

   **若选阿里云**，可按下表选择（二选一即可）：

   | 产品 | 推荐配置 | 说明 |
   |------|----------|------|
   | **轻量应用服务器** | 2 核 2GB、60GB SSD、Ubuntu 22.04 | 固定月费、带流量包，适合个人/小项目，控制台简单 |
   | **云服务器 ECS** | 1 核 2GB 或 2 核 2GB、40GB 云盘、Ubuntu 22.04 | 按量/包月均可，配置更灵活 |

   - **轻量应用服务器**：阿里云控制台 → 产品 → 轻量应用服务器 → 创建服务器，地域选离你或学校近的（如西南可选成都），镜像选 **Ubuntu 22.04**，套餐选 2 核 2G 或更高即可。
   - **云服务器 ECS**：阿里云控制台 → ECS → 实例与镜像 → 创建实例，地域同上，镜像选 **Ubuntu 22.04**，实例规格选 1 核 2G（如 ecs.t6-c1m2.large）或 2 核 2G，系统盘 40GB+。

   **通用建议**：
   - 配置：**1 核 2GB 内存、40GB SSD** 可跑后端+前端+MySQL+NoneBot；若要同时跑 NapCatQQ（Docker），建议 **2 核 2GB** 更稳。
   - 系统：**Ubuntu 22.04 LTS**。
   - 带宽：轻量一般自带 3–5Mbps，ECS 选 1–3Mbps 即可。

2. **登录服务器**

```bash
ssh root@你的服务器IP
```

#### 二、安装环境

```bash
apt update
apt install -y python3 python3-pip python3-venv git mysql-server nginx nodejs npm
```

- 若 `nodejs` 版本过旧，可用 [NodeSource](https://github.com/nodesource/distributions) 安装 Node 18+。

#### 三、克隆项目并安装依赖

```bash
cd /opt
git clone https://gitee.com/ak-god/dorm-power-guard-lite.git
cd dorm-power-guard-lite
```

**后端：**

```bash
cd /opt/dorm-power-guard-lite/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**前端（构建静态文件）：**

```bash
cd /opt/dorm-power-guard-lite/frontend
npm install
npm run build
```

生成的前端文件在 `frontend/dist/`，供 Nginx 使用。

#### 四、MySQL 数据库

1. **启动并配置 MySQL**

```bash
sudo systemctl start mysql
sudo mysql_secure_installation  # 按提示设置 root 密码
```

2. **创建数据库和用户**

```bash
sudo mysql -u root -p
```

在 MySQL 中执行：

```sql
CREATE DATABASE dorm_power_guard CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'dorm_guard'@'localhost' IDENTIFIED BY '你的密码';
GRANT ALL ON dorm_power_guard.* TO 'dorm_guard'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

3. **初始化表结构**

```bash
mysql -u dorm_guard -p dorm_power_guard < /opt/dorm-power-guard-lite/backend/scripts/db/init_db.sql
```

#### 五、配置后端环境变量

```bash
cd /opt/dorm-power-guard-lite/backend
cp .env.example .env
nano .env
```

必填项示例：

- `DB_HOST=localhost`、`DB_PORT=3306`、`DB_USER=dorm_guard`、`DB_PASSWORD=你的密码`、`DB_NAME=dorm_power_guard`
- `CRAWLER_OPENID`、`CRAWLER_JSESSIONID`（抓包获取）
- `CRAWLER_DORM_NUMBER`、`CRAWLER_ROOM_ID`（或通过告警规则中的 room_id 配置）
- 邮件/QQ 告警按需配置（见上文「详细配置」）

云服务器上通常**不部署 NoneBot/NapCatQQ**（需图形界面登录 QQ），可关闭 QQ 告警或仅在本地运行 QQ 机器人。

#### 六、用 systemd 管理后端

创建服务文件：

```bash
sudo nano /etc/systemd/system/dorm-power-guard.service
```

内容（路径按实际修改）：

```ini
[Unit]
Description=Dorm Power Guard Backend
After=network.target mysql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/dorm-power-guard-lite/backend
Environment="PATH=/opt/dorm-power-guard-lite/backend/venv/bin:/usr/bin:/usr/local/bin"
ExecStart=/opt/dorm-power-guard-lite/backend/venv/bin/python run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

若未使用 venv，则 `ExecStart` 改为：`/usr/bin/python3 /opt/dorm-power-guard-lite/backend/run.py`。

启动并开机自启：

```bash
sudo systemctl daemon-reload
sudo systemctl enable dorm-power-guard
sudo systemctl start dorm-power-guard
sudo systemctl status dorm-power-guard
```

#### 七、Nginx 反向代理

创建站点配置：

```bash
sudo nano /etc/nginx/sites-available/dorm-power-guard
```

内容（将 `your_domain.com` 改为你的域名或服务器 IP）：

```nginx
server {
    listen 80;
    server_name your_domain.com;   # 或服务器公网IP

    # 前端静态文件
    location / {
        root /opt/dorm-power-guard-lite/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # 后端 API
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

启用站点并重启 Nginx：

```bash
sudo ln -sf /etc/nginx/sites-available/dorm-power-guard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 八、HTTPS（可选）

使用 Let's Encrypt（需已解析域名的域名）：

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your_domain.com
```

#### 九、防火墙

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

#### 十、验证

- 浏览器访问：`http://你的域名或IP`
- 应能看到前端页面，且监控/电费数据能正常加载（需先配置好抓包得到的 openid 等并在前端配置告警规则中的 room_id）。

---

#### （可选）云上同时部署 NoneBot + NapCatQQ

若希望 QQ 告警也在云服务器上运行，可在同一台机器上部署 **NoneBot** 和 **NapCatQQ**（NapCatQQ 推荐用 Docker，便于 WebUI 扫码登录）。

**1. 安装 NoneBot 依赖并配置**

```bash
cd /opt/dorm-power-guard-lite/backend/nonebot_bot
python3 -m venv venv
source venv/bin/activate
pip install nonebot2 nonebot-adapter-onebot httpx
```

确认 `backend/nonebot_bot/.env` 中：

- `HOST=0.0.0.0`、`PORT=8080`（供本机 NapCat 连接）

**2. 用 systemd 管理 NoneBot**

```bash
sudo nano /etc/systemd/system/dorm-nonebot.service
```

内容示例：

```ini
[Unit]
Description=Dorm Power Guard NoneBot QQ
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/dorm-power-guard-lite/backend/nonebot_bot
Environment="PATH=/opt/dorm-power-guard-lite/backend/nonebot_bot/venv/bin:/usr/bin"
ExecStart=/opt/dorm-power-guard-lite/backend/nonebot_bot/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable dorm-nonebot
sudo systemctl start dorm-nonebot
sudo systemctl status dorm-nonebot
```

**3. 用 Docker 部署 NapCatQQ（推荐）**

NapCatQQ 需扫码登录，Docker 版提供 WebUI（端口 6099）用于扫码。

- 安装 Docker（若未装）：`apt install -y docker.io docker-compose`
- 创建数据目录并运行容器（按需替换镜像名，以官方/社区文档为准）：

```bash
sudo mkdir -p /opt/napcat/data
sudo docker run -d \
  --name napcat \
  --restart unless-stopped \
  -p 6099:6099 \
  -v /opt/napcat/data:/app/napcat/data \
  -e WEBUI_TOKEN=你的WebUI访问令牌 \
  mlikiowa/napcat-docker:latest
```

- 首次登录：浏览器访问 `http://你的服务器IP:6099`（或 `https://你的域名` 若用 Nginx 反代 6099），在 WebUI 中扫码登录 QQ。
- 配置连接 NoneBot：在 NapCat 的 WebUI 或挂载的配置里，添加**反向 WebSocket** 客户端，地址为 `ws://宿主机IP:8080/onebot/v11/ws`（若 NapCat 与 NoneBot 同机，填 `ws://127.0.0.1:8080/onebot/v11/ws`）。保存后 NapCat 会连上 NoneBot。

**4. 后端配置**

在 `backend/.env` 中开启 QQ 告警并指向本机 NoneBot：

```env
QQ_BOT_ENABLED=true
QQ_BOT_API_URL=http://127.0.0.1:8080
```

告警规则中的接收 QQ/群号仍在前端「告警规则」里配置（qq_receiver_id）。

**5. 防火墙（仅需时开放）**

若通过公网访问 WebUI 扫码，临时开放 6099：

```bash
sudo ufw allow 6099/tcp
sudo ufw reload
```

更安全的做法是：不开放 6099，在本地用 SSH 隧道访问 WebUI：

```bash
ssh -L 6099:127.0.0.1:6099 root@你的服务器IP
```

然后在本地浏览器打开 `http://localhost:6099` 进行扫码和配置。

**6. 扫码提示「网络不稳定」时**

部分云机房 IP 会被 QQ 限制，可尝试：

- 用 SSH 隧道在本地浏览器打开 WebUI 再扫码（出口 IP 为服务器，有时可过）；
- 或在本机/家里电脑先跑一遍 NapCatQQ，登录成功后把 NapCat 的登录凭证（如 device、session 等）拷贝到服务器 NapCat 数据目录再启动（具体文件名见 NapCat 文档）。

**7. 更新代码后重启**

```bash
sudo systemctl restart dorm-power-guard
sudo systemctl restart dorm-nonebot
sudo docker restart napcat
```

按以上步骤即可在云服务器上同时跑 **后端 + 前端 + NoneBot + NapCatQQ**，实现 24 小时电费监控与 QQ 告警。

---

## 代码更新和维护

### 使用Git更新（推荐）

#### 工作流程

1. **本地修改代码**
2. **提交并推送**：`git push`
3. **服务器拉取**：`git pull`
4. **重启服务**：`sudo systemctl restart dorm-power-guard`

整个过程通常不到1分钟。

#### 具体步骤

**在本地（您的电脑）**：

```bash
cd c:\GitCloneRepository\dorm-power-guard-lite
git add .
git commit -m "描述你的修改"
git push origin master
```

**在服务器上**：

```bash
cd /opt/dorm-power-guard-lite
git pull origin master
sudo systemctl restart dorm-power-guard
```

#### 自动化更新脚本

创建 `backend/update.sh`：

```bash
#!/bin/bash
cd /opt/dorm-power-guard-lite
git pull origin master
cd backend
pip3 install -r requirements.txt
sudo systemctl restart dorm-power-guard
```

使用：

```bash
chmod +x backend/update.sh
./backend/update.sh
```

### 使用VS Code Remote SSH（推荐给开发者）

1. **安装VS Code扩展**
   - 搜索并安装 "Remote - SSH"

2. **配置SSH连接**
   - 按 `F1` → "Remote-SSH: Connect to Host"
   - 配置SSH hosts

3. **连接到服务器**
   - 选择服务器
   - 打开项目文件夹

4. **编辑和调试**
   - 就像编辑本地文件一样
   - 保存后重启服务

---

## 常见问题

### Q1: 如何获取认证信息？

**A**: 使用抓包工具（Charles/Fiddler）抓取小程序请求，提取 `openid` 和 `JSESSIONID`。详细教程请参考[抓包获取认证信息](#抓包获取认证信息)章节。

### Q2: 认证信息会过期吗？

**A**: 通常不会过期，小程序会保持登录状态。如果过期，需要重新抓包获取。

### Q3: 邮件发送失败怎么办？

**A**: 
1. 检查QQ邮箱授权码是否正确（不是QQ密码）
2. 检查网络连接
3. 查看后端日志：`backend/logs/` 目录
4. 参考[邮件告警配置](#邮件告警配置)章节

### Q4: 如何修改抓取频率？

**A**: 当前版本固定为**每小时执行一次**。若需修改，请直接改 `backend/app/scheduler.py` 中 `IntervalTrigger(hours=1)` 的参数并重启后端。

### Q5: 如何部署到云服务器？

**A**: 详细步骤请参考[部署指南](#部署指南)章节。

### Q6: 如何更新代码？

**A**: 详细步骤请参考[代码更新和维护](#代码更新和维护)章节。

### Q7: 数据存储在哪里？

**A**: 所有数据存储在本地MySQL数据库中，不会上传到第三方服务器。

### Q8: 如何备份数据？

**A**: 
```bash
# 备份数据库
mysqldump -u root -p dorm_power_guard > backup.sql

# 恢复数据库
mysql -u root -p dorm_power_guard < backup.sql
```

### Q9: 程序无法启动怎么办？

**A**: 
1. 检查Python和Node.js版本是否符合要求
2. 检查数据库是否正常运行
3. 检查 `.env` 文件配置是否正确
4. 查看后端日志：`backend/logs/` 目录

### Q10: 如何查看服务日志？

**A**: 
```bash
# systemd服务日志
sudo journalctl -u dorm-power-guard -f

# 应用日志（如果配置了日志文件）
tail -f backend/logs/app.log
```

### Q11: 告警没有发送怎么办？

**A**: 
1. 检查告警规则是否启用
2. 检查余量是否低于阈值
3. 检查是否在防频繁告警时间窗口内（1小时）
4. 手动触发爬虫测试：`POST /api/system/crawl`
5. 查看告警日志页面

### Q12: 如何测试后端功能？

**A**: 
1. 执行数据库迁移（如需要）：`python migrations/add_qq_receiver_id.py` 和 `python migrations/add_room_id.py`
2. 启动服务：`python run.py`
3. 访问API文档：http://localhost:8000/docs
4. 使用Swagger UI测试各个接口

---

## 联系与支持

- **管理员QQ**：714085964
- **项目用途**：仅供西华大学学生个人使用
- **数据安全**：所有数据存储在本地，不会上传到第三方服务器

如有问题或建议，欢迎通过QQ联系管理员。

---

## 相关文档

- **技术栈文档**: [技术栈文档.md](技术栈文档.md) - 系统架构、技术实现细节、技术栈详解
- **开发日志**: [CHANGELOG.md](CHANGELOG.md) - 版本更新记录、开发历程、故障排查记录

---

## 贡献

欢迎提交Issue和Pull Request！

---

## 许可证

MIT License

---

**开发说明**：本项目为开源项目，欢迎提交Issue和Pull Request。  
**注意**：本项目仅用于学习和个人使用，请遵守西华大学相关规定，不得用于商业用途。

**文档维护原则**：项目只保留核心文档（README.md、技术栈文档.md、CHANGELOG.md），不再生成多余的文档和测试内容，只根据最新代码更新现有文档。
