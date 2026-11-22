# [D05] Any authenticated user can view any application (broken access control)

**Requirement violated:** USR-05

**Description:**
USR-05/SEC-05: a Student sees only their own data; access control is enforced on the server. `ApplicationController.view` loads the application by id and renders it without calling `AccessGuard.assertCanView`, so any logged-in user can read any application — its letter, the student's GPA (to recruiters) and the offer — by changing the id in the URL.

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. Log in as student.omar.
2. Open /applications/3 (an application that belongs to Amal).

**Expected result:** Access-denied page; nothing about the record is revealed (USR-05).

**Actual result:** HTTP 200 showing Amal's posting, motivation letter and offer.

**Severity:** Critical
**Priority:** P1
**Category:** security
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** qa:SecurityAccessTest.studentCannotOpenAnotherStudentsApplication.
**Discovered by:** Abdulaziz Debs
**Technique that found it:** Forced-browsing / IDOR
