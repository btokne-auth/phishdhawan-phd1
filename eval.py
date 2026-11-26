"""
eval.py - how well did the agent do? Compares results.csv to data/labels.csv.
Run it:  python eval.py
   or:   python eval.py data/inbox_today_labels.csv results_today.csv
"""

import csv
import sys
from collections import Counter

labels_path = sys.argv[1] if len(sys.argv) > 1 else "data/labels.csv"
results_path = sys.argv[2] if len(sys.argv) > 2 else "results.csv"

with open(labels_path, newline="", encoding="utf-8") as f:
    labels = {row["id"]: row["label"] for row in csv.DictReader(f)}
with open(results_path, newline="", encoding="utf-8") as f:
    results = {row["id"]: row for row in csv.DictReader(f)}

correct = 0
mistakes = []
pairs = Counter()          # (expected, got) -> how many times
for eid, expected in labels.items():
    got = results[eid]["verdict"] if eid in results else "(missing)"
    pairs[(expected, got)] += 1
    if got == expected:
        correct += 1
    else:
        mistakes.append((eid, expected, got, results.get(eid, {}).get("reason", "")))

total = len(labels)
print(f"Accuracy: {correct}/{total} = {correct / total:.0%}\n")

# The worst mistake: a dangerous email marked safe.
dangerous_as_safe = [m for m in mistakes if m[1] == "phishing" and m[2] == "safe"]
print(f"Phishing marked SAFE (worst mistake): {len(dangerous_as_safe)}")
overrides = sum(1 for r in results.values() if r["overridden"] == "True")
print(f"Safety overrides used: {overrides}\n")

print("Expected -> Got (count)")
for (expected, got), n in sorted(pairs.items()):
    mark = "  " if expected == got else "X "
    print(f"  {mark}{expected:12} -> {got:12} {n}")

if mistakes:
    print("\nMistakes:")
    for eid, expected, got, reason in mistakes:
        print(f"  {eid}: expected {expected}, got {got} | {reason[:70]}")
