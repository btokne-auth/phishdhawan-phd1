"""
tests/test_safety.py - proves PHD1's safety rules hold, with no AI and no internet.

The LLM only proposes. These tests check that CODE keeps the final say:
  - a high-risk flag always waits for a human
  - anything outside the policy is rejected
  - a phishing wave needs 5+ fakes of one brand within 60 minutes

Run it:  python -m unittest discover tests
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("LLM_API_KEY", "not-used-in-tests")  # no real LLM calls happen here

from flags import FLAG_BANNER, FLAG_BLOCK_LINKS
from respond import Action, Plan, decide
from wave import find_waves

ALL_OFF = {FLAG_BANNER: False, FLAG_BLOCK_LINKS: False}


def plan(*flags):
    return Plan(summary="test", actions=[Action(flag=f, why="test") for f in flags])


class TheGate(unittest.TestCase):
    """decide(): code checks every proposal the LLM makes."""

    def modes(self, the_plan, flags=ALL_OFF):
        return {s["flag"]: s["mode"] for s in decide(the_plan, flags)}

    def test_low_risk_runs_alone(self):
        self.assertEqual(self.modes(plan(FLAG_BANNER)), {FLAG_BANNER: "auto"})

    def test_high_risk_always_asks_a_human(self):
        self.assertEqual(self.modes(plan(FLAG_BLOCK_LINKS)), {FLAG_BLOCK_LINKS: "ask"})

    def test_unknown_action_is_rejected(self):
        # e.g. an injected email convinces the LLM to propose something else
        modes = self.modes(plan("disable_spam_filter", "whitelist_sender"))
        self.assertEqual(set(modes.values()), {"rejected"})

    def test_flag_already_on_is_skipped(self):
        modes = self.modes(plan(FLAG_BANNER), {FLAG_BANNER: True, FLAG_BLOCK_LINKS: False})
        self.assertEqual(modes, {FLAG_BANNER: "skipped"})

    def test_low_risk_goes_before_asking(self):
        steps = decide(plan(FLAG_BLOCK_LINKS, FLAG_BANNER), ALL_OFF)
        self.assertEqual([s["mode"] for s in steps], ["auto", "ask"])

    def test_repeats_and_spaces_cannot_sneak_past(self):
        modes = decide(plan(f" {FLAG_BLOCK_LINKS} ", FLAG_BLOCK_LINKS), ALL_OFF)
        self.assertEqual([s["mode"] for s in modes], ["ask"])


def emails_at(*times, sender="alerts@lumen-bank-secure.com"):
    emails, results = [], []
    for i, t in enumerate(times):
        eid = f"X{i}"
        emails.append({"id": eid, "received_at": t, "from_name": "Lumen Bank",
                       "from_address": sender, "reply_to": "",
                       "subject": "Verify your account", "body": "Log in now."})
        results.append({"id": eid, "verdict": "phishing"})
    return emails, results


class TheWaveRule(unittest.TestCase):
    """find_waves(): plain code decides what counts as a wave, not the AI."""

    def test_five_within_an_hour_is_a_wave(self):
        waves, _ = find_waves(*emails_at("09:00", "09:10", "09:20", "09:30", "09:59"))
        self.assertEqual(len(waves), 1)
        self.assertEqual(waves[0]["count"], 5)

    def test_four_is_not_a_wave(self):
        waves, _ = find_waves(*emails_at("09:00", "09:10", "09:20", "09:30"))
        self.assertEqual(waves, [])

    def test_five_spread_over_hours_is_not_a_wave(self):
        waves, _ = find_waves(*emails_at("08:00", "09:01", "10:02", "11:03", "12:04"))
        self.assertEqual(waves, [])

    def test_safe_emails_are_never_counted(self):
        emails, results = emails_at("09:00", "09:05", "09:10", "09:15", "09:20")
        for r in results:
            r["verdict"] = "safe"
        waves, _ = find_waves(emails, results)
        self.assertEqual(waves, [])


if __name__ == "__main__":
    unittest.main()
