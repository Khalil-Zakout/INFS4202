# [D17] Engine accepts interviews that end after 18:00

**Requirement violated:** INT-02

**Description:**
INT-02: an interview must end at or before 18:00. The Engine checks the start time but not the end, so slots ending at 18:01 or 18:15 are accepted.

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. POST /schedule/validate with a Sunday slot 17:01–18:01 (and 17:30–18:15).

**Expected result:** valid = false (ends after 18:00).

**Actual result:** valid = true.

**Severity:** Major
**Priority:** P2
**Category:** integration
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** api:Schedule.test_TC_ENG_SLOT_03_must_end_by_18_00_DEFECT.
**Discovered by:** Monir Skaik
**Technique that found it:** Boundary value analysis
