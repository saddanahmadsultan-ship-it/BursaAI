from pathlib import Path
import sys
import tempfile

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Bootstrap.regression_report import RegressionReport
from Bootstrap.regression_suite import FullRegressionSuite


def main():
    suite = FullRegressionSuite()

    suite.add_check(
        "basic:arithmetic",
        lambda: "2 + 2 = 4" if 2 + 2 == 4 else (_ for _ in ()).throw(
            AssertionError("Arithmetic failed")
        ),
    )

    suite.add_check(
        "basic:filesystem",
        lambda: "filesystem available"
        if PROJECT_ROOT.exists()
        else (_ for _ in ()).throw(
            AssertionError("Project root missing")
        ),
    )

    suite.add_check(
        "import:framework",
        lambda: (
            __import__("Framework.infrastructure"),
            "Framework imported",
        )[1],
    )

    suite.add_check(
        "import:bootstrap",
        lambda: (
            __import__("Bootstrap.regression_suite"),
            "Bootstrap imported",
        )[1],
    )

    result = suite.run()

    assert result.success is True
    assert result.passed == 4
    assert result.failed == 0

    report = RegressionReport(result=result)
    rendered = report.render_text()

    assert "BURSAAI v6 FULL REGRESSION REPORT" in rendered
    assert "Status : PASSED" in rendered

    with tempfile.TemporaryDirectory() as folder:
        paths = report.export(folder)

        assert Path(paths["text"]).exists()
        assert Path(paths["json"]).exists()

    print("=" * 92)
    print("BURSAAI v6.0 SPRINT 6G.4 TEST")
    print("=" * 92)
    print("Regression Models       : OK")
    print("Regression Suite        : OK")
    print("Custom Checks           : OK")
    print("Import Checks           : OK")
    print("Regression Report       : OK")
    print("TXT / JSON Export       : OK")
    print("=" * 92)
    print("SPRINT 6G.4 FULL REGRESSION SUITE OK")


if __name__ == "__main__":
    main()
