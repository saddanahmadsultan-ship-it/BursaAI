BursaAI v6.0 Professional Framework
Sprint 5C.3 - Portfolio Allocator Adapter

IMPORTANT
---------
Portfolio allocation is a batch operation across all completed
AnalysisContext objects. It is not a per-stock pipeline engine.

FILES
-----
Adapters/portfolio_allocator_adapter.py
Adapters/portfolio_registry.py
Adapters/__init__.py
Tests/test_sprint5c3.py
Tests/test_sprint5c3_core_imports.py

CORE FUNCTION
-------------
Core.portfolio_allocator.allocate_portfolio

EVENT
-----
PortfolioAllocated

USAGE
-----
adapter = PortfolioAllocatorAdapter(
    services=infrastructure.services
)

portfolio_data = adapter.allocate(contexts)

TESTS
-----
python Tests/test_sprint5c3.py
python Tests/test_sprint5c3_core_imports.py
