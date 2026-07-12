from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Iterable, List, Tuple


PROJECT_ROOT = Path(__file__).resolve().parents[1]

EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "Logs",
    "Cache",
    "Experiments",
    "ResearchResults",
    "Reports",
    "Data",
    "MarketData",
    "Dist",
}

TEXT_SUFFIXES = {
    ".py",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".cfg",
    ".md",
    ".txt",
    ".cmd",
    ".bat",
    ".ps1",
}

ALLOWLIST_FILES = {
    ".env.example",
    "pre_commit_security_check.py",
}

PATTERNS = [
    (
        "Telegram bot token",
        re.compile(r"\b\d{8,12}:[A-Za-z0-9_-]{30,}\b"),
    ),
    (
        "Private key",
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    ),
    (
        "Generic secret assignment",
        re.compile(
            r"(?i)\b(?:api[_-]?key|secret|password|passwd|token)\b"
            r"\s*[:=]\s*[\"'][^\"'\s]{12,}[\"']"
        ),
    ),
]

MAX_FILE_BYTES = 50 * 1024 * 1024


def iter_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if not path.is_file():
            continue

        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue

        yield path


def scan(root: Path) -> Tuple[List[str], List[str]]:
    secrets: List[str] = []
    large_files: List[str] = []

    for path in iter_files(root):
        relative = path.relative_to(root)

        try:
            size = path.stat().st_size
        except OSError:
            continue

        if size > MAX_FILE_BYTES:
            large_files.append(
                f"{relative} ({size / 1024 / 1024:.1f} MB)"
            )

        if (
            path.suffix.lower() not in TEXT_SUFFIXES
            and path.name not in ALLOWLIST_FILES
        ):
            continue

        if path.name in ALLOWLIST_FILES:
            continue

        try:
            content = path.read_text(
                encoding="utf-8",
                errors="ignore",
            )
        except OSError:
            continue

        for label, pattern in PATTERNS:
            if pattern.search(content):
                secrets.append(f"{relative}: {label}")

    return secrets, large_files


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--ci",
        action="store_true",
        help="Use non-interactive CI output.",
    )
    args = parser.parse_args()

    secrets, large_files = scan(PROJECT_ROOT)

    print("=" * 64)
    print("BursaAI Repository Security Check")
    print("=" * 64)

    if secrets:
        print("\nPotential secrets:")
        for item in secrets:
            print(f"  - {item}")

    if large_files:
        print("\nFiles larger than 50 MB:")
        for item in large_files:
            print(f"  - {item}")

    if secrets or large_files:
        print("\nCHECK FAILED")
        return 1

    print("No obvious secrets or oversized files detected.")
    print("CHECK PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
