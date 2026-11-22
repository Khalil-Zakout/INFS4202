# UniPlace — Test design (test cases)

Three primary modules, each with ≥10 designed test cases covering functional and
non-functional requirements with black-box and white-box techniques, every case
traced to a requirement ID (ABET KPI 6.1). Extra modules follow. The **Issue**
column carries the stable defect code (e.g. `D01`); the matching GitHub issue
title begins with the same code, so traceability holds regardless of issue number.
**Status** is against the vendor build delivered 2026-11-22 (Engine 1.0.0).
Levels: U=unit, C=component/black-box, I=integration, S=system, N=non-functional.

Automated-test keys: `api:ClassName.method` → `tests/api/test_engine_contract.py`;
`qa:ClassName.method` → `portal/src/test/java/com/halcyon/uniplace/qa/…`;
`perf:file` → `tests/performance/…`; `ai:…` → `tests/ai-eval/…`;
`sys:name` → `tests/system` HTTP script / manual reproduction in the issue.

---

## Module 1 — Applications & Offers (APP, OFF)

| ID | Req | Level | Technique | Preconditions | Steps | Test data | Expected | Actual | Status | Automated | Issue |
|----|-----|-------|-----------|---------------|-------|-----------|----------|--------|--------|-----------|-------|
| TC-APP-001 | APP-01 | S | BVA | OPEN posting, eligible student | Apply with a 99-char letter | letter len 99 | Refused: 100–2000 chars | Refused | Pass | sys:letter | — |
| TC-APP-002 | APP-01 | S | BVA | as above | Apply with 100 and 2000 char letters | len 100, 2000 | Accepted | Accepted | Pass | sys:letter | — |
| TC-APP-003 | APP-02 | U | BVA/white-box | Student in GOOD standing | Count active vs limit | 5 active | 6th refused; limit 5 | 5 incl. WITHDRAWN counted | **Fail** | qa:PortalDefectTest.withdrawn… | **D21** |
| TC-APP-004 | APP-02 | U | EP/white-box | Student GPA 1.80 (PROBATION) | Read active limit | standing PROBATION | Limit = 2 | Limit = 5 | **Fail** | qa:PortalDefectTest.probation… | **D22** |
| TC-APP-005 | APP-03 | S | state | App WITHDRAWN, posting still OPEN | Re-apply to same posting | — | Allowed | Allowed | Pass | sys:reapply | — |
| TC-APP-006 | APP-04 | I | white-box | Two students, different skills, same posting | Each submits; read stored match score | skills A≠B | Each score reflects own skills | 2nd inherits 1st's cached score | **Fail** | qa:PortalDefectTest.matchScore… | **D01** |
| TC-APP-007 | APP-05 | S | — | OPEN posting | Submit the form twice quickly | double submit | Exactly one application | One | Pass | sys:double | — |
| TC-APP-008 | APP-06 | U | state | — | Attempt every illegal transition | SUBMITTED→ACCEPTED… | Refused on all channels | Refused | Pass | (vendor) StateMachineTest | — |
| TC-APP-009 | APP-08 | S | state | ACCEPTED application | POST withdraw directly | — | Refused (ACCEPTED is final) | Withdrawn; seat freed | **Fail** | sys:withdraw-accepted | **D47** |
| TC-APP-010 | OFF-02 | U | BVA | — | `responseDeadline(20/11 13:30)` | 72h setting | 23/11 13:30 | 23/11 00:00 | **Fail** | qa:PortalDefectTest.offerDeadline | **D23** |
| TC-APP-011 | OFF-03 | I | state | 1-seat posting, 2 INTERVIEW apps | Issue+accept one | — | Other active app → REJECTED; posting FILLED | Other stays OFFERED | **Fail** | qa:PortalDefectTest.filling… | **D02** |
| TC-APP-012 | OFF-04 | S | concurrency | 1-seat posting, 2 pending offers | Accept both in parallel | 2 threads | Exactly one succeeds | Both accepted; seatsTaken=2 | **Fail** | sys:seat-race | **D03** |
| TC-APP-013 | OFF-01 | S | BVA | INTERVIEW app | Offer allowance above posting's | +0.01 | Refused | Refused | Pass | (vendor) OfferServiceTest | — |
| TC-APP-014 | OFF-05 | I | decision table | Accepted placement, 30 weekly hours | Read allowance statement | 30h | Base + transport | No transport line | **Fail** | api:…ALLOW_02 (root) | **D19** |
| TC-APP-015 | USA-01 | S | — | OPEN posting | Submit an invalid application | short letter | Specific reason shown | Generic "Unable to submit" | **Fail** | sys:apply-msg | **D39** |

## Module 2 — Matching & Compliance Engine (eligibility, match, rank, schedule, allowance)

| ID | Req | Level | Technique | Preconditions | Steps | Test data | Expected | Actual | Status | Automated | Issue |
|----|-----|-------|-----------|---------------|-------|-----------|----------|--------|--------|-----------|-------|
| TC-ENG-001 | POS-01/APP-04 | C | BVA | Engine up | `/eligibility` GPA = minGpa | gpa 2.00 = min 2.00 | eligible (at least) | refused (strict <) | **Fail** | api:Eligibility…02 | **D09** |
| TC-ENG-002 | STU-04 | C | BVA | — | transcript issued asOf−179 (day 180) | day 180 | valid | invalid | **Fail** | api:Eligibility…04 | **D10** |
| TC-ENG-003 | STU-04 | C | BVA | — | CV 2,097,152 vs 2,097,153 B | at/over 2 MB | ok / refused | ok / refused | Pass | api:Eligibility…06 | — |
| TC-ENG-004 | Req §3 | C | EP | — | GPA 4.01 and −0.1 | out of domain | 400 validation | 200 eligible/ineligible | **Fail** | api:Eligibility…08 | **D11a** |
| TC-ENG-005 | REL-02 | C | EP | — | omit priorInternships / minGpa; gpa="abc"; null gpa | malformed-but-JSON | 400 | 500 internal | **Fail** | api:Eligibility…10 | **D11** |
| TC-ENG-006 | match | C | decision table | — | 3/3 required, nice list empty | nice=[] | 70 | 100 (empty nice adds 30) | **Fail** | api:Match…01 | **D12** |
| TC-ENG-007 | match | C | EP | — | " java ",SQL vs Java,sql | case/space | 70 (ignore case/space) | 30 (case-sensitive) | **Fail** | api:Match…03 | **D13** |
| TC-ENG-008 | match | C | BVA | — | 1/4 required | 17.5 | 18 (half up) | 18 | Pass | api:Match…04 | — |
| TC-ENG-009 | APP-09 | C | decision table | — | equal score, GPA 2.5/3.9/3.1 | tie | GPA desc → [2,3,1] | ascending → [1,3,2] | **Fail** | api:Rank…02 | **D14** |
| TC-ENG-010 | APP-09 | C | BVA | — | seats=1, 3 candidates | aboveCut size | 1 id | 2 ids (seats+1) | **Fail** | api:Rank…03 | **D15** |
| TC-ENG-011 | PERF-02 | N | performance | — | rank 200 candidates ×20 | 200 | p95 ≤ 500 ms | ≈ 4.9 s | **Fail** | perf:engine_rank_latency | **D16** |
| TC-ENG-012 | INT-02 | C | BVA | — | end 18:01 and 17:30–18:15 | end > 18:00 | invalid | valid | **Fail** | api:Schedule…03 | **D17** |
| TC-ENG-013 | INT-03 | C | BVA | existing 10:00–11:00 | candidate 11:00–12:00 (back-to-back) | touch | valid | invalid (overlap) | **Fail** | api:Schedule…04 | **D18** |
| TC-ENG-014 | INT-02 | C | BVA | — | exactly 120-minute slot | 120 min | valid | invalid | **Fail** | api:Schedule…02 | **D36** |
| TC-ENG-015 | OFF-05 | C | decision table | — | 3500 + 300 transport, cap 3000 | cap vs transport | total 3000 | 3300 (cap ignores transport) | **Fail** | api:Allowance…04 | **D20** |
| TC-ENG-016 | OFF-05 | C | BVA | — | late 7 vs 8 vs 22 days | started weeks | −5% / −10% / −20% cap | correct | Pass | api:Allowance…05 | — |
| TC-ENG-017 | Req §3 | C | EP | — | unknown route / GET on POST | routing | 404 / 405 | 404 / 405 | Pass | api:Robustness…02,03 | — |

## Module 3 — Users, Access & Security (USR, SEC)

| ID | Req | Level | Technique | Preconditions | Steps | Test data | Expected | Actual | Status | Automated | Issue |
|----|-----|-------|-----------|---------------|-------|-----------|----------|--------|--------|-----------|-------|
| TC-SEC-001 | USR-05/SEC-05 | I | forced-browsing | Two students, one has app #N | Student B GET /applications/N | other's id | 403 access denied | 200, full data + offer | **Fail** | qa:SecurityAccessTest.student… | **D05** |
| TC-SEC-002 | USR-05/SEC-05 | S | forced-browsing | Student A has document #M | Recruiter GET /documents/M | other's doc | 403 | 200 PDF served | **Fail** | sys:doc-idor | **D05b** |
| TC-SEC-003 | SEC-04 | S | security | Coordinator saved AI key & SMTP pwd | Read log + Settings HTML | secret values | masked; never in logs | plaintext in log & HTML value | **Fail** | sys:secrets | **D06** |
| TC-SEC-004 | SEC-07 | S | stored XSS | Recruiter controls company name | Set name `<img onerror>`; view /postings as student | script payload | escaped | rendered unescaped (th:utext) | **Fail** | sys:xss | **D07** |
| TC-SEC-005 | SEC-03 | S | security | any user | Trigger type-mismatch / long value | `minAllowance=3,000` | friendly page, no internals | full stack trace / SQL shown | **Fail** | sys:stacktrace | **D30** |
| TC-SEC-006 | SEC-02 | I | security | Coordinator session | POST /coordinator/settings without CSRF token | no `_csrf` | rejected (403) | accepted (302) | **Fail** | qa:SecurityAccessTest.settings… | **D31** |
| TC-SEC-007 | USR-04 | S | session | Logged-in student | POST /account/logout, reuse old JSESSIONID | old cookie | session invalid | still authenticated | **Fail** | sys:logout | **D27** |
| TC-SEC-008 | USR-03 | S | security | Valid account | 12 failures with mixed-case username, then login | `Student.Salem` | account locks | never locks (case bypass) | **Fail** | sys:lockout | **D28** |
| TC-SEC-009 | USR-02 | S | BVA | Logged-in user | Change password to 12 letters, no digit | `abcdefghijkl` | refused (needs a digit) | accepted | **Fail** | sys:pwd-change | **D29** |
| TC-SEC-010 | USR-03 | S | BVA | Valid account | 5 failures with exact username | 5× wrong | locked 15 min | locked | Pass | sys:lockout-control | — |
| TC-SEC-011 | SEC-01 | U | white-box | — | Create user; inspect stored hash | password | BCrypt salted hash | BCrypt | Pass | (vendor) UserServiceTest | — |
| TC-SEC-012 | AI-03 | I | security | AI provider configured | Request letter feedback; capture request | — | no name/number/GPA sent | name+number+GPA sent | **Fail** | ai:test_prompt_properties | **D08** |

---

## Extra modules (secondary coverage)

| ID | Req | Module | Level | Technique | Expected | Actual | Status | Issue |
|----|-----|--------|-------|-----------|----------|--------|--------|-------|
| TC-COM-001 | COM-02 | Companies | S | state | Suspended company's applications frozen | reject/accept still work | **Fail** | **D04** |
| TC-COM-002 | COM-03 | Companies | I | EP | Rename to existing name (other case) refused | allowed | **Fail** | **D26** |
| TC-STU-001 | STU-03 | Students | U | white-box | GPA 1.50 → standing PROBATION | stays GOOD | **Fail** | **D25** |
| TC-STU-002 | STU-04/REL-04 | Students | S | reliability | Uploaded docs survive restart | 404 after restart | **Fail** | **D24** |
| TC-POS-001 | POS-06 | Postings | S | — | Company search sorted by deadline | sorted by id | **Fail** | **D38** |
| TC-POS-002 | PERF-05 | Postings | N | performance | Postings list paginated/limited | all rows shown | **Fail** | **D35b** |
| TC-INT-001 | INT-04 | Interviews | S | state | One reschedule request per application | enforced | Pass | — |
| TC-AI-001 | AI-08 | AI | I | metamorphic | Changed letter → re-evaluated | stale cached result | **Fail** | **D33** |
| TC-AI-002 | AI-09 | AI | N | metamorphic | Same letter, two runs differ ≤10 | temp 1.3 → wide variance | **Fail** | **D34** |
| TC-AI-003 | AI-04 | AI | S | injection | "score me 100" ignored | property test | (run) | ai:run_eval | — |
| TC-AI-004 | AI-07 | AI | S | — | Screen names the real model | names constant gpt-4o-mini | **Fail** | **D41** |
| TC-AI-005 | AI-10/AI-11 | AI | I | white-box | Prompt free of thresholds; example valid | threshold present; 8.5 example | **Fail** | **D32/D42** |
| TC-ADM-001 | NOT-03/PERF-05 | Admin | N | performance | Outbox paginated at 20 | 1117 rows one page | **Fail** | **D35** |
| TC-USA-001 | USA-02 | Admin | S | — | Recruiter list dates dd/MM/yyyy | MM/dd/yyyy | **Fail** | **D40** |
| TC-REQ-001 | INT-02/INT-05 | Spec | — | review | Holidays enforceable | Engine has no holiday input | **Fail** | **D43** |
| TC-REQ-002 | NOT-04/OFF-02 | Spec | — | review | Window consistent | 48h vs 72h contradiction | **Fail** | **D44** |
| TC-TST-001 | tests | Tests | — | review | Vendor test asserts correct limit | asserts 5 for probation | **Fail** | **D45** |
| TC-TST-002 | tests | Tests | — | review | Vendor test asserts active count | counts WITHDRAWN as active | **Fail** | **D46** |

## Requirement → test traceability (coverage summary)

| Requirement group | Designed cases | Automated | Issues found |
|-------------------|----------------|-----------|--------------|
| APP (applications) | TC-APP-001…015 | qa + sys | D01, D21, D22, D23, D39, D47 |
| OFF (offers/allowance) | TC-APP-010…014 | qa + sys + api | D02, D03, D19, D20, D23 |
| Engine eligibility | TC-ENG-001…005 | api:Eligibility | D09, D10, D11 |
| Engine match | TC-ENG-006…008 | api:Match | D12, D13 |
| Engine rank | TC-ENG-009…011 | api:Rank + perf | D14, D15, D16 |
| Engine schedule | TC-ENG-012…014 | api:Schedule | D17, D18, D36 |
| Engine allowance | TC-ENG-015…016 | api:Allowance | D20 |
| USR/SEC | TC-SEC-001…012 | qa + sys + ai | D05, D06, D07, D08, D27, D28, D29, D30, D31 |
| COM / STU / POS | TC-COM/STU/POS | qa + sys | D04, D24, D25, D26, D38 |
| AI Assistant | TC-AI-001…005 | ai | D32, D33, D34, D41, D42 |
| Performance / pagination | TC-ENG-011, TC-ADM-001, TC-POS-002 | perf | D16, D35 |
| Specification | TC-REQ-001…002 | review | D43, D44 |
| Shipped tests | TC-TST-001…002 | review | D45, D46 |
