"""
wave.py - is a phishing wave hitting the inbox? Plain Python, no AI.

A wave = at least WAVE_MIN_EMAILS phishing emails imitating the SAME brand
within WAVE_WINDOW_MINUTES of each other. One phishing email is not a wave.

Run it:  python wave.py data/inbox_today.csv results_today.csv
"""

import csv
import sys

from tools import KNOWN_BRANDS, run_all_checks

WAVE_MIN_EMAILS = 5        # how many fakes of one brand count as a wave
WAVE_WINDOW_MINUTES = 60   # ...within this many minutes


def to_minutes(hhmm):
    """'09:14' -> 554 (minutes after midnight), so times are easy to compare."""
    hours, minutes = hhmm.split(":")
    return int(hours) * 60 + int(minutes)


def imitated_brand(email, checks):
    """Which brand is this email pretending to be? Returns its official domain.
    First choice: a lookalike domain the code found. Second: the brand name in
    the display name (e.g. 'Lumen Bank' sending from gmail.com)."""
    if checks["lookalikes"]:
        return checks["lookalikes"][0]["imitates"]
    name = email["from_name"].lower().replace(" ", "")
    for brand, official in KNOWN_BRANDS.items():
        if brand in name:
            return official
    return None


def biggest_burst(hits):
    """The largest group of emails that all arrived within the time window.
    hits must already be sorted by time."""
    best, start = [], 0
    for end in range(len(hits)):
        while (to_minutes(hits[end]["email"]["received_at"])
               - to_minutes(hits[start]["email"]["received_at"])) > WAVE_WINDOW_MINUTES:
            start += 1
        if end - start + 1 > len(best):
            best = hits[start:end + 1]
    return best


def find_waves(emails, results):
    """Returns (waves, singles).
    waves:   one dict per brand under attack
    singles: {brand: count} for phishing that did NOT reach wave size"""
    verdicts = {r["id"]: r["verdict"] for r in results}

    by_brand = {}
    for email in emails:
        if verdicts.get(email["id"]) != "phishing":
            continue
        checks = run_all_checks(email)
        brand = imitated_brand(email, checks)
        if brand:
            by_brand.setdefault(brand, []).append({"email": email, "checks": checks})

    waves, singles = [], {}
    for brand, hits in by_brand.items():
        hits.sort(key=lambda h: to_minutes(h["email"]["received_at"]))
        burst = biggest_burst(hits)
        if len(burst) < WAVE_MIN_EMAILS:
            singles[brand] = len(hits)
            continue
        fake_domains = sorted({l["domain"] for h in burst for l in h["checks"]["lookalikes"]})
        waves.append({
            "brand": brand,
            "count": len(burst),
            "first": burst[0]["email"]["received_at"],
            "last": burst[-1]["email"]["received_at"],
            "ids": [h["email"]["id"] for h in burst],
            "fake_domains": fake_domains,
            "lures": [(h["email"]["received_at"], h["email"]["id"], h["email"]["subject"])
                      for h in burst],
        })
    return waves, singles


def load_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def print_report(waves, singles):
    if not waves:
        print("No phishing wave detected.")
    for w in waves:
        print(f"WAVE DETECTED: {w['count']} phishing emails imitating {w['brand']} "
              f"between {w['first']} and {w['last']}")
        print(f"  Fake domains used ({len(w['fake_domains'])}): {', '.join(w['fake_domains'])}")
        print("  Lures seen:")
        for time_, eid, subject in w["lures"]:
            print(f"    {time_}  {eid}  {subject}")
    for brand, n in singles.items():
        print(f"Not a wave: {n} phishing email(s) imitating {brand} (below {WAVE_MIN_EMAILS})")


if __name__ == "__main__":
    emails_path = sys.argv[1] if len(sys.argv) > 1 else "data/inbox_today.csv"
    results_path = sys.argv[2] if len(sys.argv) > 2 else "results_today.csv"
    waves, singles = find_waves(load_csv(emails_path), load_csv(results_path))
    print_report(waves, singles)
