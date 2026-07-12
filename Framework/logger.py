"""
=========================================================
BursaAI Framework Logger
Version : 6.0 Sprint 2
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional


@dataclass(slots=True)
class LogRecord:
    timestamp: str
    level: str
    message: str
    engine: str = ""

    def format(self) -> str:
        engine_part = (
            f"[{self.engine}] "
            if self.engine
            else ""
        )

        return (
            f"{self.timestamp} "
            f"[{self.level}] "
            f"{engine_part}"
            f"{self.message}"
        )


class FrameworkLogger:
    """
    Lightweight central logger for BursaAI framework components.
    """

    VALID_LEVELS = {
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
    }

    def __init__(
        self,
        log_file: Optional[str] = None,
        echo: bool = True,
    ):
        self.log_file = (
            Path(log_file)
            if log_file
            else None
        )
        self.echo = bool(echo)
        self.records: List[LogRecord] = []

    def _write(
        self,
        level: str,
        message: str,
        engine: str = "",
    ) -> LogRecord:
        normalized_level = str(level).upper().strip()

        if normalized_level not in self.VALID_LEVELS:
            normalized_level = "INFO"

        record = LogRecord(
            timestamp=datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            level=normalized_level,
            message=str(message),
            engine=str(engine),
        )

        self.records.append(record)

        formatted = record.format()

        if self.echo:
            print(formatted)

        if self.log_file:
            self.log_file.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            with self.log_file.open(
                "a",
                encoding="utf-8",
            ) as file:
                file.write(formatted + "\n")

        return record

    def debug(self, message: str, engine: str = ""):
        return self._write("DEBUG", message, engine)

    def info(self, message: str, engine: str = ""):
        return self._write("INFO", message, engine)

    def warning(self, message: str, engine: str = ""):
        return self._write("WARNING", message, engine)

    def error(self, message: str, engine: str = ""):
        return self._write("ERROR", message, engine)

    def clear(self) -> None:
        self.records.clear()

    def export_text(self) -> str:
        return "\n".join(
            record.format()
            for record in self.records
        )
