# [D19] No transport supplement at exactly 30 weekly hours

**Requirement violated:** OFF-05

**Description:**
OFF-05: the transport supplement applies when weekly hours are 30 or more. At exactly 30 hours the Engine omits it, so a 30-hour placement is under-paid. This shows end-to-end: a seeded 30-hour placement's allowance statement has no transport line.

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. POST /allowance with weeklyHours=30 (one month, 3000).
2. Or: accept the 30-hour "Sustainability Reporting Intern" placement and read its statement.

**Expected result:** Base + transport (total 3300 for one month).

**Actual result:** Base only (3000); no transport line.

**Severity:** Major
**Priority:** P2
**Category:** integration
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** api:Allowance.test_TC_ENG_ALLOW_02_transport_at_exactly_30_hours_DEFECT.
**Discovered by:** Monir Skaik
**Technique that found it:** Boundary value analysis
