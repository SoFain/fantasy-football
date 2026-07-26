# Phase 16.6 Real Segment Packet Report

Date: 2026-06-16

Final status: GO WITH WARNINGS

## Goal

Materialize real deterministic segment packets beyond Sleeper Breakout where source data supports it.

Target families:

- `fraud_watch_packets`
- `trade_review_packets`
- claim grades or accountability packets
- content briefs from newly materialized packets

No LLM calls were made. No scraping was performed. No production claims or trade takes were fabricated. No Firebase artifacts were created.

## Starting State

Initial counts:

```text
fraud_watch_packets: 0
sleeper_breakout_packets: 2
trade_review_packets: 0
content_briefs: 3
content_brief_items: 18
claim_grades: 0
```

Claim status:

```text
draft: 3
```

No reviewed or ready-to-grade real claims existed.

## Fraud Watch Source Slice

`analytics_fraud_watch` does not have `scoring_profile_id`; its source grain is season and week. Scoring context is added by the packet builder through compatibility joins.

Recent available scored slices:

```text
2016 week 17: 82 rows, 82 scored
2016 week 16: 83 rows, 83 scored
2016 week 15: 66 rows, 66 scored
2016 week 14: 69 rows, 69 scored
2016 week 13: 66 rows, 66 scored
```

Chosen source slice:

```text
season=2016
week=17
scoring_profile_id=ppr
limit=3
```

Reason:

- It is the newest available Fraud Watch slice with source rows.
- It has enough rows for a bounded packet run.
- The packet builder can attach `ppr`, `redraft`, and `one_qb` context through compatibility objects.

## Fraud Watch Dry-Run

Command:

```powershell
.\venv\Scripts\python.exe -m src.segment_packets --packet-type fraud-watch --season 2016 --week 17 --scoring-profile ppr --limit 3 --dry-run
```

Result:

- Dry-run returned 3 deterministic packet previews.
- Players:
  - Tom Brady
  - Philip Rivers
  - Ryan Fitzpatrick
- No rows were written during dry-run.

Known data caveat:

- The historical Fraud Watch source is 2016, while some compatibility context is current as of 2025.
- Packets and brief items include missing-data flags such as `missing_current_season_scoring`, `missing_model_run_id`, and `missing_pigskin_rank`.
- This is acceptable for bounded historical packet activation, but not yet enough for a current-week production segment.

## Fraud Watch Materialization

Command:

```powershell
.\venv\Scripts\python.exe -m src.segment_packets --packet-type fraud-watch --season 2016 --week 17 --scoring-profile ppr --limit 3
```

Materialized packet IDs:

```text
ef768555dfb0a6ff9c1fe20868d33518
17620dceb0f862458d264bdab7998fa7
3f9f72016f2b9562b7e81683fa2d8719
```

Packet sample:

```text
Tom Brady, QB, TB, fraud_score=77.004
Philip Rivers, QB, IND, fraud_score=74.164
Ryan Fitzpatrick, QB, WAS, fraud_score=68.758
```

Fraud Watch packet counts:

```text
fraud_watch_packets before: 0
fraud_watch_packets after: 3
fraud_watch_packets for 2016 week 17 PPR after: 3
```

## Fraud Watch Content Brief

Dry-run command:

```powershell
.\venv\Scripts\python.exe -m src.content_briefs --brief-type fraud_watch_show --season 2016 --week 17 --scoring-profile ppr --dry-run
```

Dry-run result:

- Returned the known shape-only `missing_source_rows` placeholder because the current content brief CLI uses `client=None` in dry-run mode.
- No rows were written during dry-run.

Materialization command:

```powershell
.\venv\Scripts\python.exe -m src.content_briefs --brief-type fraud_watch_show --season 2016 --week 17 --scoring-profile ppr
```

Materialized brief:

```text
content_brief_id=brief-fraud_watch_show-2016-w17-20260616T153304Z-ea3173c5
content_brief_run_id=fraud_watch_show-2016-w17-20260616T153304Z-252597c3
brief_type=fraud_watch_show
review_status=draft
item_count=3
token_estimate=814
```

Brief items:

```text
Fraud Watch: Tom Brady
Fraud Watch: Philip Rivers
Fraud Watch: Ryan Fitzpatrick
```

Content counts:

```text
content_briefs before: 3
content_briefs after: 4
content_brief_items before: 18
content_brief_items after: 21
fraud_watch_show briefs for 2016 week 17 PPR: 1
```

## Trade Review Packets

Command inspected:

```powershell
.\venv\Scripts\python.exe -m src.trade_review_packets --help
```

Result:

- The CLI requires explicit `--side-a` and `--side-b` trade assets.
- No real operator-provided trade input was available in this phase.

Decision:

- No trade review packet was materialized.
- No demo trade was materialized.
- `ENABLE_DEMO_TRADE_REVIEW` was unset.

Reason:

- Creating trade inputs from our own guesses would fabricate a production trade take.
- The system should only materialize trade packets from real operator or viewer trade input.

Current count:

```text
trade_review_packets: 0
```

## Claim Grading And Accountability

Current claim state:

```text
fantasy_claims draft: 3
claim_grades: 0
ENABLE_DEMO_CLAIM_GRADING=<unset>
```

Dry-run command:

```powershell
.\venv\Scripts\python.exe -m src.claim_grading --season 2026 --week 1 --dry-run
```

Dry-run result:

```text
claim_count=0
grade_count=0
scorecard_count=0
```

Decision:

- No claim grades were materialized.
- No Meatbag Accountability packet was materialized.

Reason:

- Phase 16.5 confirmed only draft demo claims exist.
- No real reviewed or ready-to-grade claims exist.
- Demo draft claims must not be graded unless explicitly enabled in demo mode.

## Final Counts

```text
fraud_watch_packets: 3
fraud_watch_packets_2016_w17_ppr: 3
sleeper_breakout_packets: 2
trade_review_packets: 0
content_briefs: 4
content_brief_items: 21
fraud_watch_show_briefs_2016_w17_ppr: 1
claim_grades: 0
```

## Validation

Commands:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern content_brief
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern claim
```

Results:

```text
content_brief: 11 passed, 0 failed
claim: 17 passed, 0 failed
```

Expected claim informational warnings remain:

```text
120_claims_player_identity_coverage.sql
identity_missing_rate = 0.3333333333333333
```

This is expected because one demo draft claim has an unresolved player.

```text
142_claim_ledger_ui_sources_exist.sql
claim_source_count = 3
active_claim_source_count = 3
```

This is informational.

```text
143_claim_ledger_ui_draft_claims_allowed_missing_fields.sql
draft_claims_missing_review_fields = 1
```

This is expected because the unresolved demo claim is draft-only.

Safety validation still passed:

```text
145_claim_ledger_ui_player_resolution_flags.sql
non_draft_unresolved_player_rows = 0
```

## Remaining Gaps

1. Current-week Fraud Watch needs `analytics_fraud_watch` populated for a modern 2025 or 2026 slice.
2. Trade Review packets need real operator or viewer trade input.
3. Meatbag Accountability needs real reviewed or ready-to-grade claims.
4. The content brief dry-run mode is still shape-only because it does not read BigQuery source rows.
5. Historical Fraud Watch packets carry honest missing-data flags because current ranking/model-run context is not available for 2016 players.

## Decision

GO WITH WARNINGS

At least one additional real packet family was materialized: `fraud_watch_packets`. A deterministic `fraud_watch_show` content brief was also created as a draft. Trade Review and Meatbag Accountability remain blocked by missing real operator inputs, not by packet infrastructure.
