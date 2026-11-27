# Automated tests

Five suites at four levels (unit, integration, component/black-box, system) plus non-functional tests.
Every test names the requirement and the designed test case it implements (see `docs/test-cases.md`).

Tests whose name ends in `_DEFECT` (Python) or whose Javadoc names an issue (JUnit, `qa/`) assert the
**specified** behaviour, so they **fail on the vendor build**: each failure is the evidence for a GitHub
issue, and the test will pass once the vendor fixes that defect. A red run is therefore the expected result.

| Suite | Level | Tool | What it covers | Command |
|---|---|---|---|---|
| `portal/src/test/.../qa/` | Unit + integration, **white-box** | JUnit 5, Spring Test, MockMvc | Portal services, state machine, access control, CSRF, the real AI prompt, Engine outage | `cd portal` then `.\mvnw.cmd test` (macOS/Linux `./mvnw test`) |
| `tests/api` | Component, **black-box** | Python 3 `unittest` | Engine REST contract (`engine/openapi.yaml`) | `python tests/run_all.py api` |
| `tests/performance` | Non-functional | Python 3 | Engine ranking latency (PERF-02); list pages and pagination (PERF-01, PERF-05) | `python tests/run_all.py rank` / `pages` |
| `tests/system` | System | Python 3 | Portal defects reproduced over HTTP as each role; last-seat race | `python tests/run_all.py system` / `race` |
| `tests/ai-eval` | AI properties + experiment | Python 3 | Prompt privacy and format (model-free); repeated runs on the 20 ai-eval letters | `python tests/run_all.py ai`; experiment below |

Only a JDK 17+ (for the Portal suite) and Python 3.8+ are needed; the Python suites use only the standard
library. On macOS/Linux write `python3` where this page says `python`.

## How to run

1. Start the system on fresh data: Windows `.\start.cmd --reset`, macOS/Linux `./start.sh --reset`
   (Engine on 8081, Portal on 8080).
2. From the repository folder:

```powershell
python tests/run_all.py                   # api, rank, ai: these never change any data
python tests/run_all.py system race       # these CHANGE data: run them once, right after --reset
python tests/run_all.py pages             # adds 1,000 applications, then measures the list pages
python tests/run_all.py api rank --save   # --save also writes docs/results/<suite>.txt (dated, with your name)
```

3. The Portal white-box suite (needs the JDK; the first run downloads Maven and the libraries):

```powershell
cd portal
.\mvnw.cmd test "-Dmaven.test.failure.ignore=true"   # macOS/Linux: ./mvnw test -Dmaven.test.failure.ignore=true
# results: portal/target/surefire-reports    coverage: portal/target/site/jacoco/index.html
```

If `mvnw.cmd` says `JAVA_HOME not found`, set it for the current window to your JDK folder, for example
`$env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-17.0.13.11-hotspot"`.

## Results on the vendor build (27/11/2026, Engine 1.0.0, fresh `--reset`)

| Suite | Tests | Pass | Fail = defects | Notes |
|---|---|---|---|---|
| Portal, vendor's own tests | 147 | 147 | 0 | Three of them assert buggy behaviour and are reported as defects (D45, D46, D52) |
| Portal, our `qa/` tests | 16 | 0 | 16 | `PortalDefectTest` 8, `SecurityAccessTest` 3, `AiPromptDefectTest` 3, `EngineOutageTest` 2 |
| Engine contract (`api`) | 39 | 20 | 19 | |
| Engine ranking latency (`rank`) | 1 | 0 | 1 | 150 candidates p95 0.3 s; 200 candidates p95 5.1 s (budget 0.5 s) |
| Portal list pages (`pages`) | 5 | 3 | 2 | with 1,000 extra applications: Outbox 1,121 rows and Postings 31 rows on one page; all pages render in < 0.2 s |
| System reproductions (`system`) | 12 | 0 | 12 | D05, D48, D06, D07, D27, D28, D29, D39, D47, D35, D49, D33 |
| Last-seat race (`race`) | 1 | 0 | 1 | both students accepted for one seat (D03) |
| AI prompt properties (`ai`) | 6 | 3 | 3 | the shipped prompt (v1) fails all three; our v2 passes |

**Coverage (JaCoCo, all Portal tests):** service layer 77.1% of lines and 55.4% of branches; whole Portal
61.1% of lines. The vendor's suite alone also reaches 77.1% of service lines, so MAINT-01 (at least 70%) is
met; our `qa/` tests do not add coverage — each one targets one specific defect.

`system` and `race` change the data (a password, a withdrawal, an acceptance), so a second run without
`--reset` reports some checks as `ok` or `ERROR`. That is expected; run them right after a reset.

## AI Assistant experiment (needs a free AI key; never commit it)

The criterion for adopting the improved prompt v2 was fixed before any run (top of `ai-eval/analyze.py`).
A free **Groq** key (console.groq.com -> API Keys) is enough for 20 letters x 3 runs x 2 prompts:

```powershell
Remove-Item tests/ai-eval/raw -Recurse -ErrorAction SilentlyContinue    # start from a clean folder
$env:AI_API_KEY  = "paste-your-key-here"
$env:AI_BASE_URL = "https://api.groq.com/openai/v1"
$env:AI_MODEL    = "llama-3.1-8b-instant"       # high free limits; a larger model may hit the daily token cap
python tests/ai-eval/run_eval.py --prompt v1 --runs 3 --sleep 3
python tests/ai-eval/run_eval.py --prompt v2 --runs 3 --sleep 3
python tests/ai-eval/analyze.py --save          # prints the table and writes docs/results/ai-experiment.txt
```

If many lines say `ERROR`, the key, the base URL or the model name is wrong (or the rate limit was hit):
fix it, clear the `raw` folder and run again. OpenRouter also works (`https://openrouter.ai/api/v1`, a model
ending in `:free`), but its free tier allows only about 50 requests a day. Raw answers stay in
`tests/ai-eval/raw/` (ignored by Git); only the summary is committed.
`python tests/ai-eval/run_eval.py --prompt v2 --runs 3 --simulate` checks the harness offline (not a model).
