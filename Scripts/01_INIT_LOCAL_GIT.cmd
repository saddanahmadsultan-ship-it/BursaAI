@echo off
setlocal
cd /d "%~dp0\.."

echo ============================================================
echo  BursaAI Local Git Initializer
echo ============================================================

where git >nul 2>nul
if errorlevel 1 (
    echo ERROR: Git tidak ditemui.
    echo Install Git for Windows dahulu.
    exit /b 1
)

if exist ".git" (
    echo Repository Git sudah wujud.
    git status --short
    exit /b 0
)

python Tools\pre_commit_security_check.py
if errorlevel 1 (
    echo.
    echo Git initialization dibatalkan kerana security check gagal.
    exit /b 1
)

git init -b main
if errorlevel 1 exit /b 1

git add .
git commit -m "chore(repo): initialize BursaAI repository"
if errorlevel 1 (
    echo.
    echo Commit gagal. Tetapkan nama dan email Git:
    echo git config --global user.name "Nama Anda"
    echo git config --global user.email "email@example.com"
    exit /b 1
)

git branch develop
git branch release/7.0

echo.
echo Repository lokal berjaya dibina.
echo Branch:
git branch
echo.
echo Langkah seterusnya:
echo Scripts\02_CONNECT_GITHUB.cmd
endlocal
