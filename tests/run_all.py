#!/usr/bin/env python3
"""Run the Python test suites with one command (Windows, macOS, Linux), optionally saving the results.

Start the system first (Windows: .\\start.cmd --reset   macOS/Linux: ./start.sh --reset), then from the
repository folder:

    python tests/run_all.py                    # api, rank, ai  (these do not change any data)
    python tests/run_all.py api rank --save    # chosen suites; --save writes docs/results/<suite>.txt
    python tests/run_all.py system race pages  # these CHANGE data: run them once, right after --reset

Suites
    api     Engine REST contract, black-box            tests/api/test_engine_contract.py
    rank    Engine ranking latency (PERF-02)           tests/performance/engine_rank_latency.py
    ai      AI prompt properties, model-free           tests/ai-eval/test_prompt_properties.py
    system  System reproductions of the Portal defects tests/system/reproduce.py         (changes data)
    race    Two students accept the last seat (D03)    tests/system/seat_race.py         (changes data)
    pages   Portal list pages with 1,000 extra
            applications (PERF-01, PERF-05)            tests/performance/portal_pages.py (adds data)

The Portal white-box suite (JUnit) runs with Maven:  cd portal; .\\mvnw.cmd test   (./mvnw test)

A suite "fails" when it finds defects: each failing check is the evidence for a reported issue.
"""
import datetime
import os
import platform
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RESULTS = os.path.join(ROOT, "docs", "results")

SUITES = {
    "api": ("api", ["-m", "unittest", "-v"]),
    "rank": ("performance", ["engine_rank_latency.py"]),
    "ai": ("ai-eval", ["-m", "unittest", "-v", "test_prompt_properties.py"]),
    "system": ("system", ["reproduce.py"]),
    "race": ("system", ["seat_race.py"]),
    "pages": ("performance", ["portal_pages.py", "--generate", "1000"]),
}
DEFAULT = ["api", "rank", "ai"]


def who():
    try:
        return subprocess.run(["git", "config", "user.name"], cwd=ROOT, capture_output=True,
                              text=True).stdout.strip() or "unknown"
    except OSError:
        return "unknown"


def run(name, save):
    folder, args = SUITES[name]
    cmd = [sys.executable, *args]
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
    started = datetime.datetime.now()
    p = subprocess.run(cmd, cwd=os.path.join(HERE, folder), capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=env)
    output = (p.stdout + p.stderr).rstrip()
    verdict = "PASS" if p.returncode == 0 else "FAIL (defects found)"
    print(f"\n===== {name}: {verdict} =====\n{output}")
    if save:
        os.makedirs(RESULTS, exist_ok=True)
        header = [f"Suite: {name}  ({SUITES[name][0]}/{' '.join(args)})",
                  f"Run by: {who()}  on {started:%d/%m/%Y %H:%M}",
                  f"Machine: {platform.system()} {platform.release()}, Python {platform.python_version()}",
                  f"Result: {verdict} (exit code {p.returncode})", "-" * 72]
        path = os.path.join(RESULTS, f"{name}.txt")
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(header) + "\n" + output + "\n")
        print(f"(saved to {os.path.relpath(path, ROOT)})")
    return p.returncode == 0


def main(argv):
    save = "--save" in argv
    names = [a for a in argv if not a.startswith("--")] or DEFAULT
    unknown = [n for n in names if n not in SUITES]
    if unknown or "-h" in argv or "--help" in argv:
        print(__doc__)
        return 2
    results = {n: run(n, save) for n in names}
    print("\nSummary: " + ", ".join(f"{n} {'PASS' if ok else 'FAIL'}" for n, ok in results.items()))
    print("A FAIL here means the suite found the documented defects (see tests/README.md).")
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
