import os
from datetime import datetime


def write_markdown_report(summary: dict, path: str = "reports/latest.md") -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        f"# PCT Report — {summary['suite']}",
        f"",
        f"**Date:** {now}  ",
        f"**Total:** {summary['total']}  **Passed:** {summary['passed']}  **Failed:** {summary['failed']}",
        f"",
        f"---",
        f"",
    ]
    for case in summary["cases"]:
        status = "PASS" if case["passed"] else "FAIL"
        lines.append(f"## [{status}] {case['name']}")
        if case["errors"]:
            for err in case["errors"]:
                lines.append(f"- {err}")
        else:
            lines.append("- All assertions passed.")
        lines.append("")

    with open(path, "w") as f:
        f.write("\n".join(lines))
