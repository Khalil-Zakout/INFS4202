# [D41] Letter feedback names the wrong model

**Requirement violated:** AI-07

**Description:**
AI-07: the screen names the model that produced the result. For feedback, `AiAssistantService.feedback` labels the source with the constant `AiClient.DEFAULT_MODEL` ("gpt-4o-mini") instead of the configured model, so the screen names the wrong model whenever a different one is configured (the interview-questions path labels it correctly).

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. Configure a model name other than gpt-4o-mini; request letter feedback.

**Expected result:** The screen names the configured model.

**Actual result:** It always says "Model gpt-4o-mini".

**Severity:** Minor
**Priority:** P3
**Category:** ai
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** Observed source label vs configured model; AiAssistantService.feedback.
**Discovered by:** Abdulaziz Debs
**Technique that found it:** White-box review
