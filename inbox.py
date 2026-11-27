"""
inbox.py - a tiny local inbox that reacts live to PHD1's flags.

  phishing_warning_banner ON -> warning banner on emails imitating the attacked brand
  block_external_links    ON -> every external link is blocked (even real ones)

Run it, then open http://127.0.0.1:8000 in your browser:
    python inbox.py          the demo inbox (16 emails, Lumen Bank wave)
    python inbox.py hard     the harder test inbox (30 emails, StreamBox wave)
    python inbox.py all      both together (46 emails, both waves)
For "hard" and "all", run agent.py on the hard inbox first so results_hard.csv exists.

Demo safety: links are never real, clickable links here. Email text is shown
as plain text (never as HTML), because it is written by attackers.
"""

import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from flags import FLAG_BANNER, FLAG_BLOCK_LINKS, read_flags
from tools import extract_urls
from wave import find_waves, load_csv

TODAY = ("data/inbox_today.csv", "results_today.csv")   # (emails, AI verdicts)
HARD = ("data/inbox_hard.csv", "results_hard.csv")
INBOXES = {
    # name: ([(emails, verdicts), ...], older mail shown under "Earlier")
    "today": ([TODAY], "data/inbox_older.csv"),
    "hard": ([HARD], None),
    "all": ([TODAY, HARD], "data/inbox_older.csv"),
}
INBOX = sys.argv[1] if len(sys.argv) > 1 else "today"
if INBOX not in INBOXES:
    sys.exit(f"Unknown inbox '{INBOX}'. Use one of: {', '.join(INBOXES)}")
SOURCES, OLDER_PATH = INBOXES[INBOX]
HOST, PORT = "127.0.0.1", 8000   # only reachable from this laptop

# Display realism only: today's emails the user has already opened.
ALREADY_READ = {"T01", "T03", "T07", "T11"}


def to_view(e, day, time_, read, wave_brand):
    return {
        "id": e["id"],
        "day": day,
        "time": time_,
        "from_name": e["from_name"],
        "from_address": e["from_address"],
        "subject": e["subject"],
        "body": e["body"],
        "links": extract_urls(e["body"]),
        "read": read,
        "in_wave": wave_brand is not None,
        "brand": wave_brand,                     # which brand this email's wave imitates
    }


def build_state():
    """Everything the page needs: emails, which ones get a banner, live flags."""
    emails, results = [], []
    for emails_path, results_path in SOURCES:
        emails += load_csv(emails_path)
        try:
            results += load_csv(results_path)
        except FileNotFoundError:                # AI hasn't sorted this inbox yet
            pass
    waves, _ = find_waves(emails, results)
    wave_brand = {eid: w["brand"] for w in waves for eid in w["ids"]}
    brand = waves[0]["brand"] if waves else None

    try:
        flags, flags_error = read_flags(), None
    except Exception as e:                       # Flagsmith unreachable, bad key...
        flags, flags_error = {FLAG_BANNER: False, FLAG_BLOCK_LINKS: False}, str(e)

    emails.sort(key=lambda e: e["received_at"], reverse=True)   # newest first, like a real inbox
    today = [to_view(e, "Today", e["received_at"], e["id"] in ALREADY_READ, wave_brand.get(e["id"]))
             for e in emails]
    try:
        older = [to_view(e, e["day"], e["time"], e["read"] == "yes", None)
                 for e in load_csv(OLDER_PATH)] if OLDER_PATH else []
    except FileNotFoundError:
        older = []

    return {"flags": flags, "flags_error": flags_error, "brand": brand, "emails": today + older}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/state":
            body = json.dumps(build_state()).encode("utf-8")
            content_type = "application/json"
        elif self.path in ("/", "/index.html"):
            with open("inbox.html", "rb") as f:
                body = f.read()
            content_type = "text/html; charset=utf-8"
        else:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):                # keep the terminal quiet
        pass


if __name__ == "__main__":
    print(f"Inbox '{INBOX}' running at http://{HOST}:{PORT}  (Ctrl + C to stop)")
    for emails_path, results_path in SOURCES:
        try:
            load_csv(results_path)
        except FileNotFoundError:
            print(f"Note: {results_path} is missing, so its wave isn't marked yet. Run first:\n"
                  f"    python agent.py {emails_path} {results_path}")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
