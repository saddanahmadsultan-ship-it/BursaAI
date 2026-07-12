from __future__ import annotations

from importlib import import_module
from pathlib import Path
from time import perf_counter
from typing import Callable, List

from Release.rc_validation_models import (
    RCValidationCheck,
    RCValidationResult,
)


class RCValidator:
    REQUIRED_PATHS = [
        "VERSION",
        "CHANGELOG.md",
        "RELEASE_NOTES.md",
        "main_v6.py",
        "Config/default_config.json",
        "Core",
        "Framework",
        "Adapters",
        "Trading",
        "Notifications",
        "Journal",
        "Analytics",
        "WalkForward",
        "Bootstrap",
        "Release",
        "Scripts",
        "Tests",
    ]

    REQUIRED_IMPORTS = [
        "Config.config_loader",
        "Bootstrap.service_bootstrap",
        "Bootstrap.application_runner",
        "Bootstrap.regression_suite",
        "Release.preflight",
        "Release.rc_builder",
        "Framework.infrastructure",
        "Framework.execution_manager",
        "Adapters.full_pipeline_registry",
        "Trading.paper_execution",
        "Notifications.notification_hub",
        "Journal.trade_journal",
        "Analytics.performance_engine",
        "WalkForward.pipeline",
    ]

    def __init__(self, project_root: str | Path):
        self.project_root = Path(project_root).resolve()

    def _run_check(
        self,
        name: str,
        function: Callable[[], str],
    ) -> RCValidationCheck:
        started = perf_counter()

        try:
            details = function() or "OK"

            return RCValidationCheck(
                name=name,
                success=True,
                duration_ms=(perf_counter() - started) * 1000,
                details=str(details),
            )

        except Exception as error:
            return RCValidationCheck(
                name=name,
                success=False,
                duration_ms=(perf_counter() - started) * 1000,
                error=f"{type(error).__name__}: {error}",
            )

    def _check_version(self) -> str:
        path = self.project_root / "VERSION"

        if not path.exists():
            raise FileNotFoundError("VERSION file missing.")

        version = path.read_text(encoding="utf-8").strip()

        if version != "6.0.0-rc1":
            raise ValueError(
                f"Expected 6.0.0-rc1, found {version!r}."
            )

        return version

    def _check_path(self, relative: str) -> str:
        path = self.project_root / relative

        if not path.exists():
            raise FileNotFoundError(relative)

        return "present"

    def _check_import(self, module_name: str) -> str:
        import_module(module_name)
        return "imported"

    def _check_config(self) -> str:
        from Config.config_loader import load_app_config

        config = load_app_config(
            str(
                self.project_root
                / "Config"
                / "default_config.json"
            )
        )

        if config.version != "6.0":
            raise ValueError(
                f"Unexpected config version: {config.version}"
            )

        return (
            f"mode={config.execution.mode}, "
            f"symbols={len(config.execution.symbols)}"
        )

    def _check_manifest_tools(self) -> str:
        from Release.release_manifest import RCManifestBuilder

        builder = RCManifestBuilder()
        manifest = builder.build(
            self.project_root,
            metadata={"validation": True},
        )

        if not manifest.files:
            raise ValueError(
                "Release manifest contains no files."
            )

        return f"files={len(manifest.files)}"

    def run(self) -> RCValidationResult:
        checks: List[RCValidationCheck] = []

        checks.append(
            self._run_check(
                "version",
                self._check_version,
            )
        )

        for relative in self.REQUIRED_PATHS:
            checks.append(
                self._run_check(
                    f"path:{relative}",
                    lambda item=relative: self._check_path(item),
                )
            )

        for module_name in self.REQUIRED_IMPORTS:
            checks.append(
                self._run_check(
                    f"import:{module_name}",
                    lambda item=module_name: self._check_import(item),
                )
            )

        checks.append(
            self._run_check(
                "config:default",
                self._check_config,
            )
        )

        checks.append(
            self._run_check(
                "release:manifest_tools",
                self._check_manifest_tools,
            )
        )

        version = "UNKNOWN"

        version_path = self.project_root / "VERSION"

        if version_path.exists():
            version = version_path.read_text(
                encoding="utf-8"
            ).strip()

        return RCValidationResult(
            version=version,
            checks=checks,
        )
