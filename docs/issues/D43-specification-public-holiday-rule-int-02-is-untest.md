# [D43] Specification: public-holiday rule (INT-02) is untestable and unenforced

**Requirement violated:** INT-02

**Description:**
INT-02 forbids interviews on public holidays, and INT-05 says slot validation (INT-02 and INT-03) is performed by the Engine's schedule endpoint. But the Engine contract (`openapi.yaml`, /schedule/validate) has no holiday input and no holiday list, and the Portal sends none, so the "except on public holidays" clause can never be enforced or tested. The Engine accepts an interview on a Qatar public holiday (e.g. a Tuesday Sport Day).

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. Quote INT-02, INT-05 and the /schedule/validate schema.
2. POST /schedule/validate for a weekday public holiday — it is accepted.

**Expected result:** Either the contract carries the holiday calendar (so INT-02 is enforceable) or INT-02 drops the clause.

**Actual result:** No holiday data flows to the Engine; holidays are silently allowed.

**Severity:** Major
**Priority:** P2
**Category:** requirements
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** openapi.yaml /schedule/validate schema; Engine accepts a public-holiday weekday slot.
**Discovered by:** Monir Skaik
**Technique that found it:** Specification review
