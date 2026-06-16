@echo off
setlocal enabledelayedexpansion
title Logistics Server
chcp 65001 >nul

cd /d "%~dp0"

:: 기본값
set PORT=5000

:: .env 파일이 있으면 환경변수로 로드
if exist ".env" (
    for /f "usebackq tokens=1,* delims==" %%A in (".env") do (
        set "_ln=%%A"
        if not "!_ln:~0,1!"=="#" if not "%%A"=="" (
            set "%%A=%%B"
        )
    )
)

:: Python 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python을 찾을 수 없습니다. Python을 설치한 후 다시 실행하세요.
    pause
    exit /b 1
)

:: Flask 설치 확인
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Flask 설치 중...
    pip install -r LogisticsWeb\requirements.txt
)

set PYTHONIOENCODING=utf-8

echo.
echo  ============================================
echo   물류창고 자동화 시스템 - 대시보드 서버
echo   http://127.0.0.1:%PORT%
echo   종료: Ctrl+C
echo  ============================================
echo.

cd LogisticsWeb
python LogisticsWeb.py

pause
