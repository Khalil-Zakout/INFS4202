# [D25] Academic standing is not recomputed when the Coordinator changes the GPA

**Requirement violated:** STU-03

**Description:**
STU-03: standing is derived (GPA below 2.00 → PROBATION) and recomputed whenever a Coordinator updates the GPA. `StudentService.updateAcademicRecord` saves the GPA but never recomputes `standing`, so a student dropped below 2.00 keeps GOOD standing (and the wrong application limit).

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. As coordinator, open a GOOD student and set the GPA to 1.50, Save.

**Expected result:** Standing becomes PROBATION.

**Actual result:** Standing stays GOOD.

**Severity:** Major
**Priority:** P2
**Category:** functional
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** qa:PortalDefectTest.loweringGpaBelowTwoSetsProbation.
**Discovered by:** Khalil Zakout
**Technique that found it:** White-box review + unit test
