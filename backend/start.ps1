# PowerShell启动脚本
# 宿舍电费监控系统 - 后端启动脚本

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "宿舍电费监控系统 - 启动脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查.env文件是否存在
if (-not (Test-Path .env)) {
    Write-Host "[警告] 未找到 .env 文件" -ForegroundColor Yellow
    Write-Host "正在从 .env.example 创建..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "请编辑 .env 文件配置数据库等信息" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "按回车键退出"
    exit 1
}

# 检查Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[1/3] Python版本: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[错误] 未检测到Python" -ForegroundColor Red
    Write-Host "请确保Python已安装并添加到PATH环境变量" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

# 检查依赖
Write-Host "[2/3] 检查依赖..." -ForegroundColor Cyan
try {
    python -c "import fastapi" 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "FastAPI未安装"
    }
    Write-Host "  依赖检查通过" -ForegroundColor Green
} catch {
    Write-Host "[警告] 依赖未安装，正在安装..." -ForegroundColor Yellow
    python -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[错误] 依赖安装失败" -ForegroundColor Red
        Write-Host "请检查网络连接或手动运行: pip install -r requirements.txt" -ForegroundColor Red
        Read-Host "按回车键退出"
        exit 1
    }
}

# 启动服务
Write-Host "[3/3] 启动服务..." -ForegroundColor Cyan
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "服务启动中..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "后端服务: http://localhost:8000" -ForegroundColor Green
Write-Host "API文档:  http://localhost:8000/docs" -ForegroundColor Green
Write-Host "健康检查: http://localhost:8000/health" -ForegroundColor Green
Write-Host ""
Write-Host "按 Ctrl+C 停止服务" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

python run.py
