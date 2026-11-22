# [D15] aboveCut returns one id more than the number of seats

**Requirement violated:** APP-09

**Description:**
`aboveCut` must hold the first `seats` identifiers of `ranked`. The Engine returns seats+1 ids, so the recruiter's "within seats" marking always includes one candidate too many.

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. POST /rank with seats=1 and three candidates.

**Expected result:** aboveCut has 1 id.

**Actual result:** aboveCut has 2 ids.

**Severity:** Major
**Priority:** P1
**Category:** integration
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** api:Rank.test_TC_ENG_RANK_03_above_cut_has_exactly_seats_ids_DEFECT.
**Discovered by:** Monir Skaik
**Technique that found it:** Boundary value analysis
