BursaAI v6.0 Professional Framework
Sprint 3 - Pipeline Execution Layer

NEW FILES
---------
Framework/pipeline.py
Framework/pipeline_policy.py
Framework/pipeline_report.py
Tests/test_sprint3.py
Tests/test_sprint3_failure_modes.py

UPDATED
-------
Framework/__init__.py

FEATURES
--------
- controlled pipeline execution
- engine priority ordering
- dependency validation
- failure modes:
    continue
    stop
    skip_dependents
- before and after hooks
- disabled engine handling
- execution report
- context snapshot
- logger integration
- profiler integration

INSTALLATION
------------
Extract the package into the BursaAI project root.
Merge Framework and Tests with Sprint 1 and Sprint 2.

DO NOT modify:
- main.py
- Core/
- existing trading engines

TESTS
-----
From BursaAI root:

python -c "from Framework.pipeline import Pipeline; print('PIPELINE OK')"
python -c "from Framework.pipeline_policy import PipelinePolicy; print('POLICY OK')"
python -c "from Framework.pipeline_report import PipelineExecutionReport; print('REPORT OK')"
python Tests/test_sprint3.py
python Tests/test_sprint3_failure_modes.py

From Tests folder:

python test_sprint3.py
python test_sprint3_failure_modes.py
