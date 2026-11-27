# [D35] List pages are not paginated (Outbox and Postings)

**Requirement violated:** PERF-05

**Description:**
PERF-05: no page returns an unbounded list; every list is paginated or limited. The coordinator Outbox (`CoordinatorController.outbox`) wraps the full notification list in a single `PageImpl`, and the student postings list returns every visible posting, so both grow without bound with volume data.

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. As coordinator, generate volume data (Tools → Generate, 1000).
2. Open /coordinator/outbox and /postings.

**Expected result:** At most 20 rows per page with a pager.

**Actual result:** With 1,000 generated applications the Outbox shows about 1,100 rows on one page and the Postings list 31 rows, with no pager.

**Severity:** Major
**Priority:** P2
**Category:** performance
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** `python tests/performance/portal_pages.py --generate 1000` (27/11/2026): "Outbox (coordinator) rows/page=1121 ... not paginated (PERF-05)" and "Postings (student) rows/page=31 ... not paginated".
**Discovered by:** Monir Skaik
**Technique that found it:** Performance / volume testing
