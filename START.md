# 🚀 快速启动指南

## 一键启动（推荐）

### Windows系统

**打开两个命令提示符窗口：**

**窗口1 - 启动后端：**

**如果使用 CMD（命令提示符）：**
```cmd
cd backend
start.bat
```

**如果使用 PowerShell：**
```powershell
cd backend
.\start.bat
# 或
.\start.ps1
```

**窗口2 - 启动前端：**
```cmd
cd frontend
npm install
npm run dev
```

### Linux/Mac系统

**打开两个终端窗口：**

**终端1 - 启动后端：**
```bash
cd backend
chmod +x start.sh && ./start.sh
```

**终端2 - 启动前端：**
```bash
cd frontend
npm install
npm run dev
```

---

## 📋 首次启动前的准备

### 1. 安装MySQL并创建数据库

```sql
CREATE DATABASE dorm_power_guard CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. 配置后端环境变量

```bash
cd backend
cp .env.example .env  # Linux/Mac
# 或
copy .env.example .env  # Windows
```

编辑 `.env`，至少配置：
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=你的密码
DB_NAME=dorm_power_guard
```

### 3. 安装依赖

**后端：**
```bash
cd backend
pip install -r requirements.txt
```

**前端：**
```bash
cd frontend
npm install
```

---

## ✅ 验证启动

- 后端：http://localhost:8000/docs
- 前端：http://localhost:3000

---

## 📖 详细文档

查看 `项目启动指南.md` 获取完整说明和故障排查。
