"""
Sprint 5C.3 real Core import test.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main():
    from Core.portfolio_allocator import allocate_portfolio
    from Adapters.portfolio_allocator_adapter import (
        PortfolioAllocatorAdapter,
    )

    assert callable(allocate_portfolio)

    PortfolioAllocatorAdapter(
        allocator_function=allocate_portfolio
    )

    print("=" * 88)
    print("BURSAAI v6.0 SPRINT 5C.3 CORE IMPORT TEST")
    print("=" * 88)
    print("Core.portfolio_allocator : OK")
    print("Portfolio Function       : OK")
    print("Portfolio Adapter        : OK")
    print("=" * 88)
    print("SPRINT 5C.3 CORE IMPORTS OK")


if __name__ == "__main__":
    main()
