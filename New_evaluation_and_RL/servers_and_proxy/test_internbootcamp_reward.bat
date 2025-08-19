@echo off
REM =============================================
REM Test InternBootcamp Reward Server with curl
REM =============================================

echo ===============================================
echo Testing InternBootcamp Reward Server
echo ===============================================

REM Test health check
echo.
echo Testing Health Check...
curl -X GET http://localhost:8899/health

echo.
echo.
echo Testing Config...
curl -X GET http://localhost:8899/config

echo.
echo.
echo Testing Available Tasks...
curl -X GET http://localhost:8899/tasks

echo.
echo.
echo Testing Compute Score...
curl -X POST http://localhost:8899/compute_score ^
  -H "Content-Type: application/json" ^
  -d @test_request_internbootcamp.json

echo.
echo.
echo ===============================================
echo Test Complete
echo ===============================================
pause