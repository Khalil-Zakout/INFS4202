# [D36] Engine rejects an interview of exactly 120 minutes

**Requirement violated:** INT-02

**Description:**
INT-02: a slot lasts 15 to 120 minutes (inclusive). A slot of exactly 120 minutes is rejected.

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. POST /schedule/validate with a Sunday slot 10:00–12:00.

**Expected result:** valid = true.

**Actual result:** valid = false ("Duration must be between 15 and 120 minutes").

**Severity:** Minor
**Priority:** P3
**Category:** functional
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** api:Schedule.test_TC_ENG_SLOT_02_exactly_120_minutes_is_valid_DEFECT.
**Discovered by:** Monir Skaik
**Technique that found it:** Boundary value analysis
