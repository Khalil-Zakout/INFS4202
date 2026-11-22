# [D04] A suspended company's applications are not frozen

**Requirement violated:** COM-02

**Description:**
COM-02: when a company is suspended, its applications are frozen (no state changes) until it is approved again. `ApplicationService.assertNotFrozen` only blocks companies that are PENDING, not SUSPENDED, so recruiters can still shortlist/reject and students can still accept offers while the company is suspended.

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. As coordinator, suspend "Pearl Logistics" (Companies page).
2. Log in as recruiter.pearl and reject any of its applications — or as student.amal accept the pending Pearl offer (app id 3).

**Expected result:** Every state change is refused while the company is suspended (COM-02).

**Actual result:** The rejection and the acceptance both succeed.

**Severity:** Critical
**Priority:** P1
**Category:** functional
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** qa:PortalDefectTest.suspendedCompanyApplicationsAreFrozen.
**Discovered by:** Khalil Zakout
**Technique that found it:** State-transition testing
