# [D42] The AI prompt's worked example is malformed

**Requirement violated:** AI-11

**Description:**
AI-11: every prompt states the scale, the number of items and the exact format, with examples consistent with that format. The feedback prompt's example uses "score": 8.5 (a non-integer on the wrong scale) and instructs "Always give exactly three strengths", contradicting "1 to 5 strengths".

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. Read PromptBuilder.FEEDBACK_INSTRUCTIONS (or capture the prompt).

**Expected result:** The example is a valid answer in the required 0–100 integer format and is consistent with the item counts.

**Actual result:** The example shows 8.5 and the instructions demand exactly three strengths.

**Severity:** Minor
**Priority:** P3
**Category:** ai
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** ai:test_prompt_properties.test_v1_example_score_is_malformed_DEFECT.
**Discovered by:** Abdulaziz Debs
**Technique that found it:** White-box review
