"""
BursaAI v6.0 Sprint 6F.7 Walk Forward Final Report test.
"""

from pathlib import Path
import sys
import tempfile

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Framework.infrastructure import (
    build_infrastructure,
)
from WalkForward.analyzer_models import (
    WalkForwardAnalysisResult,
    WindowAnalysis,
)
from WalkForward.final_report_exporter import (
    WalkForwardFinalReportExporter,
)
from WalkForward.final_report_renderer import (
    WalkForwardFinalReportRenderer,
)
from WalkForward.final_report_services import (
    register_walkforward_final_report,
)
from WalkForward.historical_models import (
    HistoricalRunResult,
)
from WalkForward.optimization_models import (
    OptimizationCandidateResult,
    OptimizationRunResult,
)
from WalkForward.training_models import (
    TrainingRunResult,
    TrainingWindowResult,
)
from WalkForward.validation_models import (
    ValidationRunResult,
    ValidationWindowResult,
)


def build_inputs():
    historical = HistoricalRunResult(
        symbol="1155.KL",
        windows_generated=5,
        splits_created=5,
        splits=[],
        metadata={
            "dataset_rows": 1200,
            "dataset_source": "loader",
            "missing_intervals": 0,
        },
        warnings=[],
    )

    training_results = [
        TrainingWindowResult(
            window_id=index,
            symbol="1155.KL",
            success=True,
            parameters={
                "ema_fast": 10,
                "ema_slow": 50,
            },
            metrics={
                "training_score": 80 + index,
            },
        )
        for index in range(1, 6)
    ]

    training = TrainingRunResult(
        symbol="1155.KL",
        total_windows=5,
        successful_windows=5,
        failed_windows=0,
        results=training_results,
        duration_ms=100.0,
    )

    validation_results = [
        ValidationWindowResult(
            window_id=index,
            symbol="1155.KL",
            success=True,
            parameters={
                "ema_fast": 10,
                "ema_slow": 50,
            },
            metrics={
                "validation_score": 75 + index,
            },
        )
        for index in range(1, 6)
    ]

    validation = ValidationRunResult(
        symbol="1155.KL",
        total_windows=5,
        successful_windows=5,
        failed_windows=0,
        results=validation_results,
        duration_ms=80.0,
    )

    windows = [
        WindowAnalysis(
            window_id=index,
            symbol="1155.KL",
            training_metric=80 + index,
            validation_metric=75 + index,
            degradation_percent=6.0,
            passed=True,
            status="PASS",
        )
        for index in range(1, 6)
    ]

    analysis = WalkForwardAnalysisResult(
        symbol="1155.KL",
        total_windows=5,
        passed_windows=5,
        failed_windows=0,
        average_training_metric=83.0,
        average_validation_metric=78.0,
        average_degradation_percent=6.0,
        stability_score=95.0,
        consistency_score=100.0,
        robustness_score=92.5,
        best_window_id=5,
        worst_window_id=1,
        verdict="ROBUST",
        windows=windows,
        warnings=[],
    )

    best = OptimizationCandidateResult(
        parameter_id=4,
        parameters={
            "ema_fast": 10,
            "ema_slow": 50,
            "rsi_period": 14,
        },
        success=True,
        optimization_score=91.75,
        metrics={
            "robustness_score": 92.5,
            "profit_factor": 2.1,
        },
    )

    optimization = OptimizationRunResult(
        strategy_name="ema_rsi",
        total_candidates=18,
        completed_candidates=18,
        failed_candidates=0,
        best_candidate=best,
        candidates=[best],
        duration_ms=200.0,
    )

    return (
        historical,
        training,
        validation,
        analysis,
        optimization,
    )


def main():
    infrastructure = build_infrastructure()

    builder = register_walkforward_final_report(
        infrastructure.services
    )

    (
        historical,
        training,
        validation,
        analysis,
        optimization,
    ) = build_inputs()

    report = builder.build(
        strategy_name="ema_rsi",
        historical_result=historical,
        training_result=training,
        validation_result=validation,
        analysis_result=analysis,
        optimization_result=optimization,
        metadata={
            "test_run": True,
        },
    )

    summary = report.summary

    assert summary.symbol == "1155.KL"
    assert summary.strategy_name == "ema_rsi"
    assert summary.dataset_rows == 1200
    assert summary.windows_generated == 5
    assert summary.training_windows == 5
    assert summary.validation_windows == 5
    assert summary.passed_windows == 5
    assert summary.failed_windows == 0
    assert summary.robustness_score == 92.5
    assert summary.verdict == "ROBUST"
    assert (
        summary.recommendation
        == "APPROVED FOR PAPER TRADING"
    )
    assert summary.best_parameters == {
        "ema_fast": 10,
        "ema_slow": 50,
        "rsi_period": 14,
    }
    assert summary.best_optimization_score == 91.75

    renderer = WalkForwardFinalReportRenderer(
        report=report
    )

    text = renderer.render_text()
    json_text = renderer.render_json()

    assert (
        "BURSAAI WALK FORWARD FINAL REPORT"
        in text
    )
    assert (
        "Verdict                   : ROBUST"
        in text
    )
    assert (
        "APPROVED FOR PAPER TRADING"
        in text
    )
    assert '"symbol": "1155.KL"' in json_text

    with tempfile.TemporaryDirectory() as folder:
        exporter = WalkForwardFinalReportExporter()

        paths = exporter.export(
            report,
            output_directory=folder,
        )

        text_path = Path(paths["text"])
        json_path = Path(paths["json"])

        assert text_path.exists()
        assert json_path.exists()

        assert (
            "BURSAAI WALK FORWARD FINAL REPORT"
            in text_path.read_text(
                encoding="utf-8"
            )
        )

        assert (
            '"strategy_name": "ema_rsi"'
            in json_path.read_text(
                encoding="utf-8"
            )
        )

    assert (
        infrastructure.services.resolve(
            "walkforward_final_report_builder"
        )
        is builder
    )

    assert infrastructure.services.contains(
        "walkforward_final_report_exporter"
    )

    print("=" * 96)
    print("BURSAAI v6.0 SPRINT 6F.7 TEST")
    print("=" * 96)
    print("Final Summary Model          : OK")
    print("Final Report Data Model      : OK")
    print("Historical Result Merge      : OK")
    print("Training Result Merge        : OK")
    print("Validation Result Merge      : OK")
    print("Analyzer Result Merge        : OK")
    print("Optimization Result Merge    : OK")
    print("Verdict Recommendation       : OK")
    print("Text Report                  : OK")
    print("JSON Report                  : OK")
    print("Report Export                : OK")
    print("Service Registration         : OK")
    print("=" * 96)
    print("SPRINT 6F.7 WALK FORWARD FINAL REPORT OK")


if __name__ == "__main__":
    main()
