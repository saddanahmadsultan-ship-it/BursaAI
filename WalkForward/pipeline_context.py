"""
=========================================================
BursaAI Walk Forward Pipeline Context
Version : 6.0 Sprint 6F.8
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass(slots=True)
class WalkForwardPipelineContext:
    symbol: str
    strategy_name: str
    config: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    historical_result: Any = None
    training_result: Any = None
    validation_result: Any = None
    analysis_result: Any = None
    optimization_result: Any = None
    final_report: Any = None
    export_paths: Dict[str, str] = field(default_factory=dict)

    current_stage: str = "PENDING"
    failed: bool = False
    error: str = ""
