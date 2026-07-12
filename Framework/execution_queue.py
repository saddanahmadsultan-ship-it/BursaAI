"""
=========================================================
BursaAI Execution Queue
Version : 6.0 Sprint 6A
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional

from Framework.execution_state import ExecutionState


@dataclass(slots=True)
class ExecutionItem:
    symbol: str
    state: ExecutionState = ExecutionState.PENDING
    error: str = ""
    warnings: List[str] = field(default_factory=list)


class ExecutionQueue:
    def __init__(self, symbols: Iterable[str]):
        self._items: Dict[str, ExecutionItem] = {
            str(symbol): ExecutionItem(symbol=str(symbol))
            for symbol in symbols
        }

    def get(self, symbol: str) -> ExecutionItem:
        return self._items[str(symbol)]

    def set_state(
        self,
        symbol: str,
        state: ExecutionState,
        error: str = "",
    ) -> None:
        item = self.get(symbol)
        item.state = state
        item.error = str(error)

    def add_warning(self, symbol: str, warning: str) -> None:
        self.get(symbol).warnings.append(str(warning))

    def items(self) -> List[ExecutionItem]:
        return list(self._items.values())

    def symbols(self) -> List[str]:
        return list(self._items.keys())

    def by_state(self, state: ExecutionState) -> List[ExecutionItem]:
        return [
            item for item in self._items.values()
            if item.state == state
        ]

    def counts(self) -> Dict[str, int]:
        return {
            state.value: len(self.by_state(state))
            for state in ExecutionState
        }
