# [D02] Filling a posting does not reject its remaining active applications

**Requirement violated:** OFF-03

**Description:**
OFF-03: when the last seat is taken the posting becomes FILLED and its remaining active applications become REJECTED. `OfferService.accept` sets the posting FILLED but never rejects the other active applications, so candidates stay OFFERED/SUBMITTED on a posting that can no longer place them.

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. On a fresh start, "Sustainability Reporting Intern" (Doha Energy, 1 seat) has three applicants: Ibrahim Al-Kuwari (OFFERED), Mubarak Al-Jaber (OFFERED), Ruqaya Al-Thani (SUBMITTED).
2. Log in as student.ibrahim and accept the offer.
3. As the coordinator, open the other two applications and the posting.

**Expected result:** Posting is FILLED; Mubarak's and Ruqaya's applications are REJECTED (OFF-03).

**Actual result:** Posting is FILLED but Mubarak stays OFFERED and Ruqaya stays SUBMITTED.

**Severity:** Critical
**Priority:** P1
**Category:** state
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** qa:PortalDefectTest.fillingThePostingRejectsTheOtherActiveApplications.
**Discovered by:** Khalil Zakout
**Technique that found it:** State-transition testing
