# [D16] Ranking 200 candidates takes about 5 seconds (budget 500 ms)

**Requirement violated:** PERF-02

**Description:**
PERF-02: the Engine ranks 200 candidates in at most 500 ms at p95. Measured p95 for 200 candidates is about 4.9 s, and the time is grossly non-linear in the candidate count, pointing to an accidentally quadratic sort.

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. Run tests/performance/engine_rank_latency.py against the Engine.

**Expected result:** p95 ≤ 500 ms at 200 candidates.

**Actual result:** p95 ≈ 4,900 ms at 200 candidates (10→50→100→150→200 is non-monotonic).

**Severity:** Major
**Priority:** P2
**Category:** performance
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** perf:engine_rank_latency.py output.
**Discovered by:** Monir Skaik
**Technique that found it:** Performance testing
