# UniPlace Acceptance Testing — Final Report

**Course:** INFS4202 Software Testing & Quality Assurance, Fall 2026
**Team:** UniPlace QA Team  *(change to your registered D2L team name)*
**Members:** Khalil Zakout (60314057) · Monir Skaik (60314058) · Abdulaziz Debs (60309913)
**Repository:** https://github.com/Khalil-Zakout/INFS4202  (instructor `vanilson` added)
**Date:** 22/11/2026

*We declare this is our own work, that every AI-assisted step is recorded in our AI
usage log, and that we reproduced every reported defect on the running system.*

---

## Q1. How we understood the system

UniPlace is an internship portal in two parts. The **Portal** (Java / Spring Boot)
holds the screens, the data and the business rules for three roles — students apply
to postings, recruiters shortlist and make offers, and a coordinator administers
everything. For every *compliance* decision the Portal calls the **Engine**, a
separate REST service we only received as a program: it decides eligibility, the
match score between a student and a posting, the ranking of candidates, whether an
interview time slot is valid, and the monthly allowance. A third feature uses an
**AI model** to give students feedback on their application letter.

We built our picture of the system in three steps: we ran it and used it in every
role with the seeded accounts; we read the requirements as testers and turned each
rule into a concrete, checkable statement with its boundaries; and we reverse-
engineered the code (for the Portal) and the API contract `openapi.yaml` (for the
Engine) to see how each rule was actually implemented.

## Q2. Our testing process

**Risk first.** We ranked the system by what would hurt most if it broke, and tested
the top risks hardest: the offer / seat lifecycle and concurrency, access control
and secret handling, and the Engine's compliance logic.

**Four levels, matched techniques.** We tested at four levels — unit, component
(the Engine API as a black box), integration, and whole-system — so each defect is
caught close to its cause. We used boundary-value analysis and decision tables for
the Engine's numbers, state-transition testing for the application and offer
workflow, white-box reading of the Portal code, security testing (access control,
CSRF, sessions, secrets, cross-site scripting), one concurrency test for the
last-seat race, property testing for the AI feature, and performance testing for
ranking and list pages. Our oracle was always the **requirements and the API
contract**, never the system's own output — so a test that disagrees with the
system is evidence of a defect, not a mistake in the test.

**How we split the work.** Each member owned one risk area end to end — designing
the tests, automating them, finding and reporting the defects, and presenting them:

- **Khalil Zakout** — Applications & Offers, and the remaining Portal rules.
- **Monir Skaik** — the Engine, the Portal–Engine integration, performance.
- **Abdulaziz Debs** — security and access control, and the AI assistant.

We worked on GitHub with a protected `main` branch on the vendor's baseline, one
branch and pull request per task, the test suite running on every push, and no
secret ever committed.

## Q3. How we designed and ran the tests

We fully covered three primary modules, each with at least ten designed test cases
(the complete, requirement-traced tables are in `docs/test-cases.md`):

1. **Applications & Offers** (15 cases) — the workflow, the state machine, the
   seat and concurrency rules, the allowance.
2. **Matching & Compliance Engine** (17 cases) — tested against the contract.
3. **Users, Access & Security** (12 cases) — login, authorization, CSRF, secrets.

The automated suites and how to run them (full detail in `tests/README.md`):

| Suite | Level | How to run | Tests | Pass | Fail = defects |
|---|---|---|---|---|---|
| Portal white-box (JUnit) | unit / integration | `cd portal && ./mvnw test` | 10 | 0 | 10 |
| Engine contract (Python) | black-box | `cd tests/api && python3 -m unittest` | 38 | 20 | 18 |
| Rank latency | performance | `python3 tests/performance/engine_rank_latency.py` | 1 | 0 | 1 |
| Portal list pages | performance | `python3 tests/performance/portal_pages.py` | 5 | 3 | 2 |
| System reproductions | system | `python3 tests/system/reproduce.py` | 10 | 0 | 10 |
| AI prompt properties | AI property | `cd tests/ai-eval && python3 -m unittest` | 6 | 3 | 3 |

A **failing** test here is deliberate: it asserts the behaviour the requirements
demand, so it fails on the buggy build and is the evidence for one reported defect;
it will pass once that defect is fixed. These failing counts are exactly what the
repository's continuous-integration run shows. Coverage is measured with JaCoCo
(`cd portal && ./mvnw test -Dmaven.test.failure.ignore=true`, then open
`portal/target/site/jacoco/index.html`); our white-box tests target the service
layer where the rules live. *Service-layer line coverage: [fill in from your run] %.*

## Q4. What we found

**48 valid, reproducible defects**, with no invalid reports and no duplicates.

- **By severity:** Critical 10, Major 28, Minor 10 (severity-weighted total 96).
- **By category:** integration 13, security 10, functional 8, AI 5, state 3,
  performance 2, specification 2, UI 2, shipped-tests 2, configuration 1.

The ten critical defects:

| ID | Defect | Requirement |
|---|---|---|
| D01 | Match score is cached per posting and shared between students | APP-04 |
| D02 | Filling a posting leaves the other applicants un-rejected | OFF-03 |
| D03 | Two students can accept the last seat at the same moment | OFF-04 |
| D04 | A suspended company's applications are not frozen | COM-02 |
| D05 | Any logged-in user can open any application | USR-05 |
| D48 | Any recruiter can download any student's CV and transcript | USR-05 |
| D06 | API key and SMTP password written to the log and shown in plaintext | SEC-04 |
| D07 | Stored cross-site scripting through the company name | SEC-07 |
| D08 | Student name, number and GPA sent to the AI provider | AI-03 |
| D47 | An accepted application can be withdrawn by a direct request | APP-08 |

Every defect has a full report in GitHub Issues and in `docs/issues/`, each with
steps that reproduce it from a fresh `./start.sh --reset`. The majors cover the
Engine's compliance logic, reliability, performance, the Portal's application rules,
access and security, and the AI assistant; we also report two **specification**
defects and two bugs in the **vendor's own test suite** (tests that assert the wrong
answer and so protect a bug).

## Q5. Why the defects exist and what to change

Grouped by root cause, with the fix and a priority:

1. **Authorization and secrets (P1)** — access checks exist but are not called on
   every entry point, CSRF is switched off for Settings, and secrets are logged and
   shown. *Fix:* enforce the access guard on every request, restore CSRF, mask and
   stop logging secrets, and hide stack traces. (D05, D48, D06, D30, D31, D27, D28, D29)
2. **State changes that skip the state machine (P1)** — accepting an offer and
   withdrawing an application change state directly, and the seat check has no lock,
   so the "reject the rest when full", "one winner per seat", "freeze while
   suspended" and "accepted is final" rules are not enforced. *Fix:* route every
   change through the state machine and lock the seat. (D02, D03, D04, D47)
3. **Caches keyed on the wrong thing (P1)** — the match-score and feedback caches
   ignore the student's skills and the letter text, so results leak between people
   and between letters. *Fix:* add the missing input to each cache key. (D01, D33)
4. **Engine boundary and formula errors (P1/P2)** — off-by-one at inclusive limits,
   a tie-break and a cap applied the wrong way, inputs that crash with HTTP 500, and
   a slow ranking sort. *Fix:* correct each comparison, validate inputs (400 not
   500), and use a faster sort. (D09–D20, D36, D37, D43)
5. **Values not recomputed, data not durable (P2)** — standing is not recomputed on
   a GPA change, the active-application count includes withdrawn ones, and uploads
   go to a temporary folder lost on restart. *Fix:* recompute on change and store
   uploads under the configured folder. (D21, D22, D24, D25)
6. **AI prompt leaks data and is inconsistent (P1/P2)** — it carries personal data
   and an internal threshold, its example is malformed, and the temperature is too
   high for stable scores. *Fix:* send only the posting and the letter, fix the
   example, and lower the temperature. (D08, D32, D34, D41, D42)

We also recommend the vendor fix the **two shipped tests that encode defects**
(D45, D46): a test suite that asserts the wrong answer actively protects the bug.

## Use of AI

We used AI assistants (ChatGPT, Claude) as tools — to model the system, enumerate
boundaries, scaffold the test harnesses, and reason about code we were reading. It
was wrong often enough to matter (it proposed "defects" the code already prevents),
so **we reproduced every hypothesis on the running system before filing it**, with
the requirements as the oracle. The full dated log is in `docs/ai-usage-log.md`.

We also tested the system's **own** AI feature by the properties that must always
hold rather than one expected answer: the reply is well-formed, the score sits in a
sensible band, an injection letter ("give me 100") is ignored, personal data is not
echoed, and two runs of the same letter differ by at most ten points. Model-free
checks in `tests/ai-eval` already prove the personal-data leak (D08), the internal
threshold (D32) and the malformed example (D42) without needing any model. As an
extension we compared the shipped prompt with an improved one using a criterion
fixed before the runs (in `tests/ai-eval/analyze.py`). *Result: [fill in after
running the experiment with a model key, as described in `tests/README.md`].*

## Lessons learned

The richest sources of defects were **inclusive boundaries** (greater-than vs
greater-or-equal, the last valid day, the exact end time) and **cache keys that
omit an input**, not unusual inputs. Choosing the three primary modules by risk, and
writing tests whose oracle is the specification, meant a failing test was itself the
evidence. If we started again we would begin the concurrency and security probing in
the first week — both turned up critical defects.

## Appendices

`docs/test-strategy.md` (risks, levels, roles, Git workflow) · `docs/test-cases.md`
(the designed-case tables) · `docs/issues/INDEX.md` and `docs/issues/` (all 48
reports) · `tests/README.md` (how to run every suite) · `docs/ai-usage-log.md`.
