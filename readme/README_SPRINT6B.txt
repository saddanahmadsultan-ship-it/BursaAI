BursaAI v6.0 Final Architecture
Sprint 6B - Paper Trading Engine

FILES
-----
Trading/__init__.py
Trading/paper_order.py
Trading/paper_position.py
Trading/paper_account.py
Trading/paper_execution.py
Trading/paper_portfolio.py
Trading/paper_services.py
Tests/test_sprint6b.py

FEATURES
--------
- simulated cash account
- BUY and SELL market orders
- position average price
- realized and unrealized P/L
- commissions
- slippage
- insufficient cash rejection
- insufficient shares rejection
- allocated portfolio to paper orders
- event publication

EVENT
-----
PaperOrderUpdated

TEST
----
python Tests/test_sprint6b.py

EXPECTED
--------
SPRINT 6B PAPER TRADING ENGINE OK
