# [D03] Two students can accept offers for the last seat at the same moment

**Requirement violated:** OFF-04

**Description:**
OFF-04: if two students accept offers for the last seat simultaneously, exactly one succeeds. `OfferService.accept` checks `seatsLeft()` and increments `seatsTaken` without any lock or optimistic version, so concurrent acceptances both succeed and the seat count exceeds the seats.

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. "Sustainability Reporting Intern" has 1 seat and two pending offers (Ibrahim app id 7, Mubarak app id 8).
2. POST /offers/2/accept (Ibrahim) and /offers/3/accept (Mubarak) concurrently (see tests/system seat-race).
3. As coordinator open the posting and both applications.

**Expected result:** One acceptance succeeds; the other is refused with an explanation (OFF-04). Seats never exceed 1.

**Actual result:** Both acceptances succeed; both applications become ACCEPTED and the posting's seatsTaken = 2 on a 1-seat posting.

**Severity:** Critical
**Priority:** P1
**Category:** state
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** Reproduced on the first of six parallel attempts; tests/system/seat_race.py.
**Discovered by:** Khalil Zakout
**Technique that found it:** Concurrency testing
