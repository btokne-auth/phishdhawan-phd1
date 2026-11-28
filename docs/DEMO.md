# Demo checklist

## Before

- [ ] Close any editor tab showing `.env`. Keys must never appear on screen.
- [ ] `python flag_admin.py --reset-demo`: both flags OFF, like a fresh morning.
- [ ] Terminal 1: `python inbox.py` (the 16-email demo inbox), then open http://127.0.0.1:8000.
- [ ] Terminal 2: ready for `python respond.py`.
- [ ] Inbox and terminal side by side; terminal font large enough to read in a video.
- [ ] Maximize or size the terminal **before** running, and don't resize it during the run: the boxes are drawn for the width at that moment, and resizing re-wraps them. (From Neiko's test runs.)
- [ ] Optional: the Flagsmith dashboard open in another tab, to show the flags flipping there too.

## The run

1. `python respond.py`
2. The top line shows **banners off · link block off · ready**.
3. WAVE DETECTED: 9 fake Lumen Bank emails in 33 minutes.
4. Warning banners switch on by themselves. In the inbox, the warning icons appear within a few seconds. Open a fake email to show the "PHISHING WARNING" label.
5. PHD1 stops at **Your call**: read the Why and the Cost.
6. Type `y`. In the inbox, the links turn gray with "BLOCKED" (allow a few seconds).
7. The last line shows **banners on · link block on · wave handled**, and where the report was saved.

Flagsmith takes a few seconds to share a change, and the inbox checks every 3 seconds, so wait a beat on the inbox after each switch.

## After

- [ ] Open the new report in `incidents/` if you want to show it.
- [ ] `python flag_admin.py --reset-demo` before the next take.

## Sharing the inbox with someone else

```bash
cloudflared tunnel --url http://127.0.0.1:8000
```

Share the `.trycloudflare.com` link it prints. It works only while both the inbox and the tunnel are running, and it changes every time the tunnel restarts.
