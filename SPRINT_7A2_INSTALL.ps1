Write-Host "BursaAI Sprint 7A.2 Validation"
python -c "from Research import ExperimentRegistry; print('SPRINT 7A.2 IMPORT OK')"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python Tests\test_sprint7a2.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host "Sprint 7A.2 validated successfully."
