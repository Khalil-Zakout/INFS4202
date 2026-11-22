# [D01] Match score is cached per posting and shared across students

**Requirement violated:** APP-04

**Description:**
The stored match score of an application is taken from a cache keyed only by posting id and its required skills (`MatchScoreService.key`), ignoring the student's own skills. The first applicant to a posting populates the cache; every later applicant to the same posting is given the first applicant's score. Match score drives shortlisting (APP-07), ranking (APP-09) and the average-score report (ADM-02), so all of these are corrupted.

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. Log in as student.amal and apply to "Supply Chain Intern" (Pearl Logistics). Score shown: 35.
2. Log in as student.mubarak (Mubarak Al-Jaber) and apply to the same posting.
3. Open the application (as the recruiter or coordinator) and read its match score.

**Expected result:** Mubarak's skills (Excel, SQL, Power BI) match the posting fully, so his score is 100 (POST /match confirms 100).

**Actual result:** The application stores 35 — Amal's cached score — not 100.

**Severity:** Critical
**Priority:** P1
**Category:** integration
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** Engine /match returns 100 for Mubarak's skills but the Portal stores 35; `MatchScoreService.key()` omits studentSkills. qa:PortalDefectTest.matchScoreIsNotSharedBetweenStudents.
**Discovered by:** Khalil Zakout
**Technique that found it:** White-box code review + integration test
