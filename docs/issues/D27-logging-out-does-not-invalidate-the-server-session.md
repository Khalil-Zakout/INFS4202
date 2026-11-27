# [D27] Logging out does not invalidate the server session

**Requirement violated:** USR-04

**Description:**
USR-04: logging out invalidates the session immediately. The app's "Log out" posts to `/account/logout`, which only clears the JSESSIONID cookie in the browser and redirects; it never invalidates the HttpSession. A captured session id keeps working after logout.

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. Log in as a student; note the JSESSIONID.
2. Click Log out (POST /account/logout).
3. Replay a request with the old JSESSIONID cookie.

**Expected result:** The old session is invalid; the request is sent to login.

**Actual result:** The old session still loads the dashboard.

**Severity:** Major
**Priority:** P2
**Category:** security
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** tests/system/reproduce.py prints "[D27] DEFECT old session id still authenticated after /account/logout". Control: Spring's own /logout does invalidate the session; the app's /account/logout only deletes the cookie.
**Discovered by:** Abdulaziz Debs
**Technique that found it:** Session management testing
