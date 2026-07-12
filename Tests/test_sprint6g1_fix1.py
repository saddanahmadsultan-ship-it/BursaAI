"""
BursaAI v6 Sprint 6G.1 Circular Import Fix Test.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main():
    from Framework.context import AnalysisContext
    from Adapters.portfolio_allocator_adapter import (
        PortfolioAllocatorAdapter,
    )
    from Framework.execution_manager import ExecutionManager
    from Bootstrap.import_health import ImportHealthChecker
    from Bootstrap.service_bootstrap import UnifiedServiceBootstrap

    assert AnalysisContext is not None
    assert PortfolioAllocatorAdapter is not None
    assert ExecutionManager is not None
    assert ImportHealthChecker is not None
    assert UnifiedServiceBootstrap is not None

    result = ImportHealthChecker().run()

    if not result.success:
        print("IMPORT FAILURES")

        for module, error in result.failures().items():
            print(f"- {module}: {error}")

    assert result.success is True

    print("=" * 92)
    print("BURSAAI v6.0 SPRINT 6G.1 FIX 1 TEST")
    print("=" * 92)
    print("Framework Lightweight Init : OK")
    print("Adapters Lightweight Init  : OK")
    print("Bootstrap Lazy Import      : OK")
    print("Portfolio Adapter Import   : OK")
    print("Execution Manager Import   : OK")
    print("Full Import Health         : OK")
    print("=" * 92)
    print("SPRINT 6G.1 CIRCULAR IMPORT FIX OK")


if __name__ == "__main__":
    main()
