# [D10] Transcript valid-window is one day short (day 180 rejected)

**Requirement violated:** STU-04

**Description:**
A transcript is valid for 180 days counting the issue date as day 1, so an issue date 179 days before `asOf` is day 180 and still valid. The Engine rejects it.

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. POST /eligibility with the transcript issued exactly 179 days before asOf.

**Expected result:** eligible = true (day 180 is within the 180-day window).

**Actual result:** eligible = false ("not valid on …").

**Severity:** Major
**Priority:** P2
**Category:** integration
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** api:Eligibility.test_TC_ENG_ELIG_04_transcript_valid_on_day_180_DEFECT.
**Discovered by:** Monir Skaik
**Technique that found it:** Boundary value analysis
