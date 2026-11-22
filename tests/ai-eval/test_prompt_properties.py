"""Model-free property tests on the letter-feedback prompt (AI-03, AI-10, AI-11).

These assert the privacy and content properties that must hold for the request the
Portal sends to the AI provider, independent of any model. They check the baseline
prompt v1 (copied verbatim from the shipped PromptBuilder) and the candidate v2.

The v1 cases named _DEFECT currently FAIL: they document that the shipped prompt
leaks personal data and an internal threshold. v2 passes all of them.

Run:  cd tests/ai-eval && python3 -m unittest -v test_prompt_properties.py
"""
import re
import unittest

from prompts import PROMPTS

SAMPLE = {"posting": "Backend Developer Intern", "requiredSkills": ["Java", "SQL"],
          "niceToHaveSkills": ["Git"], "letter": "I used Java and SQL in two course projects."}

PERSONAL_MARKERS = [r"\bGPA\b", r"\bStudent:\b", r"\b\d{8}\b"]            # name/number/GPA  (AI-03)
INTERNAL_MARKERS = [r"reject applications that score below", r"\b60\b"]   # threshold        (AI-10)


def full_prompt(version, letter):
    cfg = PROMPTS[version]
    return cfg["system"] + "\n\n" + cfg["context"](letter)


class PromptPrivacy(unittest.TestCase):

    def test_v1_leaks_personal_data_DEFECT(self):
        text = full_prompt("v1", SAMPLE)
        hits = [m for m in PERSONAL_MARKERS if re.search(m, text)]
        self.assertEqual([], hits, f"AI-03: prompt must carry no personal data, found {hits}")

    def test_v1_contains_internal_threshold_DEFECT(self):
        text = full_prompt("v1", SAMPLE)
        self.assertFalse(re.search(INTERNAL_MARKERS[0], text),
                         "AI-10: prompt must not disclose the internal shortlist threshold")

    def test_v2_carries_no_personal_data(self):
        text = full_prompt("v2", SAMPLE)
        self.assertEqual([], [m for m in PERSONAL_MARKERS if re.search(m, text)])

    def test_v2_carries_no_internal_threshold(self):
        text = full_prompt("v2", SAMPLE)
        self.assertFalse(re.search(INTERNAL_MARKERS[0], text))

    def test_v2_example_score_is_integer_on_0_100_scale(self):
        # AI-11: the worked example must be consistent with the required format.
        system = PROMPTS["v2"]["system"]
        example = re.search(r'\{"score":\s*([0-9.]+)', system)
        self.assertIsNotNone(example)
        self.assertNotIn(".", example.group(1), "example score must be an integer")
        self.assertTrue(0 <= int(example.group(1)) <= 100)

    def test_v1_example_score_is_malformed_DEFECT(self):
        system = PROMPTS["v1"]["system"]
        example = re.search(r'\{"score":\s*([0-9.]+)', system)
        self.assertNotIn(".", example.group(1),
                         "AI-11: shipped example uses 8.5, inconsistent with the 0..100 integer format")


if __name__ == "__main__":
    unittest.main(verbosity=2)
