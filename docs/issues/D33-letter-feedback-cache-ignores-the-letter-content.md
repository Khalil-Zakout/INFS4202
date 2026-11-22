# [D33] Letter-feedback cache ignores the letter content

**Requirement violated:** AI-08

**Description:**
AI-08: feedback is cached per student, posting and letter content; the same letter returns the identical result within 10 minutes. `FeedbackCache.key` is `studentId|postingId` only, so a student who edits their letter and asks again gets the stale result for the old letter — and a changed letter is never re-evaluated within the window.

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. As a student, request feedback on a posting with letter A.
2. Within 10 minutes, change the letter substantially and request feedback again on the same posting.

**Expected result:** The new letter is evaluated (AI-08 keys on letter content).

**Actual result:** The cached result for letter A is returned; no new provider call is made.

**Severity:** Major
**Priority:** P2
**Category:** ai
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** Capture shows one provider call for two different letters on the same posting.
**Discovered by:** Abdulaziz Debs
**Technique that found it:** Metamorphic testing
