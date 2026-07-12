BursaAI v6.0 Professional Framework
Sprint 1 - Domain Foundation

FILES
-----
Framework/__init__.py
Framework/domain.py
Framework/context.py
Framework/engine_result.py
Framework/metadata.py
Framework/exceptions.py
Tests/test_sprint1.py

INSTALLATION
------------
Copy the Framework and Tests folders into the BursaAI project root.

DO NOT replace:
- main.py
- Core/result_model.py
- any existing trading engine

TEST
----
Run from the BursaAI project root:

python -c "from Framework.context import AnalysisContext; print('CONTEXT OK')"
python -c "from Framework.domain import AnalysisModel; print('DOMAIN OK')"
python -c "from Framework.engine_result import EngineResult; print('ENGINE RESULT OK')"
python -c "from Framework.metadata import EngineMetadata; print('METADATA OK')"
python Tests/test_sprint1.py

Sprint 1 is isolated and does not change the current BursaAI execution flow.
