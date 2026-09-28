# Phase 15.2 Segment Packet Materialization Report

Final status: GO WITH WARNINGS

Validation date: 2026-06-16

Project: `fantasy-football-498121`

Dataset: `fantasy_football_brain`

## Purpose

Phase 15.2 materialized bounded deterministic segment packet data so content brief review can move beyond `weekly_streamers_show`.

No LLM calls were made. No scraping was performed. No Firebase artifacts were created. No production claims or takes were fabricated. No live Cloud Run Jobs were triggered.

## Source Inventory

Initial bounded source counts:

| Table | Total rows | 2025 week 1 PPR rows |
| --- | ---: | ---: |
| `analytics_fraud_watch` | 3,638 | 0 |
| `compat_sleeper_watch_candidates` | 1,652 | 5 |
| `compat_trade_assets_current` | 1,383 | 461 |
| `compat_trade_player_history` | 55,617 | 1,071 |
| `compat_player_profiles_current` | 27,864 | 9,288 |
| `llm_player_context_packet` | 9,340 | 9,340 |
| `projection_rankings_current` | 50 | 50 |
| `fantasy_claims` | 3 | 0 |
| `fantasy_claim_players` | 3 | not week-grained |
| `claim_evaluation_windows` | 3 | not week-grained |
| `claim_grades` | 0 | 0 |
| `fraud_watch_packets` | 0 | 0 |
| `sleeper_breakout_packets` | 0 | 0 |
| `trade_review_packets` | 0 | 0 |
| `content_briefs` | 2 | 2 |
| `content_brief_items` | 16 | not week-grained |

## Fraud Watch Packets

Dry-run command:

```powershell
.\venv\Scripts\python.exe -m src.segment_packets --packet-type fraud-watch --season 2025 --week 1 --scoring-profile ppr --dry-run
```

Result:

- Returned `[]`.
- No rows were materialized.

Blocker:

- `analytics_fraud_watch` has historical data, but has 0 rows for the requested `season=2025`, `week=1` slice.

Next step:

- Run Fraud Watch for a season/week slice with source rows, or materialize/update `analytics_fraud_watch` for the target week before building packets.

## Sleeper Breakout Packets

Dry-run command:

```powershell
.\venv\Scripts\python.exe -m src.segment_packets --packet-type sleeper-breakout --season 2025 --week 1 --scoring-profile ppr --dry-run
```

Result:

- Returned deterministic packets from `compat_sleeper_watch_candidates`.
- Source data existed for `season=2025`, `week=1`, `scoring_profile_id=ppr`.

Materialization command:

```powershell
.\venv\Scripts\python.exe -m src.segment_packets --packet-type sleeper-breakout --season 2025 --week 1 --scoring-profile ppr
```

Materialized packet IDs:

- `3fbbacbe9840a19e3a68e3337301ec81`
- `3fd331d5db5147d7a9a36a27cf4f14db`

Packet row counts:

| Table | Before | After |
| --- | ---: | ---: |
| `sleeper_breakout_packets` | 0 | 2 |
| `sleeper_breakout_packets` for 2025 week 1 PPR | 0 | 2 |

Known data caveat:

- Both materialized packets are for Ulysses Bentley. One row uses canonical `sleeper:12826`; the other uses temporary `source:00-0040476`.
- The generated packets carry missing-data flags that make this explicit, including `temporary_source_key_identity` on the temporary row.
- Future identity cleanup should dedupe or reconcile this source/canonical duplicate before wider in-season use.

## Trade Review Packets

Environment:

- `ENABLE_DEMO_TRADE_REVIEW` was not set.

Dry-run command:

```powershell
.\venv\Scripts\python.exe -m src.trade_review_packets --side-a "Ja'Marr Chase" --side-b "Justin Jefferson" --scoring-profile ppr --league-type redraft --roster-format one_qb --dry-run
```

Result:

- Dry-run returned a deterministic packet preview.
- No trade review packet was written.

Reason:

- The task only allowed deterministic/manual demo trade materialization when `ENABLE_DEMO_TRADE_REVIEW=true`.
- The flag was not set, so `trade_review_packets` remains an expected empty-state.

## Claim Grading And Accountability

Environment:

- `ENABLE_DEMO_CLAIM_GRADING` was not set.

Current claim state:

- Only demo draft claims exist.
- `claim_grades` has 0 rows.

Result:

- No claim grading was run.
- No receipt/accountability packet was generated.

Reason:

- Demo draft claims must not be graded unless `ENABLE_DEMO_CLAIM_GRADING=true`.
- Real Meatbag Accountability content remains pending reviewed or ready-to-grade claims.

## Content Briefs From Packets

Dry-run command:

```powershell
.\venv\Scripts\python.exe -m src.content_briefs --brief-type sleeper_breakout_show --season 2025 --week 1 --scoring-profile ppr --dry-run
```

Dry-run result:

- Returned a draft no-write placeholder with `missing_source_rows`.
- This is expected because the current CLI dry-run path does not read BigQuery source rows.
- The no-write dry-run still validated brief shape and did not persist rows.

Materialization command:

```powershell
.\venv\Scripts\python.exe -m src.content_briefs --brief-type sleeper_breakout_show --season 2025 --week 1 --scoring-profile ppr
```

Materialized content brief:

- `content_brief_id`: `brief-sleeper_breakout_show-2025-w1-20260616T141456Z-9bfab9e5`
- `content_brief_run_id`: `sleeper_breakout_show-2025-w1-20260616T141456Z-855e9bbf`
- `brief_type`: `sleeper_breakout_show`
- `review_status`: `draft`
- `item_count`: 2

Content brief row counts:

| Item | Before | After |
| --- | ---: | ---: |
| `content_briefs` | 2 | 3 |
| `content_brief_items` | 16 | 18 |
| `sleeper_breakout_show` briefs | 0 | 1 |
| `sleeper_breakout_show` items | 0 | 2 |

## Final Packet Counts

| Table | Rows after Phase 15.2 |
| --- | ---: |
| `fraud_watch_packets` | 0 |
| `sleeper_breakout_packets` | 2 |
| `trade_review_packets` | 0 |
| `claim_grades` | 0 |
| `content_briefs` | 3 |
| `content_brief_items` | 18 |

## Validation

Commands run:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern content_brief
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern claim
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern market
```

Results:

| Pattern | Result |
| --- | --- |
| `content_brief` | 11 passed, 0 failed |
| `claim` | 17 passed, 0 failed |
| `market` | 9 passed, 0 failed |

Expected claim informational warnings remain:

- `120_claims_player_identity_coverage.sql`: 3 claim-player rows, 1 intentionally unresolved draft demo row.
- `142_claim_ledger_ui_sources_exist.sql`: 3 active claim sources.
- `143_claim_ledger_ui_draft_claims_allowed_missing_fields.sql`: 1 draft claim missing review fields.

## Remaining Gaps

1. Fraud Watch packets need a season/week slice where `analytics_fraud_watch` has source rows, or the 2025 week 1 source mart needs to be populated.
2. Trade Review packets need either an explicit demo flag or a real manual trade request workflow.
3. Meatbag Accountability needs reviewed or ready-to-grade non-demo claims before claim grading should run.
4. Sleeper Breakout source identity should be reconciled so the same player does not appear as both `sleeper:12826` and `source:00-0040476`.
5. The content brief dry-run CLI is shape-only when `--dry-run` is used. A future enhancement could add a no-write live-source preview mode.

## Decision

GO WITH WARNINGS.

Acceptance criteria were met because at least one non-streamer packet family, `sleeper_breakout_packets`, was materialized and content brief review now has an additional deterministic brief type, `sleeper_breakout_show`.
