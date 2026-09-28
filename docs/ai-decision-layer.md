# AI Decision Layer (Jev)

Status: design, started 2026-09-27. Nothing here changes ranks yet.

## Idea

The pipeline makes many small judgments about players that today are either hard-coded rules, owner exceptions, or left for a language model to work out while it writes. The decision layer moves those judgments into a fast, calibrated classifier (TypeSafe Jev: yes or no, choose one, or score on a rubric, each with a confidence) that runs once a day and stores typed answers. Every consumer then reads a decision that is already made instead of re-deriving it from raw text:

- the formula and guardrails (later, after backtests),
- the public rankings feed,
- the site, Pigskin Studio, and the Article Desk, which get compact settled facts instead of long rationale text.

Jev is not used for numbers, counting, dates, ranking math, or writing. Those stay in BigQuery, Python, and the writer models. Jev turns text and messy signals into fields the math and the writers can rely on.

## Owner decisions (2026-09-27)

1. **Home: the rankings pipeline.** A daily, versioned decisions table built in this project after the current-season stats refresh, with a confidence on every value, published in the rankings feed. The site and Pigskin only read it, so every consumer sees the same decision.
2. **First use: context only, then backtest.** Decisions feed Pigskin, articles, and the site as settled facts. Ranks stay formula-only until each decision family is backtested against past seasons, per the runbook rule that formula changes need backtests and owner review.
3. **Low confidence: leave it blank and log it.** Below a decision's threshold the field is empty and nothing downstream uses it. The miss is logged so the question or threshold can be improved. Nothing guesses.
4. **First pilot: availability from injury text.** Turn injury designations, practice reports, and news into an availability class and a games-missed bucket, checked against who actually played.

## Pilot 1: availability (open design)

Split the work by what each tool is good at:

- **Code, from history:** base rates for structured designations (Out, Doubtful, Questionable, practice DNP, Limited, Full) against whether the player actually played, from past seasons.
- **Jev, from text:** what the words add that the designation does not, for example "expected to miss two to four weeks", "trending toward playing", "season-ending", "no structural damage".
- **Ground truth:** did the player appear in the next game, and how many games he missed.

To be settled: the exact questions and answer sets, the confidence threshold per question, the text sources (Sleeper injury fields, news wire items, practice reports), the historical data for the backtest, and where the fields appear in the feed schema.

## Prerequisites

- A TypeSafe API key from the owner (console.typesafe.ai), stored with the other pipeline secrets as `TYPESAFE_API_KEY`.
- The Python SDK (`typesafe-sdk`, Python 3.10 or newer) in this project's venv.
