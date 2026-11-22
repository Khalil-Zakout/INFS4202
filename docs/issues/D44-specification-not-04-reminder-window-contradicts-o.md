# [D44] Specification: NOT-04 reminder window contradicts OFF-02

**Requirement violated:** NOT-04

**Description:**
NOT-04 states a reminder is recorded "24 hours before the end of the 48-hour response window of a pending offer", but OFF-02 sets the response window from Settings (default 72 hours). The two requirements give different window lengths, so the reminder timing is unspecified. The code reminds 24 h before the actual respond-by, implicitly following OFF-02 and leaving NOT-04's "48-hour" wrong.

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. Quote NOT-04 and OFF-02.

**Expected result:** One consistent response-window length across requirements.

**Actual result:** NOT-04 says 48 hours; OFF-02 says the Settings value (default 72).

**Severity:** Minor
**Priority:** P3
**Category:** requirements
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** Requirements §1.7 (OFF-02) and §1.8 (NOT-04).
**Discovered by:** Monir Skaik
**Technique that found it:** Specification review
