@echo off
setlocal
cd /d "%~dp0\.."

echo ============================================================
echo  BursaAI GitHub Remote Setup
echo ============================================================

if not exist ".git" (
    echo ERROR: Jalankan Scripts\01_INIT_LOCAL_GIT.cmd dahulu.
    exit /b 1
)

set /p REMOTE_URL=Paste URL repository GitHub kosong: 

if "%REMOTE_URL%"=="" (
    echo ERROR: URL kosong.
    exit /b 1
)

git remote get-url origin >nul 2>nul
if not errorlevel 1 (
    git remote set-url origin "%REMOTE_URL%"
) else (
    git remote add origin "%REMOTE_URL%"
)

git push -u origin main
if errorlevel 1 exit /b 1

git push -u origin develop
if errorlevel 1 exit /b 1

git push -u origin release/7.0
if errorlevel 1 exit /b 1

echo.
echo BursaAI berjaya dipush ke GitHub.
echo Aktifkan branch protection untuk main dan develop.
endlocal
