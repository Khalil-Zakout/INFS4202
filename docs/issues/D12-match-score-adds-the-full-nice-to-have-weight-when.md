# [D12] Match score adds the full nice-to-have weight when the list is empty

**Requirement violated:** POS-01

**Description:**
score = 70×(matched required/required) + 30×(matched nice/nice, or 0 when the nice list is empty). When a posting lists no nice-to-have skills the Engine adds the whole 30 points instead of 0, inflating every such posting's scores by 30.

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. POST /match with studentSkills=requiredSkills=[Java,SQL,Spring] and niceToHaveSkills=[].

**Expected result:** score = 70.

**Actual result:** score = 100.

**Severity:** Major
**Priority:** P1
**Category:** integration
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** api:Match.test_TC_ENG_MATCH_01_all_required_no_nice_is_70_DEFECT.
**Discovered by:** Monir Skaik
**Technique that found it:** Decision table
