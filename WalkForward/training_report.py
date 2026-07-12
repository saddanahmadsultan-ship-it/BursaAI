from __future__ import annotations
from dataclasses import dataclass
from WalkForward.training_models import TrainingRunResult

@dataclass(slots=True)
class TrainingReport:
    result: TrainingRunResult

    def render_text(self) -> str:
        value = self.result
        return '\n'.join([
            '=' * 58,
            'BURSAAI TRAINING WINDOW REPORT',
            '=' * 58,
            f'Symbol              : {value.symbol}',
            f'Total Windows       : {value.total_windows}',
            f'Successful Windows  : {value.successful_windows}',
            f'Failed Windows      : {value.failed_windows}',
            f'Duration            : {value.duration_ms:.2f} ms',
            f"Status              : {'SUCCESS' if value.success else 'PARTIAL/FAILED'}",
            '=' * 58,
        ])
