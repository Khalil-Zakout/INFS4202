# [D13] Match skill comparison is case- and space-sensitive

**Requirement violated:** POS-06

**Description:**
Skill comparison must ignore letter case and surrounding spaces. The Engine compares skills exactly, so " java " does not match "Java" and scores drop to 0 for required skills that differ only in case or spacing.

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. POST /match with studentSkills=[" java ", "SQL"], requiredSkills=["Java", "sql"].

**Expected result:** score = 70 (both required matched).

**Actual result:** score = 30 / no required matched.

**Severity:** Major
**Priority:** P1
**Category:** integration
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** api:Match.test_TC_ENG_MATCH_03_case_and_space_insensitive_DEFECT.
**Discovered by:** Monir Skaik
**Technique that found it:** Equivalence partitioning
