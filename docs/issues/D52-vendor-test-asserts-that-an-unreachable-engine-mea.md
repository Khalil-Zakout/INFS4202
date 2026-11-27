# [D52] Vendor test asserts that an unreachable Engine means eligible

**Requirement violated:** REL-01

**Description:**
The vendor's own test `EngineClientTest.engineUnavailableDegradesGracefully` stubs the Engine to answer 503 and then asserts `r.eligible()` is true with no reasons. That is the opposite of REL-01 (never treat a student as eligible when the Engine could not be reached): the shipped suite passes because of defect D51 and would fail on a correct fix, so it protects the bug.

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. Open portal/src/test/java/com/halcyon/uniplace/engine/EngineClientTest.java, method `engineUnavailableDegradesGracefully`.
2. Run it: `cd portal` then `.\mvnw.cmd test -Dtest=EngineClientTest` (macOS/Linux `./mvnw test -Dtest=EngineClientTest`).

**Expected result:** The test asserts that a 503 from the Engine leads to a refusal (an exception or a not-eligible result with a reason), as REL-01 requires.

**Actual result:** The test asserts `assertTrue(r.eligible())` and passes on the vendor build.

**Severity:** Minor
**Priority:** P3
**Category:** tests
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** EngineClientTest lines 102-108; passes with the build (147 of 147 vendor tests pass), while our qa:EngineOutageTest for the same requirement fails.
**Discovered by:** Monir Skaik
**Technique that found it:** Review of the vendor's test suite against the Requirements
