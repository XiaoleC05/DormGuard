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
- [联系与支持](#联系与支持)

---

## 项目简介

这是一个针对**西华大学一卡通宿舍用电小程序**的轻量级电费监控系统，通过Python爬虫定时抓取电费数据，当余额低于设定阈值时自动发送邮件或QQ消息告警。

### 数据来源

- **系统名称**：西华大学一卡通宿舍用电小程序
- **访问地址**：https://ecard.xhu.edu.cn
- **数据接口**：通过抓包分析微信小程序API获取

### 核心功能

1. **定时爬虫** - 每天在指定时间点（默认：8:00, 12:00, 18:00, 22:00）自动抓取电费数据
2. **数据存储** - 将电费记录存入MySQL数据库，支持历史查询
3. **告警通知** - 余额低于阈值时自动发送邮件或QQ消息
4. **监控面板** - Web界面查看电费状态、趋势图和用电量统计
5. **手动刷新** - 支持手动触发数据获取
6. **多用户系统** - 学生注册登录，提交宿舍信息，自主管理监控
7. **管理员系统** - 管理员账号密码登录，管理用户和监控
8. **安全机制** - 学生确认机制防止错误提交，登录失败限制，Session管理

---

## 项目特点

- ✅ **专门针对西华大学**：适配西华大学一卡通系统（https://ecard.xhu.edu.cn）
- ✅ **自动监控**：定时抓取电费数据，无需手动查询
- ✅ **智能告警**：电费低于阈值时自动发送邮件/QQ通知
- ✅ **数据可视化**：Web界面展示电费趋势和用电量统计
- ✅ **易于部署**：支持本地部署和云服务器部署
- ✅ **分类监控**：支持空调和照明分别设置阈值和告警
- ✅ **防频繁告警**：1小时内不重复告警（手动触发除外）
- ✅ **多用户支持**：学生可注册账号，提交自己的宿舍信息
- ✅ **安全确认**：学生提交后需确认电费数据，防止误填其他宿舍
- ✅ **提交限制**：同一邮箱每天最多提交3次，防止恶意提交
- ✅ **管理员管理**：管理员可管理用户、审批多宿舍申请

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
| BeautifulSoup4 | 4.12+ | HTML解析（备用） |
| python-dotenv | 1.0+ | 环境变量管理 |
| passlib[bcrypt] | 1.7+ | 密码哈希加密 |
| python-jose | 3.3+ | JWT Token支持（备用） |
| itsdangerous | 2.1+ | Session签名支持 |

### 前端技术

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue | 3.3+ | 前端框架 |
| Vue Router | 4.2+ | 路由管理 |
| Pinia | 2.1+ | 状态管理 |
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
│   │   │   ├── auth.py    # 认证API（用户/管理员登录）
│   │   │   ├── submissions.py # 宿舍提交API
│   │   │   ├── multi_dorm.py  # 多宿舍申请API
│   │   │   ├── my_monitor.py  # 我的监控API
│   │   │   ├── admin.py       # 管理员管理API
│   │   │   └── admin_users.py # 管理员用户管理API
│   │   ├── models.py       # 数据库模型（SQLAlchemy）
│   │   ├── schemas.py      # Pydantic模型（数据验证）
│   │   ├── services.py     # 业务逻辑层
│   │   ├── crawler.py      # 爬虫模块
│   │   ├── auth_manager.py # 认证管理模块（爬虫认证）
│   │   ├── auth.py         # 认证服务（密码哈希、登录限制）
│   │   ├── session.py      # Session管理
│   │   ├── email_service.py # 邮件服务（验证邮件、密码重置）
│   │   ├── alert.py        # 告警模块
│   │   ├── scheduler.py    # 定时任务模块
│   │   ├── templates.py    # 邮件模板
│   │   ├── database.py     # 数据库连接
│   │   ├── config.py       # 配置管理
│   │   └── main.py         # FastAPI应用入口
│   ├── requirements.txt    # Python依赖
│   ├── .env.example        # 环境变量示例
│   ├── init_db.sql         # 数据库初始化SQL
│   ├── migrate_add_user_system.py # 用户系统数据库迁移脚本
│   ├── create_admin.py     # 创建管理员账号脚本
│   ├── run.py              # 启动脚本
│   ├── start.bat           # Windows启动脚本
│   └── start.ps1           # PowerShell启动脚本
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── api/           # API调用
│   │   │   ├── index.js   # Axios配置
│   │   │   ├── power.js   # 电费记录API
│   │   │   ├── alert.js   # 告警API
│   │   │   └── system.js  # 系统管理API
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
mysql -u root -p < init_db.sql
```

**方式二：手动创建**

```bash
mysql -u root -p
```

```sql
CREATE DATABASE dorm_power_guard CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

#### 3.2.1 执行用户系统数据库迁移

```bash
python migrate_add_user_system.py
```

这会创建用户系统相关的表（users, admins, dorm_submissions等）。

#### 3.2.2 创建管理员账号

```bash
python create_admin.py --username admin --password your_password --email admin@example.com --role super_admin
```

#### 3.3 配置环境变量

复制 `.env.example` 为 `.env`：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入实际配置（详见[详细配置](#详细配置)章节）。

#### 3.4 启动后端

**Windows系统：**

```bash
# 方式一：使用批处理文件
start.bat

# 方式二：手动启动
python run.py
```

**Linux/Mac系统：**

```bash
python3 run.py
```

后端将在 `http://localhost:8000` 启动。

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

#### 4.3 构建生产版本

```bash
npm run build
```

构建产物在 `dist/` 目录。

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

```env
# 每天执行时间点（小时，用逗号分隔）
SCHEDULER_HOURS=8,12,18,22
```

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

### 5. QQ机器人配置（可选）

```env
# QQ机器人配置
QQ_BOT_ENABLED=true
QQ_BOT_TYPE=go-cqhttp
QQ_BOT_API_URL=http://localhost:5700
QQ_BOT_GROUP_ID=123456789
```

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

系统默认在以下时间点自动获取电费数据：
- 08:00
- 12:00
- 18:00
- 22:00

可在 `.env` 文件中修改 `SCHEDULER_HOURS` 配置。

### 6. 用户系统功能

#### 6.1 学生功能

- **注册登录**：邮箱注册，邮箱验证，密码登录
- **提交宿舍信息**：填写宿舍信息，系统立即抓取电费数据，学生确认后激活监控
- **我的监控**：查看自己的监控列表，查看电费记录，修改告警规则
- **多宿舍申请**：申请监控多个宿舍，等待管理员审批

#### 6.2 管理员功能

- **管理员登录**：账号密码登录
- **用户管理**：查看用户列表，启用/禁用用户
- **监控管理**：查看所有监控，编辑告警规则，手动触发抓取
- **多宿舍审批**：审批学生的多宿舍申请

#### 6.3 安全机制

- **学生确认机制**：提交后立即显示电费数据，学生确认后才激活，防止误填其他宿舍
- **提交限制**：同一邮箱每天最多提交3次
- **登录失败限制**：5次失败后锁定30分钟
- **Session管理**：7天自动过期，支持登出

### 告警功能

- **邮件告警**：使用QQ邮箱发送告警邮件到指定邮箱
- **QQ机器人告警**：支持go-cqhttp等QQ机器人
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

#### 3. 用户认证API

- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/verify-email` - 验证邮箱
- `POST /api/auth/logout` - 登出
- `GET /api/auth/me` - 获取当前用户信息
- `POST /api/auth/forgot-password` - 忘记密码
- `POST /api/auth/reset-password` - 重置密码

#### 4. 宿舍提交API

- `POST /api/submissions` - 提交宿舍信息
- `GET /api/submissions/{id}` - 获取提交详情
- `POST /api/submissions/{id}/confirm` - 确认提交
- `GET /api/submissions/my/list` - 我的提交列表
- `GET /api/submissions/check-limit` - 检查提交限制

#### 5. 多宿舍申请API

- `POST /api/multi-dorm/request` - 提交多宿舍申请
- `GET /api/multi-dorm/my-requests` - 我的申请列表

#### 6. 我的监控API

- `GET /api/my/monitors` - 我的监控列表
- `GET /api/my/power-records/{dorm_number}` - 我的电费记录
- `PUT /api/my/alert-rules/{dorm_number}` - 更新告警规则

#### 7. 管理员认证API

- `POST /api/auth/admin/login` - 管理员登录
- `POST /api/auth/admin/logout` - 管理员登出
- `GET /api/auth/admin/me` - 获取当前管理员信息

#### 8. 管理员管理API

- `GET /api/admin/admins` - 管理员列表
- `POST /api/admin/admins` - 创建管理员（需要超级管理员）
- `PUT /api/admin/admins/{id}` - 更新管理员（需要超级管理员）
- `DELETE /api/admin/admins/{id}` - 删除管理员（需要超级管理员）
- `POST /api/admin/change-password` - 修改密码

#### 9. 管理员用户管理API

- `GET /api/admin/users` - 用户列表
- `GET /api/admin/users/{id}` - 用户详情
- `PUT /api/admin/users/{id}/status` - 更新用户状态

#### 10. 管理员多宿舍申请管理API

- `GET /api/multi-dorm/admin/requests` - 申请列表
- `GET /api/multi-dorm/admin/requests/{id}` - 申请详情
- `PUT /api/multi-dorm/admin/requests/{id}/approve` - 批准申请
- `PUT /api/multi-dorm/admin/requests/{id}/reject` - 拒绝申请

#### 11. 系统管理API

- `POST /api/system/crawl` - 手动触发爬虫任务

**请求示例：**

```bash
curl -X POST http://localhost:8000/api/system/crawl
```

---

## 数据库设计

### 表结构

#### 1. `power_records` - 电费记录表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键，自增 |
| dorm_number | VARCHAR(50) | 宿舍号 |
| kbalance | FLOAT | 空调余量（度） |
| zbalance | FLOAT | 照明余量（度） |
| kpower_consumption | FLOAT | 空调用电量（度），与上次记录的差值 |
| zpower_consumption | FLOAT | 照明用电量（度），与上次记录的差值 |
| record_time | DATETIME | 记录时间 |
| created_at | DATETIME | 创建时间 |

**索引建议：**

```sql
CREATE INDEX idx_dorm_number ON power_records(dorm_number);
CREATE INDEX idx_record_time ON power_records(record_time);
```

#### 2. `alert_rules` - 告警规则表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键，自增 |
| dorm_number | VARCHAR(50) | 宿舍号（唯一） |
| kthreshold | FLOAT | 空调告警阈值（度） |
| zthreshold | FLOAT | 照明告警阈值（度） |
| enabled | BOOLEAN | 是否启用告警 |
| email_enabled | BOOLEAN | 是否启用邮件告警 |
| email_address | VARCHAR(255) | 接收邮箱地址（多个用逗号分隔） |
| qq_enabled | BOOLEAN | 是否启用QQ告警 |
| last_alert_time | DATETIME | 最后告警时间 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

**唯一约束：**

```sql
ALTER TABLE alert_rules ADD UNIQUE KEY uk_dorm_number (dorm_number);
```

**注意**：`alert_rules` 表已更新，添加了 `user_id` 和 `dorm_submission_id` 字段，用于关联用户和提交记录。

#### 3. `alert_logs` - 告警日志表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键，自增 |
| dorm_number | VARCHAR(50) | 宿舍号 |
| alert_category | VARCHAR(20) | 告警类别（ac=空调，light=照明） |
| balance | FLOAT | 触发告警时的余量（度） |
| threshold | FLOAT | 告警阈值（度） |
| alert_type | VARCHAR(20) | 告警类型（email=邮件，qq=QQ机器人） |
| alert_status | VARCHAR(20) | 告警状态（success=成功，failed=失败） |
| alert_message | TEXT | 告警消息 |
| created_at | DATETIME | 创建时间 |

#### 4. `users` - 用户表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键，自增 |
| email | VARCHAR(255) | 邮箱（唯一） |
| password_hash | VARCHAR(255) | 密码哈希 |
| email_verified | BOOLEAN | 邮箱是否已验证 |
| email_verification_code | VARCHAR(50) | 邮箱验证码 |
| email_verified_at | DATETIME | 邮箱验证时间 |
| status | VARCHAR(20) | 状态：pending/active/banned |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

#### 5. `admins` - 管理员表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键，自增 |
| username | VARCHAR(50) | 管理员账号（唯一） |
| password_hash | VARCHAR(255) | 密码哈希 |
| email | VARCHAR(255) | 邮箱（可选） |
| nickname | VARCHAR(100) | 昵称 |
| role | VARCHAR(20) | 角色：admin/super_admin |
| status | VARCHAR(20) | 状态：active/banned |
| created_at | DATETIME | 创建时间 |
| last_login_at | DATETIME | 最后登录时间 |

#### 6. `dorm_submissions` - 宿舍提交表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键，自增 |
| user_id | INT | 用户ID（外键） |
| dorm_number | VARCHAR(50) | 宿舍号 |
| room_id | INT | 房间ID |
| kbalance | FLOAT | 提交时的空调余量（用于确认） |
| zbalance | FLOAT | 提交时的照明余量（用于确认） |
| status | VARCHAR(20) | 状态：pending_confirmation/confirmed/active/rejected |
| confirmed_at | DATETIME | 确认时间 |
| alert_rule_id | INT | 关联的告警规则ID |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

#### 7. `submission_limits` - 提交限制表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键，自增 |
| email | VARCHAR(255) | 邮箱 |
| submission_date | DATE | 提交日期 |
| submission_count | INT | 提交次数 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

#### 8. `multi_dorm_requests` - 多宿舍申请表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键，自增 |
| user_id | INT | 用户ID（外键） |
| dorm_number | VARCHAR(50) | 宿舍号 |
| room_id | INT | 房间ID |
| reason | TEXT | 申请理由 |
| status | VARCHAR(20) | 状态：pending/approved/rejected |
| admin_id | INT | 处理的管理员ID |
| processed_at | DATETIME | 处理时间 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

#### 9. `login_attempts` - 登录尝试记录表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键，自增 |
| identifier | VARCHAR(255) | 标识符（邮箱或用户名） |
| attempt_type | VARCHAR(20) | 尝试类型：user/admin |
| failed_count | INT | 失败次数 |
| last_attempt_at | DATETIME | 最后尝试时间 |
| locked_until | DATETIME | 锁定到期时间 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

---

## 部署指南

### Windows系统部署

#### 方式一：使用批处理文件（推荐）

```bash
# 后端
cd backend
start.bat

# 前端（新终端）
cd frontend
npm run dev
```

#### 方式二：注册为Windows服务（24小时运行）

```powershell
# 以管理员身份运行PowerShell
cd backend
.\install_windows_service.ps1
```

### Linux/Mac系统部署

```bash
# 后端
cd backend
python3 run.py

# 前端（新终端）
cd frontend
npm run dev
```

### 云服务器部署（24小时运行）

#### 为什么需要云服务器？

要让程序在个人电脑关闭后也能一直运行，需要将程序部署到一台**24小时运行的服务器**上。

#### 推荐方案：云服务器部署

**优点**：
- ✅ 成本低：每月约 ¥20-50（如阿里云/腾讯云轻量应用服务器）
- ✅ 稳定可靠：24小时运行，有专业维护
- ✅ 易于访问：有公网IP，可随时随地访问
- ✅ 易于扩展：可根据需要升级配置

#### 快速开始

1. **购买云服务器**
   - 推荐：阿里云/腾讯云轻量应用服务器
   - 配置：1核2GB内存，40GB SSD
   - 系统：Ubuntu 22.04 LTS
   - 价格：约 ¥24/月

2. **连接到服务器**

```bash
ssh root@your_server_ip
```

3. **安装依赖**

```bash
apt update
apt install -y python3 python3-pip git mysql-server nginx
```

4. **部署程序**

```bash
cd /opt
git clone https://gitee.com/ak-god/dorm-power-guard-lite.git
cd dorm-power-guard-lite/backend
pip3 install -r requirements.txt
```

5. **配置环境变量**

```bash
cp .env.example .env
nano .env  # 编辑配置文件
```

6. **创建systemd服务**

```bash
sudo nano /etc/systemd/system/dorm-power-guard.service
```

内容：

```ini
[Unit]
Description=Dorm Power Guard Backend Service
After=network.target mysql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/dorm-power-guard-lite/backend
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/python3 /opt/dorm-power-guard-lite/backend/run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

7. **启动服务**

```bash
sudo systemctl daemon-reload
sudo systemctl enable dorm-power-guard
sudo systemctl start dorm-power-guard
sudo systemctl status dorm-power-guard
```

8. **配置Nginx反向代理**

```bash
sudo nano /etc/nginx/sites-available/dorm-power-guard
```

内容：

```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        root /opt/dorm-power-guard-lite/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/dorm-power-guard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 配置SSL证书（可选）

使用Let's Encrypt免费SSL证书：

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your_domain.com
```

#### 配置防火墙

```bash
# Ubuntu/Debian (ufw)
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

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

**A**: 编辑 `backend/.env` 文件中的 `SCHEDULER_HOURS`，例如：
```env
SCHEDULER_HOURS=8,12,18,22  # 每天8点、12点、18点、22点
```

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
1. 执行数据库迁移：`python migrate_add_user_system.py`
2. 创建管理员账号：`python create_admin.py --username admin --password admin123`
3. 启动服务：`python run.py`
4. 访问API文档：http://localhost:8000/docs
5. 使用Swagger UI测试各个接口

### Q13: 学生提交宿舍信息时如何防止误填？

**A**: 
1. 学生提交后，系统立即抓取电费数据
2. 显示当前电费余额（空调余量、照明余量）
3. 学生需要确认"这是我宿舍的电费"
4. 确认后才激活监控
5. 如果填错了，看到的数据不对，就不会确认

### Q14: 如何申请监控多个宿舍？

**A**: 
1. 学生提交多宿舍申请（填写宿舍号和申请理由）
2. 管理员审批申请（批准/拒绝）
3. 如果批准，系统创建待确认的提交记录
4. 学生需要确认提交（显示电费数据）
5. 确认后激活监控

---

## 联系与支持

- **管理员QQ**：714085964
- **项目用途**：仅供西华大学学生个人使用
- **数据安全**：所有数据存储在本地，不会上传到第三方服务器

如有问题或建议，欢迎通过QQ联系管理员。

---

## 更新日志

- **v2.0.0** - 多用户系统版本
  - 新增用户注册/登录系统（邮箱+密码）
  - 新增管理员系统（账号密码登录）
  - 新增宿舍提交功能（学生提交，确认后激活）
  - 新增多宿舍申请功能（学生申请，管理员审批）
  - 新增我的监控功能（查看列表，修改规则）
  - 新增邮件服务（邮箱验证、密码重置）
  - 新增安全机制（学生确认、提交限制、登录失败限制）
  - 完善Session管理
  - 完善管理员管理功能

- **v1.0.0** - 初始版本
  - 支持西华大学一卡通系统
  - 支持邮件和QQ告警
  - 支持数据可视化
  - 支持空调和照明分类监控

---

## 贡献

欢迎提交Issue和Pull Request！

---

## 许可证

MIT License

---

**开发说明**：本项目为开源项目，欢迎提交Issue和Pull Request。  
**注意**：本项目仅用于学习和个人使用，请遵守西华大学相关规定，不得用于商业用途。

**技术知识点文档**：详细的技术栈和使用方法请参考 `技术知识点文档.md`  
**开发日志**：开发历史和版本记录请参考 `开发日志.md`
