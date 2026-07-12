@echo off
setlocal
cd /d "%~dp0\.."

echo ============================================================
echo  BursaAI Sprint 7 Repository Cleanup RC0
echo ============================================================

where git >nul 2>nul
if errorlevel 1 (
    echo ERROR: Git tidak ditemui.
    exit /b 1
)

if not exist ".git" (
    echo ERROR: Folder ini bukan Git repository.
    exit /b 1
)

echo Current branch:
git branch --show-current

echo.
echo Creating safety branch...
git branch backup/repository-cleanup-before-rc0 2>nul

echo.
echo Ensuring Archive ignore rule...
findstr /x /c:"Archive/" .gitignore >nul 2>nul
if errorlevel 1 (
    echo.>> .gitignore
    echo # Local release archives>> .gitignore
    echo Archive/>> .gitignore
)

echo.
echo Removing local artifacts from Git index...
git rm -r --cached --ignore-unmatch Archive
git rm -r --cached --ignore-unmatch Reports
git rm -r --cached --ignore-unmatch Experiments/checkpoints
git rm -r --cached --ignore-unmatch Experiments/locks
git rm -r --cached --ignore-unmatch Experiments/records
git rm --cached --ignore-unmatch Experiments/registry_manifest.json
git rm -r --cached --ignore-unmatch ResearchResults/results
git rm -r --cached --ignore-unmatch ResearchResults/by_experiment
git rm --cached --ignore-unmatch ResearchResults/manifest.json
git rm -r --cached --ignore-unmatch Logs
git rm -r --cached --ignore-unmatch Cache
git rm -r --cached --ignore-unmatch Data
git rm -r --cached --ignore-unmatch MarketData

git add .gitignore
git add Tools\repository_cleanup_audit.py
git add README_REPOSITORY_CLEANUP_RC0.md
git add CHANGELOG_REPOSITORY_CLEANUP_RC0.md
git add VERSION_REPOSITORY_CLEANUP_RC0.json

python Tools\repository_cleanup_audit.py --staged
if errorlevel 1 (
    echo CLEANUP AUDIT FAILED.
    exit /b 1
)

echo.
echo Cleanup staging completed.
echo Review with:
echo   git status
echo   git diff --cached --name-only
echo.
echo Commit with:
echo   git commit -m "chore(repo): clean repository and exclude local artifacts"
endlocal
