# Session 3: AI accuracy re-runs

- **Date:** 2026-11-28
- **Tester:** Neiko Sarandon
- **Model:** `openai/gpt-oss-120b` on Groq (my key)
- **Repo:** `main` at commit `b9047ab`
- **Safety tests on this commit:** `python -m unittest discover tests` → expected `Ran 14 tests ... OK`. Result: ✅ 14 tests OK (2026-11-28 20:29)

Results go to separate files inside `Dry_runs/`, so Pau's `results_today.csv` and `results_hard.csv` are not overwritten.

## Commands

```
python agent.py data/inbox_today.csv Dry_runs/results_today_neiko.csv
python eval.py data/inbox_today_labels.csv Dry_runs/results_today_neiko.csv

python agent.py data/inbox_hard.csv Dry_runs/results_hard_neiko.csv
python eval.py data/inbox_hard_labels.csv Dry_runs/results_hard_neiko.csv
```

## Results

| Set | Pau's score (README) | My score | Phishing marked SAFE | Safety overrides |
| --- | --- | --- | --- | --- |
| Demo inbox (16) | 16/16 | **16/16** | 0 | 0 |
| Hard inbox (30) | 28/30 | **28/30** | 0 | 0 |

My per-email verdicts are in `results_today_neiko.csv` and `results_hard_neiko.csv`. **All 46 verdicts are identical to Pau's** (`results_today.csv`, `results_hard.csv`), on a different machine, Groq account and day.

## Mistakes

Both are cautious misses: something flagged as phishing that wasn't clear-cut. No phishing email was marked safe.

| Email | Expected | AI said | Same miss as Pau's run? |
| --- | --- | --- | --- |
| H16: job offer asking for an ID and home address | needs_human | phishing | Yes |
| H25: landlord announcing a new bank account for rent | safe | phishing | Yes |

## Notes

- No errors or rate limits from Groq during the two runs.
- Results are reproducible: same scores and same verdicts as Pau's run. The AI is called with `temperature=0`, which helps keep answers stable.
