BursaAI v6.0 Professional Framework
Sprint 2 - Engine Foundation

NEW FILES
---------
Framework/base_engine.py
Framework/engine_registry.py
Framework/logger.py
Framework/profiler.py
Tests/test_sprint2.py

UPDATED
-------
Framework/__init__.py

INSTALLATION
------------
Copy the Framework and Tests folders into the BursaAI project root.
Allow Sprint 2 files to merge with the existing Sprint 1 folders.

DO NOT replace or modify:
- main.py
- Core/
- existing trading engines

TESTS
-----
Run from BursaAI root or Tests folder:

python -c "from Framework.base_engine import BaseEngine; print('BASE ENGINE OK')"
python -c "from Framework.engine_registry import EngineRegistry; print('REGISTRY OK')"
python -c "from Framework.logger import FrameworkLogger; print('LOGGER OK')"
python -c "from Framework.profiler import EngineProfiler; print('PROFILER OK')"
python Tests/test_sprint2.py

If currently inside Tests:
python test_sprint2.py
