# [D28] Account lockout can be bypassed by varying the username case

**Requirement violated:** USR-03

**Description:**
USR-03: after 5 consecutive failed logins the account is locked for 15 minutes. `LoginAttemptService.failed` records failures against the raw submitted username, while login resolves the user case-insensitively. Failed attempts sent with a different letter case are never counted, so an attacker can try unlimited passwords and the account never locks.

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. Submit 12 failed logins with the username "Student.Salem" (note the capitals).
2. Then log in as "Student.Salem" with the correct password.

**Expected result:** The account locks after 5 failures (USR-03).

**Actual result:** It never locks; the correct password logs in normally.

**Severity:** Major
**Priority:** P2
**Category:** security
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** tests/system lockout; the exact-case control does lock after 5.
**Discovered by:** Abdulaziz Debs
**Technique that found it:** Security testing
