# UniPlace — Test strategy

Team: **UniPlace QA Team** · INFS4202 Software Testing & Quality Assurance, Fall 2026
Members: Khalil Zakout (60314057), Monir Skaik (60314058), Abdulaziz Debs (60309913)
Presented at M1 (Week 13) and kept up to date. Change log at the end.

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
- `main` is protected and always builds; the vendor's *Initial import* is the
  baseline and is never rewritten.
- One **branch per work item**, named `area/short-description`
  (e.g. `offers/seat-race`, `engine/rank-order`).
- **Pull requests** reviewed by one other member before merge; the review checks
  that each new test names its requirement and designed case, and that any
  reported defect has a reproduction.
- **Conventions:** test case IDs `TC-<MODULE>-NNN`; issues use the template and
  carry one category + one severity + one priority label and the discoverer as
  assignee; commits reference the issue (`#12`) they relate to.
- **CI:** the *Tests* workflow runs on every push; our defect-reproduction tests
  are expected to fail until the vendor fixes them — the failing count is tracked
  in `tests/README.md` and the final report, so the numbers match.
- **Secrets:** API keys are read from environment variables only; `.gitignore`
  keeps `bin/`, `portal/data/`, logs and `*.env` out of the repository.

## 7. Change log

| Date | Change | Why |
|------|--------|-----|
| [Week 13] | Initial strategy presented at M1. | — |
| [Week 13] | Added a concurrency level after reading `OfferService.accept` (no lock around the seat check). | Code review showed a likely OFF-04 race; a single-thread suite would miss it. |
| [Week 14] | Promoted "Users, Access & Security" to a primary module (was secondary). | Early probing found server-side authorization gaps (IDOR) and secret exposure — higher impact than first judged. |
| [Week 14] | Added model-free AI prompt-property tests and a pre-registered prompt experiment. | We could not rely on a model being available in CI; the privacy/format defects are provable without one. |
