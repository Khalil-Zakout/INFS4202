# [D30] Error pages expose stack traces and SQL

**Requirement violated:** SEC-03

**Description:**
SEC-03: error pages never show stack traces, SQL, class names or other internals. `application.properties` sets `server.error.include-stacktrace=always` and `include-exception=true`, and the error template renders them, so a bad parameter shows a full Spring stack trace; an over-long shortlist justification shows the failing SQL INSERT.

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. Open /postings?minAllowance=3,000 (a comma makes the BigDecimal conversion fail).
2. Or shortlist with a justification longer than 1000 characters.

**Expected result:** A friendly error page with no internal details.

**Actual result:** The page shows the exception class, message and stack frames (and the audit-log SQL in the second case).

**Severity:** Major
**Priority:** P2
**Category:** security
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** tests/system stacktrace; captured page bodies.
**Discovered by:** Abdulaziz Debs
**Technique that found it:** Security testing (information disclosure)
