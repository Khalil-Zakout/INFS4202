"""Non-functional test for PERF-02: the Engine must rank 200 candidates in <= 500 ms
at the 95th percentile. Prints the p50/p95/max per candidate count and exits non-zero
if the 200-candidate p95 exceeds the budget.

Run:  cd tests/performance && python3 engine_rank_latency.py
Needs the Engine running (./start.sh) or ENGINE_URL set.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "api"))
from engine_client import call, engine_available  # noqa: E402

T = "2026-11-20T09:00:00+03:00"
BUDGET_MS = 500
REPEATS = 20


def candidates(n):
    return [{"applicationId": i, "score": (i * 37) % 101,
             "gpa": round(2 + (i % 20) / 10, 2), "submittedAt": T} for i in range(1, n + 1)]


def percentile(values, p):
    s = sorted(values)
    return s[min(len(s) - 1, int(len(s) * p / 100))]


def main():
    if not engine_available():
        print("SKIP: Engine not reachable on ENGINE_URL")
        return 0
    worst_200 = None
    for n in (10, 50, 100, 150, 200):
        times = [call("/rank", {"seats": 3, "candidates": candidates(n)}).elapsed_ms for _ in range(REPEATS)]
        p50, p95, mx = percentile(times, 50), percentile(times, 95), max(times)
        flag = "" if n != 200 else ("  <= budget" if p95 <= BUDGET_MS else f"  EXCEEDS {BUDGET_MS} ms budget (PERF-02)")
        print(f"n={n:4d}  p50={p50:8.1f} ms  p95={p95:8.1f} ms  max={mx:8.1f} ms{flag}")
        if n == 200:
            worst_200 = p95
    if worst_200 is not None and worst_200 > BUDGET_MS:
        print(f"\nFAIL: 200-candidate ranking p95 = {worst_200:.0f} ms, budget {BUDGET_MS} ms (issue: Engine rank is super-linear).")
        return 1
    print("\nPASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
