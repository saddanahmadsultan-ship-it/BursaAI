@echo off
setlocal
cd /d "%~dp0\.."

echo ============================================================
echo  BursaAI Repository Validation
echo ============================================================

python -m compileall -q .
if errorlevel 1 exit /b 1

python Tools\pre_commit_security_check.py
if errorlevel 1 exit /b 1

python -m unittest discover -s Tests -p "test_*.py" -v
if errorlevel 1 exit /b 1

echo.
echo Repository validation PASSED.
endlocal
