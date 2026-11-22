# [D34] Letter-feedback scores vary by more than 10 points across runs

**Requirement violated:** AI-09

**Description:**
AI-09: outside the cache window, two evaluations of the same letter and posting return scores that differ by at most 10 points. `AiClient.TEMPERATURE = 1.3` makes the model highly non-deterministic, so repeated evaluations of the same letter vary far more than 10 points (and the cache above masks it in the UI rather than fixing it).

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. Run the AI evaluation (tests/ai-eval) with the shipped prompt at temperature 1.3, 5 runs per letter.
2. Compute the max−min score per letter.

**Expected result:** Within-letter spread ≤ 10 points.

**Actual result:** Spread exceeds 10 points for many letters at temperature 1.3.

**Severity:** Major
**Priority:** P2
**Category:** ai
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** tests/ai-eval run_eval.py + analyze.py (mean within-letter spread).
**Discovered by:** Abdulaziz Debs
**Technique that found it:** Metamorphic testing (repeated runs)
