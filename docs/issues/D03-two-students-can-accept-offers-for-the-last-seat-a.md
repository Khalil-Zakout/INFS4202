# [D03] Two students can accept offers for the last seat at the same moment

**Requirement violated:** OFF-04

**Description:**
OFF-04: if two students accept offers for the last seat simultaneously, exactly one succeeds. `OfferService.accept` checks `seatsLeft()` and increments `seatsTaken` without any lock or optimistic version, so concurrent acceptances both succeed and the seat count exceeds the seats.

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. On a fresh start, "Sustainability Reporting Intern" (Doha Energy Partners, 1 seat) has two pending offers: Ibrahim (application 7) and Mubarak (application 8).
2. Log in as student.ibrahim and as student.mubarak in two browsers (or two private windows) and press Accept on both offers at the same moment. The script `python tests/system/seat_race.py` does exactly this with two parallel requests.
3. As coordinator, open the posting and both applications.

**Expected result:** One acceptance succeeds; the other is refused with an explanation (OFF-04). Seats never exceed 1.

**Actual result:** Both applications are ACCEPTED while the posting shows 1 seat, 0 left, status FILLED: two students hold one seat.

**Severity:** Critical
**Priority:** P1
**Category:** state
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** Output of `tests/system/seat_race.py` on a fresh start (27/11/2026): "application states: {7: 'Accepted', 8: 'Accepted', 9: 'Submitted'} / posting 8: seats = 1 (0 left), status = Filled / DEFECT reproduced: both acceptances succeeded for one seat." Cause: `OfferService.accept` checks the free seats and then saves without a lock.
**Discovered by:** Khalil Zakout
**Technique that found it:** Concurrency testing
