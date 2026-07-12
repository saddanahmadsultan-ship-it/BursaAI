"""
=========================================================
BursaAI Execution State
Version : 6.0 Sprint 6A
=========================================================
"""

from enum import Enum


class ExecutionState(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
