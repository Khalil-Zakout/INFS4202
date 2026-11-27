# UniPlace Acceptance Testing — Final Report

| Field | Value |
|------|------------------------------|
| Course | INFS4202 Software Testing & Quality Assurance, Fall 2026 |
| Project | UniPlace acceptance testing |
| Team name | UniPlace QA Team |
| Members | Khalil Zakout (60314057); Monir Skaik (60314058); Abdulaziz Debs (60309913) |
| Repository | https://github.com/Khalil-Zakout/INFS4202 (public; instructor `vanilson` added as collaborator) |
| Final tag and date | `final`, __/__/2026 |
| Primary modules | 1. Applications & Offers (APP, OFF) · 2. Matching & Compliance Engine (eligibility, match, rank, schedule, allowance) · 3. Users, Access & Security (USR, SEC) |
| Declaration | We declare that this work is our own, that every AI-assisted part is recorded in our AI usage log, and that every reported defect was reproduced by us on the running system. |

**Summary.** We found **52 valid, reproducible defects** — 12 critical, 28 major and
12 minor (severity-weighted 104) — across all ten categories, including two defects in the
specification and three in the vendor's own test suite. They are backed by 67 designed test cases and by
automated tests at four levels that run from the repository with one command each.

## Q1. How did we understand the system? [R1]

**Our model.** UniPlace has two parts. The **Portal** (Java 17, Spring Boot 3, Thymeleaf, H2) holds the screens,
the data and the business rules for three roles: **students** keep a profile and documents and apply to
postings; **recruiters** register their company, publish postings, shortlist, interview and make offers; the
**coordinator** approves companies, manages users, settings and reports. For every *compliance* decision the
Portal calls the **Engine**, a separate REST service delivered only as a program with an OpenAPI contract:
eligibility (`/eligibility`), the match score (`/match`), the ranking of candidates (`/rank`), interview slots
(`/schedule/validate`) and the monthly allowance (`/allowance`). A third component, the **AI Assistant**,
sends the student's motivation letter to an external language model and shows a score with strengths, gaps
and improvements; without a key a built-in simulated assistant answers.

**Main flows.** Apply (Portal → `/eligibility` → `/match` → application SUBMITTED with a stored score) →
shortlist (score against the threshold in Settings) → rank (`/rank`) → interview (`/schedule/validate`) →
offer with a response deadline → accept (seat taken; when the last seat is taken the posting becomes FILLED
and the other applications must be rejected) → allowance statement (`/allowance`). The application follows a
state machine (SUBMITTED, SHORTLISTED, INTERVIEW, OFFERED, ACCEPTED / REJECTED / WITHDRAWN).

**What we inferred about the Engine.** From `openapi.yaml` and from its answers to boundary probes we learned
its rules and its weak spots: inclusive limits implemented as exclusive ones (GPA equal to the minimum, day 180
of the transcript, exactly 30 weekly hours, exactly 120 minutes), formulas that ignore part of the input (the
cap ignores the transport supplement), invalid input answered with 200 or 500 instead of 400, and a ranking
whose time grows super-linearly with the number of candidates.

**How we built this understanding.** (1) We explored the running system in every role with the seeded
accounts; (2) we read the Requirements as testers and turned each rule into a checkable statement with its
boundaries; (3) we reverse-engineered the Portal code — `SecurityConfig`, the services, `EngineClient` and the
caches — to see how each rule is really implemented; (4) we probed the Engine's API directly. The code reading
drove our test choices: for example `OfferService.accept` checks the free seats and saves without a lock, which
is why we added a concurrency test, and `SecurityConfig` lists the Coordinator URLs one by one, which is why we
tried every Coordinator URL as the other roles.

## Q2. What process did we define, and did we follow it? [R1]

The full strategy, with its dated change log, is in `docs/test-strategy.md`.

**Risks and scope.** We ranked areas by impact x likelihood: the offer/seat lifecycle and concurrency, access
control and secrets, and the Engine's compliance logic came first; then Portal-Engine integration, eligibility
rules, scheduling, the AI Assistant, performance and usability. The three highest-risk areas became our primary
modules. Out of scope: PERF-03 (50 concurrent users for 5 minutes) and browser compatibility (COMP-01).

**Levels, techniques and tools.** Unit and integration tests of the Portal (white-box, JUnit 5, Spring Test,
MockMvc, WireMock for the Engine); component tests of the Engine through its API (black-box, Python
`unittest`, oracle = the contract); system tests over HTTP as each role (Python); non-functional tests for
response time and pagination; and model-free property tests plus a repeated-run experiment for the AI. We chose
Python's standard library for everything outside the Portal so that every member and the grader can run it
without installing anything, and techniques by the kind of rule: boundary-value analysis and equivalence
partitioning for numeric rules, decision tables for combined conditions, state-transition testing for the
application/offer workflow, forced browsing and CSRF checks for access control, fault injection for the
Engine-down path, concurrency testing for the last seat, and metamorphic testing for the AI.

**Roles.** Each member owned one risk area end to end — design, automation, reporting, presentation:
Khalil Zakout — Applications & Offers and the remaining Portal rules; Monir Skaik — the Engine, Portal-Engine
integration and performance; Abdulaziz Debs — security and access control, and the AI Assistant.

**Git workflow, templates and conventions.** The vendor's *Initial import* is the untouched baseline. In the
first phase each owner's work was imported into `main` as one commit in the owner's name, pushed together
from one machine (a stray invisible character in those three author e-mails stops GitHub linking them to the
accounts; every later commit, pull request and issue is linked); `main` is now protected and, from
27/11 every change goes through a branch and a pull request approved by another member (the change log explains
why: informal reviews left no record). Every defect is a GitHub issue that uses the issue template, has one
category, one severity and one priority label, starts its title with a stable code (`[D01] ...`) used in the
test cases and this report, and is filed by and assigned to the member who discovered it. Test case IDs follow
`TC-<MODULE>-NNN`; failing reproduction tests are named `_DEFECT` (Python) or name their issue in the Javadoc
(JUnit). The *Tests* workflow runs the Portal suite on every push; it is red on purpose (see Q3).

**What we changed along the way.** We added a concurrency level after reading `OfferService.accept`; promoted
Users, Access & Security to a primary module once the first probes exposed authorization gaps; added model-free
AI tests because no model is available in CI; switched to pull requests with review; moved our AI tests from a
copy of the prompt to the real `PromptBuilder`; and, after a review against the rubric, swept every Coordinator
URL with the other roles and injected an Engine outage — which found D49 and D51. Each change is dated in the
strategy.

## Q3. How did we design and run our tests? [R2, R3]

**Primary modules and why.** They concentrate the highest risks and each needs a different technique mix: the
stateful core workflow (Applications & Offers), the black-box compliance logic (the Engine) and the
cross-cutting security rules (Users, Access & Security). The test design goes beyond them (companies,
students, postings, interviews, AI, reports, the specification and the vendor's tests).

| Module | Test cases | Black-box | White-box | Functional | Non-functional |
|--------------------|------|------|------|------|----------|
| Applications & Offers | 17 | 12 | 5 | 14 | 3 (PERF-01, REL-01) |
| Matching & Compliance Engine | 18 | 18 | 0 * | 16 | 2 (PERF-02, REL-02) |
| Users, Access & Security | 13 | 12 | 1 | 5 | 8 (SEC) |
| Other modules | 19 | 17 | 2 | 15 | 4 |
| **Total** | **67** | **59** | **8** | **50** | **17** |

\* The Engine was delivered only as a program, so it can be tested black-box only; its integration with the
Portal is covered white-box (`EngineOutageTest`, the match-score cache). Every case is traced to a requirement
and, where it fails, to its issue (`docs/test-cases.md`); all 52 defects trace to at least one case.

**Automated tests by level** (commands in `tests/README.md`; results on the vendor build, 27/11/2026, fresh
`--reset`). A failing test asserts the behaviour the Requirements demand, so it fails on the buggy build and is
the evidence for one issue; it will pass once that defect is fixed. Results files are committed in
`docs/results/`.

| Suite | Level | Tool | Tests | Passed | Failed | Notes |
|------------|----------|---------|------|------|------|---------------------|
| Portal, vendor's own tests | Unit, integration | JUnit 5 | 147 | 147 | 0 | 2 of them assert buggy behaviour (D45, D46) and 1 asserts D51 (D52) |
| Portal, our `qa/` tests | Unit, integration (white-box) | JUnit 5, MockMvc, WireMock | 16 | 0 | 16 | PortalDefectTest 8, SecurityAccessTest 3, AiPromptDefectTest 3, EngineOutageTest 2 |
| Engine contract | Component (black-box) | Python unittest | 39 | 20 | 19 | `python tests/run_all.py api` |
| Engine ranking latency | Non-functional | Python | 1 | 0 | 1 | 200 candidates: p95 5.1 s, budget 0.5 s (D16) |
| Portal list pages | Non-functional | Python | 5 | 3 | 2 | +1,000 applications: all pages < 0.2 s; Outbox and Postings unpaginated (D35) |
| System reproductions | System | Python | 12 | 0 | 12 | `python tests/run_all.py system` |
| Last-seat race | System (concurrency) | Python | 1 | 0 | 1 | both students accepted for one seat (D03) |
| AI prompt properties | AI (model-free) | Python unittest | 6 | 3 | 3 | shipped prompt fails, improved prompt passes |

**Coverage.** JaCoCo, all Portal tests: service layer **77.1% of lines and 55.4% of branches**, whole Portal
61.1% of lines. The vendor's suite alone reaches the same 77.1% of service lines, so MAINT-01 (at least 70%) is
met; our 16 `qa/` tests add no coverage on purpose — each one targets a specific defect.

**CI and one-command runs.** The *Tests* workflow runs the Portal suite on every push and is red by design
(16 failing defect tests); `python tests/run_all.py` runs the Python suites on Windows, macOS and Linux.

## Q4. What did we find? [R4, R5]

**52 defects**, all reproduced on a fresh start; **0 reports closed as duplicate or invalid** at the time of
writing.


- **By severity:** Critical 12, Major 28, Minor 12 — severity-weighted 104 (3/2/1).

- **By category:** integration 15, security 11, functional 8, ai 5, state 3, tests 3, performance 2, requirements 2, ui 2, configuration 1.

- **By member:** Khalil Zakout 16 (5 critical, 6 major, 5 minor); Monir Skaik 20 (1 critical, 14 major, 5 minor); Abdulaziz Debs 16 (6 critical, 8 major, 2 minor).

**The 12 critical defects**

| Issue | Critical defect | Requirement | Found by |
|------|-------------------------------|--------|--------|
| #1 (D01) | Match score is cached per posting and shared across students | APP-04 | Khalil |
| #2 (D02) | Filling a posting does not reject its remaining active applications | OFF-03 | Khalil |
| #3 (D03) | Two students can accept offers for the last seat at the same moment | OFF-04 | Khalil |
| #4 (D04) | A suspended company's applications are not frozen | COM-02 | Khalil |
| #17 (D05) | Any authenticated user can view any application (broken access control) | USR-05 | Abdulaziz |
| #19 (D06) | API key and SMTP password are written to the log and shown in plaintext | SEC-04 | Abdulaziz |
| #20 (D07) | Stored XSS via company name on the postings list | SEC-07 | Abdulaziz |
| #21 (D08) | Student name, number and GPA are sent to the AI provider | AI-03 | Abdulaziz |
| #5 (D47) | An ACCEPTED application can be withdrawn via a direct POST | APP-08 | Khalil |
| #18 (D48) | Any recruiter can download any student's CV and transcript | USR-05 | Abdulaziz |
| #49 (D49) | Students and recruiters can open the Coordinator reports and export them as CSV | USR-05, SEC-05 | Abdulaziz |
| #51 (D51) | When the Engine is down, every student is treated as eligible and applications are accepted with match score 0 | REL-01 | Monir |

Every report in GitHub Issues has the requirement, a description, steps from a fresh `--reset`, expected and
actual results, severity, priority, category, environment, evidence (a failing test or captured output),
the discoverer and the technique. The full list (the issue title on GitHub starts with the code):

| Issue | Title | Category | Severity | Requirement | Discovered by |
|------|-----------------------------|-----------|-------|---------|----------|
| #1 (D01) | Match score is cached per posting and shared across students | integration | Critical | APP-04 | Khalil Zakout |
| #2 (D02) | Filling a posting does not reject its remaining active applications | state | Critical | OFF-03 | Khalil Zakout |
| #3 (D03) | Two students can accept offers for the last seat at the same moment | state | Critical | OFF-04 | Khalil Zakout |
| #4 (D04) | A suspended company's applications are not frozen | functional | Critical | COM-02 | Khalil Zakout |
| #17 (D05) | Any authenticated user can view any application (broken access control) | security | Critical | USR-05 | Abdulaziz Debs |
| #19 (D06) | API key and SMTP password are written to the log and shown in plaintext | security | Critical | SEC-04 | Abdulaziz Debs |
| #20 (D07) | Stored XSS via company name on the postings list | security | Critical | SEC-07 | Abdulaziz Debs |
| #21 (D08) | Student name, number and GPA are sent to the AI provider | security | Critical | AI-03 | Abdulaziz Debs |
| #5 (D47) | An ACCEPTED application can be withdrawn via a direct POST | state | Critical | APP-08 | Khalil Zakout |
| #18 (D48) | Any recruiter can download any student's CV and transcript | security | Critical | USR-05 | Abdulaziz Debs |
| #49 (D49) | Students and recruiters can open the Coordinator reports and export them as CSV | security | Critical | USR-05, SEC-05 | Abdulaziz Debs |
| #51 (D51) | When the Engine is down, every student is treated as eligible and applications are accepted with match score 0 | integration | Critical | REL-01 | Monir Skaik |
| #32 (D09) | Engine refuses eligibility when GPA exactly equals the minimum | integration | Major | POS-01 | Monir Skaik |
| #33 (D10) | Transcript valid-window is one day short (day 180 rejected) | integration | Major | STU-04 | Monir Skaik |
| #34 (D11) | Engine returns HTTP 500 to well-formed JSON | integration | Major | REL-02 | Monir Skaik |
| #35 (D12) | Match score adds the full nice-to-have weight when the list is empty | integration | Major | POS-01 | Monir Skaik |
| #36 (D13) | Match skill comparison is case- and space-sensitive | integration | Major | POS-06 | Monir Skaik |
| #37 (D14) | Candidate ranking breaks GPA ties in ascending order | integration | Major | APP-09 | Monir Skaik |
| #38 (D15) | aboveCut returns one id more than the number of seats | integration | Major | APP-09 | Monir Skaik |
| #39 (D16) | Ranking 200 candidates takes about 5 seconds (budget 500 ms) | performance | Major | PERF-02 | Monir Skaik |
| #40 (D17) | Engine accepts interviews that end after 18:00 | integration | Major | INT-02 | Monir Skaik |
| #41 (D18) | Back-to-back interviews are rejected as overlapping | integration | Major | INT-03 | Monir Skaik |
| #42 (D19) | No transport supplement at exactly 30 weekly hours | integration | Major | OFF-05 | Monir Skaik |
| #43 (D20) | Monthly cap ignores the transport supplement | integration | Major | OFF-05 | Monir Skaik |
| #6 (D21) | Withdrawn applications count against the active-application limit | functional | Major | APP-02 | Khalil Zakout |
| #7 (D22) | Probation active-application limit is never applied | functional | Major | APP-02 | Khalil Zakout |
| #8 (D23) | Offer response deadline is rounded to midnight and drops the time | functional | Major | OFF-02 | Khalil Zakout |
| #9 (D24) | Uploaded documents are lost on every restart | configuration | Major | REL-04 | Khalil Zakout |
| #10 (D25) | Academic standing is not recomputed when the Coordinator changes the GPA | functional | Major | STU-03 | Khalil Zakout |
| #11 (D26) | Company name uniqueness is case-sensitive when renaming | functional | Major | COM-03 | Khalil Zakout |
| #22 (D27) | Logging out does not invalidate the server session | security | Major | USR-04 | Abdulaziz Debs |
| #23 (D28) | Account lockout can be bypassed by varying the username case | security | Major | USR-03 | Abdulaziz Debs |
| #24 (D29) | Password change accepts a password with no digit | security | Major | USR-02 | Abdulaziz Debs |
| #25 (D30) | Error pages expose stack traces and SQL | security | Major | SEC-03 | Abdulaziz Debs |
| #26 (D31) | CSRF protection is disabled on the Settings endpoints | security | Major | SEC-02 | Abdulaziz Debs |
| #27 (D32) | The AI prompt discloses the internal shortlist threshold | ai | Major | AI-10 | Abdulaziz Debs |
| #28 (D33) | Letter-feedback cache ignores the letter content | ai | Major | AI-08 | Abdulaziz Debs |
| #29 (D34) | Letter-feedback scores vary by more than 10 points across runs | ai | Major | AI-09 | Abdulaziz Debs |
| #44 (D35) | List pages are not paginated (Outbox and Postings) | performance | Major | PERF-05 | Monir Skaik |
| #48 (D43) | Specification: public-holiday rule (INT-02) is untestable and unenforced | requirements | Major | INT-02 | Monir Skaik |
| #45 (D36) | Engine rejects an interview of exactly 120 minutes | functional | Minor | INT-02 | Monir Skaik |
| #46 (D37) | Allowance whole-month count is off at month-end start dates | integration | Minor | OFF-05 | Monir Skaik |
| #12 (D38) | Searching postings by company is not sorted by deadline | functional | Minor | POS-06 | Khalil Zakout |
| #13 (D39) | A refused application shows a generic message, not the reason | ui | Minor | USA-01 | Khalil Zakout |
| #14 (D40) | Recruiter applications list shows dates as MM/dd/yyyy | ui | Minor | USA-02 | Khalil Zakout |
| #30 (D41) | Letter feedback names the wrong model | ai | Minor | AI-07 | Abdulaziz Debs |
| #31 (D42) | The AI prompt's worked example is malformed | ai | Minor | AI-11 | Abdulaziz Debs |
| #47 (D44) | Specification: NOT-04 reminder window contradicts OFF-02 | requirements | Minor | NOT-04 | Monir Skaik |
| #15 (D45) | Vendor test encodes the wrong probation limit | tests | Minor | APP-02 | Khalil Zakout |
| #16 (D46) | Vendor test counts withdrawn applications as active | tests | Minor | APP-02 | Khalil Zakout |
| #50 (D50) | Engine accepts out-of-range GPA and an unknown standing instead of answering 400 | integration | Minor | REL-02, Requirements section 3 (Errors) | Monir Skaik |
| #52 (D52) | Vendor test asserts that an unreachable Engine means eligible | tests | Minor | REL-01 | Monir Skaik |

## Q5. Why do these defects exist, and what should change? [R6]

We grouped the defects by root cause. For each: the cause, why it got past the vendor's development and testing,
and our recommendation with its priority.

**1. Access control is listed by hand and checked in only some places (P1).** D05 (#17), D48 (#18), D49 (#49), D31 (#26), D06 (#19), D07 (#20),
D27 (#22), D28 (#23), D29 (#24), D30 (#25). *Cause:* `SecurityConfig` protects Coordinator URLs one by one (`/coordinator/reports` was
forgotten); the record-level check (`AccessGuard`) exists but is not called on every read; CSRF is switched off for
Settings; secrets are logged and rendered; output is not escaped everywhere; logout only deletes the cookie.
*Why it got past:* the vendor's `SecurityTest` checks a few role-to-URL pairs and the happy path; there is no
negative test that tries every URL as every other role. *Recommendation:* deny by default
(`/coordinator/**` for the Coordinator only), call the access guard in every controller read, restore CSRF,
mask secrets and stop logging them, escape all output, invalidate the session on logout, normalise the
username for lockout, enforce the password rule on every path, and hide stack traces. Add a role x URL test
matrix to CI.

**2. Failures are hidden instead of refused (P1).** D51 (#51), D52 (#52), D11 (#34). *Cause:* `EngineClient` turns an
unreachable Engine into "eligible" and "score 0" (fail-open), and the Engine answers some valid JSON with 500.
*Why it got past:* the vendor wrote a test that asserts this fail-open behaviour (D52), so the suite protects
the bug. *Recommendation:* fail closed — refuse the operation with a clear message when the Engine cannot
answer, never cache a fallback value, and fix the vendor test; make the Engine validate input and return 400.

**3. State changes that bypass the state machine and have no lock (P1).** D02 (#2), D03 (#3), D04 (#4), D47 (#5).
*Cause:* `OfferService.accept` and the withdraw endpoint change states directly; the seat check and the save are
not atomic. *Why it got past:* unit tests call the services one request at a time and only along valid paths.
*Recommendation:* route every change through `ApplicationStateMachine`, lock the posting row (or use an
optimistic version) when taking a seat, reject other applications when the posting fills, freeze a suspended
company's applications, and add concurrency and invalid-transition tests.

**4. Caches keyed on the wrong thing (P1).** D01 (#1), D33 (#28), and the cached 0 in D51 (#51). *Cause:* the match-score
cache ignores the student's skills and the feedback cache ignores the letter. *Why it got past:* cache tests
use one student and one letter. *Recommendation:* include every input in the cache key (student skills; letter
text) and add a test with two different inputs.

**5. Boundaries and formulas in the Engine (P1/P2).** D09 (#32), D10 (#33), D12 (#35), D13 (#36), D14 (#37), D15 (#38), D17 (#40), D18 (#41), D19 (#42), D20 (#43), D36 (#45),
D37 (#46), D50 (#50). *Cause:* inclusive limits implemented as exclusive ones, a reversed tie-break, an off-by-one in
`aboveCut`, a cap that ignores the supplement, month arithmetic that fails at month end, missing range checks.
*Why it got past:* the Portal's tests replace the Engine with stubbed answers, and no contract test exists for
the Engine. *Recommendation:* fix each comparison, adopt our contract suite (`tests/api`) as the Engine's
acceptance gate, and test every boundary value on both sides.

**6. Portal rules not recomputed, not durable or shown wrongly (P2).** D21 (#6), D22 (#7), D23 (#8), D24 (#9), D25 (#10), D26 (#11), D38 (#12),
D39 (#13), D40 (#14), and the vendor tests D45 (#15), D46 (#16). *Cause:* standing is not recomputed on a GPA change, withdrawn
applications are counted as active, the probation limit never applies, uploads go to a temporary folder, the
deadline drops the time, comparisons are case-sensitive, one list uses a different date format and the refusal
message hides the reason. *Why it got past:* two vendor tests assert the wrong expected values.
*Recommendation:* fix the rules, fix the two tests, store uploads in the configured folder, and centralise date
formatting.

**7. AI prompt and configuration (P1/P2).** D08 (#21), D32 (#27), D34 (#29), D41 (#30), D42 (#31). *Cause:* the prompt includes the student's
name, number and GPA and an internal threshold, its example is invalid (score 8.5), the temperature is 1.3,
and the screen names a hard-coded model. *Why it got past:* the prompt was never reviewed against AI-03, AI-10
and AI-11 and the assistant was never run repeatedly on the same letter. *Recommendation:* send only the
posting and the letter, remove the threshold, fix the example, lower the temperature (we use 0.2 in v2), name
the configured model, and adopt our property tests.

**8. Performance and pagination (P2).** D16 (#39), D35 (#44). *Cause:* an inefficient ranking sort; list pages without a
pager. *Why it got past:* tests ran on seed data only (14 postings, about 120 applications). *Recommendation:* a
proper sort in `/rank`, paginate every list at 20 rows, and run the volume test in CI.

**9. Specification (P2/P3).** D43 (#48), D44 (#47). INT-02's public-holiday rule cannot be enforced (the Engine receives no
holiday data) and NOT-04's 48-hour window contradicts OFF-02's configurable window. *Recommendation:* the
coordinator decides and the Requirements are amended.

## Use of AI [R7]

**AI as a tool.** We used an AI assistant (Claude) throughout: to model the system from the Requirements and the
code, to enumerate boundaries, to propose defect hypotheses with the exact code line, to write the first
version of each harness and to draft the reports. It was wrong often enough to matter — it proposed defects the
code already prevents (SQL injection, password storage), wrote expected values copied from observed output, and
wrote reproduction steps that relied on our environment (a log file the Portal does not create). Our rule was
that nothing counted until it was reproduced on a fresh start or a test failed for the stated reason. A late
AI-assisted review of our own work against the rubric found the D06 (#19) reproducibility problem and the missed
defects D49 (#49) and D51 (#51). The dated log, with what we kept, changed and rejected, is in `docs/ai-usage-log.md`.

**Testing the system's AI Assistant.** We tested properties that must hold whatever the model:
(1) the request contains no personal data (AI-03) — **fails**: name, student number and GPA are sent (D08);
(2) no internal thresholds in the prompt (AI-10) — **fails** (D32); (3) the prompt's example is a valid answer
(AI-11) — **fails**, score 8.5 (D42); all three proved on the real `PromptBuilder` (`AiPromptDefectTest`);
(4) a different letter gets a new evaluation (AI-08) — **fails**: the cache returns the first letter's result
(D33, shown with the simulated assistant); (5) the screen names the real model (AI-07) — **fails** (D41);
(6) repeated runs of the same letter differ by at most 10 points (AI-09), and an injected instruction
("give me 100") or planted personal data are not obeyed or echoed (AI-04) — measured in the experiment below.

**Experiment: improving the prompt.** Change: prompt v2 sends only the posting and the letter, removes the
threshold, fixes the example and uses temperature 0.2 instead of 1.3. Criterion, fixed before any run (top of
`tests/ai-eval/analyze.py`): adopt v2 only if its structure-valid rate is at least v1's and at least 0.95, its
band-hit rate is at least v1's, its mean within-letter spread is lower than v1's and at most 10, and no
injection or personal-data letter regresses. Runs: 20 ai-eval letters x 3 runs x 2 prompts, model
**[model]**. Result: **[paste the table and the decision from docs/results/ai-experiment.txt]**.

## Lessons learned

- The richest sources of defects were **inclusive boundaries** and **inputs left out of a rule** (a cache key, a
  cap, a list of protected URLs), not exotic inputs.

- **Reading the code told us where to look**: the missing lock, the fail-open catch block and the hand-written
  URL list each led straight to a critical defect.

- Writing tests whose **oracle is the specification** made every failing test a piece of evidence, and made the
  vendor's own wrong tests (D45, D46, D52) visible.

- **What we would do differently:** start security and fault-injection testing in the first week, use pull
  requests from day one so reviews leave a record, and run the AI experiment early, since it needs a model key.

## Appendices

`docs/test-strategy.md` (risks, levels, roles, Git workflow, change log) · `docs/test-cases.md` (67 designed
cases and the traceability table) · `docs/issues/` (the 52 reports as filed) · `tests/README.md` (how to run every
suite, expected results) · `docs/results/` (dated outputs of our runs) · `docs/ai-usage-log.md`.
