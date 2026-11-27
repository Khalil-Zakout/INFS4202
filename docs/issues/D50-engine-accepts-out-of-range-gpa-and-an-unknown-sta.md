# [D50] Engine accepts out-of-range GPA and an unknown standing instead of answering 400

**Requirement violated:** REL-02, Requirements section 3 (Errors)

**Description:**
REL-02: the Engine answers invalid input with HTTP 400 and a JSON body naming the invalid field. Section 3 of the Requirements adds: numeric fields outside their domain (negative GPA, GPA above 4.00, seats of 0) are validation errors; openapi.yaml declares gpa with minimum 0 and maximum 4 and standing as GOOD or PROBATION. POST /eligibility instead evaluates such requests and answers 200, so a caller gets an eligibility decision computed from impossible data. The Portal itself refuses GPAs outside 0.00-4.00, so the effect today is limited to other callers of the Engine.

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. With the Engine running, POST to http://127.0.0.1:8081/api/v1/eligibility the JSON {"gpa":4.01,"creditsCompleted":60,"standing":"GOOD","priorInternships":0,"minGpa":2.0,"minCredits":30,"documents":[],"asOf":"2026-11-27"}.
2. Repeat with "gpa":-0.1, then with "gpa":3.0 and "standing":"BAD".
3. Control: send "creditsCompleted":200 (outside 0-140).

**Expected result:** HTTP 400 with {"error":"validation","field":"gpa"} (or "standing") for the three invalid requests, as for the control.

**Actual result:** All three invalid requests get HTTP 200 and an eligibility answer (for GPA -0.1: "GPA -0.1 is below the minimum 2.0"). The control correctly gets 400 "creditsCompleted must be between 0 and 140".

**Severity:** Minor
**Priority:** P3
**Category:** integration
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** api:Eligibility.test_TC_ENG_ELIG_08_gpa_out_of_domain_is_400_DEFECT fails. Live check on 27/11/2026: gpa 4.01 -> 200, gpa -0.1 -> 200, standing BAD -> 200, creditsCompleted 200 -> 400 {"error":"validation","field":"creditsCompleted","message":"must be between 0 and 140"}.
**Discovered by:** Monir Skaik
**Technique that found it:** Equivalence partitioning (invalid classes) + boundary value analysis, black-box
