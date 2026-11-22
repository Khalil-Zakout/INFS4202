# [D31] CSRF protection is disabled on the Settings endpoints

**Requirement violated:** SEC-02

**Description:**
SEC-02: every form that changes data is protected against CSRF. `SecurityConfig` calls `csrf.ignoringRequestMatchers("/coordinator/settings/**")`, so the Settings save and the AI "Test connection" accept cross-site POSTs with no token — and Settings control thresholds, the Engine URL and secrets.

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. As coordinator, POST to /coordinator/settings with valid fields but no _csrf parameter.

**Expected result:** Rejected (403) for the missing CSRF token.

**Actual result:** Accepted (302, "Settings saved").

**Severity:** Major
**Priority:** P2
**Category:** security
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** qa:SecurityAccessTest.settingsPostWithoutCsrfTokenIsRejected.
**Discovered by:** Abdulaziz Debs
**Technique that found it:** Security testing (CSRF)
