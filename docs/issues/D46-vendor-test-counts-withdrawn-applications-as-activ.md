# [D46] Vendor test counts withdrawn applications as active

**Requirement violated:** APP-02

**Description:**
`ApplicationServiceTest.withdrawnApplicationsRemainInHistoryCount` asserts countActive = 5 for a student with 4 withdrawn and 1 submitted application, encoding the APP-02 active-count defect (D21). WITHDRAWN is not an active state, so the correct expectation is 1.

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. Run: cd portal && ./mvnw test -Dtest=ApplicationServiceTest#withdrawnApplicationsRemainInHistoryCount.

**Expected result:** countActive = 1 (only the submitted application is active).

**Actual result:** The test asserts 5 and passes on the buggy build.

**Severity:** Minor
**Priority:** P3
**Category:** tests
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** portal/src/test/.../ApplicationServiceTest.java.
**Discovered by:** Khalil Zakout
**Technique that found it:** Test-suite review
