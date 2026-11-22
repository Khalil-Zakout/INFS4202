# [D35] List pages are not paginated (Outbox and Postings)

**Requirement violated:** PERF-05

**Description:**
PERF-05: no page returns an unbounded list; every list is paginated or limited. The coordinator Outbox (`CoordinatorController.outbox`) wraps the full notification list in a single `PageImpl`, and the student postings list returns every visible posting, so both grow without bound with volume data.

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. As coordinator, generate volume data (Tools → Generate, 1000).
2. Open /coordinator/outbox and /postings.

**Expected result:** At most 20 rows per page with a pager.

**Actual result:** The Outbox shows 1117 rows on one page; the postings list shows all postings. No pager.

**Severity:** Major
**Priority:** P2
**Category:** performance
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** perf:portal_pages.py (rows/page = 1117 for Outbox).
**Discovered by:** Monir Skaik
**Technique that found it:** Performance / volume testing
