# PowerShell 启动说明

## ⚠️ 重要提示

在 **PowerShell** 中运行脚本时，需要使用 `.\` 前缀来执行当前目录下的脚本文件。

---

## 🚀 PowerShell 启动方式

### 方式1：使用 PowerShell 脚本（推荐）

```powershell
cd backend
.\start.ps1
```

### 方式2：使用批处理文件

```powershell
cd backend
.\start.bat
```

### 方式3：直接运行 Python

```powershell
cd backend
python run.py
```

---

## 📝 完整启动流程（PowerShell）

### 终端1 - 启动后端

```powershell
# 进入后端目录
cd backend

# 首次运行：安装依赖
pip install -r requirements.txt

# 首次运行：配置环境变量
Copy-Item .env.example .env
# 然后编辑 .env 文件配置数据库

# 启动后端
.\start.ps1
# 或
.\start.bat
# 或
python run.py
```

### 终端2 - 启动前端

```powershell
# 进入前端目录
cd frontend

# 首次运行：安装依赖
npm install

# 启动前端
npm run dev
```

---

## 🔧 如果遇到执行策略错误

如果运行 `.\start.ps1` 时出现执行策略错误：

```
无法加载文件，因为在此系统上禁止运行脚本
```

**解决方案：**

1. **临时允许（推荐）：**
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
   .\start.ps1
   ```

2. **永久允许（需要管理员权限）：**
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

3. **或者直接使用批处理文件：**
   ```powershell
   .\start.bat
   ```

---

## ✅ 验证启动

- 后端：http://localhost:8000/docs
- 前端：http://localhost:3000

---

## 💡 提示

- PowerShell 中运行脚本必须使用 `.\` 前缀
- 如果不想使用脚本，可以直接运行 `python run.py`
- 批处理文件（.bat）在 PowerShell 中也可以正常运行
