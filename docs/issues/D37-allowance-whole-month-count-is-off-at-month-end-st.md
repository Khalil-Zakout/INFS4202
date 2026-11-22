# [D37] Allowance whole-month count is off at month-end start dates

**Requirement violated:** OFF-05

**Description:**
OFF-05: a month runs from a day to the day before the same day of the next month; when the next month has no such day, the month runs to the end of that next month. For a start date of 31 Jan to 28 Feb (a whole month by that rule) the Engine reports 1.03 months and adds a spurious extra day.

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. POST /allowance monthlyAllowance=3000, startDate 2027-01-31, endDate 2027-02-28, 40h.

**Expected result:** 1 month (base 3000.00).

**Actual result:** 1.03 months (base 3100.00).

**Severity:** Minor
**Priority:** P3
**Category:** integration
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** Engine /allowance output; see docs/test-cases TC-ENG (allowance boundary).
**Discovered by:** Monir Skaik
**Technique that found it:** Boundary value analysis
