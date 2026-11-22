# [D20] Monthly cap ignores the transport supplement

**Requirement violated:** OFF-05

**Description:**
OFF-05: cap adjustment = −(monthlyAllowance + monthly transport − monthlyCap) when positive, i.e. the cap applies to the monthly total after transport. The Engine caps the base allowance only, so the capped total still exceeds the cap once transport is added.

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. POST /allowance monthlyAllowance=3500, one month, 40h, monthlyCap=3000, transport=300.

**Expected result:** total = 3000 (3500+300 capped to 3000).

**Actual result:** total = 3300 (base capped to 3000, then +300 transport).

**Severity:** Major
**Priority:** P2
**Category:** integration
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** api:Allowance.test_TC_ENG_ALLOW_04_cap_includes_transport_DEFECT.
**Discovered by:** Monir Skaik
**Technique that found it:** Decision table
