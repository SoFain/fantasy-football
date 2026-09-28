# AI Decision Layer (Jev)

Status: Pilot 1 (availability) built on branch `availability-pilot`, 2026-09-27. Log-only and context-only: nothing here changes ranks, boards, the public feed, or the daily chain.

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

## Pilot 1: availability (as built)

Split of work: code owns every date, schedule, count, and probability; Jev owns only judgments over text. A structured base-rate model (no language model) gives the prior; Jev reads the candidate text and the prior and answers three choices plus one relevance noul per text item, in one call.

### Tables (all new, `fantasy_football_brain`, written only by the pilot)

| Table | Grain | Rows (2026-09-28) |
|---|---|---:|
| `availability_team_games` | team x game, nflverse schedule 2014 to 2026, kickoff in UTC | 7,134 |
| `availability_player_games` | player x game with at least one snap (offense, defense, or special teams), GSIS keyed | 303,887 |
| `availability_labels_hist` | official injury report entry x REG game (2014 to 2026 week 2) | 63,772 |
| `availability_text_items` | DraftSharks items archived at first sight (URL, headline, 300-character summary, keywords) | 100 |
| `availability_decisions_daily` | decision_date x run_mode x player x target game | 431 (120 live, 311 retro) |
| `availability_decision_misses` | one row per blanked answer | 550 |

`src/availability_bq.py` refuses writes to any table without the `availability_` prefix. The 2026 raw rows were loaded with the existing gated loader (`src/nflverse_backfill.py`, MERGE on natural keys, no other season touched): injuries +734 (weeks 1 to 3), snap counts +3,086 (weeks 1 and 2 complete, week 3 only the Thursday game so far), weekly rosters +8,036.

Played signal: a snap-count row with any snap. Identity is the staging identity CTE (PFR id through rosters and player bridges), then a unique normalized name within the same season, week, and team (350 of the 3,085 2026 rows, mostly rookies the player bridge lacks). 77 rows from 2023 onward stay unmatched. It reproduces the surveyed base rates exactly (QB/RB/WR/TE REG 2016 to 2025: Out 0.06 percent played, Doubtful 1.2, Questionable 66.6, practice-only 92.0).

### Labels (`src/availability_labels.py`, pure and unit tested)

Features: normalized report status (Out, Doubtful, Questionable, Probable, NONE), practice code (DNP, LP, FP, NONE; "Out (Definitely Will Not Play)" counts as DNP), primary and secondary body part plus a keyword body-part group, position group, previous team game state (NOT_LISTED, LISTED_PLAYED, LISTED_MISSED) and status, episode_id (a run of consecutive team games on the report), team game index, games remaining, weekly roster status, `era_pre_2016`.

Labels: `played_this_game`, `played_next_game`, `games_missed_until_return` (team-game index distance to the next snap; byes are not games), `missed_bucket` (0, 1, 2_4, 5_plus_or_season), `censored` with `censor_reason`. A season-end censor with two or more games missed is a rest-of-season absence (top bucket); one missed final game is ambiguous and gets no bucket. A data-horizon censor (games not played yet) resolves only at five games. `excluded_from_fit` covers team changes, a CUT weekly status before return, and "not injury related" or rest entries. Duplicate entries per player-week keep the most severe status.

### Base-rate model (`src/availability_base_rates.py`, artifact `docs/availability-base-rates-v1.json`)

Hierarchically smoothed empirical rates: each cell is `(hits + k * parent) / (n + k)` down the chain global, status, status x practice, status x practice x previous state, then x body-part group. The bucket distribution uses the same chain with Dirichlet smoothing. `k = 50`, chosen by validation log loss (fit 2016 to 2021, validate 2022 to 2023), then refit on 2016 to 2023 (11,636 rows, QB/RB/WR/TE, not excluded). The artifact stores raw counts, so every prior can be recomputed by hand. Extra lanes: `play_next_game` (this week's report plus whether he played this game) and `roster_next_game` (weekly roster status, not on the report).

Holdout 2024 to 2025 (3,104 rows) against the status-only baseline (same estimator, status level only):

| Target | Rows | Model Brier | Model log loss | Status-only Brier | Status-only log loss |
|---|---:|---:|---:|---:|---:|
| Played this game | 3,104 | 0.0803 | 0.2558 | 0.0918 | 0.2994 |
| Played, designated O/D/Q only | 1,532 | 0.1091 | 0.3146 | 0.1158 | 0.3361 |
| Played, Questionable only | 749 | 0.2232 | 0.6401 | 0.2359 | 0.6651 |
| Missed bucket (4 classes) | 3,004 | 0.3331 | 0.6307 | 0.3531 | 0.6750 |
| Played next game | 2,892 | 0.1452 | 0.4546 | 0.1643 | 0.5053 |

Calibration, played this game (model, predicted vs observed): 0.003 vs 0.000 (n 777); 0.06 vs 0.00 (6); 0.32 vs 0.32 (85); 0.56 vs 0.49 (211); 0.72 vs 0.67 (339); 0.87 vs 0.86 (599); 0.97 vs 0.97 (1,087). The middle bins run about five points optimistic. The status-only baseline has no cells between 0.2 and 0.6 at all.

### Text sources (`src/availability_text.py`)

- DraftSharks injury news RSS, `https://www.draftsharks.com/rss/injury-news` (the GNG site news wire feed, `PIGSKIN_ARTICLE_DESK_NEWS_FEEDS` in `site/app/pigskin_article_desk.php`). Headlines and the feed's short description only, for internal classification; never republished. The feed holds only its latest 100 items (2026-05-29 to 2026-09-27 at first archive), so each live run archives new items first.
- `team_news_items` (team blog RSS, since 2026-07-31): a code-cut snippet of about 440 characters around the player's surname.
- Sleeper injury status, body part, note, practice participation, and how long the designation has run (from `sleeper_players_history`) go in the structured state, not the text list.

Matching favors recall: full name or feed keyword, or surname inside the player's own team feed. At most the 8 most recent items within 10 days before the as-of moment.

### Jev stage (`scripts/run_availability_decisions.py`, question set `availability_qs_v1`, model `jev-latest`)

State, all built in code: player, team, position, today's date as a weekday and date, the next game's week, date with "in N days", opponent and home or away, team games remaining, the official report sentence, the Sleeper block, the last two team games with played or not (or "snap counts not available yet"), the base-rate prior as a sentence, and the news items with source and "N days ago". No raw ISO dates reach the model.

Prior lanes, chosen by code: `report_this_game` (official report for the target game), `report_last_game` (report for his last game, through the next-game lane; the last game's outcome is used only once its snaps are loaded), `roster_status` (weekly roster status such as RES, or Sleeper IR/PUP mapped to RES/PUP), `sleeper_designation_only` (Sleeper Out/Doubtful/Questionable with no official entry; status-level prior). Sleeper Sus and DNR are skipped as non-injury. Sleeper `LAR` is normalized to nflverse `LA`.

Questions (one call per player, fan-out):

| Question | Type | Options | Threshold |
|---|---|---|---|
| `relevance_i`, one per text item | Noul | is the item about this player's own current injury or availability | keep at 0.50 |
| `availability` | Choice | will_play, game_time_decision, will_miss | confidence 0.60 (top option at least 0.733) |
| `absence` | Choice | 0, 1, 2_4, 5_plus_or_season | confidence 0.50 (top option at least 0.625) |
| `trend` | Choice | improving, unchanged, worsening, unknown | confidence 0.50 |

Thresholds were fixed before any retro scoring, from TypeSafe's guidance (0.5 is the "genuinely uncertain" floor; confidence is `(n * peak - 1) / (n - 1)`) and the stakes: a wrong context value costs a misleading sentence, not a rank move, so the 3-way availability call sits a little above the floor and the 4-way calls at it. Tuning them on the retro set would leak. Below a threshold the field is NULL, `<question>_blank` is TRUE, the probabilities stay in `<question>_probs_json` for analysis, and a row goes to `availability_decision_misses`. Nothing downstream may read a blank field.

Each row also stores the prior lane, prior play probability and bucket distribution, `combined_play_prob`, the text items with relevance, question-set version, thresholds, base-rate version, the Jev model version from the response, request id, input hash, tokens, and cost. Idempotent per decision_date, run_mode, player, and target game: an unchanged input hash is not re-called, a changed one replaces the row (MERGE from a load-job stage), and its misses are replaced with it.

`combined_play_prob` is a fixed a priori rule used only to measure what the text adds: when the availability answer is blank or no item was judged relevant, the prior stands; otherwise will_play and will_miss mass is taken as stated and game_time_decision mass is handed back to the prior. It was not fitted.

### Live run, 2026-09-27 23:30 ET

120 Sleeper-injured QB/RB/WR/TE with a team (lanes: roster_status 80, report_last_game 35, report_this_game 3 for the Monday night teams, sleeper_designation_only 2). 39 had candidate text, 30 at least one relevant item. Blank: availability 75, absence 14, trend 90. One player skipped (Sleeper `NA`, no roster status).

### Retro run, 2026 weeks 1 to 3

State rebuilt as of the last daily Sleeper snapshot before each kickoff (about 07:00 ET on game day); text only if published before that snapshot; the official report row for that week; previous games' snaps. Population: Sleeper-injured skill players on that team plus official Out/Doubtful/Questionable skill entries. 311 decisions; 198 scored (week 1: 88, week 2: 103, week 3: 7 from the Thursday game); 113 pending until week 3 snap counts load.

| Subset | Rows | Played | Prior Brier / log loss | Prior plus Jev Brier / log loss |
|---|---:|---:|---:|---:|
| All scored | 198 | 5.1% | 0.0338 / 0.1244 | 0.0336 / 0.1240 |
| At least one relevant text item | 10 | 20% | 0.0584 / 0.1973 | 0.0558 / 0.1895 |
| Official Out/Doubtful/Questionable | 48 | 18.8% | 0.1026 / 0.3040 | 0.1021 / 0.3029 |
| Official Questionable | 20 | 45% | 0.2458 / 0.7173 | 0.2446 / 0.7148 |

Jev changed the probability on 6 rows. Its 103 non-blank will_play or will_miss calls were all correct, and so was the base rate at 0.5 on the same rows. It chose game_time_decision 9 times (1 played) and will_play only once in 311 decisions. Absence, 53 rows with a prior distribution (20 resolved, the rest scored against every bucket still possible): set log loss 0.5959 prior vs 0.5587 prior plus Jev; on the 8 with relevant text 0.4524 vs 0.2060, and Jev's answer was consistent with the outcome 7 of 7 times vs 5 of 7 for the prior's top bucket.

Reading: the text adds almost nothing measurable yet. Almost all scored decisions are players the prior already puts near zero (IR, Out), the relevant-text sample is 10 rows, and every difference above is inside noise. The absence question is the most promising signal and needs weeks of live data.

Leakage and bias risks: DraftSharks items were archived on 2026-09-28, after every retro game, so an item edited after publication would leak, and the 100-item feed window keeps fewer early-week items. `team_news_items` summaries are as of fetch time. The official report row is the final pre-game report, which could be revised; game-day inactives are not in it. Previous-game snaps are assumed known by the as-of time (they usually load within two days). Jev 1.13 was reviewed 2026-09-17; whether its training saw any 2026 news is unknown. The base-rate model has no 2026 data.

### Cost

Jev bills input tokens only, $0.042 per million (jev-1.13.0). All pilot calls so far: 540,715 input tokens and 69,296 output tokens, about $0.023 (live 163,146 input, retro 377,195 including 8 re-calls after the LAR fix, smoke test 374).

### Commands

```powershell
# Daily decisions (log-only; archives new DraftSharks items first)
.\venv\Scripts\python.exe scripts\run_availability_decisions.py --live
.\venv\Scripts\python.exe scripts\run_availability_decisions.py --live --dry-run   # states only, no calls, no writes

# Weekly outcome refresh, then scoring
$env:ALLOW_NFLVERSE_HISTORICAL_BACKFILL='true'
.\venv\Scripts\python.exe -m src.nflverse_backfill --write --source-family injuries,snap_counts,rosters_weekly --season-start 2026 --season-end 2026
Remove-Item Env:ALLOW_NFLVERSE_HISTORICAL_BACKFILL
.\venv\Scripts\python.exe scripts\build_availability_labels_hist.py --apply
.\venv\Scripts\python.exe scripts\evaluate_availability_decisions.py --run-mode live
.\venv\Scripts\python.exe scripts\evaluate_availability_decisions.py --run-mode retro

# Rebuild the base-rate artifact (read-only on BigQuery; bump the version for any change)
.\venv\Scripts\python.exe scripts\fit_availability_base_rates.py

# Retro reconstruction
.\venv\Scripts\python.exe scripts\run_availability_decisions.py --retro-season 2026 --weeks 1-3

# Tests
.\venv\Scripts\python.exe -m unittest tests.test_availability_pilot
```

The TypeSafe key comes from `TYPESAFE_API_KEY`, else `E:\cbs-league-history\.secrets\typesafe-ai-api.txt`. It is never printed or logged.

### Proposed chain step (for owner review; not installed)

Insert in `scripts/daily_pigskin_chain.ps1` after `verify-public-rankings` succeeds and before `done: chain succeeded`, non-fatal:

```powershell
$availabilityExit = Invoke-Logged 'availability-decisions' "$root\venv\Scripts\python.exe" `
    ('"{0}\scripts\run_availability_decisions.py" --live' -f $root) $root
if ($availabilityExit -ne 0) {
    Write-Log "AVAILABILITY DECISIONS FAILED (exit=$availabilityExit); non-fatal, rankings already published."
}
```

It runs after publication and import, so it cannot delay or block a release, and it never exits the chain nonzero. The 12:30 leg re-runs it; unchanged states cost nothing and changed ones replace the morning row.

### Limitations and open items

- Sample: 198 scored retro rows, 10 with relevant text. No claim that text helps is supported yet.
- Jev leans to will_miss and long absences on this population; will_play appeared once. Official Questionable players were blank on availability 12 of 20 times.
- Relevance nouls run in the same call as the availability questions, so those answers saw irrelevant items too. A two-call variant (filter, then decide) is the obvious next test.
- Name matching can attach one player's items to a namesake (two players named Marquise Brown in week 3); the relevance noul rejected both.
- The live prior for a player whose last game has no snap counts yet drops one feature level.
- `sleeper_designation_only` and the roster mappings approximate the official-report lanes.
- Nothing is published in the feed yet; schema placement waits for backtested value.

## Prerequisites

- A TypeSafe API key (console.typesafe.ai) as `TYPESAFE_API_KEY` or in `E:\cbs-league-history\.secrets\typesafe-ai-api.txt`.
- The Python SDK (`typesafe-sdk>=0.7.2`, in `requirements.txt`), installed in this project's venv.
