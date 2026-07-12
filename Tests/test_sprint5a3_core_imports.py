"""
Sprint 5A.3 import-only smoke test for the real Core module.

No market data is downloaded.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main():
    from Core.ai_brain import apply_ai_brain
    from Adapters.ai_brain_adapter import AIBrainAdapter

    assert callable(apply_ai_brain)

    AIBrainAdapter(
        brain_function=apply_ai_brain
    )

    print("=" * 86)
    print("BURSAAI v6.0 SPRINT 5A.3 CORE IMPORT TEST")
    print("=" * 86)
    print("Core.ai_brain        : OK")
    print("AI Brain Function    : OK")
    print("AI Brain Adapter     : OK")
    print("=" * 86)
    print("SPRINT 5A.3 CORE IMPORTS OK")


if __name__ == "__main__":
    main()
