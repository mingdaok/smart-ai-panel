@echo off
chcp 65001 > nul
echo ========================================
echo 正在启动 AI Panel 演播厅项目...
echo ========================================

echo 正在启动后端服务 (FastAPI)...
start "AI Panel Backend" cmd /k "python -m uvicorn backend.main:app --host 127.0.0.1 --port 3000 --reload"

echo 正在启动前端服务 (Vite)...
start "AI Panel Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo 服务正在独立窗口中启动...
echo [前端地址] http://localhost:5174
echo [后端地址] http://localhost:3000
echo.
echo 如果需要关闭服务，请直接关闭弹出的两个黑色命令行窗口即可。
echo.
pause
