# [D29] Password change accepts a password with no digit

**Requirement violated:** USR-02

**Description:**
USR-02: passwords have at least 10 characters including at least one digit, and the rule applies when any user changes their password. `UserService.changePassword` only checks the length, so a 10+ character password with no digit is accepted on change (creation enforces the digit correctly).

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. Log in as a student and change the password to "abcdefghijkl" (12 letters, no digit).
2. Log in again with the new password.

**Expected result:** Refused: the password needs at least one digit.

**Actual result:** Accepted; the new password works.

**Severity:** Major
**Priority:** P2
**Category:** security
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** tests/system/reproduce.py prints "[D29] DEFECT password changed to 12 letters with no digit". Control: Coordinator -> Users rejects the same password when creating a user.
**Discovered by:** Abdulaziz Debs
**Technique that found it:** Boundary value analysis
