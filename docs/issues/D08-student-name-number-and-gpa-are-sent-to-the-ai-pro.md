# [D08] Student name, number and GPA are sent to the AI provider

**Requirement violated:** AI-03

**Description:**
AI-03/AI-10: the request to the provider contains only the posting title, the skills and the letter — never the student's name, number, e-mail or GPA. `PromptBuilder.postingAndLetter` prepends `Student: <full name> (<student number>), GPA <gpa>` to the prompt, so personal data is sent to a third party on every feedback/questions request with a real provider configured.

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. Read `PromptBuilder.postingAndLetter` (portal/src/main/java/com/halcyon/uniplace/ai/PromptBuilder.java): it starts the prompt with "Student: <full name> (<student number>), GPA <gpa>".
2. Run `cd portal && ./mvnw test -Dtest=AiPromptDefectTest`; the test builds the real feedback prompt for a student and checks it.
3. Optional on the running system: Coordinator -> Settings, choose provider Ollama or any endpoint you control, request letter feedback as a student and look at the request body.

**Expected result:** The request carries only posting title, required/nice-to-have skills and the letter.

**Actual result:** The request sent to the AI provider contains the student's full name, student number and GPA.

**Severity:** Critical
**Priority:** P1
**Category:** security
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** qa:AiPromptDefectTest.promptCarriesNoPersonalData fails: "AI-03: the student's name is sent to the provider". Source: PromptBuilder line 43.
**Discovered by:** Abdulaziz Debs
**Technique that found it:** Integration + prompt capture
