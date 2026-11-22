# -*- coding: utf-8 -*-
"""Single source of truth for the defect reports.

Each entry becomes (a) a committed Markdown body under docs/issues/ and
(b) a `gh issue create` call in scripts/create_issues.sh. Keep steps reproducible
from a fresh `./start.sh --reset`; seeded ids are deterministic on a fresh start.

discoverer is a member KEY resolved against scripts/members.env
(M1..M4 -> GitHub usernames + display names).
"""

PASSWORD = "Uniplace!2026"

# Real team (INFS4202, 3 members). Area owners:
#   M1 Khalil Zakout   — Applications & Offers + Portal misc
#   M2 Monir Skaik     — Engine, integration, performance, specification
#   M3 Abdulaziz Debs  — Security, access control, AI assistant
NAMES = {"M1": "Khalil Zakout", "M2": "Monir Skaik", "M3": "Abdulaziz Debs"}

ISSUES = [
    # ---------------------------------------------------------------- CRITICAL
    dict(code="D01", sev="critical", prio="p1", cat="integration", req="APP-04", who="M1",
         title="Match score is cached per posting and shared across students",
         desc="The stored match score of an application is taken from a cache keyed only by posting id and its "
              "required skills (`MatchScoreService.key`), ignoring the student's own skills. The first applicant "
              "to a posting populates the cache; every later applicant to the same posting is given the first "
              "applicant's score. Match score drives shortlisting (APP-07), ranking (APP-09) and the average-score "
              "report (ADM-02), so all of these are corrupted.",
         steps=["Log in as student.amal and apply to \"Supply Chain Intern\" (Pearl Logistics). Score shown: 35.",
                "Log in as student.mubarak (Mubarak Al-Jaber) and apply to the same posting.",
                "Open the application (as the recruiter or coordinator) and read its match score."],
         expected="Mubarak's skills (Excel, SQL, Power BI) match the posting fully, so his score is 100 "
                  "(POST /match confirms 100).",
         actual="The application stores 35 — Amal's cached score — not 100.",
         evidence="Engine /match returns 100 for Mubarak's skills but the Portal stores 35; "
                  "`MatchScoreService.key()` omits studentSkills. qa:PortalDefectTest.matchScoreIsNotSharedBetweenStudents.",
         tech="White-box code review + integration test"),

    dict(code="D02", sev="critical", prio="p1", cat="state", req="OFF-03", who="M1",
         title="Filling a posting does not reject its remaining active applications",
         desc="OFF-03: when the last seat is taken the posting becomes FILLED and its remaining active applications "
              "become REJECTED. `OfferService.accept` sets the posting FILLED but never rejects the other active "
              "applications, so candidates stay OFFERED/SUBMITTED on a posting that can no longer place them.",
         steps=["On a fresh start, \"Sustainability Reporting Intern\" (Doha Energy, 1 seat) has three applicants: "
                "Ibrahim Al-Kuwari (OFFERED), Mubarak Al-Jaber (OFFERED), Ruqaya Al-Thani (SUBMITTED).",
                "Log in as student.ibrahim and accept the offer.",
                "As the coordinator, open the other two applications and the posting."],
         expected="Posting is FILLED; Mubarak's and Ruqaya's applications are REJECTED (OFF-03).",
         actual="Posting is FILLED but Mubarak stays OFFERED and Ruqaya stays SUBMITTED.",
         evidence="qa:PortalDefectTest.fillingThePostingRejectsTheOtherActiveApplications.",
         tech="State-transition testing"),

    dict(code="D03", sev="critical", prio="p1", cat="state", req="OFF-04", who="M1",
         title="Two students can accept offers for the last seat at the same moment",
         desc="OFF-04: if two students accept offers for the last seat simultaneously, exactly one succeeds. "
              "`OfferService.accept` checks `seatsLeft()` and increments `seatsTaken` without any lock or optimistic "
              "version, so concurrent acceptances both succeed and the seat count exceeds the seats.",
         steps=["\"Sustainability Reporting Intern\" has 1 seat and two pending offers (Ibrahim app id 7, Mubarak app id 8).",
                "POST /offers/2/accept (Ibrahim) and /offers/3/accept (Mubarak) concurrently (see tests/system seat-race).",
                "As coordinator open the posting and both applications."],
         expected="One acceptance succeeds; the other is refused with an explanation (OFF-04). Seats never exceed 1.",
         actual="Both acceptances succeed; both applications become ACCEPTED and the posting's seatsTaken = 2 on a 1-seat posting.",
         evidence="Reproduced on the first of six parallel attempts; tests/system/seat_race.py.",
         tech="Concurrency testing"),

    dict(code="D04", sev="critical", prio="p1", cat="functional", req="COM-02", who="M1",
         title="A suspended company's applications are not frozen",
         desc="COM-02: when a company is suspended, its applications are frozen (no state changes) until it is "
              "approved again. `ApplicationService.assertNotFrozen` only blocks companies that are PENDING, not "
              "SUSPENDED, so recruiters can still shortlist/reject and students can still accept offers while "
              "the company is suspended.",
         steps=["As coordinator, suspend \"Pearl Logistics\" (Companies page).",
                "Log in as recruiter.pearl and reject any of its applications — or as student.amal accept the "
                "pending Pearl offer (app id 3)."],
         expected="Every state change is refused while the company is suspended (COM-02).",
         actual="The rejection and the acceptance both succeed.",
         evidence="qa:PortalDefectTest.suspendedCompanyApplicationsAreFrozen.",
         tech="State-transition testing"),

    dict(code="D05", sev="critical", prio="p1", cat="security", req="USR-05", who="M3",
         title="Any authenticated user can view any application (broken access control)",
         desc="USR-05/SEC-05: a Student sees only their own data; access control is enforced on the server. "
              "`ApplicationController.view` loads the application by id and renders it without calling "
              "`AccessGuard.assertCanView`, so any logged-in user can read any application — its letter, the "
              "student's GPA (to recruiters) and the offer — by changing the id in the URL.",
         steps=["Log in as student.omar.",
                "Open /applications/3 (an application that belongs to Amal)."],
         expected="Access-denied page; nothing about the record is revealed (USR-05).",
         actual="HTTP 200 showing Amal's posting, motivation letter and offer.",
         evidence="qa:SecurityAccessTest.studentCannotOpenAnotherStudentsApplication.",
         tech="Forced-browsing / IDOR"),

    dict(code="D48", sev="critical", prio="p1", cat="security", req="USR-05", who="M3",
         title="Any recruiter can download any student's CV and transcript",
         desc="USR-05: a Recruiter sees only data of their own company. `StudentController.download` authorises the "
              "download if the user is a Coordinator, the owning Student, OR any Recruiter — so a recruiter from an "
              "unrelated company can fetch any student's documents by id.",
         steps=["Log in as recruiter.gulfbank.",
                "GET /documents/1 (Amal's CV) and /documents/2 (Amal's transcript)."],
         expected="Access-denied; a recruiter may only reach documents of applicants to their own company's postings.",
         actual="The PDF is served.",
         evidence="tests/system doc-idor; `StudentController.download` allows `user.is(Role.RECRUITER)` unconditionally.",
         tech="Forced-browsing / IDOR"),

    dict(code="D06", sev="critical", prio="p1", cat="security", req="SEC-04", who="M3",
         title="API key and SMTP password are written to the log and shown in plaintext",
         desc="SEC-04: secrets are never written to logs and are masked on screen. On saving Settings, "
              "`SettingsController.save` logs the old and new values of every changed key, including the AI API key "
              "and SMTP password, in plaintext; and the Settings page renders them in the input's `value` attribute "
              "(the masked hint is shown next to, not instead of, the real value).",
         steps=["As coordinator, open Settings, set an AI provider API key and an SMTP password, Save.",
                "Inspect logs/portal.log and view-source of /coordinator/settings."],
         expected="Secrets never appear in the log and are masked on screen (SEC-04).",
         actual="`Setting ai.apiKey changed from '' to 'sk-...'` appears in the log; the HTML `value=\"sk-...\"` carries the key.",
         evidence="logs/portal.log lines and page source captured in the issue.",
         tech="Security testing (secret handling)"),

    dict(code="D07", sev="critical", prio="p1", cat="security", req="SEC-07", who="M3",
         title="Stored XSS via company name on the postings list",
         desc="SEC-07: all user-entered text is escaped when displayed. `templates/postings/list.html` renders the "
              "company name with `th:utext` (unescaped). A recruiter who sets their company name to an HTML/script "
              "payload has it executed in the browser of every student who opens the postings list.",
         steps=["Log in as recruiter.qtech and set the company name to "
                "`QTech <img src=x onerror=alert(document.cookie)>`.",
                "Log in as any student and open /postings."],
         expected="The name is shown as text; no markup executes (SEC-07).",
         actual="The <img> tag is injected unescaped and the onerror handler runs.",
         evidence="Raw payload present in the /postings response; `th:utext` in postings/list.html.",
         tech="Stored XSS"),

    dict(code="D08", sev="critical", prio="p1", cat="security", req="AI-03", who="M3",
         title="Student name, number and GPA are sent to the AI provider",
         desc="AI-03/AI-10: the request to the provider contains only the posting title, the skills and the letter — "
              "never the student's name, number, e-mail or GPA. `PromptBuilder.postingAndLetter` prepends "
              "`Student: <full name> (<student number>), GPA <gpa>` to the prompt, so personal data is sent to a "
              "third party on every feedback/questions request with a real provider configured.",
         steps=["As coordinator, configure any OpenAI-compatible provider (a local echo endpoint suffices).",
                "As a student, request letter feedback on a posting.",
                "Capture the outgoing request body."],
         expected="The request carries only posting title, required/nice-to-have skills and the letter.",
         actual="The system prompt contains `Student: Amal Al-Kuwari (20231001), GPA 3.40`.",
         evidence="Captured request body (tests/ai-eval and the capture harness); ai:test_prompt_properties.",
         tech="Integration + prompt capture"),

    dict(code="D47", sev="critical", prio="p1", cat="state", req="APP-08", who="M1",
         title="An ACCEPTED application can be withdrawn via a direct POST",
         desc="APP-06/APP-08: ACCEPTED is final and an accepted application cannot be withdrawn. "
              "`ApplicationService.withdraw` sets the state to WITHDRAWN directly (`a.setState(WITHDRAWN)`) without "
              "going through the state machine, so a direct POST withdraws an ACCEPTED placement. The button is "
              "hidden in the UI but the endpoint is reachable.",
         steps=["Log in as student.amna (has an ACCEPTED application, id 116).",
                "POST /applications/116/withdraw."],
         expected="Refused: an ACCEPTED application cannot be withdrawn (APP-08).",
         actual="The application becomes WITHDRAWN; the confirmed placement is lost (the seat stays taken, leaving the data inconsistent).",
         evidence="Reproduced on app 116; `withdraw()` bypasses `ApplicationStateMachine`.",
         tech="State-transition testing (direct URL)"),

    # ------------------------------------------------------------------- MAJOR (Engine)
    dict(code="D09", sev="major", prio="p2", cat="integration", req="POS-01", who="M2",
         title="Engine refuses eligibility when GPA exactly equals the minimum",
         desc="The eligibility rule is \"GPA at least minGpa\". The Engine uses a strict greater-than, so a GPA equal "
              "to the minimum is reported ineligible.",
         steps=["POST /api/v1/eligibility with gpa=2.00 and minGpa=2.00 (CV+transcript valid)."],
         expected="eligible = true (2.00 is at least 2.00).",
         actual="eligible = false, reason \"GPA 2.0 is below the minimum 2.0\".",
         evidence="api:Eligibility.test_TC_ENG_ELIG_02_gpa_equal_to_minimum_is_eligible_DEFECT.",
         tech="Boundary value analysis"),

    dict(code="D10", sev="major", prio="p2", cat="integration", req="STU-04", who="M2",
         title="Transcript valid-window is one day short (day 180 rejected)",
         desc="A transcript is valid for 180 days counting the issue date as day 1, so an issue date 179 days before "
              "`asOf` is day 180 and still valid. The Engine rejects it.",
         steps=["POST /eligibility with the transcript issued exactly 179 days before asOf."],
         expected="eligible = true (day 180 is within the 180-day window).",
         actual="eligible = false (\"not valid on …\").",
         evidence="api:Eligibility.test_TC_ENG_ELIG_04_transcript_valid_on_day_180_DEFECT.",
         tech="Boundary value analysis"),

    dict(code="D11", sev="major", prio="p1", cat="integration", req="REL-02", who="M2",
         title="Engine returns HTTP 500 to well-formed JSON",
         desc="REL-02: the Engine never answers 500 to well-formed JSON; a missing/invalid field is a 400 naming the "
              "field. Several well-formed requests crash with 500 instead: eligibility missing priorInternships or "
              "minGpa, gpa as a string or null, rank missing seats, allowance missing lateDays or monthlyAllowance, "
              "and any request sent with Content-Type text/plain.",
         steps=["POST /eligibility omitting priorInternships.",
                "POST /rank with candidates but no seats.",
                "POST /allowance omitting lateDays."],
         expected="400 with {error, field, message}.",
         actual="500 {\"error\":\"internal\",\"message\":\"Unexpected error\"}.",
         evidence="api:Eligibility…10, Rank…05, Allowance…07, Robustness…04.",
         tech="Equivalence partitioning / negative testing"),

    dict(code="D12", sev="major", prio="p1", cat="integration", req="POS-01", who="M2",
         title="Match score adds the full nice-to-have weight when the list is empty",
         desc="score = 70×(matched required/required) + 30×(matched nice/nice, or 0 when the nice list is empty). "
              "When a posting lists no nice-to-have skills the Engine adds the whole 30 points instead of 0, inflating "
              "every such posting's scores by 30.",
         steps=["POST /match with studentSkills=requiredSkills=[Java,SQL,Spring] and niceToHaveSkills=[]."],
         expected="score = 70.",
         actual="score = 100.",
         evidence="api:Match.test_TC_ENG_MATCH_01_all_required_no_nice_is_70_DEFECT.",
         tech="Decision table"),

    dict(code="D13", sev="major", prio="p1", cat="integration", req="POS-06", who="M2",
         title="Match skill comparison is case- and space-sensitive",
         desc="Skill comparison must ignore letter case and surrounding spaces. The Engine compares skills exactly, "
              "so \" java \" does not match \"Java\" and scores drop to 0 for required skills that differ only in case "
              "or spacing.",
         steps=["POST /match with studentSkills=[\" java \", \"SQL\"], requiredSkills=[\"Java\", \"sql\"]."],
         expected="score = 70 (both required matched).",
         actual="score = 30 / no required matched.",
         evidence="api:Match.test_TC_ENG_MATCH_03_case_and_space_insensitive_DEFECT.",
         tech="Equivalence partitioning"),

    dict(code="D14", sev="major", prio="p1", cat="integration", req="APP-09", who="M2",
         title="Candidate ranking breaks GPA ties in ascending order",
         desc="APP-09: order by score descending, then GPA descending. On equal scores the Engine orders by GPA "
              "ascending, placing the weakest GPA first.",
         steps=["POST /rank with equal scores and GPAs 2.5, 3.9, 3.1."],
         expected="ranked = highest GPA first.",
         actual="ranked = lowest GPA first.",
         evidence="api:Rank.test_TC_ENG_RANK_02_gpa_tiebreak_descending_DEFECT.",
         tech="Decision table"),

    dict(code="D15", sev="major", prio="p1", cat="integration", req="APP-09", who="M2",
         title="aboveCut returns one id more than the number of seats",
         desc="`aboveCut` must hold the first `seats` identifiers of `ranked`. The Engine returns seats+1 ids, so the "
              "recruiter's \"within seats\" marking always includes one candidate too many.",
         steps=["POST /rank with seats=1 and three candidates."],
         expected="aboveCut has 1 id.",
         actual="aboveCut has 2 ids.",
         evidence="api:Rank.test_TC_ENG_RANK_03_above_cut_has_exactly_seats_ids_DEFECT.",
         tech="Boundary value analysis"),

    dict(code="D16", sev="major", prio="p2", cat="performance", req="PERF-02", who="M2",
         title="Ranking 200 candidates takes about 5 seconds (budget 500 ms)",
         desc="PERF-02: the Engine ranks 200 candidates in at most 500 ms at p95. Measured p95 for 200 candidates is "
              "about 4.9 s, and the time is grossly non-linear in the candidate count, pointing to an accidentally "
              "quadratic sort.",
         steps=["Run tests/performance/engine_rank_latency.py against the Engine."],
         expected="p95 ≤ 500 ms at 200 candidates.",
         actual="p95 ≈ 4,900 ms at 200 candidates (10→50→100→150→200 is non-monotonic).",
         evidence="perf:engine_rank_latency.py output.",
         tech="Performance testing"),

    dict(code="D17", sev="major", prio="p2", cat="integration", req="INT-02", who="M2",
         title="Engine accepts interviews that end after 18:00",
         desc="INT-02: an interview must end at or before 18:00. The Engine checks the start time but not the end, so "
              "slots ending at 18:01 or 18:15 are accepted.",
         steps=["POST /schedule/validate with a Sunday slot 17:01–18:01 (and 17:30–18:15)."],
         expected="valid = false (ends after 18:00).",
         actual="valid = true.",
         evidence="api:Schedule.test_TC_ENG_SLOT_03_must_end_by_18_00_DEFECT.",
         tech="Boundary value analysis"),

    dict(code="D18", sev="major", prio="p2", cat="integration", req="INT-03", who="M2",
         title="Back-to-back interviews are rejected as overlapping",
         desc="INT-03: a slot that starts exactly when another ends does not overlap it. The Engine treats touching "
              "slots as overlapping, so a recruiter or student cannot schedule consecutive interviews.",
         steps=["POST /schedule/validate with candidate 11:00–12:00 and an existing recruiter slot 10:00–11:00."],
         expected="valid = true (back-to-back allowed).",
         actual="valid = false (\"Overlaps with an interview of the recruiter\").",
         evidence="api:Schedule.test_TC_ENG_SLOT_04_back_to_back_is_allowed_DEFECT.",
         tech="Boundary value analysis"),

    dict(code="D19", sev="major", prio="p2", cat="integration", req="OFF-05", who="M2",
         title="No transport supplement at exactly 30 weekly hours",
         desc="OFF-05: the transport supplement applies when weekly hours are 30 or more. At exactly 30 hours the "
              "Engine omits it, so a 30-hour placement is under-paid. This shows end-to-end: a seeded 30-hour "
              "placement's allowance statement has no transport line.",
         steps=["POST /allowance with weeklyHours=30 (one month, 3000).",
                "Or: accept the 30-hour \"Sustainability Reporting Intern\" placement and read its statement."],
         expected="Base + transport (total 3300 for one month).",
         actual="Base only (3000); no transport line.",
         evidence="api:Allowance.test_TC_ENG_ALLOW_02_transport_at_exactly_30_hours_DEFECT.",
         tech="Boundary value analysis"),

    dict(code="D20", sev="major", prio="p2", cat="integration", req="OFF-05", who="M2",
         title="Monthly cap ignores the transport supplement",
         desc="OFF-05: cap adjustment = −(monthlyAllowance + monthly transport − monthlyCap) when positive, i.e. the "
              "cap applies to the monthly total after transport. The Engine caps the base allowance only, so the "
              "capped total still exceeds the cap once transport is added.",
         steps=["POST /allowance monthlyAllowance=3500, one month, 40h, monthlyCap=3000, transport=300."],
         expected="total = 3000 (3500+300 capped to 3000).",
         actual="total = 3300 (base capped to 3000, then +300 transport).",
         evidence="api:Allowance.test_TC_ENG_ALLOW_04_cap_includes_transport_DEFECT.",
         tech="Decision table"),

    # ------------------------------------------------------------------- MAJOR (Portal)
    dict(code="D21", sev="major", prio="p1", cat="functional", req="APP-02", who="M1",
         title="Withdrawn applications count against the active-application limit",
         desc="APP-02: an application is active only while SUBMITTED, SHORTLISTED, INTERVIEW or OFFERED. "
              "`ApplicationService.countActive` counts everything except REJECTED and ACCEPTED, so WITHDRAWN "
              "applications are counted as active and students are blocked from applying earlier than the rules allow.",
         steps=["On a fresh start, student.amal has 3 active applications and 1 withdrawn.",
                "Open the student dashboard."],
         expected="Active applications: 3 of 5.",
         actual="Active applications: 4 of 5 (the withdrawn one is counted).",
         evidence="qa:PortalDefectTest.withdrawnApplicationsAreNotCountedAsActive.",
         tech="White-box review + unit test"),

    dict(code="D22", sev="major", prio="p1", cat="functional", req="APP-02", who="M1",
         title="Probation active-application limit is never applied",
         desc="APP-02: a student on probation may hold at most 2 active applications. `activeLimitFor` compares the "
              "String \"PROBATION\" to a `Standing` enum (`\"PROBATION\".equals(student.getStanding())`), which is "
              "always false, so probation students get the GOOD limit of 5.",
         steps=["Log in as student.omar (GPA 1.85, PROBATION).",
                "Read the dashboard limit, or add applications past 2."],
         expected="Limit of 2 active applications.",
         actual="Limit of 5; Omar can hold 5 active applications.",
         evidence="qa:PortalDefectTest.probationStudentLimitIsTwo.",
         tech="White-box review + unit test"),

    dict(code="D23", sev="major", prio="p2", cat="functional", req="OFF-02", who="M1",
         title="Offer response deadline is rounded to midnight and drops the time",
         desc="OFF-02: the student must respond within the response window (default 72 hours). "
              "`OfferService.responseDeadline` computes `issuedAt.toLocalDate().plusDays(hours/24).atStartOfDay()`, "
              "which truncates to midnight and uses integer day division, so the deadline is earlier than 72 hours "
              "(and wrong for any window that is not a whole number of days).",
         steps=["As a recruiter, issue an offer at, say, 13:30.",
                "Read the offer's \"Answer by\" time."],
         expected="72 hours later, same time of day (e.g. 23/11 13:30).",
         actual="Midnight of that day (23/11 00:00) — about 13.5 hours early.",
         evidence="qa:PortalDefectTest.offerDeadlineKeepsTheTimeOfDay.",
         tech="Boundary value analysis"),

    dict(code="D24", sev="major", prio="p2", cat="configuration", req="REL-04", who="M1",
         title="Uploaded documents are lost on every restart",
         desc="REL-04: restarting loses no committed business data. `DocumentService` stores uploads in a brand-new "
              "temporary directory created with `Files.createTempDirectory` on each start, so after a restart every "
              "stored document (including the seeded CVs and transcripts) 404s, while the database rows remain.",
         steps=["As a student, upload a CV; download it (works).",
                "Restart the Portal (./start.sh).",
                "Download the same document, or any seeded document (/documents/1)."],
         expected="The document is still available after the restart.",
         actual="404 Not found; the file path from the previous run no longer exists.",
         evidence="A fresh /tmp/uniplace-uploads-* directory per start; documents 404 after restart.",
         tech="Reliability testing (restart)"),

    dict(code="D25", sev="major", prio="p2", cat="functional", req="STU-03", who="M1",
         title="Academic standing is not recomputed when the Coordinator changes the GPA",
         desc="STU-03: standing is derived (GPA below 2.00 → PROBATION) and recomputed whenever a Coordinator updates "
              "the GPA. `StudentService.updateAcademicRecord` saves the GPA but never recomputes `standing`, so a "
              "student dropped below 2.00 keeps GOOD standing (and the wrong application limit).",
         steps=["As coordinator, open a GOOD student and set the GPA to 1.50, Save."],
         expected="Standing becomes PROBATION.",
         actual="Standing stays GOOD.",
         evidence="qa:PortalDefectTest.loweringGpaBelowTwoSetsProbation.",
         tech="White-box review + unit test"),

    dict(code="D26", sev="major", prio="p2", cat="functional", req="COM-03", who="M1",
         title="Company name uniqueness is case-sensitive when renaming",
         desc="COM-03: company names are unique ignoring case and surrounding spaces. Registration enforces this, but "
              "`CompanyService.update` uses `existsByNameAndIdNot`, a case-sensitive derived query, so a company can "
              "be renamed to an existing name in a different case.",
         steps=["As recruiter.gulfbank, rename the company to \"qtech solutions\" (QTech Solutions exists)."],
         expected="Refused (name already exists, ignoring case).",
         actual="Saved; two companies now share the name QTech Solutions / qtech solutions.",
         evidence="qa:PortalDefectTest.renamingToAnExistingNameInAnotherCaseIsRefused.",
         tech="Equivalence partitioning"),

    dict(code="D27", sev="major", prio="p2", cat="security", req="USR-04", who="M3",
         title="Logging out does not invalidate the server session",
         desc="USR-04: logging out invalidates the session immediately. The app's \"Log out\" posts to "
              "`/account/logout`, which only clears the JSESSIONID cookie in the browser and redirects; it never "
              "invalidates the HttpSession. A captured session id keeps working after logout.",
         steps=["Log in as a student; note the JSESSIONID.",
                "Click Log out (POST /account/logout).",
                "Replay a request with the old JSESSIONID cookie."],
         expected="The old session is invalid; the request is sent to login.",
         actual="The old session still loads the dashboard.",
         evidence="tests/system logout; Spring's /logout (control) does invalidate, /account/logout does not.",
         tech="Session management testing"),

    dict(code="D28", sev="major", prio="p2", cat="security", req="USR-03", who="M3",
         title="Account lockout can be bypassed by varying the username case",
         desc="USR-03: after 5 consecutive failed logins the account is locked for 15 minutes. "
              "`LoginAttemptService.failed` records failures against the raw submitted username, while login resolves "
              "the user case-insensitively. Failed attempts sent with a different letter case are never counted, so "
              "an attacker can try unlimited passwords and the account never locks.",
         steps=["Submit 12 failed logins with the username \"Student.Salem\" (note the capitals).",
                "Then log in as \"Student.Salem\" with the correct password."],
         expected="The account locks after 5 failures (USR-03).",
         actual="It never locks; the correct password logs in normally.",
         evidence="tests/system lockout; the exact-case control does lock after 5.",
         tech="Security testing"),

    dict(code="D29", sev="major", prio="p2", cat="security", req="USR-02", who="M3",
         title="Password change accepts a password with no digit",
         desc="USR-02: passwords have at least 10 characters including at least one digit, and the rule applies when "
              "any user changes their password. `UserService.changePassword` only checks the length, so a 10+ "
              "character password with no digit is accepted on change (creation enforces the digit correctly).",
         steps=["Log in as a student and change the password to \"abcdefghijkl\" (12 letters, no digit).",
                "Log in again with the new password."],
         expected="Refused: the password needs at least one digit.",
         actual="Accepted; the new password works.",
         evidence="tests/system pwd-change; the create-user path (control) rejects the same password.",
         tech="Boundary value analysis"),

    dict(code="D30", sev="major", prio="p2", cat="security", req="SEC-03", who="M3",
         title="Error pages expose stack traces and SQL",
         desc="SEC-03: error pages never show stack traces, SQL, class names or other internals. "
              "`application.properties` sets `server.error.include-stacktrace=always` and `include-exception=true`, "
              "and the error template renders them, so a bad parameter shows a full Spring stack trace; an over-long "
              "shortlist justification shows the failing SQL INSERT.",
         steps=["Open /postings?minAllowance=3,000 (a comma makes the BigDecimal conversion fail).",
                "Or shortlist with a justification longer than 1000 characters."],
         expected="A friendly error page with no internal details.",
         actual="The page shows the exception class, message and stack frames (and the audit-log SQL in the second case).",
         evidence="tests/system stacktrace; captured page bodies.",
         tech="Security testing (information disclosure)"),

    dict(code="D31", sev="major", prio="p2", cat="security", req="SEC-02", who="M3",
         title="CSRF protection is disabled on the Settings endpoints",
         desc="SEC-02: every form that changes data is protected against CSRF. `SecurityConfig` calls "
              "`csrf.ignoringRequestMatchers(\"/coordinator/settings/**\")`, so the Settings save and the AI "
              "\"Test connection\" accept cross-site POSTs with no token — and Settings control thresholds, the "
              "Engine URL and secrets.",
         steps=["As coordinator, POST to /coordinator/settings with valid fields but no _csrf parameter."],
         expected="Rejected (403) for the missing CSRF token.",
         actual="Accepted (302, \"Settings saved\").",
         evidence="qa:SecurityAccessTest.settingsPostWithoutCsrfTokenIsRejected.",
         tech="Security testing (CSRF)"),

    dict(code="D32", sev="major", prio="p2", cat="ai", req="AI-10", who="M3",
         title="The AI prompt discloses the internal shortlist threshold",
         desc="AI-10: prompts contain no internal business rules or thresholds. The feedback prompt includes "
              "\"Internal note: recruiters reject applications that score below 60, so be strict around that value\", "
              "steering the model with an internal rule and biasing scores around 60.",
         steps=["Configure a provider and capture the request for letter feedback (or read PromptBuilder)."],
         expected="The prompt carries only the posting and the letter.",
         actual="The prompt contains the \"reject below 60\" internal note.",
         evidence="ai:test_prompt_properties.test_v1_contains_internal_threshold_DEFECT; captured prompt.",
         tech="White-box review + prompt capture"),

    dict(code="D33", sev="major", prio="p2", cat="ai", req="AI-08", who="M3",
         title="Letter-feedback cache ignores the letter content",
         desc="AI-08: feedback is cached per student, posting and letter content; the same letter returns the "
              "identical result within 10 minutes. `FeedbackCache.key` is `studentId|postingId` only, so a student "
              "who edits their letter and asks again gets the stale result for the old letter — and a changed letter "
              "is never re-evaluated within the window.",
         steps=["As a student, request feedback on a posting with letter A.",
                "Within 10 minutes, change the letter substantially and request feedback again on the same posting."],
         expected="The new letter is evaluated (AI-08 keys on letter content).",
         actual="The cached result for letter A is returned; no new provider call is made.",
         evidence="Capture shows one provider call for two different letters on the same posting.",
         tech="Metamorphic testing"),

    dict(code="D34", sev="major", prio="p2", cat="ai", req="AI-09", who="M3",
         title="Letter-feedback scores vary by more than 10 points across runs",
         desc="AI-09: outside the cache window, two evaluations of the same letter and posting return scores that "
              "differ by at most 10 points. `AiClient.TEMPERATURE = 1.3` makes the model highly non-deterministic, so "
              "repeated evaluations of the same letter vary far more than 10 points (and the cache above masks it in "
              "the UI rather than fixing it).",
         steps=["Run the AI evaluation (tests/ai-eval) with the shipped prompt at temperature 1.3, 5 runs per letter.",
                "Compute the max−min score per letter."],
         expected="Within-letter spread ≤ 10 points.",
         actual="Spread exceeds 10 points for many letters at temperature 1.3.",
         evidence="tests/ai-eval run_eval.py + analyze.py (mean within-letter spread).",
         tech="Metamorphic testing (repeated runs)"),

    dict(code="D35", sev="major", prio="p2", cat="performance", req="PERF-05", who="M2",
         title="List pages are not paginated (Outbox and Postings)",
         desc="PERF-05: no page returns an unbounded list; every list is paginated or limited. The coordinator Outbox "
              "(`CoordinatorController.outbox`) wraps the full notification list in a single `PageImpl`, and the "
              "student postings list returns every visible posting, so both grow without bound with volume data.",
         steps=["As coordinator, generate volume data (Tools → Generate, 1000).",
                "Open /coordinator/outbox and /postings."],
         expected="At most 20 rows per page with a pager.",
         actual="The Outbox shows 1117 rows on one page; the postings list shows all postings. No pager.",
         evidence="perf:portal_pages.py (rows/page = 1117 for Outbox).",
         tech="Performance / volume testing"),

    # ------------------------------------------------------------------- MINOR
    dict(code="D36", sev="minor", prio="p3", cat="functional", req="INT-02", who="M2",
         title="Engine rejects an interview of exactly 120 minutes",
         desc="INT-02: a slot lasts 15 to 120 minutes (inclusive). A slot of exactly 120 minutes is rejected.",
         steps=["POST /schedule/validate with a Sunday slot 10:00–12:00."],
         expected="valid = true.",
         actual="valid = false (\"Duration must be between 15 and 120 minutes\").",
         evidence="api:Schedule.test_TC_ENG_SLOT_02_exactly_120_minutes_is_valid_DEFECT.",
         tech="Boundary value analysis"),

    dict(code="D37", sev="minor", prio="p3", cat="integration", req="OFF-05", who="M2",
         title="Allowance whole-month count is off at month-end start dates",
         desc="OFF-05: a month runs from a day to the day before the same day of the next month; when the next month "
              "has no such day, the month runs to the end of that next month. For a start date of 31 Jan to 28 Feb "
              "(a whole month by that rule) the Engine reports 1.03 months and adds a spurious extra day.",
         steps=["POST /allowance monthlyAllowance=3000, startDate 2027-01-31, endDate 2027-02-28, 40h."],
         expected="1 month (base 3000.00).",
         actual="1.03 months (base 3100.00).",
         evidence="Engine /allowance output; see docs/test-cases TC-ENG (allowance boundary).",
         tech="Boundary value analysis"),

    dict(code="D38", sev="minor", prio="p3", cat="functional", req="POS-06", who="M1",
         title="Searching postings by company is not sorted by deadline",
         desc="POS-06: results are sorted by deadline, earliest first. When a company filter is applied, "
              "`findVisibleForCompany` orders by posting id, so the results are not deadline-ordered.",
         steps=["As a student, open /postings?companyId=1 (QTech)."],
         expected="Earliest deadline first.",
         actual="\"Backend Developer Intern\" (later deadline) appears before \"QA Automation Intern\" (today).",
         evidence="Rendered order vs deadlines; the unfiltered search orders correctly (contrast).",
         tech="Equivalence / comparison"),

    dict(code="D39", sev="minor", prio="p3", cat="ui", req="USA-01", who="M1",
         title="A refused application shows a generic message, not the reason",
         desc="USA-01: every refused operation tells the user the specific reason. `ApplicationController.apply` "
              "catches the business-rule exception and replaces its message with a generic \"Unable to submit your "
              "application. Please check the posting and try again.\", hiding whether the letter is too short, the "
              "limit is reached, or a duplicate exists.",
         steps=["As a student, submit an application with a 20-character letter."],
         expected="\"The motivation letter must have between 100 and 2000 characters …\".",
         actual="\"Unable to submit your application. Please check the posting and try again.\".",
         evidence="tests/system apply-msg.",
         tech="Usability / error-message review"),

    dict(code="D40", sev="minor", prio="p3", cat="ui", req="USA-02", who="M1",
         title="Recruiter applications list shows dates as MM/dd/yyyy",
         desc="USA-02: dates are shown as dd/MM/yyyy. On the recruiter applications list "
              "(`templates/applications/list.html`) the submitted date is formatted `MM/dd/yyyy HH:mm` for "
              "non-students, so 21 November shows as 11/21/2026.",
         steps=["Log in as recruiter.qtech and open Applications."],
         expected="dd/MM/yyyy (e.g. 21/11/2026).",
         actual="MM/dd/yyyy (e.g. 11/21/2026); the student view uses dd/MM.",
         evidence="Rendered dates captured in the issue.",
         tech="UI review"),

    dict(code="D41", sev="minor", prio="p3", cat="ai", req="AI-07", who="M3",
         title="Letter feedback names the wrong model",
         desc="AI-07: the screen names the model that produced the result. For feedback, "
              "`AiAssistantService.feedback` labels the source with the constant `AiClient.DEFAULT_MODEL` "
              "(\"gpt-4o-mini\") instead of the configured model, so the screen names the wrong model whenever a "
              "different one is configured (the interview-questions path labels it correctly).",
         steps=["Configure a model name other than gpt-4o-mini; request letter feedback."],
         expected="The screen names the configured model.",
         actual="It always says \"Model gpt-4o-mini\".",
         evidence="Observed source label vs configured model; AiAssistantService.feedback.",
         tech="White-box review"),

    dict(code="D42", sev="minor", prio="p3", cat="ai", req="AI-11", who="M3",
         title="The AI prompt's worked example is malformed",
         desc="AI-11: every prompt states the scale, the number of items and the exact format, with examples "
              "consistent with that format. The feedback prompt's example uses \"score\": 8.5 (a non-integer on the "
              "wrong scale) and instructs \"Always give exactly three strengths\", contradicting \"1 to 5 strengths\".",
         steps=["Read PromptBuilder.FEEDBACK_INSTRUCTIONS (or capture the prompt)."],
         expected="The example is a valid answer in the required 0–100 integer format and is consistent with the item counts.",
         actual="The example shows 8.5 and the instructions demand exactly three strengths.",
         evidence="ai:test_prompt_properties.test_v1_example_score_is_malformed_DEFECT.",
         tech="White-box review"),

    dict(code="D44", sev="minor", prio="p3", cat="requirements", req="NOT-04", who="M2",
         title="Specification: NOT-04 reminder window contradicts OFF-02",
         desc="NOT-04 states a reminder is recorded \"24 hours before the end of the 48-hour response window of a "
              "pending offer\", but OFF-02 sets the response window from Settings (default 72 hours). The two "
              "requirements give different window lengths, so the reminder timing is unspecified. The code reminds "
              "24 h before the actual respond-by, implicitly following OFF-02 and leaving NOT-04's \"48-hour\" wrong.",
         steps=["Quote NOT-04 and OFF-02."],
         expected="One consistent response-window length across requirements.",
         actual="NOT-04 says 48 hours; OFF-02 says the Settings value (default 72).",
         evidence="Requirements §1.7 (OFF-02) and §1.8 (NOT-04).",
         tech="Specification review"),

    dict(code="D45", sev="minor", prio="p3", cat="tests", req="APP-02", who="M1",
         title="Vendor test encodes the wrong probation limit",
         desc="`ApplicationServiceTest.probationStudentUsesStandardLimit` asserts that a probation student's active "
              "limit is 5, baking the APP-02 defect (D22) into the test suite. The test name even calls it the "
              "\"standard\" limit. A correct test would expect 2.",
         steps=["Run: cd portal && ./mvnw test -Dtest=ApplicationServiceTest#probationStudentUsesStandardLimit."],
         expected="The test expects the probation limit of 2 (APP-02).",
         actual="The test asserts 5 and passes on the buggy build.",
         evidence="portal/src/test/.../ApplicationServiceTest.java.",
         tech="Test-suite review"),

    dict(code="D46", sev="minor", prio="p3", cat="tests", req="APP-02", who="M1",
         title="Vendor test counts withdrawn applications as active",
         desc="`ApplicationServiceTest.withdrawnApplicationsRemainInHistoryCount` asserts countActive = 5 for a "
              "student with 4 withdrawn and 1 submitted application, encoding the APP-02 active-count defect (D21). "
              "WITHDRAWN is not an active state, so the correct expectation is 1.",
         steps=["Run: cd portal && ./mvnw test -Dtest=ApplicationServiceTest#withdrawnApplicationsRemainInHistoryCount."],
         expected="countActive = 1 (only the submitted application is active).",
         actual="The test asserts 5 and passes on the buggy build.",
         evidence="portal/src/test/.../ApplicationServiceTest.java.",
         tech="Test-suite review"),

    dict(code="D43", sev="major", prio="p2", cat="requirements", req="INT-02", who="M2",
         title="Specification: public-holiday rule (INT-02) is untestable and unenforced",
         desc="INT-02 forbids interviews on public holidays, and INT-05 says slot validation (INT-02 and INT-03) is "
              "performed by the Engine's schedule endpoint. But the Engine contract (`openapi.yaml`, "
              "/schedule/validate) has no holiday input and no holiday list, and the Portal sends none, so the "
              "\"except on public holidays\" clause can never be enforced or tested. The Engine accepts an interview "
              "on a Qatar public holiday (e.g. a Tuesday Sport Day).",
         steps=["Quote INT-02, INT-05 and the /schedule/validate schema.",
                "POST /schedule/validate for a weekday public holiday — it is accepted."],
         expected="Either the contract carries the holiday calendar (so INT-02 is enforceable) or INT-02 drops the clause.",
         actual="No holiday data flows to the Engine; holidays are silently allowed.",
         evidence="openapi.yaml /schedule/validate schema; Engine accepts a public-holiday weekday slot.",
         tech="Specification review"),
]
