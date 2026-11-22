# [D07] Stored XSS via company name on the postings list

**Requirement violated:** SEC-07

**Description:**
SEC-07: all user-entered text is escaped when displayed. `templates/postings/list.html` renders the company name with `th:utext` (unescaped). A recruiter who sets their company name to an HTML/script payload has it executed in the browser of every student who opens the postings list.

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. Log in as recruiter.qtech and set the company name to `QTech <img src=x onerror=alert(document.cookie)>`.
2. Log in as any student and open /postings.

**Expected result:** The name is shown as text; no markup executes (SEC-07).

**Actual result:** The <img> tag is injected unescaped and the onerror handler runs.

**Severity:** Critical
**Priority:** P1
**Category:** security
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** Raw payload present in the /postings response; `th:utext` in postings/list.html.
**Discovered by:** Abdulaziz Debs
**Technique that found it:** Stored XSS
