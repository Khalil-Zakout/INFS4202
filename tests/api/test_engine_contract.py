"""Black-box contract tests for the UniPlace Matching & Compliance Engine (Part B).

Every test states the requirement / OpenAPI clause it checks and the designed
test-case ID (see docs/test-cases.md). The oracle is always the published
contract (engine/openapi.yaml) and the Requirements document, never the Engine's
own output, so a failing test is a defect in the Engine, not in the test.

Run:  cd tests/api && python3 -m unittest -v
Needs the Engine running on 127.0.0.1:8081 (./start.sh), or ENGINE_URL set.

Tests whose names end in _DEFECT currently FAIL on the vendor build and are
pinned to a GitHub issue; they are expected to pass once the defect is fixed.
"""
import datetime as dt
import unittest

from engine_client import call, engine_available

TODAY = dt.date(2026, 11, 22)


def docs(cv=True, transcript=True, cv_size=1_000_000, tr_size=1_000_000,
         cv_mime="application/pdf", tr_mime="application/pdf", issue=None):
    out = []
    if cv:
        out.append({"type": "CV", "sizeBytes": cv_size, "mimeType": cv_mime})
    if transcript:
        out.append({"type": "TRANSCRIPT", "sizeBytes": tr_size, "mimeType": tr_mime,
                    "issueDate": str(issue or (TODAY - dt.timedelta(days=30)))})
    return out


def elig(**kw):
    body = {"gpa": 3.0, "creditsCompleted": 60, "standing": "GOOD", "priorInternships": 0,
            "minGpa": 2.0, "minCredits": 45, "asOf": str(TODAY), "documents": docs()}
    body.update(kw)
    return body


def match(student, required, nice=None):
    body = {"studentSkills": student, "requiredSkills": required}
    if nice is not None:
        body["niceToHaveSkills"] = nice
    return body


def candidate(app_id, score, gpa, submitted):
    return {"applicationId": app_id, "score": score, "gpa": gpa, "submittedAt": submitted}


def allowance(monthly, start, end, hours, late=0, **kw):
    body = {"monthlyAllowance": monthly, "startDate": start, "endDate": end,
            "weeklyHours": hours, "lateDays": late}
    body.update(kw)
    return body


@unittest.skipUnless(engine_available(), "Engine not reachable on ENGINE_URL")
class Eligibility(unittest.TestCase):
    """POST /eligibility — STU-04, POS-01, APP-04."""

    def test_TC_ENG_ELIG_01_all_rules_pass(self):
        r = call("/eligibility", elig())
        self.assertTrue(r.json["eligible"], r.text)

    def test_TC_ENG_ELIG_02_gpa_equal_to_minimum_is_eligible_DEFECT(self):
        # Spec: "GPA at least minGpa". 2.00 >= 2.00 must be eligible. Issue: Engine uses strict >.
        r = call("/eligibility", elig(gpa=2.0, minGpa=2.0))
        self.assertTrue(r.json["eligible"], f"GPA == minGpa must pass: {r.text}")

    def test_TC_ENG_ELIG_03_credits_equal_to_minimum_is_eligible(self):
        self.assertTrue(call("/eligibility", elig(creditsCompleted=45)).json["eligible"])

    def test_TC_ENG_ELIG_04_transcript_valid_on_day_180_DEFECT(self):
        # 180 days counting issue date as day 1 -> issue = asOf-179 is day 180 and still valid.
        issued = TODAY - dt.timedelta(days=179)
        r = call("/eligibility", elig(documents=docs(issue=issued)))
        self.assertTrue(r.json["eligible"], f"transcript on day 180 must be valid: {r.text}")

    def test_TC_ENG_ELIG_05_transcript_day_181_invalid(self):
        issued = TODAY - dt.timedelta(days=180)
        self.assertFalse(call("/eligibility", elig(documents=docs(issue=issued))).json["eligible"])

    def test_TC_ENG_ELIG_06_cv_at_2mb_boundary_ok_over_refused(self):
        self.assertTrue(call("/eligibility", elig(documents=docs(cv_size=2_097_152))).json["eligible"])
        self.assertFalse(call("/eligibility", elig(documents=docs(cv_size=2_097_153))).json["eligible"])

    def test_TC_ENG_ELIG_07_probation_prior_internships_limit(self):
        self.assertTrue(call("/eligibility", elig(standing="PROBATION", priorInternships=1)).json["eligible"])
        self.assertFalse(call("/eligibility", elig(standing="PROBATION", priorInternships=2)).json["eligible"])

    def test_TC_ENG_ELIG_08_gpa_out_of_domain_is_400_DEFECT(self):
        # Numeric fields outside their domain are validation errors (Requirements 3, Errors).
        self.assertEqual(400, call("/eligibility", elig(gpa=4.01)).status, "GPA 4.01 must be 400")
        self.assertEqual(400, call("/eligibility", elig(gpa=-0.1)).status, "GPA -0.1 must be 400")

    def test_TC_ENG_ELIG_09_unknown_standing_is_400_DEFECT(self):
        # standing enum is [GOOD, PROBATION]; anything else must be a validation error.
        self.assertEqual(400, call("/eligibility", elig(standing="BAD")).status)

    def test_TC_ENG_ELIG_10_missing_required_field_is_400_not_500_DEFECT(self):
        # REL-02: the Engine never answers 500 to well-formed JSON; a missing required field is 400.
        for field in ("priorInternships", "minGpa"):
            body = {k: v for k, v in elig().items() if k != field}
            self.assertEqual(400, call("/eligibility", body).status, f"missing {field} must be 400")


@unittest.skipUnless(engine_available(), "Engine not reachable on ENGINE_URL")
class Match(unittest.TestCase):
    """POST /match — the score formula and skill comparison."""

    def test_TC_ENG_MATCH_01_all_required_no_nice_is_70_DEFECT(self):
        # 3/3 required, nice list empty -> 70 + 0 = 70 (second term is 0 when the list is empty).
        r = call("/match", match(["Java", "SQL", "Spring"], ["Java", "SQL", "Spring"], []))
        self.assertEqual(70, r.json["score"], f"empty nice-to-have must add 0: {r.text}")

    def test_TC_ENG_MATCH_02_all_matched_is_100(self):
        r = call("/match", match(["Java", "SQL", "Spring", "Git", "Docker"],
                                 ["Java", "SQL", "Spring"], ["Git", "Docker"]))
        self.assertEqual(100, r.json["score"])

    def test_TC_ENG_MATCH_03_case_and_space_insensitive_DEFECT(self):
        # "Skill comparison ignores letter case and surrounding spaces."
        r = call("/match", match([" java ", "SQL"], ["Java", "sql"], []))
        self.assertEqual(70, r.json["score"], f"case/space-insensitive match expected: {r.text}")

    def test_TC_ENG_MATCH_04_half_rounds_up(self):
        # 1/4 required = 17.5 -> 18.
        self.assertEqual(18, call("/match", match(["Java"], ["Java", "SQL", "Spring", "Docker"], [])).json["score"])

    def test_TC_ENG_MATCH_05_partial_required_and_nice(self):
        self.assertEqual(50, call("/match", match(["Java", "Git"], ["Java", "SQL"], ["Git", "Docker"])).json["score"])

    def test_TC_ENG_MATCH_06_empty_required_is_400(self):
        self.assertEqual(400, call("/match", match(["Java"], [], [])).status)


@unittest.skipUnless(engine_available(), "Engine not reachable on ENGINE_URL")
class Rank(unittest.TestCase):
    """POST /rank — APP-09 ordering and the above-cut set."""

    T = "2026-11-20T09:00:00+03:00"

    def test_TC_ENG_RANK_01_by_score_descending(self):
        r = call("/rank", {"seats": 1, "candidates": [
            candidate(1, 50, 3.0, self.T), candidate(2, 90, 3.0, self.T), candidate(3, 70, 3.0, self.T)]})
        self.assertEqual([2, 3, 1], r.json["ranked"])

    def test_TC_ENG_RANK_02_gpa_tiebreak_descending_DEFECT(self):
        # Equal score -> higher GPA first.
        r = call("/rank", {"seats": 3, "candidates": [
            candidate(1, 80, 2.5, self.T), candidate(2, 80, 3.9, self.T), candidate(3, 80, 3.1, self.T)]})
        self.assertEqual([2, 3, 1], r.json["ranked"], f"GPA must break ties descending: {r.text}")

    def test_TC_ENG_RANK_03_above_cut_has_exactly_seats_ids_DEFECT(self):
        r = call("/rank", {"seats": 1, "candidates": [
            candidate(1, 50, 3.0, self.T), candidate(2, 90, 3.0, self.T), candidate(3, 70, 3.0, self.T)]})
        self.assertEqual(1, len(r.json["aboveCut"]), f"aboveCut must hold exactly 'seats' ids: {r.text}")

    def test_TC_ENG_RANK_04_submittedAt_then_applicationId(self):
        r = call("/rank", {"seats": 3, "candidates": [
            candidate(9, 80, 3.0, self.T), candidate(4, 80, 3.0, self.T), candidate(7, 80, 3.0, self.T)]})
        self.assertEqual([4, 7, 9], r.json["ranked"])

    def test_TC_ENG_RANK_05_missing_seats_is_400_not_500_DEFECT(self):
        self.assertEqual(400, call("/rank", {"candidates": [candidate(1, 50, 3.0, self.T)]}).status)


@unittest.skipUnless(engine_available(), "Engine not reachable on ENGINE_URL")
class Schedule(unittest.TestCase):
    """POST /schedule/validate — INT-02, INT-03."""

    SUN = "2026-11-29"
    Q = "+03:00"

    def slot(self, a, b):
        return {"start": a, "end": b}

    def validate(self, cand, rec=(), stu=()):
        return call("/schedule/validate", {"candidate": cand,
                    "recruiterSlots": list(rec), "studentSlots": list(stu)})

    def test_TC_ENG_SLOT_01_valid_weekday_slot(self):
        self.assertTrue(self.validate(self.slot(f"{self.SUN}T10:00:00{self.Q}", f"{self.SUN}T11:00:00{self.Q}")).json["valid"])

    def test_TC_ENG_SLOT_02_exactly_120_minutes_is_valid_DEFECT(self):
        r = self.validate(self.slot(f"{self.SUN}T10:00:00{self.Q}", f"{self.SUN}T12:00:00{self.Q}"))
        self.assertTrue(r.json["valid"], f"120 minutes is within 15..120: {r.text}")

    def test_TC_ENG_SLOT_03_must_end_by_18_00_DEFECT(self):
        r = self.validate(self.slot(f"{self.SUN}T17:01:00{self.Q}", f"{self.SUN}T18:01:00{self.Q}"))
        self.assertFalse(r.json["valid"], f"interview ending after 18:00 must be invalid: {r.text}")

    def test_TC_ENG_SLOT_04_back_to_back_is_allowed_DEFECT(self):
        existing = self.slot(f"{self.SUN}T10:00:00{self.Q}", f"{self.SUN}T11:00:00{self.Q}")
        r = self.validate(self.slot(f"{self.SUN}T11:00:00{self.Q}", f"{self.SUN}T12:00:00{self.Q}"), rec=[existing])
        self.assertTrue(r.json["valid"], f"a slot starting when another ends must not overlap: {r.text}")

    def test_TC_ENG_SLOT_05_friday_is_rejected(self):
        self.assertFalse(self.validate(self.slot("2026-12-04T10:00:00+03:00", "2026-12-04T11:00:00+03:00")).json["valid"])

    def test_TC_ENG_SLOT_06_real_overlap_is_rejected(self):
        existing = self.slot(f"{self.SUN}T10:00:00{self.Q}", f"{self.SUN}T11:00:00{self.Q}")
        self.assertFalse(self.validate(self.slot(f"{self.SUN}T10:30:00{self.Q}", f"{self.SUN}T11:30:00{self.Q}"), stu=[existing]).json["valid"])


@unittest.skipUnless(engine_available(), "Engine not reachable on ENGINE_URL")
class Allowance(unittest.TestCase):
    """POST /allowance — OFF-05."""

    def test_TC_ENG_ALLOW_01_three_months_with_transport(self):
        r = call("/allowance", allowance(3000, "2027-01-01", "2027-03-31", 40))
        self.assertAlmostEqual(9900.00, float(r.json["total"]), places=2)

    def test_TC_ENG_ALLOW_02_transport_at_exactly_30_hours_DEFECT(self):
        # Transport applies "when weekly hours are 30 or more"; 30 is included.
        r = call("/allowance", allowance(3000, "2027-01-01", "2027-01-31", 30))
        self.assertAlmostEqual(3300.00, float(r.json["total"]), places=2,
                               msg=f"30h must earn transport: {r.text}")

    def test_TC_ENG_ALLOW_03_no_transport_below_30_hours(self):
        r = call("/allowance", allowance(3000, "2027-01-01", "2027-01-31", 29))
        self.assertAlmostEqual(3000.00, float(r.json["total"]), places=2)

    def test_TC_ENG_ALLOW_04_cap_includes_transport_DEFECT(self):
        # cap adjustment = -(monthlyAllowance + monthly transport - monthlyCap) when positive.
        # 3500 + 300 - 3000 = 800 -> total capped to 3000.00.
        r = call("/allowance", allowance(3500, "2027-01-01", "2027-01-31", 40,
                                         transportSupplement=300, monthlyCap=3000, penaltyRate=0.05, penaltyCap=0.20))
        self.assertAlmostEqual(3000.00, float(r.json["total"]), places=2,
                               msg=f"cap must account for transport: {r.text}")

    def test_TC_ENG_ALLOW_05_late_penalty_started_weeks_and_cap(self):
        self.assertAlmostEqual(9405.00, float(call("/allowance", allowance(3000, "2027-01-01", "2027-03-31", 40, 7)).json["total"]), places=2)
        self.assertAlmostEqual(7920.00, float(call("/allowance", allowance(3000, "2027-01-01", "2027-03-31", 40, 22)).json["total"]), places=2)

    def test_TC_ENG_ALLOW_06_out_of_range_inputs_are_400(self):
        self.assertEqual(400, call("/allowance", allowance(5000.01, "2027-01-01", "2027-01-31", 40)).status)
        self.assertEqual(400, call("/allowance", allowance(3000, "2027-01-01", "2027-01-31", 41)).status)

    def test_TC_ENG_ALLOW_08_month_end_start_is_one_whole_month_DEFECT(self):
        # OFF-05: a month runs to the day before the same day of the next month; when that day does not
        # exist, to the end of the next month. 31 Jan -> 28 Feb and 31 Mar -> 30 Apr are one month each.
        for start, end in (("2027-01-31", "2027-02-28"), ("2027-03-31", "2027-04-30")):
            r = call("/allowance", allowance(3000, start, end, 29))
            self.assertAlmostEqual(3000.00, float(r.json["total"]), places=2,
                                   msg=f"{start}..{end} is one whole month: {r.text}")

    def test_TC_ENG_ALLOW_07_missing_lateDays_is_400_not_500_DEFECT(self):
        body = {"monthlyAllowance": 3000, "startDate": "2027-01-01", "endDate": "2027-01-31", "weeklyHours": 40}
        self.assertEqual(400, call("/allowance", body).status)


@unittest.skipUnless(engine_available(), "Engine not reachable on ENGINE_URL")
class Robustness(unittest.TestCase):
    """REL-02 and routing."""

    def test_TC_ENG_ROB_01_malformed_json_is_400(self):
        self.assertEqual(400, call("/eligibility", raw=b'{"gpa": 3.0,').status)

    def test_TC_ENG_ROB_02_unknown_route_is_404(self):
        self.assertEqual(404, call("/nope", {"a": 1}).status)

    def test_TC_ENG_ROB_03_wrong_method_is_405(self):
        self.assertEqual(405, call("/match", method="GET").status)

    def test_TC_ENG_ROB_04_wrong_content_type_is_not_500_DEFECT(self):
        # A well-formed-JSON body with the wrong Content-Type must not crash with 500 (REL-02 / SEC-03).
        self.assertNotEqual(500, call("/eligibility", raw=b'{}', content_type="text/plain").status)


if __name__ == "__main__":
    unittest.main(verbosity=2)
