# [D47] An ACCEPTED application can be withdrawn via a direct POST

**Requirement violated:** APP-08

**Description:**
APP-06/APP-08: ACCEPTED is final and an accepted application cannot be withdrawn. `ApplicationService.withdraw` sets the state to WITHDRAWN directly (`a.setState(WITHDRAWN)`) without going through the state machine, so a direct POST withdraws an ACCEPTED placement. The button is hidden in the UI but the endpoint is reachable.

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. Log in as student.amna (has an ACCEPTED application, id 116).
2. POST /applications/116/withdraw.

**Expected result:** Refused: an ACCEPTED application cannot be withdrawn (APP-08).

**Actual result:** The application becomes WITHDRAWN; the confirmed placement is lost (the seat stays taken, leaving the data inconsistent).

**Severity:** Critical
**Priority:** P1
**Category:** state
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** Reproduced on app 116; `withdraw()` bypasses `ApplicationStateMachine`.
**Discovered by:** Khalil Zakout
**Technique that found it:** State-transition testing (direct URL)
