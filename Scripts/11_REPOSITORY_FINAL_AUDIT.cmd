@echo off
setlocal
cd /d "%~dp0\.."

python Tools\repository_cleanup_audit.py
if errorlevel 1 exit /b 1

python Tools\pre_commit_security_check.py
if errorlevel 1 exit /b 1

python -m compileall -q .
if errorlevel 1 exit /b 1

echo FINAL REPOSITORY AUDIT PASSED.
endlocal
