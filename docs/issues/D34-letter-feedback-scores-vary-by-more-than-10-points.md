# [D34] Letter-feedback scores vary by more than 10 points across runs

**Requirement violated:** AI-09

**Description:**
AI-09: outside the cache window, two evaluations of the same letter and posting return scores that differ by at most 10 points. The provider is called with `AiClient.TEMPERATURE = 1.3`, a very high sampling temperature, so repeated evaluations of the same letter are expected to vary widely. The measurement over repeated runs is attached as a comment on this issue.

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. Get a free AI key and set it as described in tests/README.md, section "AI Assistant experiment" (key, base URL and model in environment variables).
2. Run the shipped prompt (v1, temperature 1.3) over the 20 ai-eval letters, 3 runs each: `python tests/ai-eval/run_eval.py --prompt v1 --runs 3 --sleep 3`.
3. Run `python tests/ai-eval/analyze.py` and read the "spread" column: the mean over the letters of (highest score - lowest score) across the runs.

**Expected result:** Within-letter spread ≤ 10 points.

**Actual result:** See the measurement comment: per-letter score spread above 10 points for the shipped prompt.

**Severity:** Major
**Priority:** P2
**Category:** ai
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** tests/ai-eval/run_eval.py + analyze.py output, posted as a comment with model name, date and number of runs. Source: AiClient line 24 `TEMPERATURE = 1.3`.
**Discovered by:** Abdulaziz Debs
**Technique that found it:** Metamorphic testing (repeated runs)
