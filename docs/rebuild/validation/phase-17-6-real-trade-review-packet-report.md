# Phase 17.6 Real Trade Review Packet Report

Date: 2026-06-16

Final status: BLOCKED PENDING OPERATOR-SUPPLIED TRADE INPUT

## Purpose

Materialize at least one real Trade Review packet from operator or viewer supplied trade sides, then generate a deterministic `trade_review_show` content brief.

No packet was materialized in this phase because no real trade sides were supplied.

## Required Input

The trade packet CLI requires explicit trade assets:

```text
--side-a SIDE_A
--side-b SIDE_B
```

Required context:

- `scoring_profile_id`
- `league_type_id`
- `roster_format_id`
- optional `league_id`
- optional `roster_id`
- optional context notes

## Input Search Result

No real operator or viewer trade input was found.

Checked:

- prompt content for explicit trade sides
- repo files under `data/`, `docs/rebuild/`, `src/`, and `tests/`
- environment variables `SIDE_A`, `SIDE_B`, `TRADE_SIDE_A`, and `TRADE_SIDE_B`
- `ENABLE_DEMO_TRADE_REVIEW`

Result:

```text
ENABLE_DEMO_TRADE_REVIEW=<missing>
SIDE_A=<missing>
SIDE_B=<missing>
TRADE_SIDE_A=<missing>
TRADE_SIDE_B=<missing>
```

No demo trade was created because demo packet generation was not explicitly enabled.

## CLI Shape

Command:

```powershell
.\venv\Scripts\python.exe -m src.trade_review_packets --help
```

Relevant output:

```text
usage: python.exe -m src.trade_review_packets [-h] --side-a SIDE_A --side-b SIDE_B
                                              [--scoring-profile SCORING_PROFILE]
                                              [--league-type LEAGUE_TYPE]
                                              [--roster-format ROSTER_FORMAT]
                                              [--league-id LEAGUE_ID]
                                              [--roster-id ROSTER_ID]
                                              [--dry-run]
```

Interpretation:

- A real dry-run requires actual `--side-a` and `--side-b` values.
- Running without sides would only prove argument validation, not a real trade packet.

## Warehouse Readiness

Read-only BigQuery counts:

```text
trade_review_packets: 0
content_briefs where brief_type = trade_review_show: 0
compat_trade_assets_current: 1383
compat_trade_player_history: 55617
compat_player_profiles_current: 27864
```

Interpretation:

- The supporting compatibility data exists.
- The blocker is missing operator/viewer trade input, not missing market or player-history data.

## Dry-Run Result

No real trade packet dry-run was executed because no real trade sides were supplied.

Expected future command shape:

```powershell
.\venv\Scripts\python.exe -m src.trade_review_packets `
  --side-a "<operator supplied assets>" `
  --side-b "<operator supplied assets>" `
  --scoring-profile ppr `
  --league-type redraft `
  --roster-format one_qb `
  --dry-run
```

## Materialization Result

No rows were written.

| Object | Rows written |
|---|---:|
| `trade_review_packets` | 0 |
| `trade_review_packet_players`, if implemented | 0 |
| `content_briefs` with `trade_review_show` | 0 |
| `content_brief_items` from trade packets | 0 |

No packet IDs or brief IDs were created.

## Validation Results

Content brief validation:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern content_brief
```

Result:

```text
11 passed, 0 failed
```

Market validation:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern market
```

Result:

```text
9 passed, 0 failed
```

Deployment safety:

```powershell
.\venv\Scripts\python.exe scripts\check_deployment_safety.py
```

Result:

```text
pass
```

## No LLM and No Scraping Confirmation

- No LLM calls were made.
- No scraping occurred.
- No URLs were fetched.
- No trade inputs were fabricated.
- No demo trade packets were created.
- No Firebase artifacts were created.

## Next Step

Provide at least one real trade using this shape:

```text
side_a: <operator supplied assets>
side_b: <operator supplied assets>
scoring_profile_id: ppr
league_type_id: redraft
roster_format_id: one_qb
context notes: optional viewer/team context
```

Then run:

```powershell
.\venv\Scripts\python.exe -m src.trade_review_packets --side-a "<side a assets>" --side-b "<side b assets>" --scoring-profile ppr --league-type redraft --roster-format one_qb --dry-run
```

Only after dry-run asset resolution is clean should a bounded materialization run be approved.

## Final Decision

Phase 17.6 remains blocked until real operator or viewer trade sides are supplied. The warehouse is ready enough to support the workflow, but no production trade review packet should be created without real input.
