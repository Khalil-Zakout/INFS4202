# [D11] Engine returns HTTP 500 to well-formed JSON

**Requirement violated:** REL-02

**Description:**
REL-02: the Engine never answers 500 to well-formed JSON; a missing/invalid field is a 400 naming the field. Several well-formed requests crash with 500 instead: eligibility missing priorInternships or minGpa, gpa as a string or null, rank missing seats, allowance missing lateDays or monthlyAllowance, and any request sent with Content-Type text/plain.

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. POST /eligibility omitting priorInternships.
2. POST /rank with candidates but no seats.
3. POST /allowance omitting lateDays.

**Expected result:** 400 with {error, field, message}.

**Actual result:** 500 {"error":"internal","message":"Unexpected error"}.

**Severity:** Major
**Priority:** P1
**Category:** integration
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** api:Eligibility…10, Rank…05, Allowance…07, Robustness…04.
**Discovered by:** Monir Skaik
**Technique that found it:** Equivalence partitioning / negative testing
