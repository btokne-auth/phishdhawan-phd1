# PHD1: Summary (read this first)

Toggle Wars (WeMakeDevs x Flagsmith Experimentation Hackathon) · Track 02: AI Agents and Feature Flags · team PHishDhawan
Build window: Nov 26, 10:30 AM – Nov 29, 10:30 PM (Manila time). Team target: submit Sunday afternoon, well before the deadline.

## What PHD1 is

PHD1 is a **phishing incident-response agent**. It watches an inbox for a **phishing wave** (many fake emails imitating one brand in a short time) and responds through **Flagsmith feature flags**: the low-risk response it does alone, the high-risk response it asks a human about first.

**One-line pitch:** "PHD1 switches on the warnings by itself in seconds, and waits for your yes before it blocks every link."

## Principles (never break these)

1. **Code has the final say.** The AI proposes; code checks every proposal against a fixed policy, and a confirmed wave always gets at least the warning banners.
2. **Risk lives in the policy, not in the AI's answer.** The AI can't make a step look safer than it is.
3. **High risk always waits for a human.** Pressing Enter means No.
4. **PHD1 only switches flags on.** Switching off is a human's job.
5. **Email text is data, never instructions.** Including emails that talk to "the AI security agent".
6. **Flagsmith is the only bridge.** The agent never touches the inbox app directly.
7. **Everything is logged.** Every run writes an incident report.

## Where to find things

| File | What's in it |
| --- | --- |
| `docs/SUMMARY.md` | This page |
| `docs/DECISIONS.md` | Why a terminal agent, why Flagsmith, the risk tiers and the wave rule |
| `docs/STORY.md` | The scenario (a Filipino weekday morning) and the demo video plan |
| `docs/DESIGN.md` | Design rules for the inbox page and the terminal output, and the references used |
| `docs/TESTING.md` | The three test inboxes, results, every miss, and the safety tests |
| `docs/DEMO.md` | Checklist for running or recording the demo |
| `docs/COMMANDS.md` | Every command, with what it does, plus quick fixes |
| `docs/BUILD-LOG.md` | What was built before vs during Toggle Wars, day by day |
| `docs/screenshots/` | Screenshots used in the README |
