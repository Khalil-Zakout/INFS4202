# [D51] When the Engine is down, every student is treated as eligible and applications are accepted with match score 0

**Requirement violated:** REL-01

**Description:**
REL-01: if the Engine is unreachable or returns an error, the Portal refuses the operation with a clear message; it never treats a student as eligible or a result as computed when the Engine could not be reached. `EngineClient.checkEligibility` catches EngineUnavailableException and returns `EligibilityResult.ok()` (eligible, no reasons), and `EngineClient.match` returns a score of 0. So during an Engine outage any student, eligible or not, can apply, and the application is stored with a false match score of 0. `MatchScoreService` then caches that 0 for the posting, so students who apply after the Engine is back still get 0 (see also D01). A score of 0 is below the shortlist threshold, so these students are silently disadvantaged.

**Steps to reproduce** (from a fresh start of the system: `./start.sh --reset`; dates are relative to the day of the start, the login password for every account is `Uniplace!2026`):
1. Start the system (`--reset`) and wait until both parts are up.
2. Stop only the Engine: on Windows close the minimised window "UniPlace Engine - close this window to stop it"; on macOS/Linux stop the `uniplace-engine.jar` process. The Portal keeps running.
3. Log in as student.yousef and apply to posting 1 ("Java, SQL, Spring") with a 200-character letter.
4. Start the Engine again (`java -jar engine/uniplace-engine.jar`), then log in as student.amna (skills Python, SQL, Statistics, Excel) and apply to posting 1.

**Expected result:** Step 3 is refused with a clear message (eligibility cannot be checked). In step 4 Amna's application gets her real match score: 70 x 1/3 required skills = 23.

**Actual result:** Step 3: "Your application was submitted. Match score: 0." although eligibility was never checked. Step 4, with the Engine back: "Your application was submitted. Match score: 0." (the outage's 0 is served from the cache).

**Severity:** Critical
**Priority:** P1
**Category:** integration
**Environment:** Portal (Java 17, Spring Boot 3) + Engine 1.0.0 on 127.0.0.1; Chrome/Firefox current; AI provider only where noted.
**Evidence:** qa:EngineOutageTest.engineErrorIsNeverTreatedAsEligible and engineErrorIsNeverTreatedAsAComputedMatchScore fail ("the Engine answered 503 but the Portal reports the student as eligible"; "... returned a match score of 0"). Reproduced on the running system on 27/11/2026 exactly as in the steps. Source: EngineClient lines 88-102.
**Discovered by:** Monir Skaik
**Technique that found it:** Fault injection (Engine stopped) on the system + white-box review of the degradation path
