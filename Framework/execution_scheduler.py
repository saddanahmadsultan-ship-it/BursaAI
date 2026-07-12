"""
=========================================================
BursaAI Execution Scheduler
Version : 6.0 Sprint 6A
=========================================================

Sprint 6A provides schedule definitions only.
Actual recurring execution will be added later.
"""

from dataclasses import dataclass
from typing import List


@dataclass(slots=True)
class ExecutionSchedule:
    name: str
    times: List[str]
    enabled: bool = True


class ExecutionScheduler:
    def __init__(self):
        self.schedules: List[ExecutionSchedule] = []

    def add(self, schedule: ExecutionSchedule) -> None:
        self.schedules.append(schedule)

    def enabled(self) -> List[ExecutionSchedule]:
        return [
            schedule
            for schedule in self.schedules
            if schedule.enabled
        ]
