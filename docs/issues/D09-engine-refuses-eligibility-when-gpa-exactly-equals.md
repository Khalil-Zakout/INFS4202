# [D09] Engine refuses eligibility when GPA exactly equals the minimum

**Requirement violated:** POS-01

**Description:**
The eligibility rule is "GPA at least minGpa". The Engine uses a strict greater-than, so a GPA equal to the minimum is reported ineligible.

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. POST /api/v1/eligibility with gpa=2.00 and minGpa=2.00 (CV+transcript valid).

**Expected result:** eligible = true (2.00 is at least 2.00).

**Actual result:** eligible = false, reason "GPA 2.0 is below the minimum 2.0".

**Severity:** Major
**Priority:** P2
**Category:** integration
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** api:Eligibility.test_TC_ENG_ELIG_02_gpa_equal_to_minimum_is_eligible_DEFECT.
**Discovered by:** Monir Skaik
**Technique that found it:** Boundary value analysis
