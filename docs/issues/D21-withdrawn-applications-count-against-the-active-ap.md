# [D21] Withdrawn applications count against the active-application limit

**Requirement violated:** APP-02

**Description:**
APP-02: an application is active only while SUBMITTED, SHORTLISTED, INTERVIEW or OFFERED. `ApplicationService.countActive` counts everything except REJECTED and ACCEPTED, so WITHDRAWN applications are counted as active and students are blocked from applying earlier than the rules allow.

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. On a fresh start, student.amal has 3 active applications and 1 withdrawn.
2. Open the student dashboard.

**Expected result:** Active applications: 3 of 5.

**Actual result:** Active applications: 4 of 5 (the withdrawn one is counted).

**Severity:** Major
**Priority:** P1
**Category:** functional
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** qa:PortalDefectTest.withdrawnApplicationsAreNotCountedAsActive.
**Discovered by:** Khalil Zakout
**Technique that found it:** White-box review + unit test
