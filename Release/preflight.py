from __future__ import annotations

from dataclasses import asdict, dataclass, field
from importlib import import_module
from pathlib import Path
from typing import Callable, Iterable, List
import sys


@dataclass(slots=True)
class PreflightCheck:
    name: str
    success: bool
    details: str = ""

    def to_dict(self):
        return asdict(self)


@dataclass(slots=True)
class PreflightResult:
    checks: List[PreflightCheck] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return all(item.success for item in self.checks)

    @property
    def passed(self) -> int:
        return sum(1 for item in self.checks if item.success)

    @property
    def failed(self) -> int:
        return len(self.checks) - self.passed


class ReleasePreflight:
    REQUIRED_PATHS = [
        "Core",
        "Framework",
        "Adapters",
        "Trading",
        "Notifications",
        "Journal",
        "Analytics",
        "WalkForward",
        "Bootstrap",
        "Config",
        "Tests",
        "main_v6.py",
    ]

    REQUIRED_IMPORTS = [
        "Framework.infrastructure",
        "Framework.execution_manager",
        "Adapters.full_pipeline_registry",
        "Trading.paper_execution",
        "Notifications.notification_hub",
        "Journal.trade_journal",
        "Analytics.performance_engine",
        "WalkForward.pipeline",
        "Bootstrap.service_bootstrap",
        "Config.config_loader",
    ]

    def __init__(self, project_root: str | Path):
        self.root = Path(project_root).resolve()

    def run(self) -> PreflightResult:
        checks = []

        for relative in self.REQUIRED_PATHS:
            path = self.root / relative
            checks.append(
                PreflightCheck(
                    name=f"path:{relative}",
                    success=path.exists(),
                    details="present" if path.exists() else "missing",
                )
            )

        root_text = str(self.root)

        if root_text not in sys.path:
            sys.path.insert(0, root_text)

        for module_name in self.REQUIRED_IMPORTS:
            try:
                import_module(module_name)
                checks.append(
                    PreflightCheck(
                        name=f"import:{module_name}",
                        success=True,
                        details="imported",
                    )
                )
            except Exception as error:
                checks.append(
                    PreflightCheck(
                        name=f"import:{module_name}",
                        success=False,
                        details=f"{type(error).__name__}: {error}",
                    )
                )

        version_path = self.root / "VERSION"
        version_ok = (
            version_path.exists()
            and version_path.read_text(encoding="utf-8").strip()
            == "6.0.0-rc1"
        )

        checks.append(
            PreflightCheck(
                name="version:6.0.0-rc1",
                success=version_ok,
                details="valid" if version_ok else "invalid or missing",
            )
        )

        return PreflightResult(checks=checks)
