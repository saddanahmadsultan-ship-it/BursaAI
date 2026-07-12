BursaAI v6.0 Final Architecture
Sprint 6D - Trade Journal

FILES
-----
Journal/__init__.py
Journal/journal_models.py
Journal/trade_journal.py
Journal/event_journal_bridge.py
Journal/journal_services.py
Tests/test_sprint6d.py

FEATURES
--------
- SQLite persistent journal
- signal records
- decision records
- paper order records
- trade records
- position records
- portfolio records
- execution records
- event-driven automatic logging
- symbol and event queries
- journal summary

DEFAULT DATABASE
----------------
Data/bursaai_journal.db

REGISTRATION
------------
from Journal.journal_services import register_trade_journal

journal = register_trade_journal(
    infrastructure.services
)

TEST
----
python Tests/test_sprint6d.py

EXPECTED
--------
SPRINT 6D TRADE JOURNAL OK
