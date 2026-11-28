# PHD1: a phishing incident-response agent

**Team PHishDhawan** · Toggle Wars (WeMakeDevs x Flagsmith) · Track 02: AI Agents and Feature Flags

PHD1 watches an inbox for a **phishing wave**: many fake emails imitating the same brand in a short time. When it finds one, it responds through **Flagsmith feature flags**:

- the **low-risk** response (warning banners) it switches on **by itself**, within seconds
- the **high-risk** response (blocking every link) it **asks a human first**, showing why and what it costs

Then it writes an incident log. A small local inbox reads the same flags from Flagsmith and changes live as PHD1 acts.

**The story:** a Filipino weekday morning. A fake "financial assistance" email arrives at 9 AM, then fake bank alerts from the same "bank". By the time the ninth one lands, PHD1 has already put warnings on them, and it's waiting for your yes to block the links.

![A real PHD1 run in the terminal: the wave it found, what the AI saw, the warning banners switched on alone in 2.5 seconds, and the link block approved by a human](docs/screenshots/terminal-run.png)

| Before PHD1 | After PHD1 |
| --- | --- |
| ![The same fake email with no warning and a live link](docs/screenshots/inbox-before.png) | ![The fake email with a phishing warning and the link blocked](docs/screenshots/inbox-protected.png) |

| The cost of blocking: real links pause too | The injection email, still caught |
| --- | --- |
| ![A real delivery email whose tracking link is blocked as well](docs/screenshots/real-link-blocked.png) | ![The email telling "the AI security agent" to turn warnings off, shown with a phishing warning and its link blocked](docs/screenshots/injection.png) |

More detail in [`docs/`](docs/SUMMARY.md): design decisions, the story, testing, and the demo checklist.

## How it works

```mermaid
flowchart LR
    A[inbox_today.csv] --> B[agent.py<br/>AI sorts each email]
    B --> C[wave.py<br/>code finds the wave]
    C --> D[respond.py<br/>AI proposes a plan]
    D --> E{Code checks it<br/>against the policy}
    E -- low risk --> F[Switch ON alone]
    E -- high risk --> G[Ask a human y/N]
    E -- not allowed --> H[Rejected]
    F --> I[(Flagsmith)]
    G -- yes --> I
    I --> J[inbox.py<br/>live inbox reacts]
    D --> K[incidents/*.md<br/>incident log]
```

**Who decides what:**

| Decision | Who makes it |
| --- | --- |
| Is this email phishing? | The AI, checked by code (lookalike domains, sender mismatch) |
| Is this a wave? | Plain code: 5+ phishing emails imitating one brand within 60 minutes |
| What should we do about it? | The AI proposes, with a reason for each step |
| How risky is each step? | Code. The risk tier lives in a fixed policy, never in the AI's answer |
| Switch on warning banners | PHD1 alone (low risk) |
| Block all links | **A human**, after seeing why and the cost (high risk) |
| Switch any flag off | **Only a human.** PHD1 can only switch flags on |

## Why it's built this way

### Why feature flags

A **feature flag** is an on/off switch for part of an app, flipped from a dashboard or an API without changing or redeploying the app. Teams normally use flags to release features gradually, run A/B tests, turn features on for certain users only, change settings remotely, and, most importantly here, as **kill switches**: an emergency off (or on) for risky behaviour.

That makes flags a natural fit for a phishing wave, which moves in minutes:

- **Instant.** The warning and the link block are already built into the inbox, just switched off. Flipping a flag changes the app in seconds, with no code change or redeploy. On real runs, PHD1's first protection landed about 2–4 seconds after the wave was found.
- **Reversible.** Any switch can be turned back off in one click. That's what makes the risk tiers meaningful: banners change nothing important, while the link block also breaks real links until someone turns it off.
- **A wall between the agent and the app.** PHD1 never touches the inbox's code or data; it can only flip switches, and the app decides what each switch means. If the AI misbehaves, the damage is limited to those switches, and code narrows it to just two.
- **Separate keys.** The inbox can only read flags. Only PHD1's switching code holds the Admin API key.
- **A second record.** Flagsmith keeps its own history of flag changes, separate from PHD1's incident reports.

### Why the agent lives in the terminal

- **It's the defender's side.** PHD1 is a tool for whoever responds to an attack, not for the person reading email. Responders work with terminals, scripts and logs. The inbox page shows the other side: what the people being protected see.
- **A human can truly stop it.** At the approval prompt, PHD1 waits. Nothing continues until someone answers, and pressing Enter means No.
- **Clear output is part of the job.** The terminal output reads like a report: what was found, what the AI saw, who decides each step, and the why and the cost before every risky one.
- **Anyone can check it.** Emails, verdicts and reports are plain files, and every step is a command, so anyone can clone the repo and get the same result.

**In one line:** the agent lives where defenders work and where a human can stop it; the app never talks to the agent; Flagsmith is the only bridge between them.

More in [`docs/DECISIONS.md`](docs/DECISIONS.md).

## How Flagsmith is used

Two flags in one Flagsmith environment, both starting **OFF**:

| Flag | Risk | What it does in the inbox |
| --- | --- | --- |
| `phishing_warning_banner` | low | Warning icon and a "PHISHING WARNING" label on emails imitating the attacked brand |
| `block_external_links` | high | Every link in every email is paused with a "BLOCKED" chip, real ones too. Links are shown, and copied, as safe unclickable text (`hxxp://site[.]com`) |

- **Reading flags:** the Flagsmith Python SDK with the server-side environment key (`flags.py`). Both PHD1 and the inbox read flags this way.
- **Switching flags:** the Flagsmith Admin API with an Organisation API key (`flag_admin.py`). Before changing anything, it looks the flag up and refuses unless it finds exactly one match.
- **Flagsmith is the only connection between the agent and the app.** PHD1 never touches the inbox directly. It can't delete emails or change anything except those two switches.

## Safety

- **Code has the final say.** The AI's plan is checked against a fixed policy. Unknown actions are rejected, and flags that are already on are skipped. High risk always waits for a human, whatever the AI says. And if the AI proposes nothing, code still turns on the warning banners for a wave it confirmed.
- **Attacker text is data, never instructions.** Emails and subjects are wrapped in tags and labelled untrusted in every prompt. The dataset includes a prompt-injection email (T15) that talks to "the AI security agent".
- **The response plan sees very little.** For the plan, the model only gets the wave summary: subjects, fake domains and times. No email bodies. (The earlier triage step does read each email, wrapped as untrusted data.)
- **Links are never opened** anywhere, only read as text. The inbox shows email text as plain text, never as HTML.
- **Safe defaults.** Pressing Enter at the approval prompt means No. If the AI fails twice, PHD1 falls back to the low-risk step only.
- **Everything is logged.** Each run saves `incidents/incident-<time>.md` with the assessment, the lures, and a table of every action, who took it and why.
- **Tested without AI.** `tests/test_safety.py` proves the policy gate and the wave rule hold. These tests run on GitHub on every push.
- **Secrets stay local.** All keys live in `.env`, which is git-ignored.

## Results

- **Triage on today's inbox:** 16/16 correct (`results_today.csv`, scored by `eval.py`).
- **Triage on the hard test inbox:** 28/30 correct (93%), with 0 phishing emails marked safe (`results_hard.csv`). The 30 emails add a second brand wave (StreamBox), a slow attack spread over 3 hours that must not count as a wave, real alerts that look scary, scams from brands the code doesn't know, Taglish emails and a second prompt injection. Both misses were over-cautious: a job offer asking for an ID (expected needs_human) and a landlord announcing a new bank account, with no link and no data request (expected safe), were both flagged as phishing.
- **Triage on the original practice set:** 24/25 correct, with 0 phishing emails marked safe.
- **Response:** wave found (9 emails, 8 fake domains); first protection applied about 2–4 seconds after detection on real runs.

## Run it

You need Python 3.10+, a free [Groq](https://console.groq.com) API key, and a free [Flagsmith](https://flagsmith.com) account.

```bash
git clone https://github.com/btokne-auth/phishdhawan-phd1.git
cd phishdhawan-phd1
python -m venv .venv
source .venv/Scripts/activate     # Git Bash on Windows (.venv/bin/activate on Linux/Mac)
pip install -r requirements.txt
```

In Flagsmith, create two flags, `phishing_warning_banner` and `block_external_links`, both OFF. Then create a `.env` file:

```
GROQ_API_KEY=your_groq_key
FLAGSMITH_ENVIRONMENT_KEY=ser.your_server_side_key
FLAGSMITH_ADMIN_API_KEY=your_organisation_api_key
FLAGSMITH_ENVIRONMENT_ID=your_environment_id
APPROVER_NAME=your name
```

Then, in two terminals:

```bash
python inbox.py                 # terminal 1: open http://127.0.0.1:8000
                                #   (python inbox.py hard: the 30-email test inbox,
                                #    python inbox.py all: all 46 emails together)
python respond.py               # terminal 2: PHD1 responds to the wave
```

Other commands:

```bash
python flag_admin.py --reset-demo                        # a human switches both flags back OFF
python flag_admin.py                                     # check the Flagsmith setup, changes nothing
python -m unittest discover tests                        # safety tests, no AI or internet needed
python agent.py data/inbox_today.csv results_today.csv   # re-run the AI triage
python eval.py data/inbox_today_labels.csv results_today.csv
python agent.py data/inbox_hard.csv results_hard.csv     # the harder test inbox
python eval.py data/inbox_hard_labels.csv results_hard.csv
```

The model is `openai/gpt-oss-120b` on Groq by default. To switch providers, set `LLM_API_KEY`, `LLM_BASE_URL` and `LLM_MODEL` in `.env`.

## Project structure

```
phishdhawan-phd1/
├── respond.py          PHD1: plan, policy check, flags, approval, incident log
├── wave.py             wave detection (plain code)
├── flags.py            read flags (Flagsmith SDK)
├── flag_admin.py       switch flags (Flagsmith Admin API), --reset-demo
├── inbox.py            local inbox server that reads the flags
├── inbox.html          the inbox page
├── agent.py            AI triage of each email
├── tools.py            code checks: links, lookalike domains, sender mismatch, urgency
├── prompts.py          triage rules for the AI
├── eval.py             scores triage against an answer key
├── tests/              safety tests
├── data/               fake emails and answer keys (fictional brands)
└── incidents/          incident logs from real runs
```

## Built before vs during Toggle Wars

- **Before (practice project):** the email triage part: `agent.py`, `tools.py`, `prompts.py`, `eval.py` and the 25-email practice set. It started as a timed practice run for another challenge.
- **During Toggle Wars (from Nov 26, 2026):** everything about waves and flags: `wave.py`, `respond.py`, `flags.py`, `flag_admin.py`, the live inbox, today's inbox data, the safety tests and the GitHub test workflow.

## Docs

| File | What's in it |
| --- | --- |
| [`docs/SUMMARY.md`](docs/SUMMARY.md) | What PHD1 is and the rules it never breaks |
| [`docs/DECISIONS.md`](docs/DECISIONS.md) | Why a terminal agent, why Flagsmith, risk tiers, the wave rule, what's next |
| [`docs/STORY.md`](docs/STORY.md) | The Filipino-morning scenario and the demo video plan |
| [`docs/DESIGN.md`](docs/DESIGN.md) | Design rules for the inbox page and the terminal output |
| [`docs/TESTING.md`](docs/TESTING.md) | All three test inboxes, every miss, and the safety tests |
| [`docs/DEMO.md`](docs/DEMO.md) | Checklist for running or recording the demo |
| [`docs/BUILD-LOG.md`](docs/BUILD-LOG.md) | What was built before vs during Toggle Wars |

## Limitations

- Switching a flag uses Flagsmith's `__future__` environment-feature endpoint, because this environment has Feature Versioning on. Flagsmith marks that endpoint as experimental.
- Flagsmith takes a few seconds to share a change with every reader, so the inbox updates about 3–10 seconds after a switch.
- Only waves get a response. A single scam (like the lone PayWave email, T13) is labelled phishing but doesn't trigger banners.
- PHD1 handles the first wave it finds per run.
- PHD1 protects inside the inbox: warnings, blocked links and safe copies. It can't stop someone from typing an address into another browser tab by hand; that needs network-level protection such as a DNS filter. A future PHD1 could switch on a flag for that layer too.
- The demo inbox is local, with made-up emails and fictional brands. Real email systems also use sender authentication (SPF, DKIM, DMARC) and reputation data.

## The name

**PHishDhawan** = **phish** + **PH** (Philippines) + **padawan**, ending in *Dhawan*. **PHD1** is the agent's short name, and yes, it reads like a PhD.

## How it was built

Built by team PHishDhawan:

- **Pauline Estira**: planning, scenario, design decisions and testing.
- **Neiko Sarandon**: tester (full fresh-setup runs) and co-writer of the demo storyline.
