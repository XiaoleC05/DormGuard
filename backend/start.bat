@echo off
chcp 65001 >nul
echo ========================================
echo 宿舍电费监控系统 - 启动脚本
echo ========================================
echo.

REM 检查.env文件是否存在
if not exist .env (
    echo [警告] 未找到 .env 文件
    echo 正在从 .env.example 创建...
    copy .env.example .env >nul
    echo 请编辑 .env 文件配置数据库等信息
    echo.
    pause
    exit /b 1
)

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python
    echo 请确保Python已安装并添加到PATH环境变量
    pause
    exit /b 1
)

echo [1/2] 检查依赖...
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo [警告] 依赖未安装，正在安装...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖安装失败
        echo 请检查网络连接或手动运行: pip install -r requirements.txt
        pause
        exit /b 1
    )
)

echo [2/2] 启动服务...
echo.
echo ========================================
echo 服务启动中...
echo ========================================
echo.
echo 后端服务: http://localhost:8000
echo API文档:  http://localhost:8000/docs
echo 健康检查: http://localhost:8000/health
echo.
echo 按 Ctrl+C 停止服务
echo ========================================
echo.

python run.py

pause
