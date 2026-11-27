# [D33] Letter-feedback cache ignores the letter content

**Requirement violated:** AI-08

**Description:**
AI-08: feedback is cached per student, posting and letter content; the same letter returns the identical result within 10 minutes. `FeedbackCache.key` is `studentId|postingId` only, so a student who edits their letter and asks again gets the stale result for the old letter — and a changed letter is never re-evaluated within the window.

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. Log in as student.khalid, open posting 2 and ask for letter feedback with a short letter: "I would like this internship. I enjoy working on projects." (built-in simulated assistant, no AI key needed). Note the score (25).
2. Within 10 minutes, replace the letter with a long one that names Java, Spring Boot, SQL, REST, JUnit, Git and Linux, and ask for feedback again.
3. Control: log in as student.noor and ask for feedback on the same long letter.

**Expected result:** The new letter is evaluated (AI-08 keys on letter content).

**Actual result:** Khalid's second, completely different letter gets the same result as the first (score 25), while the same long letter evaluated fresh for Noor scores 63. The cache key ignores the letter text.

**Severity:** Major
**Priority:** P2
**Category:** ai
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** tests/system/reproduce.py prints "[D33] DEFECT same student, new letter scored 25 (= first letter 25); the new letter alone scores 63" (27/11/2026). Cause: FeedbackCache key = student + posting only.
**Discovered by:** Abdulaziz Debs
**Technique that found it:** Metamorphic testing (change the input, the output must change) on the system
