# [D18] Back-to-back interviews are rejected as overlapping

**Requirement violated:** INT-03

**Description:**
INT-03: a slot that starts exactly when another ends does not overlap it. The Engine treats touching slots as overlapping, so a recruiter or student cannot schedule consecutive interviews.

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. POST /schedule/validate with candidate 11:00–12:00 and an existing recruiter slot 10:00–11:00.

**Expected result:** valid = true (back-to-back allowed).

**Actual result:** valid = false ("Overlaps with an interview of the recruiter").

**Severity:** Major
**Priority:** P2
**Category:** integration
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** api:Schedule.test_TC_ENG_SLOT_04_back_to_back_is_allowed_DEFECT.
**Discovered by:** Monir Skaik
**Technique that found it:** Boundary value analysis
