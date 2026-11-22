"""Non-functional tests for the Portal list pages.

PERF-01: every list page renders in <= 2 s at p95 with the seed plus 1,000 extra
applications. PERF-05: no page returns an unbounded list; every list is paginated.

This script (optionally) generates volume data through Coordinator -> Tools, then
measures the p95 render time of the main list pages and checks that each is
paginated at 20 rows.

Run:  cd tests/performance && python3 portal_pages.py --generate 1000
      cd tests/performance && python3 portal_pages.py            # measure only
Needs the Portal running (./start.sh) on 127.0.0.1:8080.
"""
import sys, os, re, argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "api"))
# Reuse the lightweight Portal client kept with the performance helpers.
from portal_client import login, percentile  # noqa: E402

PAGES = {
    "Postings (student)": ("student.amal", "/postings"),
    "My applications (student)": ("student.amal", "/applications"),
    "All applications (coordinator)": ("coordinator", "/coordinator/applications"),
    "Outbox (coordinator)": ("coordinator", "/coordinator/outbox"),
    "Candidate ranking (recruiter)": ("recruiter.qtech", "/recruiter/postings/2/candidates"),
}
BUDGET_MS = 2000
REPEATS = 15


def rows_on_page(html):
    body = re.search(r"<table>(.*?)</table>", html, re.S)
    return len(re.findall(r"<tr>", body.group(1))) - 1 if body else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--generate", type=int, default=0, help="applications to add before measuring")
    args = ap.parse_args()

    if args.generate:
        c = login("coordinator")
        c.post("/coordinator/tools/generate", {"count": str(args.generate)})
        print(f"generated ~{args.generate} applications\n")

    failures = 0
    for name, (user, path) in PAGES.items():
        sess = login(user)
        times = []
        last = ""
        for _ in range(REPEATS):
            s, last, _ = sess.get(path)
            times.append(sess.ms)
        p95 = percentile(times, 95)
        rows = rows_on_page(last)
        over = p95 > BUDGET_MS
        unbounded = rows > 20
        flag = []
        if over:
            flag.append(f"EXCEEDS {BUDGET_MS} ms (PERF-01)")
        if unbounded:
            flag.append(f"{rows} rows on one page -> not paginated (PERF-05)")
        failures += 1 if (over or unbounded) else 0
        print(f"{name:34s} p95={p95:7.1f} ms  rows/page={rows:4d}  {'; '.join(flag)}")
    print("\n" + ("FAIL: see flagged pages above." if failures else "PASS"))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
