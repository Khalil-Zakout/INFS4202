# [D40] Recruiter applications list shows dates as MM/dd/yyyy

**Requirement violated:** USA-02

**Description:**
USA-02: dates are shown as dd/MM/yyyy. On the recruiter applications list (`templates/applications/list.html`) the submitted date is formatted `MM/dd/yyyy HH:mm` for non-students, so 21 November shows as 11/21/2026.

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. Log in as recruiter.qtech and open Applications.

**Expected result:** dd/MM/yyyy (e.g. 21/11/2026).

**Actual result:** MM/dd/yyyy (e.g. 11/21/2026); the student view uses dd/MM.

**Severity:** Minor
**Priority:** P3
**Category:** ui
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** Recruiter sees submitted dates such as 11/21/2026 13:30 (month first) while the student pages show 21/11/2026 (day first). Source: the recruiter applications template formats with MM/dd/yyyy.
**Discovered by:** Khalil Zakout
**Technique that found it:** UI review
