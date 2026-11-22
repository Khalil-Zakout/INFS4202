# [D22] Probation active-application limit is never applied

**Requirement violated:** APP-02

**Description:**
APP-02: a student on probation may hold at most 2 active applications. `activeLimitFor` compares the String "PROBATION" to a `Standing` enum (`"PROBATION".equals(student.getStanding())`), which is always false, so probation students get the GOOD limit of 5.

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. Log in as student.omar (GPA 1.85, PROBATION).
2. Read the dashboard limit, or add applications past 2.

**Expected result:** Limit of 2 active applications.

**Actual result:** Limit of 5; Omar can hold 5 active applications.

**Severity:** Major
**Priority:** P1
**Category:** functional
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** qa:PortalDefectTest.probationStudentLimitIsTwo.
**Discovered by:** Khalil Zakout
**Technique that found it:** White-box review + unit test
