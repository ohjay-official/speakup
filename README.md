# SpeakUp

**Do chatbots warn users who ask for help acting on a false premise?**

Ask a chatbot "should I invest in this platform that pays 100% in 30 days?" and it warns you. Ask it to calculate your 30-day profit, write the invite for your family WhatsApp group, or help you borrow the "verification fee" to unlock a withdrawal, and it may just help.

SpeakUp is a decision-making eval for the [Apart Research AI x Epistemics Research Sprint](https://apartresearch.com/sprints/ai-x-epistemics-research-sprint-2026-11-13-to-2026-11-15) (13 to 15 November 2026). It measures whether models flag false premises in the requests people actually make, using Nigerian investment schemes whose collapses are public record and matched legitimate products as controls.

## Status

Pre-sprint. This repo holds only the [pre-registration](PREREGISTRATION.md). No prompts, code or model outputs exist yet; all of them are written during the sprint, starting Friday 13 November 2026.

## What It Measures

- **Suppression:** do warnings drop when the same case is asked as a task instead of as advice?
- **Knew but helped:** when a model helps silently, does it rate the scheme as likely fraud if asked right after?
- **Claim laundering:** when asked to invite family, does the model repeat the scheme's claims in the user's own voice?
- **Smarter or jumpier:** do prompt fixes raise sensitivity (d′), or only make models warn about everything (criterion c)?
- **Warning survival:** does a warning hold after one line of pushback?
- **Frozen forecast:** fraud probabilities for live platforms flagged by Nigeria's SEC, committed before anyone knows how they end.

## Disclosure

Planning and research for this project happened on 10 and 11 November 2026, before the sprint; it is recorded in the pre-registration. Code and writing are produced with AI assistance (Claude); the author checks every number and reference.

## Licence

[MIT](LICENSE)
