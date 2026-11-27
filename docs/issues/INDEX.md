# Defect reports — index

| Issue | Code | Title | Category | Severity | Priority | Requirement | Discovered by |
|------|------|-------|----------|----------|----------|-------------|----------------|
| #1 | D01 | Match score is cached per posting and shared across students | integration | critical | p1 | APP-04 | Khalil Zakout |
| #2 | D02 | Filling a posting does not reject its remaining active applications | state | critical | p1 | OFF-03 | Khalil Zakout |
| #3 | D03 | Two students can accept offers for the last seat at the same moment | state | critical | p1 | OFF-04 | Khalil Zakout |
| #4 | D04 | A suspended company's applications are not frozen | functional | critical | p1 | COM-02 | Khalil Zakout |
| #17 | D05 | Any authenticated user can view any application (broken access control) | security | critical | p1 | USR-05 | Abdulaziz Debs |
| #18 | D48 | Any recruiter can download any student's CV and transcript | security | critical | p1 | USR-05 | Abdulaziz Debs |
| #49 | D49 | Students and recruiters can open the Coordinator reports and export them as CSV | security | critical | p1 | USR-05, SEC-05 | Abdulaziz Debs |
| #19 | D06 | API key and SMTP password are written to the log and shown in plaintext | security | critical | p1 | SEC-04 | Abdulaziz Debs |
| #20 | D07 | Stored XSS via company name on the postings list | security | critical | p1 | SEC-07 | Abdulaziz Debs |
| #21 | D08 | Student name, number and GPA are sent to the AI provider | security | critical | p1 | AI-03 | Abdulaziz Debs |
| #5 | D47 | An ACCEPTED application can be withdrawn via a direct POST | state | critical | p1 | APP-08 | Khalil Zakout |
| #32 | D09 | Engine refuses eligibility when GPA exactly equals the minimum | integration | major | p2 | POS-01 | Monir Skaik |
| #33 | D10 | Transcript valid-window is one day short (day 180 rejected) | integration | major | p2 | STU-04 | Monir Skaik |
| #34 | D11 | Engine returns HTTP 500 to well-formed JSON | integration | major | p1 | REL-02 | Monir Skaik |
| #35 | D12 | Match score adds the full nice-to-have weight when the list is empty | integration | major | p1 | POS-01 | Monir Skaik |
| #36 | D13 | Match skill comparison is case- and space-sensitive | integration | major | p1 | POS-06 | Monir Skaik |
| #37 | D14 | Candidate ranking breaks GPA ties in ascending order | integration | major | p1 | APP-09 | Monir Skaik |
| #38 | D15 | aboveCut returns one id more than the number of seats | integration | major | p1 | APP-09 | Monir Skaik |
| #39 | D16 | Ranking 200 candidates takes about 5 seconds (budget 500 ms) | performance | major | p2 | PERF-02 | Monir Skaik |
| #40 | D17 | Engine accepts interviews that end after 18:00 | integration | major | p2 | INT-02 | Monir Skaik |
| #41 | D18 | Back-to-back interviews are rejected as overlapping | integration | major | p2 | INT-03 | Monir Skaik |
| #42 | D19 | No transport supplement at exactly 30 weekly hours | integration | major | p2 | OFF-05 | Monir Skaik |
| #43 | D20 | Monthly cap ignores the transport supplement | integration | major | p2 | OFF-05 | Monir Skaik |
| #6 | D21 | Withdrawn applications count against the active-application limit | functional | major | p1 | APP-02 | Khalil Zakout |
| #7 | D22 | Probation active-application limit is never applied | functional | major | p1 | APP-02 | Khalil Zakout |
| #8 | D23 | Offer response deadline is rounded to midnight and drops the time | functional | major | p2 | OFF-02 | Khalil Zakout |
| #9 | D24 | Uploaded documents are lost on every restart | configuration | major | p2 | REL-04 | Khalil Zakout |
| #10 | D25 | Academic standing is not recomputed when the Coordinator changes the GPA | functional | major | p2 | STU-03 | Khalil Zakout |
| #11 | D26 | Company name uniqueness is case-sensitive when renaming | functional | major | p2 | COM-03 | Khalil Zakout |
| #22 | D27 | Logging out does not invalidate the server session | security | major | p2 | USR-04 | Abdulaziz Debs |
| #23 | D28 | Account lockout can be bypassed by varying the username case | security | major | p2 | USR-03 | Abdulaziz Debs |
| #24 | D29 | Password change accepts a password with no digit | security | major | p2 | USR-02 | Abdulaziz Debs |
| #25 | D30 | Error pages expose stack traces and SQL | security | major | p2 | SEC-03 | Abdulaziz Debs |
| #26 | D31 | CSRF protection is disabled on the Settings endpoints | security | major | p2 | SEC-02 | Abdulaziz Debs |
| #27 | D32 | The AI prompt discloses the internal shortlist threshold | ai | major | p2 | AI-10 | Abdulaziz Debs |
| #28 | D33 | Letter-feedback cache ignores the letter content | ai | major | p2 | AI-08 | Abdulaziz Debs |
| #29 | D34 | Letter-feedback scores vary by more than 10 points across runs | ai | major | p2 | AI-09 | Abdulaziz Debs |
| #44 | D35 | List pages are not paginated (Outbox and Postings) | performance | major | p2 | PERF-05 | Monir Skaik |
| #45 | D36 | Engine rejects an interview of exactly 120 minutes | functional | minor | p3 | INT-02 | Monir Skaik |
| #46 | D37 | Allowance whole-month count is off at month-end start dates | integration | minor | p3 | OFF-05 | Monir Skaik |
| #50 | D50 | Engine accepts out-of-range GPA and an unknown standing instead of answering 400 | integration | minor | p3 | REL-02, Requirements section 3 (Errors) | Monir Skaik |
| #51 | D51 | When the Engine is down, every student is treated as eligible and applications are accepted with match score 0 | integration | critical | p1 | REL-01 | Monir Skaik |
| #12 | D38 | Searching postings by company is not sorted by deadline | functional | minor | p3 | POS-06 | Khalil Zakout |
| #13 | D39 | A refused application shows a generic message, not the reason | ui | minor | p3 | USA-01 | Khalil Zakout |
| #14 | D40 | Recruiter applications list shows dates as MM/dd/yyyy | ui | minor | p3 | USA-02 | Khalil Zakout |
| #30 | D41 | Letter feedback names the wrong model | ai | minor | p3 | AI-07 | Abdulaziz Debs |
| #31 | D42 | The AI prompt's worked example is malformed | ai | minor | p3 | AI-11 | Abdulaziz Debs |
| #47 | D44 | Specification: NOT-04 reminder window contradicts OFF-02 | requirements | minor | p3 | NOT-04 | Monir Skaik |
| #15 | D45 | Vendor test encodes the wrong probation limit | tests | minor | p3 | APP-02 | Khalil Zakout |
| #16 | D46 | Vendor test counts withdrawn applications as active | tests | minor | p3 | APP-02 | Khalil Zakout |
| #52 | D52 | Vendor test asserts that an unreachable Engine means eligible | tests | minor | p3 | REL-01 | Monir Skaik |
| #48 | D43 | Specification: public-holiday rule (INT-02) is untestable and unenforced | requirements | major | p2 | INT-02 | Monir Skaik |

## Totals

- Issues: **52**
- By severity: critical 12, major 28, minor 12
- By category: ai 5, configuration 1, functional 8, integration 15, performance 2, requirements 2, security 11, state 3, tests 3, ui 2
- Severity-weighted (C3/Maj2/Min1/Enh0.5): **104**

