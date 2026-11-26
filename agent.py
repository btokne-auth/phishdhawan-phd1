"""
agent.py - the triage loop.

For each email:  read -> run code checks -> ask LLM -> validate -> safety rules -> write
Run it:  python agent.py
"""

import csv
import json
import os
import time
from typing import Literal

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError

from prompts import SYSTEM_PROMPT
from tools import run_all_checks

load_dotenv()

# Provider settings. Defaults = Groq. To switch to GitHub Models later, change
# these three values in .env - no code changes needed.
client = OpenAI(
    api_key=os.getenv("LLM_API_KEY", os.getenv("GROQ_API_KEY")),
    base_url=os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1"),
)
MODEL = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")

MIN_CONFIDENCE = 0.6     # below this, a human should look
SECONDS_BETWEEN_CALLS = 2.5  # stay under the free tier's requests-per-minute


# --- The shape the LLM's answer MUST have (Pydantic checks this) -------------
class Verdict(BaseModel):
    verdict: Literal["phishing", "spam", "safe", "needs_human"]
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str
    risky_links: list[str] = []


# --- Step 3: ask the LLM ------------------------------------------------------
def build_message(email, checks):
    """Wrap the email in tags so the model treats it as data, not instructions."""
    body = email["body"]
    # Remove fake tags an attacker might add to "escape" the box (see E20).
    for tag in ("<email>", "</email>"):
        body = body.replace(tag, "[removed tag]")
    return (
        "CHECK RESULTS (from reliable code):\n"
        f"{json.dumps(checks, indent=2)}\n\n"
        "<email>\n"
        f"From: {email['from_name']} <{email['from_address']}>\n"
        f"Reply-To: {email.get('reply_to') or '(same as sender)'}\n"
        f"Subject: {email['subject']}\n\n"
        f"{body}\n"
        "</email>"
    )


def parse_verdict(text):
    """Pull the JSON object out of the reply and validate it with Pydantic."""
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("no JSON object in reply")
    return Verdict.model_validate_json(text[start:end + 1])


def ask_llm(email, checks):
    """Returns (Verdict, None) on success, or (None, error message) after one retry."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_message(email, checks)},
    ]
    last_error = None
    for attempt in range(2):                     # first try + one retry
        try:
            response = client.chat.completions.create(
                model=MODEL, messages=messages, temperature=0,
            )
            reply = response.choices[0].message.content or ""
            return parse_verdict(reply), None
        except (ValidationError, ValueError) as e:
            last_error = f"bad answer format: {e}"
            # Tell the model what went wrong and let it try once more.
            messages.append({"role": "assistant", "content": reply})
            messages.append({"role": "user", "content":
                             "Your reply was not valid. Reply with ONLY the JSON object."})
        except Exception as e:                   # network error, rate limit, etc.
            last_error = f"LLM call failed: {e}"
            time.sleep(5)
    return None, last_error


# --- Step 4: safety rules (code has the last word) ----------------------------
def apply_safety_rules(result, checks):
    """Returns (verdict, confidence, reason, overridden)."""
    v = result.verdict
    if checks["lookalikes"] and v == "safe":
        return "phishing", result.confidence, \
            f"OVERRIDE: model said safe, but {checks['lookalikes'][0]['reason']}", True
    if checks["sender"]["mismatch"] and v == "safe":
        return "needs_human", result.confidence, \
            "OVERRIDE: model said safe, but sender doesn't match", True
    if result.confidence < MIN_CONFIDENCE and v != "needs_human":
        return "needs_human", result.confidence, \
            f"OVERRIDE: low confidence ({result.confidence}) for '{v}'", True
    return v, result.confidence, result.reason, False


def risky_links(result, checks):
    """Only keep links that really appear in the email (no made-up links),
    plus every link on a lookalike domain the code found."""
    real = set(checks["urls"])
    from_llm = [u for u in result.risky_links if u in real]
    bad_domains = {l["domain"] for l in checks["lookalikes"]}
    from_code = [u for u in checks["urls"] if any(d in u for d in bad_domains)]
    return sorted(set(from_llm + from_code))


# --- The loop -----------------------------------------------------------------
def triage(email):
    checks = run_all_checks(email)
    result, error = ask_llm(email, checks)
    if result is None:                           # golden rule: never guess
        return {"id": email["id"], "verdict": "needs_human", "confidence": "",
                "reason": error, "risky_links": ";".join(checks["urls"]),
                "overridden": False}
    verdict, confidence, reason, overridden = apply_safety_rules(result, checks)
    return {"id": email["id"], "verdict": verdict, "confidence": confidence,
            "reason": reason, "risky_links": ";".join(risky_links(result, checks)),
            "overridden": overridden}


def main():
    with open("data/emails.csv", newline="", encoding="utf-8") as f:
        emails = list(csv.DictReader(f))

    rows = []
    for i, email in enumerate(emails, start=1):
        row = triage(email)
        rows.append(row)
        flag = "  (overridden)" if row["overridden"] else ""
        print(f"[{i}/{len(emails)}] {row['id']}: {row['verdict']}{flag}")
        time.sleep(SECONDS_BETWEEN_CALLS)

    with open("results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print("Done. Wrote results.csv")


if __name__ == "__main__":
    main()
