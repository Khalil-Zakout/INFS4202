# [D06] API key and SMTP password are written to the log and shown in plaintext

**Requirement violated:** SEC-04

**Description:**
SEC-04: secrets are never written to logs and are masked on screen. On saving Settings, `SettingsController.save` logs the old and new values of every changed key, including the AI API key and SMTP password, in plaintext; and the Settings page renders them in the input's `value` attribute (the masked hint is shown next to, not instead of, the real value).

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. As coordinator open Coordinator -> Settings, enter AI API key `sk-demo-SECRET-0001` and SMTP password `Smtp-SECRET-0002`, press Save settings.
2. Look at the Portal console window (the terminal where start.sh / start.cmd runs the Portal).
3. Reload Settings and open the page source (Ctrl+U); search for SECRET.

**Expected result:** Secrets never appear in the log and are masked on screen (SEC-04).

**Actual result:** The console log prints both secrets in clear text, and the page source contains both values in the input fields (only masked on screen).

**Severity:** Critical
**Priority:** P1
**Category:** security
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** Console log line (27/11/2026): "c.h.uniplace.web.SettingsController : Setting ai.apiKey changed from '' to 'sk-demo-SECRET-0001' by coordinator" (same for smtp.password). tests/system/reproduce.py prints "[D06] DEFECT secret in log=True, in settings HTML value=True".
**Discovered by:** Abdulaziz Debs
**Technique that found it:** Security testing (secret handling)
