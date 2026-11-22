# [D32] The AI prompt discloses the internal shortlist threshold

**Requirement violated:** AI-10

**Description:**
AI-10: prompts contain no internal business rules or thresholds. The feedback prompt includes "Internal note: recruiters reject applications that score below 60, so be strict around that value", steering the model with an internal rule and biasing scores around 60.

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. Configure a provider and capture the request for letter feedback (or read PromptBuilder).

**Expected result:** The prompt carries only the posting and the letter.

**Actual result:** The prompt contains the "reject below 60" internal note.

**Severity:** Major
**Priority:** P2
**Category:** ai
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** ai:test_prompt_properties.test_v1_contains_internal_threshold_DEFECT; captured prompt.
**Discovered by:** Abdulaziz Debs
**Technique that found it:** White-box review + prompt capture
