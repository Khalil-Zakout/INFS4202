# [D14] Candidate ranking breaks GPA ties in ascending order

**Requirement violated:** APP-09

**Description:**
APP-09: order by score descending, then GPA descending. On equal scores the Engine orders by GPA ascending, placing the weakest GPA first.

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. POST /rank with equal scores and GPAs 2.5, 3.9, 3.1.

**Expected result:** ranked = highest GPA first.

**Actual result:** ranked = lowest GPA first.

**Severity:** Major
**Priority:** P1
**Category:** integration
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** api:Rank.test_TC_ENG_RANK_02_gpa_tiebreak_descending_DEFECT.
**Discovered by:** Monir Skaik
**Technique that found it:** Decision table
