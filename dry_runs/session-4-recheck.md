# Session 4: re-check on the latest code

- **Date:** 2026-11-28
- **Tester:** Neiko Sarandon
- **Repo:** `main` at commit `352e073`
- **Why:** Pau's commits after session 3 changed how links are found and checked (`tools.py`: links without `http://`, the `@` trick, punycode), the wave rule (`wave.py`: waves from brands PHD1 doesn't know), and how blocked links are shown (`inbox.html`). The AI gets the link-check results as input, so the accuracy scores needed re-checking too.

## Safety tests

`python -m unittest discover tests` → ✅ `Ran 21 tests ... OK` (was 14 in session 3).

## Run A: demo inbox, approve (21:48)

| Check | Result |
| --- | --- |
| Wave detected | ✅ Same as before: 9 fake Lumen Bank emails, 09:14 → 09:47 |
| Banner switched on by PHD1 alone | ✅ 4.9 s after the wave was found |
| Approved with `y` | ✅ "Links blocked, approved by Neiko". Report `incidents/incident-20261128-214857.md` |
| **New:** blocked links shown defanged on screen | ✅ `hxxps://megadeals-shop[.]com/payday`, also in the email previews in the list |
| **New:** "why blocked" note | ✅ Shown below the email text, not in the middle of a sentence |
| Copying a blocked link | ✅ "Link blocked. Copied as unclickable text." |
| Reset afterwards | ✅ Both flags OFF |

Screenshots: `s4-a-*`.

## Run B: tricks inbox, approve (22:02)

`python inbox.py tricks` + `python respond.py data/inbox_tricks.csv results_tricks.csv`

| Check | Expected | Result |
| --- | --- | --- |
| Wave from a brand PHD1 doesn't know | PesoPay wave | ✅ "Pretending to be PesoPay", 5 emails in 29 minutes (10:02 → 10:31), 5 fake domains |
| Banner switched on by PHD1 alone | ✅ | ✅ 2.8 s. Report `incidents/incident-20261128-220217.md` |
| PesoPay emails K7–K11 | Phishing warning | ✅ "This email pretends to be PesoPay but isn't", Suspicious tab shows 5 |
| `www.` link (K9) | Blocked | ✅ `www[.]pesopay-secure[.]co/login` |
| Link without `http://` (K8, K5) | Blocked | ✅ `pesopay-kyc[.]net/verify`, real `parcelgo[.]com/track` |
| Punycode look-alike (K4) | Blocked | ✅ `hxxp://xn--lumenbnk-9xa[.]ph/statement` |
| Email address in text (K6, Ate Joy) | Not treated as a link | ✅ Shown as normal text, no BLOCKED chip |
| 4 fake Lumen Bank emails (K1–K4) | No banner: below the 5-email wave rule | ✅ No warning icon (expected) |
| `@` trick (K3) | Blocked | Not screenshotted; covered by the safety tests |
| Reset afterwards | Both flags OFF | ✅ |

Screenshots: `s4-b-*`.

## Run C: AI accuracy on the new code

```
python agent.py data/inbox_today.csv dry_runs/results_today_s4.csv
python eval.py data/inbox_today_labels.csv dry_runs/results_today_s4.csv
python agent.py data/inbox_hard.csv dry_runs/results_hard_s4.csv
python eval.py data/inbox_hard_labels.csv dry_runs/results_hard_s4.csv
```

| Set | Session 3 (old code) | Session 4 (new code) | Phishing marked SAFE | Safety overrides |
| --- | --- | --- | --- | --- |
| Demo inbox (16) | 16/16 | **16/16** | 0 | 0 |
| Hard inbox (30) | 28/30 | **28/30** | 0 | 0 |

**All verdicts are identical** to session 3 and to Pau's `results_today.csv` / `results_hard.csv`. Same two cautious misses: H16 (job offer asking for an ID: expected needs_human, got phishing) and H25 (landlord's new bank account: expected safe, got phishing).

The tricks inbox has no answer key, so it can't be scored with `eval.py`; Run B checks it by eye instead.

Screenshots: `s4-c-*`.

## Summary

The new link checks and the unknown-brand wave rule work, and they didn't change any AI verdict or the demo wave. First-protection time across all 7 runs today: 2.7–6.1 s.
