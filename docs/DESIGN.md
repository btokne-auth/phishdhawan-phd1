# Design

## The inbox page (`inbox.html`)

Modelled on the structure of iOS Mail, with a strict minimal style.

- **Two typefaces only:** one sans for content, one monospace (12px) for every piece of metadata: times, addresses, labels.
- **Colour has a job or it's gray.** Black, white and grays everywhere. Blue only for the unread dot. Orange only for the suspicious icon and the phishing warning label.
- **One spacing scale** (4, 8, 12, 16, 24, 32, 48) and one corner radius (8px; 4px for chips).
- **Rows, not cards.** No boxes around emails, no coloured side stripes.
- **The warning is a label plus one sentence:** "▲ PHISHING WARNING" in mono, then plain words saying what to do instead.
- **Blocked links stay visible but gray,** with a "🔒 BLOCKED" chip, so the reader sees what was stopped.
- **The flag states live in a demo panel under the window,** not inside the inbox, so the inbox looks like a real app.
- **Safety:** email text is inserted as text only, never as HTML; links are never opened.
- **Accessibility:** light and dark themes (auto, or switchable), reduced motion, reduced transparency and higher contrast are respected, and text meets AA contrast.
- **It only redraws when something changes,** so the warning doesn't re-animate on every 3-second check.

## The terminal output (`respond.py`)

- **Same colour rule as the inbox.** Gray for labels and details, green for "on", orange only for the moment that needs a human: "high", "waiting for you" and the approval box.
- **Sections that tell the story:** WAVE DETECTED → WHAT THE AI SEES → RESPONSE.
- **A who-decides table** with the real Flagsmith flag names, so it's clear which switch each step flips.
- **Explain before asking.** The approval box shows the question, Why (the AI's reason) and Cost (what breaks) before the y/N prompt.
- **Ask the exact question.** "Block the links? [y/n]", and the default is No.
- **Status at both ends.** The first line shows where both flags start; the last line reads Flagsmith again and shows where they really ended.
- **Show what the AI was given.** "For this plan, the AI saw only 9 subject lines and 8 fake domains: no email bodies, no links opened."
- **Attacker text can't style the terminal.** Email subjects and AI output are printed as plain text, never as formatting markup.
- **Plain words:** "the AI", not "the model"; one name per flag.

## References

- iOS Mail for the inbox structure.
- Bryl Lim's minimal portfolio style for the type and colour discipline.
- [Command Line Interface Guidelines](https://clig.dev/) for output, errors and prompts.
- GitHub's Primer design guidelines for its command-line tool, for how a polished CLI uses colour and headers.
- [Rich](https://github.com/Textualize/rich) for tables, panels and the yes/no prompt.
- [gptel](https://github.com/karthink/gptel) for two ideas: a status line at the top, and showing exactly what is sent to the AI.
