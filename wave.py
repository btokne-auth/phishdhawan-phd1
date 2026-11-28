"""
wave.py - is a phishing wave hitting the inbox? Plain Python, no AI.

A wave = at least WAVE_MIN_EMAILS phishing emails imitating the SAME brand
within WAVE_WINDOW_MINUTES of each other. One phishing email is not a wave.

Run it:  python wave.py data/inbox_today.csv results_today.csv
"""

import csv
import re
import sys

from tools import KNOWN_BRANDS, get_domain, run_all_checks

WAVE_MIN_EMAILS = 5        # how many fakes of one brand count as a wave
WAVE_WINDOW_MINUTES = 60   # ...within this many minutes


def to_minutes(hhmm):
    """'09:14' -> 554 (minutes after midnight), so times are easy to compare."""
    hours, minutes = hhmm.split(":")
    return int(hours) * 60 + int(minutes)


# Words that say nothing about WHO an email claims to be ("PesoPay Support",
# "PesoPay Security Team" and "PesoPay" are all PesoPay).
GENERIC_NAME_WORDS = {
    "support", "team", "security", "alert", "alerts", "billing", "help", "helpdesk",
    "desk", "care", "cares", "assistance", "program", "fraud", "service", "services",
    "customer", "official", "online", "noreply", "no", "reply", "notification",
    "notifications", "account", "accounts", "verification", "center", "centre",
    "admin", "info", "the", "and", "of", "it", "hr", "dept", "department",
}


def imitated_brand(email, checks):
    """Which brand is this email pretending to be?
    1. A lookalike domain of a brand we know (returns its official domain).
    2. A brand we know in the display name ('Lumen Bank' sending from gmail).
    3. Any other brand: the display name without generic words, so fakes of
       a brand we've never heard of ('PesoPay', 'PesoPay Support') still group
       together. Returns that name, e.g. 'PesoPay'."""
    for lookalike in checks["lookalikes"]:
        if lookalike["imitates"]:
            return lookalike["imitates"]
    name = email["from_name"].lower().replace(" ", "")
    for brand, official in KNOWN_BRANDS.items():
        if brand in name:
            return official
    words = [w for w in re.findall(r"[A-Za-z0-9]+", email["from_name"])
             if w.lower() not in GENERIC_NAME_WORDS]
    return " ".join(words) or None


def brand_key(brand):
    """'PesoPay', 'Peso Pay' and 'pesopay' are the same brand."""
    return brand.lower().replace(" ", "")


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

    by_brand, labels = {}, {}
    for email in emails:
        if verdicts.get(email["id"]) != "phishing":
            continue
        checks = run_all_checks(email)
        brand = imitated_brand(email, checks)
        if brand:
            key = brand_key(brand)
            labels.setdefault(key, brand)          # show the first spelling seen
            by_brand.setdefault(key, []).append({"email": email, "checks": checks})

    waves, singles = [], {}
    for key, hits in by_brand.items():
        brand = labels[key]
        hits.sort(key=lambda h: to_minutes(h["email"]["received_at"]))
        burst = biggest_burst(hits)
        if len(burst) < WAVE_MIN_EMAILS:
            singles[brand] = len(hits)
            continue
        fake_domains = set()
        for h in burst:
            found = {l["domain"] for l in h["checks"]["lookalikes"]}
            if not found:      # a brand we don't know: every domain the fake used is suspect
                found = {get_domain(h["email"]["from_address"])}
                found |= {get_domain(u) for u in h["checks"]["urls"]}
            fake_domains |= {d for d in found if d}
        fake_domains = sorted(fake_domains)
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
