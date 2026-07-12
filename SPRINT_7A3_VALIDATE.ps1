python -c "from Research import ExperimentRunner, RunnerConfig; print('SPRINT 7A.3 IMPORT OK')"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python Tests\test_sprint7a3.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host "Sprint 7A.3 validated successfully."
