# [D49] Students and recruiters can open the Coordinator reports and export them as CSV

**Requirement violated:** USR-05, SEC-05

**Description:**
USR-05: a Recruiter sees only data of their own company and a Student only their own data; SEC-05: access control is enforced on the server for every request. The Coordinator reports (ADM-02) show the average match score per company, offers issued versus accepted and placement rates per program. `/coordinator/reports` and `/coordinator/reports/{name}.csv` are missing from the Coordinator-only rule in `SecurityConfig`, and the controller does not check the role, so any logged-in user can read every company's figures by typing the URL.

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. Log in as recruiter.gulfbank (or as student.omar).
2. Type the address http://127.0.0.1:8080/coordinator/reports .
3. Type http://127.0.0.1:8080/coordinator/reports/scores.csv .

**Expected result:** Access-denied page (HTTP 403) for both addresses: reports are for the Coordinator only.

**Actual result:** Both pages are served (HTTP 200): the recruiter sees the average match score and application count of every other company, and the CSV downloads.

**Severity:** Critical
**Priority:** P1
**Category:** security
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** qa:SecurityAccessTest.recruiterCannotOpenCoordinatorReports fails (expected 403, got 200). tests/system/reproduce.py prints "[D49] DEFECT recruiter.gulfbank /coordinator/reports -> 200; student.omar /coordinator/reports/scores.csv -> 200 (CSV starts: Company,Average score,Applications ...)" (27/11/2026). Source: SecurityConfig lines 28-31 list every /coordinator area except /coordinator/reports.
**Discovered by:** Abdulaziz Debs
**Technique that found it:** Forced browsing (URL tampering) + white-box review of SecurityConfig
