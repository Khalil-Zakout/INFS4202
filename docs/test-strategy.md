# UniPlace — Test strategy

Team: **UniPlace QA Team** · INFS4202 Software Testing & Quality Assurance, Fall 2026
Members: Khalil Zakout (60314057), Monir Skaik (60314058), Abdulaziz Debs (60309913)
Kept up to date during the project; every change is dated in the change log at the end.

---

## 1. Mission and scope

We are the QA team hired to assess **UniPlace**, a vendor-delivered internship
portal, against the Requirements it was contracted to. Our goal is to find and
report as many **real, reproducible** defects as possible, weighted by severity,
and to do it through a process we can show and justify.

**In scope**
- The **Portal** (Part A) — white-box: Java 17 / Spring Boot source and its test suite.
- The **Engine** (Part B) — black-box: the REST service behind `openapi.yaml`, tested through its API and through the Portal.
- The **integration** between them (eligibility, match, rank, slot validation, allowance).
- The **AI Assistant** (letter feedback and interview questions) and its prompt.
- Non-functional behaviour named in the Requirements: performance, security, reliability, usability.

**Out of scope**
- The AI model provider's internal behaviour (we test how the Portal uses it, and the properties that must hold regardless of model).
- Email delivery infrastructure (we check that notifications are recorded and that failures never block the business operation).
- Browser/OS compatibility beyond a sanity check on current Chrome and Firefox.

## 2. Risk analysis (what drives the plan)

We rank areas by **impact × likelihood**. Effort follows the top of this list.

| # | Area | Why it is risky | Impact | Priority |
|---|------|-----------------|--------|----------|
| R1 | Offer/seat lifecycle & concurrency (APP-06, OFF-03/04) | Money and placements; race conditions; state machine edges | Data/placement loss | **Highest** |
| R2 | Access control & secrets (USR-05, SEC-01/03/04/05, AI-03) | Cross-tenant data exposure, secret leakage, PII to third parties | Security breach | **Highest** |
| R3 | Engine scoring/compliance (match, rank, eligibility, allowance) | Pure logic with many boundaries; drives shortlisting, ranking, pay | Wrong decisions/pay | **High** |
| R4 | Portal↔Engine integration (REL-01/02) | Degradation paths, caching, error mapping | Silent wrong results | **High** |
| R5 | Eligibility & application rules (STU, APP-01/02) | Boundaries (GPA, credits, transcript validity, limits) | Unfair refusal/admission | **High** |
| R6 | Interview scheduling (INT-02/03) | Time zones, overlaps, working-hour edges | Invalid interviews | Medium |
| R7 | AI Assistant quality & safety (AI-04/06/08/09) | Prompt injection, PII, variance, caching | Trust/safety | Medium |
| R8 | Performance & pagination (PERF-01/02/05) | Volume data, unbounded lists, slow ranking | Unusable at scale | Medium |
| R9 | Usability & validation messages (USA-01/02/06) | Lost input, unclear errors, date formats | Friction | Low |

## 3. Primary modules (the three we cover in full)

Chosen because they concentrate the highest-risk logic and because each exercises
a different technique mix (R1–R5). The test design goes beyond them, but these
three carry the required ≥10 designed test cases each (`docs/test-cases.md`).

1. **Applications & Offers** (APP-01…APP-10, OFF-01…OFF-07) — the core workflow,
   the state machine, the seat/concurrency rules, and the allowance integration.
2. **Matching & Compliance Engine** (eligibility, match, rank, schedule, allowance) —
   the black-box compliance brain, tested against `openapi.yaml`.
3. **Users, Access & Security** (USR-01…USR-05, SEC-01…SEC-07) — authentication,
   server-side authorization, CSRF, secret handling, output escaping.

Secondary coverage: Postings (POS), Companies (COM), Interviews (INT),
AI Assistant (AI), Settings/Reports (ADM), Notifications (NOT).

## 4. Test levels, techniques and tools — and why

**Levels.** We test at four levels so a defect is caught as close to its cause as
possible: unit (Portal services, state machine, formatting), component/black-box
(Engine API), integration (Portal driving the Engine; MockMvc/HTTP through the
Portal), and system/end-to-end (a scripted HTTP client exercising full flows on
the running Portal).

**Techniques** (course material, matched to the target):
- *Equivalence partitioning & boundary value analysis* — Engine numeric domains
  (GPA 0–4, credits 0–140, sizes 2/5 MB, transcript 180 days, interview 15–120
  min and 08:00–18:00, allowance months/caps/penalty weeks). Boundaries are where
  this system breaks.
- *Decision tables* — eligibility (several independent rules combine), allowance
  (base/transport/cap/penalty), match score (required × nice-to-have).
- *State-transition testing* — the application state machine (APP-06) and offer
  status, including illegal transitions attempted via direct URL/API.
- *Control-flow / white-box* — read the service code, target branches and the
  oracles the vendor's own tests miss; measure line coverage with JaCoCo.
- *Security testing* — IDOR/forced-browsing, CSRF, session invalidation, secret
  exposure in logs/HTML, stored XSS, stack-trace leakage, prompt-data leakage.
- *Concurrency testing* — parallel acceptance of the last seat (OFF-04).
- *Metamorphic / property testing* for the AI Assistant — properties that must
  hold across runs (structure valid, score within band, injection ignored, PII
  not echoed, variance ≤ 10) rather than one golden output.
- *Performance testing* — latency percentiles for Engine ranking and Portal list
  pages under seed + volume data.

**Tools and why.**
- **JUnit 5 + Spring Boot Test + Mockito + WireMock** — already the Portal's test
  stack; white-box unit/integration with a mockable Engine. JaCoCo for coverage.
- **Python 3 standard library (`unittest`, `urllib`)** — zero-dependency, portable
  black-box tests for the Engine and end-to-end HTTP flows; runs on any lab
  machine and in CI without downloads. Chosen over Postman/newman so the whole
  suite runs with one command and lives in Git as plain text.
- **A small Python HTTP client** for system tests (cookie session, CSRF-aware
  form posts) and for the concurrency and performance scripts.
- **GitHub Issues + Actions** — defect tracking with the required labels; the
  *Tests* workflow runs the Portal suite on every push.
- **AI tools (ChatGPT / Claude)** — to speed up test-data generation, boundary
  enumeration and documentation; every kept artefact is logged and every defect
  is reproduced by hand (`docs/ai-usage-log.md`).

**Oracles.** The Requirements document and `engine/openapi.yaml` are the oracle —
never the system's own output. A test that disagrees with the system is a defect
in the system, not the test. For the AI Assistant, the oracle is the set of
properties plus the reference bands in `ai-eval/`.

## 5. Entry / exit criteria

- *Entry*: system starts from a clean `--reset`; Engine health is UP; the vendor
  suite builds.
- *Exit (per our plan)*: ≥10 reported defects with full evidence (we target
  substantially more, across all categories including the specification and the
  shipped tests); the three primary modules each have ≥10 designed cases traced
  to requirements; automated suites run from the repo with the documented
  commands; every reported defect reproduced on a fresh `--reset`.

## 6. Team organisation and Git workflow

**Roles** (each member owns a risk area end-to-end — design, automate, report,
present — so R10 is traceable):
- **Khalil Zakout — Applications & Offers, and the remaining Portal rules (R1):**
  the application/offer state machine, seats and concurrency, the allowance
  integration, plus standing, company naming, uploads and the UI defects.
- **Monir Skaik — Engine, integration and performance (R3, R4):** the API contract
  suite, eligibility/match/rank/schedule/allowance logic, degradation paths, the
  ranking and list-page performance tests, and the specification defects.
- **Abdulaziz Debs — Security, access control and the AI assistant (R2):** access
  control, CSRF, sessions, secrets, XSS, error leakage, and the AI prompt privacy,
  property tests and prompt experiment.

**Git workflow.**
- `main` holds the vendor's *Initial import* as the untouched baseline; nothing is ever force-pushed or
  rewritten. From 27/11/2026 `main` is protected on GitHub (Settings -> Branches): a change needs a pull
  request with one approval from another member.
- **Phase 1 (until 22/11/2026):** the first version of each owner's work was imported into `main` as one
  commit per owner, in the owner's name, pushed together from Khalil's machine (Khalil: strategy, test
  cases, Applications & Offers white-box tests; Monir: Engine contract and performance suites; Abdulaziz:
  security, system and AI-evaluation tests). A stray invisible character in those three author e-mails
  means GitHub does not link them to the accounts; every later commit, pull request and issue is linked.
- **Phase 2 (from 27/11/2026):** every change goes through a **branch and a pull request reviewed and approved
  by another member** before merge, named `area/short-description` (e.g. `results/engine`,
  `results/security-ai`, `docs/final-report`). The review checks that each new test names its requirement and
  designed case, and that each reported defect has a reproduction. See the change log for why we switched.
- **Conventions:** test case IDs `TC-<MODULE>-NNN`; every defect is one GitHub issue that uses the
  template, carries one category + one severity + one priority label, starts its title with a stable code
  (`[D01] ...`) used in the test cases and the report, and is filed by and assigned to the member who
  discovered it (`scripts/file_issues.py`, run by each member from their own account).
- **CI:** the *Tests* workflow runs the Portal suite on every push. Our defect-reproduction tests are
  expected to fail until the vendor fixes the defects, so a red run is the expected state; the failing
  count is tracked in `tests/README.md` and the final report so the numbers match.
- **Results:** each owner runs their suites with `python tests/run_all.py <suites> --save` and commits the
  dated output under `docs/results/` through a pull request.
- **Secrets:** API keys are read from environment variables only; `.gitignore` keeps `bin/`, `portal/data/`,
  logs, `*.env` and raw AI answers out of the repository.

## 7. Change log

| Date | Change | Why |
|------|--------|-----|
| 22/11/2026 | First version of this strategy: risk-based plan, three primary modules, four test levels. | Starting point after exploring the system and reading the Requirements and the code. |
| 22/11/2026 | Added a concurrency check after reading `OfferService.accept` (seat check and save without a lock). | Code review showed a likely OFF-04 race that single-threaded tests would never hit; `seat_race.py` then reproduced D03. |
| 22/11/2026 | Promoted "Users, Access & Security" to a primary module (it was a secondary one). | The first forced-browsing probes found server-side authorization gaps (D05, D48) and secrets in clear text (D06): higher impact than first judged. |
| 22/11/2026 | Added model-free AI prompt-property tests and a pre-registered prompt experiment. | A model key is not available in CI; the privacy and format defects can be proved without a model. |
| 27/11/2026 | Git workflow: from now on every change goes through a branch and a pull request approved by another member (Phase 2 above). | In Phase 1 the suites went straight to `main` from one machine and reviews were informal, which left no record in the repository; `main` is now protected so the rule is enforced, not just agreed. |
| 27/11/2026 | Added white-box JUnit tests that call the real `PromptBuilder` (`AiPromptDefectTest`). | The Python prompt-property tests check a copy of the shipped prompt; testing the real class is stronger evidence for D08, D32 and D42. |
| 27/11/2026 | Swept every Coordinator URL with other roles; added D49 (reports open to all) and D50 (Engine accepts an out-of-range GPA). | Re-reading `SecurityConfig` showed `/coordinator/reports` missing from the Coordinator-only rule; a designed case (TC-ENG-004) had failed without an issue. |
| 27/11/2026 | Made every suite runnable on Windows with one command (`tests/run_all.py`), and made D06/D33 reproducible without a log file or an AI key. | All three members work on Windows; a grader must be able to reproduce each issue from its text alone. |
