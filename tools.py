"""
tools.py - the reliable checks. Plain Python, no AI.

The agent runs these FIRST on every email, then hands the results to the LLM.
They are deterministic: same email in -> same result out, every time.
"""

import re
from urllib.parse import urlparse

# --- Reference list: the official domains of brands we know -----------------
# (Fictional brands from our sample dataset. In a real system this list would
#  come from the organisation's own allowlist.)
KNOWN_BRANDS = {
    "lumenbank": "lumenbank.ph",
    "parcelgo": "parcelgo.com",
    "streambox": "streambox.com",
    "paywave": "paywave.com",
    "srtc": "srtc.edu.ph",
}

# Phrases attackers use to rush people into acting without thinking
URGENCY_PHRASES = [
    "verify now", "verify your", "within 24 hours", "within 12 hours",
    "immediately", "right away", "suspended", "account will be closed",
    "avoid account lock", "confirm your", "update your card", "act now",
    "limited time", "expire", "today to avoid", "unauthorized",
]


# --- Small helpers -----------------------------------------------------------

def get_domain(text):
    """Pull the domain out of a URL or an email address, in lowercase.
    'http://Example.com/login' -> 'example.com'
    'alerts@lumenbank.ph'      -> 'lumenbank.ph'
    """
    text = text.strip().lower()
    # "Defanged" links like site[.]com or site(.)com are common in security
    # emails; read them as normal dots instead of crashing on the brackets.
    text = text.replace("[.]", ".").replace("(.)", ".").replace("[dot]", ".")
    if "@" in text and "://" not in text:
        return text.split("@")[-1]
    try:
        return urlparse(text).netloc.split(":")[0]   # drop a port like :8080
    except ValueError:                           # still not a valid URL: skip it, don't crash
        return ""


def is_official(domain, official):
    """True if domain IS the official domain or a subdomain of it.
    'forms.srtc.edu.ph' is official for 'srtc.edu.ph'; 'srtc-edu.com' is not.
    """
    return domain == official or domain.endswith("." + official)


def edit_distance(a, b):
    """How many single-letter edits (add, remove, swap) turn a into b.
    'parcelg0.com' vs 'parcelgo.com' -> 1
    """
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        curr = [i]
        for j, cb in enumerate(b, start=1):
            cost = 0 if ca == cb else 1
            curr.append(min(prev[j] + 1,        # remove a letter
                            curr[j - 1] + 1,    # add a letter
                            prev[j - 1] + cost)) # swap a letter
        prev = curr
    return prev[-1]


# --- Tool 1: extract URLs -----------------------------------------------------

def extract_urls(body):
    """Find every http/https link in the email text."""
    urls = re.findall(r"https?://[^\s\"'<>]+", body)
    return [u.rstrip(".,);]") for u in urls]   # trim punctuation stuck to the end


# --- Tool 2: lookalike domain -------------------------------------------------

def lookalike_domain(domain):
    """Is this domain pretending to be one of our known brands?"""
    domain = domain.lower()
    for brand, official in KNOWN_BRANDS.items():
        if is_official(domain, official):
            return {"is_lookalike": False, "imitates": None, "reason": "official domain"}
        if brand in domain.replace("-", "").replace(".", ""):
            return {"is_lookalike": True, "imitates": official,
                    "reason": f"uses the name '{brand}' but is not {official}"}
        distance = edit_distance(domain, official)
        if 0 < distance <= 2:
            return {"is_lookalike": True, "imitates": official,
                    "reason": f"{distance} letter(s) away from {official}"}
    return {"is_lookalike": False, "imitates": None, "reason": "no known brand imitated"}


# --- Tool 3: sender mismatch --------------------------------------------------

def sender_mismatch(from_name, from_address, reply_to=""):
    """Does the sender's display name or reply-to disagree with the real address?"""
    sender_domain = get_domain(from_address)
    name = from_name.lower().replace(" ", "")
    problems = []

    for brand, official in KNOWN_BRANDS.items():
        if brand in name and not is_official(sender_domain, official):
            problems.append(f"name says '{from_name}' but address is {sender_domain}")

    if reply_to:
        reply_domain = get_domain(reply_to)
        if reply_domain != sender_domain:
            problems.append(f"replies go to {reply_domain}, not {sender_domain}")

    return {"mismatch": bool(problems), "problems": problems}


# --- Tool 4: urgency score ----------------------------------------------------

def urgency_score(text):
    """Count pressure phrases. More phrases = more suspicious."""
    text = text.lower()
    found = [p for p in URGENCY_PHRASES if p in text]
    return {"score": len(found), "phrases": found}


# --- Run all four on one email ------------------------------------------------

def run_all_checks(email):
    """email is one row from emails.csv (a dict). Returns every check's result."""
    urls = extract_urls(email["body"])
    domains = [get_domain(email["from_address"])] + [get_domain(u) for u in urls]
    lookalikes = [dict(domain=d, **lookalike_domain(d)) for d in domains]
    return {
        "urls": urls,
        "lookalikes": [l for l in lookalikes if l["is_lookalike"]],
        "sender": sender_mismatch(email["from_name"], email["from_address"],
                                  email.get("reply_to", "")),
        "urgency": urgency_score(email["subject"] + " " + email["body"]),
    }


# --- Try it: python tools.py --------------------------------------------------
if __name__ == "__main__":
    import csv
    with open("data/emails.csv", newline="", encoding="utf-8") as f:
        for email in csv.DictReader(f):
            r = run_all_checks(email)
            flags = []
            if r["lookalikes"]:
                flags.append("LOOKALIKE " + r["lookalikes"][0]["domain"])
            if r["sender"]["mismatch"]:
                flags.append("SENDER MISMATCH")
            if r["urgency"]["score"]:
                flags.append(f"urgency {r['urgency']['score']}")
            print(f"{email['id']}: {', '.join(flags) or 'no flags'}")
