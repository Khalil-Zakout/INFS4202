# [D23] Offer response deadline is rounded to midnight and drops the time

**Requirement violated:** OFF-02

**Description:**
OFF-02: the student must respond within the response window (default 72 hours). `OfferService.responseDeadline` computes `issuedAt.toLocalDate().plusDays(hours/24).atStartOfDay()`, which truncates to midnight and uses integer day division, so the deadline is earlier than 72 hours (and wrong for any window that is not a whole number of days).

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. As a recruiter, issue an offer at, say, 13:30.
2. Read the offer's "Answer by" time.

**Expected result:** 72 hours later, same time of day (e.g. 23/11 13:30).

**Actual result:** Midnight of that day (23/11 00:00) — about 13.5 hours early.

**Severity:** Major
**Priority:** P2
**Category:** functional
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** qa:PortalDefectTest.offerDeadlineKeepsTheTimeOfDay.
**Discovered by:** Khalil Zakout
**Technique that found it:** Boundary value analysis
