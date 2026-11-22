# Automated tests

Four suites at three levels. Every test names the requirement and the designed
test case it implements (see `docs/test-cases.md`). Tests whose name ends in
`_DEFECT` (Python) or whose Javadoc cites an issue (JUnit) assert the **specified**
behaviour and therefore **fail on the vendor build**: each failure is the evidence
for a GitHub issue and is expected to pass once the defect is fixed. The counts
below are what you see on the vendor build delivered to us.

| Folder | Level | Tool | What it covers | One command |
| --- | --- | --- | --- | --- |
| `portal/src/test` (`qa/`) | Unit + integration (white-box) | JUnit 5, Spring Test, Mockito | Portal services, state machine, access control, CSRF | `cd portal && ./mvnw test` |
| `tests/api` | Component (black-box) | Python 3 `unittest` | Engine REST contract (`openapi.yaml`) | `cd tests/api && python3 -m unittest -v` |
| `tests/performance` | Non-functional | Python 3 | Engine rank latency (PERF-02), Portal list pages (PERF-01/05) | `cd tests/performance && python3 engine_rank_latency.py` |
| `tests/ai-eval` | AI property + experiment | Python 3 | Prompt privacy/format (AI-03/10/11), 20-letter evaluation (AI-01/04/06/09) | `cd tests/ai-eval && python3 -m unittest -v test_prompt_properties.py` |

Nothing but a JDK 17+ and Python 3.8+ is needed; the Python suites use only the
standard library. **Start the system first** (`./start.sh`) so the Engine (8081)
and Portal (8080) are up; set `ENGINE_URL` / the Portal base if you moved them.

## One command for the lot

```bash
tests/run_all.sh
```

runs the three Python suites and prints a pass/fail summary. The Portal JUnit
suite is run separately with Maven (it needs the dependency download):

```bash
cd portal && ./mvnw test            # Windows: .\mvnw.cmd test
# coverage even when defect tests fail:
cd portal && ./mvnw test -Dmaven.test.failure.ignore=true
# report: portal/target/surefire-reports   coverage: portal/target/site/jacoco/index.html
```

## Expected results on the vendor build (2026-11-22, Engine 1.0.0)

| Suite | Tests | Pass | Fail (= defects) |
| --- | --- | --- | --- |
| `tests/api` Engine contract | 38 | 20 | 18 |
| `tests/performance` rank latency | 1 | 0 | 1 (200 candidates p95 ≈ 4.9 s) |
| `tests/performance` portal pages | 5 checks | 3 | 2 (Outbox & Postings unpaginated) |
| `tests/ai-eval` prompt properties | 6 | 3 | 3 (v1 leaks data/threshold/example) |
| `portal` `qa/PortalDefectTest` | 8 | 0 | 8 |
| `portal` `qa/SecurityAccessTest` | 2 | 0 | 2 |

The vendor's own suite (`portal/src/test/**` outside `qa/`) passes, **except**
that two of its tests encode defects (they assert the buggy behaviour) and are
themselves reported as issues — see the `tests` category in `docs/test-cases.md`.

## AI Assistant experiment (optional, needs a model key)

Never commit a key; the runner reads it from the environment.

```bash
cd tests/ai-eval
export AI_API_KEY=sk-...                 # OpenRouter / OpenAI / Azure key
export AI_MODEL='meta-llama/llama-3.3-70b-instruct:free'
python3 run_eval.py --prompt v1 --runs 5 --sleep 1
python3 run_eval.py --prompt v2 --runs 5 --sleep 1
python3 analyze.py 'raw/*.jsonl'         # prints the metrics and the adopt/keep decision
```

The decision criterion was fixed before any run (see the top of `analyze.py`).
Run `python3 run_eval.py --prompt v2 --runs 5 --simulate` to exercise the harness
offline without a key (the stand-in is not a model and is for self-check only).
