# [D48] Any recruiter can download any student's CV and transcript

**Requirement violated:** USR-05

**Description:**
USR-05: a Recruiter sees only data of their own company. `StudentController.download` authorises the download if the user is a Coordinator, the owning Student, OR any Recruiter — so a recruiter from an unrelated company can fetch any student's documents by id.

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. Log in as recruiter.gulfbank.
2. GET /documents/1 (Amal's CV) and /documents/2 (Amal's transcript).

**Expected result:** Access-denied; a recruiter may only reach documents of applicants to their own company's postings.

**Actual result:** The PDF is served.

**Severity:** Critical
**Priority:** P1
**Category:** security
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** tests/system doc-idor; `StudentController.download` allows `user.is(Role.RECRUITER)` unconditionally.
**Discovered by:** Abdulaziz Debs
**Technique that found it:** Forced-browsing / IDOR
