# Defect reports — index

| Code | Title | Category | Severity | Priority | Requirement | Discovered by |
|------|-------|----------|----------|----------|-------------|----------------|
| D01 | Match score is cached per posting and shared across students | integration | critical | p1 | APP-04 | Khalil Zakout |
| D02 | Filling a posting does not reject its remaining active applications | state | critical | p1 | OFF-03 | Khalil Zakout |
| D03 | Two students can accept offers for the last seat at the same moment | state | critical | p1 | OFF-04 | Khalil Zakout |
| D04 | A suspended company's applications are not frozen | functional | critical | p1 | COM-02 | Khalil Zakout |
| D05 | Any authenticated user can view any application (broken access control) | security | critical | p1 | USR-05 | Abdulaziz Debs |
| D48 | Any recruiter can download any student's CV and transcript | security | critical | p1 | USR-05 | Abdulaziz Debs |
| D06 | API key and SMTP password are written to the log and shown in plaintext | security | critical | p1 | SEC-04 | Abdulaziz Debs |
| D07 | Stored XSS via company name on the postings list | security | critical | p1 | SEC-07 | Abdulaziz Debs |
| D08 | Student name, number and GPA are sent to the AI provider | security | critical | p1 | AI-03 | Abdulaziz Debs |
| D47 | An ACCEPTED application can be withdrawn via a direct POST | state | critical | p1 | APP-08 | Khalil Zakout |
| D09 | Engine refuses eligibility when GPA exactly equals the minimum | integration | major | p2 | POS-01 | Monir Skaik |
| D10 | Transcript valid-window is one day short (day 180 rejected) | integration | major | p2 | STU-04 | Monir Skaik |
| D11 | Engine returns HTTP 500 to well-formed JSON | integration | major | p1 | REL-02 | Monir Skaik |
| D12 | Match score adds the full nice-to-have weight when the list is empty | integration | major | p1 | POS-01 | Monir Skaik |
| D13 | Match skill comparison is case- and space-sensitive | integration | major | p1 | POS-06 | Monir Skaik |
| D14 | Candidate ranking breaks GPA ties in ascending order | integration | major | p1 | APP-09 | Monir Skaik |
| D15 | aboveCut returns one id more than the number of seats | integration | major | p1 | APP-09 | Monir Skaik |
| D16 | Ranking 200 candidates takes about 5 seconds (budget 500 ms) | performance | major | p2 | PERF-02 | Monir Skaik |
| D17 | Engine accepts interviews that end after 18:00 | integration | major | p2 | INT-02 | Monir Skaik |
| D18 | Back-to-back interviews are rejected as overlapping | integration | major | p2 | INT-03 | Monir Skaik |
| D19 | No transport supplement at exactly 30 weekly hours | integration | major | p2 | OFF-05 | Monir Skaik |
| D20 | Monthly cap ignores the transport supplement | integration | major | p2 | OFF-05 | Monir Skaik |
| D21 | Withdrawn applications count against the active-application limit | functional | major | p1 | APP-02 | Khalil Zakout |
| D22 | Probation active-application limit is never applied | functional | major | p1 | APP-02 | Khalil Zakout |
| D23 | Offer response deadline is rounded to midnight and drops the time | functional | major | p2 | OFF-02 | Khalil Zakout |
| D24 | Uploaded documents are lost on every restart | configuration | major | p2 | REL-04 | Khalil Zakout |
| D25 | Academic standing is not recomputed when the Coordinator changes the GPA | functional | major | p2 | STU-03 | Khalil Zakout |
| D26 | Company name uniqueness is case-sensitive when renaming | functional | major | p2 | COM-03 | Khalil Zakout |
| D27 | Logging out does not invalidate the server session | security | major | p2 | USR-04 | Abdulaziz Debs |
| D28 | Account lockout can be bypassed by varying the username case | security | major | p2 | USR-03 | Abdulaziz Debs |
| D29 | Password change accepts a password with no digit | security | major | p2 | USR-02 | Abdulaziz Debs |
| D30 | Error pages expose stack traces and SQL | security | major | p2 | SEC-03 | Abdulaziz Debs |
| D31 | CSRF protection is disabled on the Settings endpoints | security | major | p2 | SEC-02 | Abdulaziz Debs |
| D32 | The AI prompt discloses the internal shortlist threshold | ai | major | p2 | AI-10 | Abdulaziz Debs |
| D33 | Letter-feedback cache ignores the letter content | ai | major | p2 | AI-08 | Abdulaziz Debs |
| D34 | Letter-feedback scores vary by more than 10 points across runs | ai | major | p2 | AI-09 | Abdulaziz Debs |
| D35 | List pages are not paginated (Outbox and Postings) | performance | major | p2 | PERF-05 | Monir Skaik |
| D36 | Engine rejects an interview of exactly 120 minutes | functional | minor | p3 | INT-02 | Monir Skaik |
| D37 | Allowance whole-month count is off at month-end start dates | integration | minor | p3 | OFF-05 | Monir Skaik |
| D38 | Searching postings by company is not sorted by deadline | functional | minor | p3 | POS-06 | Khalil Zakout |
| D39 | A refused application shows a generic message, not the reason | ui | minor | p3 | USA-01 | Khalil Zakout |
| D40 | Recruiter applications list shows dates as MM/dd/yyyy | ui | minor | p3 | USA-02 | Khalil Zakout |
| D41 | Letter feedback names the wrong model | ai | minor | p3 | AI-07 | Abdulaziz Debs |
| D42 | The AI prompt's worked example is malformed | ai | minor | p3 | AI-11 | Abdulaziz Debs |
| D44 | Specification: NOT-04 reminder window contradicts OFF-02 | requirements | minor | p3 | NOT-04 | Monir Skaik |
| D45 | Vendor test encodes the wrong probation limit | tests | minor | p3 | APP-02 | Khalil Zakout |
| D46 | Vendor test counts withdrawn applications as active | tests | minor | p3 | APP-02 | Khalil Zakout |
| D43 | Specification: public-holiday rule (INT-02) is untestable and unenforced | requirements | major | p2 | INT-02 | Monir Skaik |

## Totals

- Issues: **48**
- By severity: critical 10, major 28, minor 10
- By category: ai 5, configuration 1, functional 8, integration 13, performance 2, requirements 2, security 10, state 3, tests 2, ui 2
- Severity-weighted (C3/Maj2/Min1/Enh0.5): **96**

