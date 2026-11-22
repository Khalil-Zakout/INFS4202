# [D08] Student name, number and GPA are sent to the AI provider

**Requirement violated:** AI-03

**Description:**
AI-03/AI-10: the request to the provider contains only the posting title, the skills and the letter — never the student's name, number, e-mail or GPA. `PromptBuilder.postingAndLetter` prepends `Student: <full name> (<student number>), GPA <gpa>` to the prompt, so personal data is sent to a third party on every feedback/questions request with a real provider configured.

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. As coordinator, configure any OpenAI-compatible provider (a local echo endpoint suffices).
2. As a student, request letter feedback on a posting.
3. Capture the outgoing request body.

**Expected result:** The request carries only posting title, required/nice-to-have skills and the letter.

**Actual result:** The system prompt contains `Student: Amal Al-Kuwari (20231001), GPA 3.40`.

**Severity:** Critical
**Priority:** P1
**Category:** security
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** Captured request body (tests/ai-eval and the capture harness); ai:test_prompt_properties.
**Discovered by:** Abdulaziz Debs
**Technique that found it:** Integration + prompt capture
