# Session 1: fresh setup from the README

- **Date:** 2026-11-28
- **Tester:** Neiko Sarandon
- **Machine:** Windows, PowerShell (inside Cursor), Python 3.14
- **Repo:** `main` at commit `2f5ed77`
- **Accounts:** my own Flagsmith Cloud account (new org + project, Development environment) and my own Groq key

## Steps and results

| # | Step | Result | Notes |
| --- | --- | --- | --- |
| 1 | `git clone` / `git pull` | ✅ | |
| 2 | Create and activate `.venv` | ✅ with a fix | README only shows the Git Bash command. PowerShell needs `.venv\Scripts\Activate.ps1` |
| 3 | `pip install -r requirements.txt` | ✅ | Installs fine on Python 3.14 (CI uses 3.12) |
| 4 | Groq sign-up | ✅ after retry | First attempt showed "Something went wrong" on console.groq.com; worked later |
| 5 | Flagsmith: create `phishing_warning_banner` and `block_external_links`, both OFF | ✅ | New accounts also get a sample `show_demo_button` flag; PHD1 ignores it |
| 6 | Flagsmith: server-side key (`ser.`) | ✅ | |
| 7 | Flagsmith: Organisation API key | ✅ | Shown only once |
| 8 | Create `.env` | ⚠️ first try failed | Three values were left empty, so `flags.py` and `flag_admin.py` said the keys were "missing from .env". Fixed by pasting the keys in |
| 9 | `python -m unittest discover tests` | ✅ | `Ran 10 tests ... OK` |
| 10 | `python flags.py` | ✅ | Both flags `off` |
| 11 | `python flag_admin.py` | ✅ | Both flags found, `Admin API setup OK. Nothing was changed.` |
| 12 | `python wave.py` | ✅ | 9-email Lumen Bank wave, 8 fake domains, PayWave not a wave |

## Suggested README changes

1. Add the PowerShell activate command: `.venv\Scripts\Activate.ps1`.
2. Say which value goes in `FLAGSMITH_ENVIRONMENT_ID`: the environment's **client-side key** (Flagsmith → SDK Keys, also in the dashboard URL after `/environment/`). It worked for me.
3. Warn that the Groq key and the Flagsmith Organisation API key are shown only once: paste them straight into `.env`.
4. Quick `.env` check that doesn't print the keys:
   ```
   python -c "from dotenv import dotenv_values; print({k: bool(v) for k, v in dotenv_values('.env').items()})"
   ```
   All five should say `True`.
