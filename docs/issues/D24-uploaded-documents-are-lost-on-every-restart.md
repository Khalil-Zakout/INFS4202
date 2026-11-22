# [D24] Uploaded documents are lost on every restart

**Requirement violated:** REL-04

**Description:**
REL-04: restarting loses no committed business data. `DocumentService` stores uploads in a brand-new temporary directory created with `Files.createTempDirectory` on each start, so after a restart every stored document (including the seeded CVs and transcripts) 404s, while the database rows remain.

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. As a student, upload a CV; download it (works).
2. Restart the Portal (./start.sh).
3. Download the same document, or any seeded document (/documents/1).

**Expected result:** The document is still available after the restart.

**Actual result:** 404 Not found; the file path from the previous run no longer exists.

**Severity:** Major
**Priority:** P2
**Category:** configuration
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** A fresh /tmp/uniplace-uploads-* directory per start; documents 404 after restart.
**Discovered by:** Khalil Zakout
**Technique that found it:** Reliability testing (restart)
