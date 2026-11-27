# [D39] A refused application shows a generic message, not the reason

**Requirement violated:** USA-01

**Description:**
USA-01: every refused operation tells the user the specific reason. `ApplicationController.apply` catches the business-rule exception and replaces its message with a generic "Unable to submit your application. Please check the posting and try again.", hiding whether the letter is too short, the limit is reached, or a duplicate exists.

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. As a student, submit an application with a 20-character letter.

**Expected result:** "The motivation letter must have between 100 and 2000 characters …".

**Actual result:** "Unable to submit your application. Please check the posting and try again.".

**Severity:** Minor
**Priority:** P3
**Category:** ui
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** tests/system/reproduce.py prints "[D39] DEFECT refused apply shows generic message: Unable to submit your application. Please check the posting and try again."
**Discovered by:** Khalil Zakout
**Technique that found it:** Usability / error-message review
