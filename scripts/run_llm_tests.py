"""Run the slow LLM tests and save the results to reports/.

Each run gets its own pair of files, named by date, time, model and prompt version:
    reports/2026-11-27_1205_qwen2.5-7b_v1.txt   (console output, UTF-8)
    reports/2026-11-27_1205_qwen2.5-7b_v1.xml   (JUnit XML for CI tools)

Extra arguments are passed to pytest:
    python scripts/run_llm_tests.py --lf
    python scripts/run_llm_tests.py -k comparison
"""

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from bot.config import load_settings

ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = ROOT / "reports"


def report_stem() -> str:
    """Build a file name without extension, e.g. '2026-11-27_1205_qwen2.5-7b_v1'."""
    settings = load_settings()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    model = settings.model.replace(":", "-").replace("/", "-")
    return f"{timestamp}_{model}_{settings.prompt_version}"


def main() -> int:
    REPORTS_DIR.mkdir(exist_ok=True)
    stem = report_stem()
    txt_path = REPORTS_DIR / f"{stem}.txt"
    xml_path = REPORTS_DIR / f"{stem}.xml"

    command = [
        sys.executable,
        "-m",
        "pytest",
        "-m",
        "llm",
        "-rfs",
        "--tb=short",
        f"--junitxml={xml_path}",
        *sys.argv[1:],
    ]

    # Force UTF-8 in the child process, so Cyrillic is not broken on Windows.
    env = {**os.environ, "PYTHONUTF8": "1"}

    with open(txt_path, "w", encoding="utf-8") as report:
        report.write(f"$ {' '.join(command)}\n\n")
        process = subprocess.Popen(
            command,
            cwd=ROOT,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        for line in process.stdout:
            print(line, end="")
            report.write(line)
        exit_code = process.wait()

    print(f"\nReports saved:\n  {txt_path}\n  {xml_path}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
