# Build log

## Before Toggle Wars

A practice project: an AI email triage agent that sorts each email into phishing, spam, safe or needs_human, with code checks for lookalike domains, sender mismatches, links and urgency, and a 25-email practice set scored by `eval.py` (24/25). Files: `agent.py`, `tools.py`, `prompts.py`, `eval.py`, `data/emails.csv`, `data/labels.csv`.

Flagsmith setup (account, project, the two flags, both OFF) was done the night before hacking started.

## Day 1: Thu Nov 26

- New public repo; flags read through the Flagsmith Python SDK (`flags.py`).
- Today's 16-email inbox built around the Filipino-morning scenario, triaged 16/16.
- Wave detection in plain code (`wave.py`).
- `respond.py`: the AI proposes a plan, code checks it against the policy, risk tiers, the y/N approval, and the incident log.
- `flag_admin.py`: switching flags through the Flagsmith Admin API (moved to the `__future__` endpoint because Feature Versioning is on), plus `--reset-demo`.
- The live inbox page (`inbox.py`, `inbox.html`), redesigned in the iOS Mail / minimal style, with light and dark themes.
- First real end-to-end run: wave found, banners on alone, links blocked after approval, inbox reacting live.

## Day 2: Fri Nov 27

- Terminal output redesigned with Rich: sections, the who-decides table, the Why / Cost approval box, status lines at both ends, a safe default of No.
- Fixed: the end status now waits for Flagsmith to share the change before reading it.
- `tests/test_safety.py`: 10 tests for the policy gate and the wave rule; GitHub runs them on every push.
- README rewritten for PHD1.
- The 30-email hard inbox (second brand wave, slow attack, unknown brands, Taglish, a second injection), scored 28/30.
- The inbox page can show the hard inbox, or all 46 emails together.
- Neiko Sarandon joined the team (tester, co-writer of the storyline).

## Day 3: Sat Nov 28

- Made-up personal email addresses switched to reserved example domains; all three test sets re-run (16/16, 28/30, 24/25).
- Terminal wording rewritten in plainer language, with the Flagsmith flag names shown in the table.
- Two fixes found by the fresh-setup test: defanged links like `site[.]com` no longer crash the link checks, and a confirmed wave always gets warning banners even if the AI proposes nothing. Safety tests: 10 → 14.
- Copying a blocked link now gives a defanged, unclickable version, so pasting it into a browser goes nowhere (Neiko's idea).
- README screenshots and this `docs/` folder.
- Planned: a fresh-setup test on a second laptop, following only the README.
- Planned: the demo video.

## Day 4: Sun Nov 29

- Planned: re-takes, the video link in the README, final checks, submit.
