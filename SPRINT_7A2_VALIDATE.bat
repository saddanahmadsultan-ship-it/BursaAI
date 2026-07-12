@echo off
cd /d "%~dp0"

echo ============================================================
echo  BursaAI Sprint 7A.2 Validation
echo ============================================================

python -c "from Research import ExperimentRegistry; print('SPRINT 7A.2 IMPORT OK')"
if errorlevel 1 goto :fail

python Tests\test_sprint7a2.py
if errorlevel 1 goto :fail

python Tools\demo_sprint7a2.py
if errorlevel 1 goto :fail

echo.
echo Sprint 7A.2 validation completed successfully.
exit /b 0

:fail
echo.
echo Sprint 7A.2 validation failed.
exit /b 1
