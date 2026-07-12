from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from Release.stability_models import (
    StabilityEvidence,
    StabilityReportResult,
)


class FinalReleaseGate:
    WEIGHTS = {
        "regression": 0.25,
        "validation": 0.25,
        "soak": 0.30,
        "manifest": 0.10,
        "version": 0.10,
    }

    MANDATORY = {
        "regression",
        "validation",
        "soak",
        "version",
    }

    def __init__(
        self,
        project_root: str | Path,
        *,
        approval_score: float = 90.0,
        conditional_score: float = 75.0,
    ):
        self.project_root = Path(
            project_root
        ).resolve()

        self.approval_score = float(
            approval_score
        )

        self.conditional_score = float(
            conditional_score
        )

    def _version_evidence(
        self,
    ) -> StabilityEvidence:
        path = self.project_root / "VERSION"

        if not path.exists():
            return StabilityEvidence(
                name="version",
                available=False,
                passed=False,
                score=0.0,
                details="VERSION file missing.",
                source=str(path),
            )

        version = path.read_text(
            encoding="utf-8"
        ).strip()

        passed = version == "6.0.0-rc1"

        return StabilityEvidence(
            name="version",
            available=True,
            passed=passed,
            score=100.0 if passed else 0.0,
            details=(
                f"version={version}"
            ),
            source=str(path),
        )

    def _simple_evidence(
        self,
        name: str,
        payload: Dict[str, Any] | None,
        *,
        success_key: str = "success",
        source: str = "",
    ) -> StabilityEvidence:
        if payload is None:
            return StabilityEvidence(
                name=name,
                available=False,
                passed=False,
                score=0.0,
                details="Evidence file missing.",
                source=source,
            )

        passed = bool(
            payload.get(
                success_key,
                False,
            )
        )

        score = 100.0 if passed else 0.0

        details = (
            f"passed={payload.get('passed', '-')}, "
            f"failed={payload.get('failed', '-')}"
        )

        return StabilityEvidence(
            name=name,
            available=True,
            passed=passed,
            score=score,
            details=details,
            source=source,
        )

    def _soak_evidence(
        self,
        payload: Dict[str, Any] | None,
        source: str,
    ) -> StabilityEvidence:
        if payload is None:
            return StabilityEvidence(
                name="soak",
                available=False,
                passed=False,
                score=0.0,
                details="Soak report missing.",
                source=source,
            )

        requested = int(
            payload.get(
                "requested",
                payload.get(
                    "iterations_requested",
                    0,
                ),
            )
            or 0
        )

        completed = int(
            payload.get(
                "completed",
                payload.get(
                    "iterations_completed",
                    0,
                ),
            )
            or 0
        )

        failed = int(
            payload.get(
                "failed",
                payload.get(
                    "failed_iterations",
                    0,
                ),
            )
            or 0
        )

        duplicates = int(
            payload.get(
                "duplicate_orders",
                0,
            )
            or 0
        )

        journal_issues = int(
            payload.get(
                "journal_inconsistencies",
                0,
            )
            or 0
        )

        passed = bool(
            payload.get(
                "success",
                False,
            )
        )

        completion_score = (
            min(
                completed / requested * 100.0,
                100.0,
            )
            if requested > 0
            else 0.0
        )

        penalty = (
            failed * 10.0
            + duplicates * 20.0
            + journal_issues * 20.0
        )

        score = max(
            completion_score - penalty,
            0.0,
        )

        return StabilityEvidence(
            name="soak",
            available=True,
            passed=passed,
            score=round(
                score,
                4,
            ),
            details=(
                f"requested={requested}, "
                f"completed={completed}, "
                f"failed={failed}, "
                f"duplicates={duplicates}, "
                f"journal_issues={journal_issues}"
            ),
            source=source,
        )

    def _manifest_evidence(
        self,
        payload: Dict[str, Any] | None,
        source: str,
    ) -> StabilityEvidence:
        if payload is None:
            return StabilityEvidence(
                name="manifest",
                available=False,
                passed=False,
                score=0.0,
                details="Release manifest missing.",
                source=source,
            )

        files = payload.get(
            "files",
            [],
        )

        passed = (
            payload.get("version")
            == "6.0.0-rc1"
            and len(files) > 0
        )

        return StabilityEvidence(
            name="manifest",
            available=True,
            passed=passed,
            score=100.0 if passed else 0.0,
            details=(
                f"files={len(files)}, "
                f"version={payload.get('version', '-')}"
            ),
            source=source,
        )

    def evaluate(
        self,
        evidence_payloads: Dict[str, Any],
    ) -> StabilityReportResult:
        regression_source = (
            self.project_root
            / "Reports"
            / "Release"
            / "regression_report.json"
        )

        validation_source = (
            self.project_root
            / "Reports"
            / "Release"
            / "rc1_validation_report.json"
        )

        soak_source = (
            self.project_root
            / "Reports"
            / "Release"
            / "rc1_paper_soak_report.json"
        )

        manifest_source = (
            self.project_root
            / "Dist"
            / "BursaAI_v6.0.0_rc1_manifest.json"
        )

        evidence = [
            self._simple_evidence(
                "regression",
                evidence_payloads.get(
                    "regression"
                ),
                source=str(
                    regression_source
                ),
            ),
            self._simple_evidence(
                "validation",
                evidence_payloads.get(
                    "validation"
                ),
                source=str(
                    validation_source
                ),
            ),
            self._soak_evidence(
                evidence_payloads.get(
                    "soak"
                ),
                str(
                    soak_source
                ),
            ),
            self._manifest_evidence(
                evidence_payloads.get(
                    "manifest"
                ),
                str(
                    manifest_source
                ),
            ),
            self._version_evidence(),
        ]

        score = sum(
            item.score
            * self.WEIGHTS.get(
                item.name,
                0.0,
            )
            for item in evidence
        )

        mandatory_passed = all(
            item.passed
            for item in evidence
            if item.name in self.MANDATORY
        )

        blockers = [
            (
                f"{item.name}: "
                f"{item.details}"
            )
            for item in evidence
            if (
                item.name in self.MANDATORY
                and not item.passed
            )
        ]

        warnings = [
            (
                f"{item.name}: "
                f"{item.details}"
            )
            for item in evidence
            if (
                item.name not in self.MANDATORY
                and not item.passed
            )
        ]

        if (
            mandatory_passed
            and score
            >= self.approval_score
        ):
            gate_status = "APPROVED"
            recommendation = (
                "APPROVED FOR EXTENDED "
                "PAPER TRADING"
            )

        elif (
            mandatory_passed
            and score
            >= self.conditional_score
        ):
            gate_status = "CONDITIONAL"
            recommendation = (
                "APPROVED WITH CONDITIONS; "
                "RESOLVE WARNINGS"
            )

        else:
            gate_status = "REJECTED"
            recommendation = (
                "DO NOT RELEASE"
            )

        version = "UNKNOWN"

        version_path = (
            self.project_root
            / "VERSION"
        )

        if version_path.exists():
            version = (
                version_path
                .read_text(
                    encoding="utf-8"
                )
                .strip()
            )

        return StabilityReportResult(
            version=version,
            generated_at=datetime.now(
                timezone.utc
            ).isoformat(),
            evidence=evidence,
            overall_score=round(
                score,
                4,
            ),
            mandatory_passed=(
                mandatory_passed
            ),
            gate_status=gate_status,
            recommendation=(
                recommendation
            ),
            blockers=blockers,
            warnings=warnings,
        )
