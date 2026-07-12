BursaAI v6.0 Final Architecture
Sprint 6C - Notification Hub

FILES
-----
Notifications/__init__.py
Notifications/notification_message.py
Notifications/base_notifier.py
Notifications/telegram_notifier.py
Notifications/message_formatter.py
Notifications/notification_hub.py
Notifications/notification_services.py
Tests/test_sprint6c.py

SUPPORTED EVENTS
----------------
ExecutionStarted
ExecutionCompleted
ExecutionFailed
PortfolioAllocated
PaperOrderUpdated
DecisionCompleted

TELEGRAM ENVIRONMENT VARIABLES
------------------------------
BURSAAI_TELEGRAM_BOT_TOKEN
BURSAAI_TELEGRAM_CHAT_ID

PowerShell example:

$env:BURSAAI_TELEGRAM_BOT_TOKEN="YOUR_TOKEN"
$env:BURSAAI_TELEGRAM_CHAT_ID="YOUR_CHAT_ID"

TEST
----
python Tests/test_sprint6c.py

EXPECTED
--------
SPRINT 6C NOTIFICATION HUB OK
