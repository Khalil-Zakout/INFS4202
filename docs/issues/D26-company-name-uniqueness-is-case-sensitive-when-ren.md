# [D26] Company name uniqueness is case-sensitive when renaming

**Requirement violated:** COM-03

**Description:**
COM-03: company names are unique ignoring case and surrounding spaces. Registration enforces this, but `CompanyService.update` uses `existsByNameAndIdNot`, a case-sensitive derived query, so a company can be renamed to an existing name in a different case.

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. As recruiter.gulfbank, rename the company to "qtech solutions" (QTech Solutions exists).

**Expected result:** Refused (name already exists, ignoring case).

**Actual result:** Saved; two companies now share the name QTech Solutions / qtech solutions.

**Severity:** Major
**Priority:** P2
**Category:** functional
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** qa:PortalDefectTest.renamingToAnExistingNameInAnotherCaseIsRefused.
**Discovered by:** Khalil Zakout
**Technique that found it:** Equivalence partitioning
