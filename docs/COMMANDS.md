# Command cheat sheet

Every command for PHD1, with one line on what it does. Run them in a terminal inside the `phishdhawan-phd1` folder. First-time setup (clone, `.env`, Flagsmith flags) is in the [README](../README.md#run-it).

## Start of every session

Turn on the venv in **every new terminal** before running anything. You'll see `(.venv)` at the start of the line when it's on.

| Command | What it does |
| --- | --- |
| `source .venv/Scripts/activate` | Turn on the project's Python (Git Bash on Windows) |
| `.venv\Scripts\Activate.ps1` | Same, in PowerShell |
| `source .venv/bin/activate` | Same, on Linux or Mac |
| `git pull` | Download the latest changes from GitHub |
| `pip install -r requirements.txt` | Install anything new the project needs; safe to repeat |

## Running PHD1

Use two terminals: one keeps the inbox running, the other runs PHD1. Press **Ctrl+C** to stop the inbox before switching to another inbox.

| Command | What it does |
| --- | --- |
| `python inbox.py` | Start the demo inbox (16 emails, Lumen Bank wave). Open http://127.0.0.1:8000 |
| `python inbox.py hard` | The 30-email hard test inbox (StreamBox wave) |
| `python inbox.py all` | Demo + hard inbox together (46 emails, both waves) |
| `python inbox.py tricks` | Sneaky links and the PesoPay wave (11 emails) |
| `python respond.py` | Run PHD1 on the demo inbox: banners on by itself, then asks "Block the links? [y/n]" (Enter = No) |
| `python respond.py data/inbox_tricks.csv results_tricks.csv` | Run PHD1 on another inbox (here: the PesoPay wave) |
| `python flag_admin.py --reset-demo` | Switch both flags OFF. Do this before every demo run or recording |
| `python flag_admin.py` | Check the Flagsmith setup; changes nothing |
| `python flags.py` | Show whether each flag is on or off |
| `python -c "from flag_admin import switch_on; switch_on('phishing_warning_banner')"` | Turn on only the warning banners (no AI) |
| `python -c "from flag_admin import switch_on; switch_on('block_external_links')"` | Turn on only the link block (no AI) |

After a change to the inbox page itself, restart `inbox.py` and hard-refresh the browser with **Ctrl+Shift+R**.

## Tests and AI scores

| Command | What it does |
| --- | --- |
| `python -m unittest discover tests` | The safety tests, no AI or internet. Expect `Ran 21 tests` and `OK` |
| `python agent.py data/inbox_today.csv results_today.csv` | The AI sorts the demo inbox (about 1 minute) |
| `python eval.py data/inbox_today_labels.csv results_today.csv` | Score it. Expect 16/16 |
| `python agent.py data/inbox_hard.csv results_hard.csv` | The AI sorts the hard inbox (about 2 minutes) |
| `python eval.py data/inbox_hard_labels.csv results_hard.csv` | Score it. Expect 28/30 |
| `python agent.py data/inbox_tricks.csv results_tricks.csv` | The AI sorts the tricks inbox, so the PesoPay wave shows |
| `python agent.py` then `python eval.py` | The original 25-email practice set. Expect 24/25 |
| `python wave.py data/inbox_hard.csv results_hard.csv` | Show which waves the code finds (no AI) |

Each AI run starts fresh with no memory, and overwrites its results file. Stopping halfway with Ctrl+C saves nothing. Groq's free tier has a daily limit, so don't loop these. To keep your own results separate (like Neiko did), give a different output file, e.g. `dry_runs/results_today_<name>.csv`.

## Sharing the inbox with a tunnel

Keep `python inbox.py` running in one terminal, then in a second terminal:

| Command | What it does |
| --- | --- |
| `cloudflared tunnel --url http://127.0.0.1:8000` | Make a temporary public link to your inbox page |
| `"/c/Program Files (x86)/cloudflared/cloudflared.exe" tunnel --url http://127.0.0.1:8000` | Same, if it says "command not found" (Git Bash) |

Share the link ending in `.trycloudflare.com`. It only works while both terminals run, and it's a new link every time you restart the tunnel. Restarting only the inbox keeps the same link. Viewers only see the inbox page, never your keys or files.

## Git

| Command | What it does |
| --- | --- |
| `git status` | See what's changed, staged, or not saved yet |
| `git pull` | Download the latest commits from GitHub |
| `git am ~/Downloads/<name>.patch` | Apply a patch file as a commit |
| `git push` | Upload your commits to GitHub |
| `git add <file>` | Mark a file to be saved in the next commit |
| `git commit -m "message"` | Save the marked files as a commit |
| `git log -5 --format="%h  %an <%ae>  %s"` | Show the last 5 commits with their author |

If the same patch name was downloaded twice, the new one may be called `name (1).patch`: use `git am ~/Downloads/"name (1).patch"`.

## Quick fixes

| Problem | Fix |
| --- | --- |
| `git am` says "Dirty index" | `git am --abort`, then `git restore --staged incidents/`, then `git am` again |
| Prompt shows `AM 1/1` or "previous rebase directory still exists" | `git am --abort` cancels the stuck patch, then try again |
| 127.0.0.1:8000 "can't be reached" | The inbox isn't running: `python inbox.py` |
| Tunnel shows red "connection refused" errors | Same: start `python inbox.py`; the tunnel itself is fine |
| Page didn't change after an update | Restart `inbox.py`, then Ctrl+Shift+R in the browser |
| PHD1 skips a flag ("already on") | `python flag_admin.py --reset-demo` first |
| No warnings in the tricks inbox | Run `python agent.py data/inbox_tricks.csv results_tricks.csv` first; only waves of 5+ get banners |
| "keys missing from .env" | Check all five values: `python -c "from dotenv import dotenv_values; print({k: bool(v) for k, v in dotenv_values('.env').items()})"` |
| `cloudflared: command not found` | Use its full path (see the tunnel section) or restart VS Code |

Before recording or sharing your screen: close the `.env` tab.
