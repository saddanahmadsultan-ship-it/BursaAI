@echo off
setlocal
cd /d "%~dp0\.."

if not exist ".git" (
    echo ERROR: Repository Git belum dimulakan.
    exit /b 1
)

set /p BRANCH_NAME=Nama feature, contoh 7a5-rc2-robustness: 

if "%BRANCH_NAME%"=="" (
    echo ERROR: Nama branch kosong.
    exit /b 1
)

git switch develop
if errorlevel 1 exit /b 1

git pull
if errorlevel 1 (
    echo Amaran: git pull gagal. Branch lokal masih boleh digunakan.
)

git switch -c feature/%BRANCH_NAME%
endlocal
