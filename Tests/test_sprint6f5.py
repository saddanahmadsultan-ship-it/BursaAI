"""
BursaAI v6.0 Sprint 6F.5 Walk Forward Analyzer test.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Framework.infrastructure import (
    build_infrastructure,
)
from WalkForward.analyzer_report import (
    WalkForwardAnalysisReport,
)
from WalkForward.analyzer_services import (
    register_walkforward_analyzer,
)
from WalkForward.training_models import (
    TrainingWindowResult,
)
from WalkForward.validation_models import (
    ValidationWindowResult,
)


def build_training_results():
    return [
        TrainingWindowResult(
            window_id=1,
            symbol="1155.KL",
            success=True,
            metrics={
                "training_score": 85,
            },
        ),
        TrainingWindowResult(
            window_id=2,
            symbol="1155.KL",
            success=True,
            metrics={
                "training_score": 82,
            },
        ),
        TrainingWindowResult(
            window_id=3,
            symbol="1155.KL",
            success=True,
            metrics={
                "training_score": 80,
            },
        ),
        TrainingWindowResult(
            window_id=4,
            symbol="1155.KL",
            success=True,
            metrics={
                "training_score": 78,
            },
        ),
        TrainingWindowResult(
            window_id=5,
            symbol="1155.KL",
            success=True,
            metrics={
                "training_score": 76,
            },
        ),
    ]


def build_validation_results():
    return [
        ValidationWindowResult(
            window_id=1,
            symbol="1155.KL",
            success=True,
            metrics={
                "validation_score": 80,
            },
        ),
        ValidationWindowResult(
            window_id=2,
            symbol="1155.KL",
            success=True,
            metrics={
                "validation_score": 77,
            },
        ),
        ValidationWindowResult(
            window_id=3,
            symbol="1155.KL",
            success=True,
            metrics={
                "validation_score": 74,
            },
        ),
        ValidationWindowResult(
            window_id=4,
            symbol="1155.KL",
            success=True,
            metrics={
                "validation_score": 72,
            },
        ),
        ValidationWindowResult(
            window_id=5,
            symbol="1155.KL",
            success=True,
            metrics={
                "validation_score": 70,
            },
        ),
    ]


def main():
    infrastructure = build_infrastructure()
    events = []

    infrastructure.events.subscribe(
        "WalkForwardAnalysisCompleted",
        lambda event: events.append(event),
    )

    analyzer = register_walkforward_analyzer(
        infrastructure.services,
        maximum_degradation_percent=20,
        minimum_validation_metric=60,
        minimum_pass_rate_percent=60,
    )

    result = analyzer.analyze(
        build_training_results(),
        build_validation_results(),
    )

    assert result.symbol == "1155.KL"
    assert result.total_windows == 5
    assert result.passed_windows == 5
    assert result.failed_windows == 0
    assert result.average_training_metric == 80.2
    assert result.average_validation_metric == 74.6
    assert result.consistency_score == 100.0
    assert result.stability_score > 90
    assert result.robustness_score > 80
    assert result.best_window_id == 1
    assert result.worst_window_id == 5
    assert result.verdict == "ROBUST"
    assert result.success is True
    assert len(result.windows) == 5

    for window in result.windows:
        assert window.passed is True
        assert window.status == "PASS"
        assert window.degradation_percent < 20

    assert len(events) == 1
    assert (
        events[0].payload["verdict"]
        == "ROBUST"
    )

    assert (
        infrastructure.services.resolve(
            "walkforward_analyzer"
        )
        is analyzer
    )

    report = WalkForwardAnalysisReport(
        result=result
    )

    rendered = report.render_text()

    assert (
        "BURSAAI WALK FORWARD ANALYSIS REPORT"
        in rendered
    )
    assert "Passed Windows            : 5" in rendered
    assert "Verdict                   : ROBUST" in rendered

    print("=" * 92)
    print("BURSAAI v6.0 SPRINT 6F.5 TEST")
    print("=" * 92)
    print("Window Analysis Model      : OK")
    print("Analysis Result Model      : OK")
    print("Training / Validation Link : OK")
    print("Degradation Calculation    : OK")
    print("Stability Score            : OK")
    print("Consistency Score          : OK")
    print("Robustness Score           : OK")
    print("Best / Worst Window        : OK")
    print("Analyzer Verdict           : OK")
    print("Analyzer Event             : OK")
    print("Service Registration       : OK")
    print("Analysis Report            : OK")
    print("=" * 92)
    print("SPRINT 6F.5 WALK FORWARD ANALYZER OK")


if __name__ == "__main__":
    main()
