# [D38] Searching postings by company is not sorted by deadline

**Requirement violated:** POS-06

**Description:**
POS-06: results are sorted by deadline, earliest first. When a company filter is applied, `findVisibleForCompany` orders by posting id, so the results are not deadline-ordered.

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. As a student, open /postings?companyId=1 (QTech).

**Expected result:** Earliest deadline first.

**Actual result:** "Backend Developer Intern" (later deadline) appears before "QA Automation Intern" (today).

**Severity:** Minor
**Priority:** P3
**Category:** functional
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** Rendered order vs deadlines; the unfiltered search orders correctly (contrast).
**Discovered by:** Khalil Zakout
**Technique that found it:** Equivalence / comparison
