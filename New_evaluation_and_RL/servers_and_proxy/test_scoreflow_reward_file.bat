@echo off
chcp 65001 >nul
echo 测试ScoreFlow Reward服务 (使用JSON文件)...
echo.

cd /d "%~dp0"

curl -X POST http://localhost:8899/compute_score ^
  -H "Content-Type: application/json" ^
  -d @test_request.json

echo.
echo 请求已发送，等待响应...
pause