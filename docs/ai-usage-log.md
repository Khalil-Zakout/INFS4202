# AI usage log

One entry per meaningful use, written on the day. We used an AI assistant heavily, as a tool: to read the
code and the Requirements quickly, to propose hypotheses and boundary values, to write test harnesses and to
draft documents. The rule we followed: **nothing the AI said counted until we reproduced it on the running
system or saw a test fail for the right reason**, with the Requirements and `openapi.yaml` as the oracle.
No API key was ever committed; the AI-eval runner reads it from an environment variable.

Each member adds their own rows for their own use of AI (date, what for, what was kept, changed, rejected).

| Date | Member | Tool and model | Purpose | Prompt summary | Kept | Modified (how) | Rejected (why) |
|------|--------|----------------|---------|----------------|------|----------------|----------------|
| 22/11 | Khalil | Claude (Anthropic) | Understand the system | "Read the Requirements, the OpenAPI contract and the Portal source; build a model of the components, the flows per role and every Portal-to-Engine call" | The component/flow model used in report Q1 and in the strategy | Each Portal-to-Engine call checked against `EngineClient` and `EngineRequestMapper` | — |
| 22/11 | Khalil | Claude | Risk-based strategy | "Rank the modules by impact and likelihood of failure; propose levels, techniques and tools that fit" | Risk table, three primary modules, four levels | Security promoted to a primary module after the first probes (see the strategy's change log) | — |
| 22/11 | Khalil | Claude | Boundary values for the Engine | "List the boundaries of every Engine rule in the contract: GPA, credits, file sizes, 180-day transcript, 15-120 min, 08:00-18:00, allowance months, caps and penalty weeks" | The boundary list behind `tests/api` | Exact byte limits (2,097,152 and 5,242,880) taken from `openapi.yaml`, not from the AI | Suggestions for fields the contract does not define |
| 22/11 | Khalil | Claude | Write the Engine contract suite | "Zero-dependency Python unittest cases asserting the contract; oracle = the specification, never the observed output" | `tests/api/test_engine_contract.py` | Every expected value re-derived from the Requirements; cases that fail named `_DEFECT` | — |
| 22/11 | Khalil | Claude | Find defects by reading the Portal code | "For each service method, which requirement could it violate? Give the exact line and a way to reproduce it" | Hypotheses behind D01-D04, D21-D26, D47 | Each one reproduced on a fresh `--reset` before an issue was written | Several "defects" the code already prevents, e.g. SQL injection in the search (queries are parameterised) and weak password storage (BCrypt is used): no issue filed, since an invalid report costs a point |
| 22/11 | Khalil | Claude | Security probes | "Which forced-browsing, CSRF, session, secret and XSS checks apply to USR-01..05 and SEC-01..07?" | Checklist behind `tests/system/reproduce.py` and D05-D07, D27-D31, D48 | Ran every check as each role on the running system | — |
| 22/11 | Khalil | Claude | Concurrency test for the last seat | "Two requests accepting the last seat at the same moment, with the session and CSRF handling of this Portal" | `tests/system/seat_race.py` | Added up to six attempts and a clear verdict line | — |
| 22/11 | Khalil | Claude | AI Assistant test design | "Which properties must hold for letter feedback whatever the model (AI-01, 03, 04, 06, 09, 10, 11)? Design an experiment with a criterion fixed before the runs" | `tests/ai-eval` (property tests, runner, analysis with a pre-registered criterion) | Criterion written into `analyze.py` before any run | An improved prompt that added a scoring rubric with thresholds: it would break AI-10 again |
| 22/11 | Khalil | Claude | Defect report wording | "Turn these reproduced findings into issues using our template; steps must work from a fresh --reset" | The 48 issue bodies in `docs/issues/` | Steps re-run as written; severity and priority set by us | — |
| 22/11 | Khalil | Claude | Report and slides wording | "Tighten these sections; every number must match the repository and the issues" | Report and slide text | Numbers re-checked against the issue list and the test output | Any claim we had not reproduced |
| 27/11 | Khalil | Claude | Review the project against the rubric and template | "Compare the repository, issues and report with the Instructions, Rubric and Submission Template; list what is wrong or missing" | Found: D06 steps relied on a log file the Portal does not write; three AI defects tested only on a copy of the prompt; a failing designed case (TC-ENG-004) with no issue; `/coordinator/reports` open to every role; Windows problems in two scripts | Each finding checked on the running system and by a failing test before it changed anything | — |
| 27/11 | Khalil | Claude | New tests and defects | "Write JUnit tests that call the real PromptBuilder; test the Coordinator reports as a recruiter; test the month-end allowance" | `AiPromptDefectTest`, `SecurityAccessTest.recruiterCannotOpenCoordinatorReports`, `TC_ENG_ALLOW_08`; issues D49, D50 | D50 kept Minor: the Portal itself refuses an out-of-range GPA | — |

## Reflection

**Where AI helped.** Speed and breadth. It read a code base we did not write in minutes and turned each
requirement into concrete hypotheses with the exact line to look at; it enumerated boundaries for every Engine
rule; and it wrote the first version of every harness, which we then corrected. It also helped as a reviewer
of our own work: a review on 27/11 against the rubric found a reproducibility problem in D06 and two
defects we had missed (D49, D50).

**Where AI was wrong or risky.** It proposed defects that do not exist (SQL injection, password storage) —
filing them would have cost us points — and its first drafts sometimes encoded the system's observed output
as the expected result, which would make a test pass on a bug. It also wrote steps that worked only in our
environment (a log file the Portal does not create). Our safeguard was the same every time: reproduce it on a
fresh start, or see a test fail for the stated reason, before it goes into an issue or the report.

**What we learned about the system's AI Assistant.** See the report, section *Use of AI*: the prompt sends
personal data, discloses an internal threshold and contains a malformed example (proved on the real
`PromptBuilder`), the feedback cache ignores the letter, and the measured run-to-run spread is reported in
`docs/results/ai-experiment.txt` and on issue D34.
