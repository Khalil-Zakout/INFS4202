# [D06] API key and SMTP password are written to the log and shown in plaintext

**Requirement violated:** SEC-04

**Description:**
SEC-04: secrets are never written to logs and are masked on screen. On saving Settings, `SettingsController.save` logs the old and new values of every changed key, including the AI API key and SMTP password, in plaintext; and the Settings page renders them in the input's `value` attribute (the masked hint is shown next to, not instead of, the real value).

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. As coordinator, open Settings, set an AI provider API key and an SMTP password, Save.
2. Inspect logs/portal.log and view-source of /coordinator/settings.

**Expected result:** Secrets never appear in the log and are masked on screen (SEC-04).

**Actual result:** `Setting ai.apiKey changed from '' to 'sk-...'` appears in the log; the HTML `value="sk-..."` carries the key.

**Severity:** Critical
**Priority:** P1
**Category:** security
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** logs/portal.log lines and page source captured in the issue.
**Discovered by:** Abdulaziz Debs
**Technique that found it:** Security testing (secret handling)
