"""
inbox.py - a tiny local inbox that reacts live to PHD1's flags.

  phishing_warning_banner ON -> warning banner on emails imitating the attacked brand
  block_external_links    ON -> every external link is blocked (even real ones)

Run it, then open http://127.0.0.1:8000 in your browser:
    python inbox.py

Demo safety: links are never real, clickable links here. Email text is shown
as plain text (never as HTML), because it is written by attackers.
"""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from flags import FLAG_BANNER, FLAG_BLOCK_LINKS, read_flags
from tools import extract_urls
from wave import find_waves, load_csv

EMAILS_PATH = "data/inbox_today.csv"
OLDER_PATH = "data/inbox_older.csv"     # display only: older mail, already triaged
RESULTS_PATH = "results_today.csv"
HOST, PORT = "127.0.0.1", 8000   # only reachable from this laptop

# Display realism only: today's emails the user has already opened.
ALREADY_READ = {"T01", "T03", "T07", "T11"}


def to_view(e, day, time_, read, in_wave):
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
        "in_wave": in_wave,
    }


def build_state():
    """Everything the page needs: emails, which ones get a banner, live flags."""
    emails = load_csv(EMAILS_PATH)
    results = load_csv(RESULTS_PATH)
    waves, _ = find_waves(emails, results)
    wave_ids = {eid for w in waves for eid in w["ids"]}
    brand = waves[0]["brand"] if waves else None

    try:
        flags, flags_error = read_flags(), None
    except Exception as e:                       # Flagsmith unreachable, bad key...
        flags, flags_error = {FLAG_BANNER: False, FLAG_BLOCK_LINKS: False}, str(e)

    today = [to_view(e, "Today", e["received_at"], e["id"] in ALREADY_READ, e["id"] in wave_ids)
             for e in reversed(emails)]          # newest first, like a real inbox
    try:
        older = [to_view(e, e["day"], e["time"], e["read"] == "yes", False) for e in load_csv(OLDER_PATH)]
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
    print(f"Inbox running at http://{HOST}:{PORT}  (Ctrl + C to stop)")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
