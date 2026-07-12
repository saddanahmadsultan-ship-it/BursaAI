from __future__ import annotations
import argparse, subprocess, sys
from pathlib import Path
from typing import List, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_TRACKED_PREFIXES = (
    "Archive/", "Reports/", "Experiments/checkpoints/",
    "Experiments/locks/", "Experiments/records/",
    "ResearchResults/results/", "ResearchResults/by_experiment/",
    "Logs/", "Cache/", "Data/", "MarketData/",
)
FORBIDDEN_SUFFIXES = (
    ".exe", ".msi", ".crdownload", ".zip", ".7z", ".rar",
    ".sqlite", ".sqlite3", ".db", ".duckdb",
)
LARGE_FILE_LIMIT = 50 * 1024 * 1024

def run_git(*args: str):
    return subprocess.run(["git", *args], cwd=PROJECT_ROOT, capture_output=True, text=True)

def tracked_files() -> List[str]:
    result = run_git("ls-files")
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git ls-files gagal.")
    return [line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip()]

def staged_files() -> List[str]:
    result = run_git("diff", "--cached", "--name-only")
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git diff --cached gagal.")
    return [line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip()]

def audit_files(paths: List[str]) -> Tuple[List[str], List[str], List[str]]:
    prefix_hits, suffix_hits, large_files = [], [], []
    for relative in paths:
        normalized = relative.replace("\\", "/")
        if normalized.startswith(FORBIDDEN_TRACKED_PREFIXES):
            prefix_hits.append(normalized)
        if normalized.lower().endswith(FORBIDDEN_SUFFIXES):
            suffix_hits.append(normalized)
        full_path = PROJECT_ROOT / relative
        if full_path.exists() and full_path.is_file():
            size = full_path.stat().st_size
            if size > LARGE_FILE_LIMIT:
                large_files.append(f"{normalized} ({size / 1024 / 1024:.2f} MB)")
    return prefix_hits, suffix_hits, large_files

def check_ignore_rule(path: str) -> bool:
    return run_git("check-ignore", "-q", path).returncode == 0

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--staged", action="store_true")
    args = parser.parse_args()

    print("=" * 72)
    print("BursaAI Sprint 7 Repository Cleanup Audit")
    print("=" * 72)

    if not (PROJECT_ROOT / ".git").exists():
        print("FAILED: Folder ini bukan Git repository.")
        return 1

    paths = staged_files() if args.staged else tracked_files()
    prefix_hits, suffix_hits, large_files = audit_files(paths)

    print(f"Files audited  : {len(paths)}")
    print(f"Archive ignored: {check_ignore_rule('Archive/')}")

    failed = False
    if prefix_hits:
        failed = True
        print("\nForbidden tracked paths:")
        for item in prefix_hits:
            print(f"  - {item}")
    if suffix_hits:
        failed = True
        print("\nForbidden tracked file types:")
        for item in suffix_hits:
            print(f"  - {item}")
    if large_files:
        failed = True
        print("\nTracked files larger than 50 MB:")
        for item in large_files:
            print(f"  - {item}")

    if failed:
        print("\nAUDIT FAILED")
        return 1

    print("\nNo forbidden tracked paths or oversized files detected.")
    print("AUDIT PASSED")
    return 0

if __name__ == "__main__":
    sys.exit(main())
