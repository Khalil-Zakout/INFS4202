# [D45] Vendor test encodes the wrong probation limit

**Requirement violated:** APP-02

**Description:**
`ApplicationServiceTest.probationStudentUsesStandardLimit` asserts that a probation student's active limit is 5, baking the APP-02 defect (D22) into the test suite. The test name even calls it the "standard" limit. A correct test would expect 2.

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. Run: cd portal && ./mvnw test -Dtest=ApplicationServiceTest#probationStudentUsesStandardLimit.

**Expected result:** The test expects the probation limit of 2 (APP-02).

**Actual result:** The test asserts 5 and passes on the buggy build.

**Severity:** Minor
**Priority:** P3
**Category:** tests
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** portal/src/test/.../ApplicationServiceTest.java.
**Discovered by:** Khalil Zakout
**Technique that found it:** Test-suite review
