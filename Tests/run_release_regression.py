from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Bootstrap.regression_report import RegressionReport
from Bootstrap.regression_suite import FullRegressionSuite


def main():
    suite = FullRegressionSuite()
    suite.add_import_checks()

    result = suite.run()
    report = RegressionReport(result=result)

    print(report.render_text())

    paths = report.export(
        "Reports/Release"
    )

    print(f"TXT  : {paths['text']}")
    print(f"JSON : {paths['json']}")

    if not result.success:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
