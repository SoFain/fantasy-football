# Phase 13.2 Initial Materialization Report

Date: 2026-06-16

Decision: GO WITH WARNINGS

## Scope

Phase 13.2 seeded governed reference/source rows and materialized the first usable Phase 12 output path.

No Firebase artifacts were created. No scraping was performed. No LLM calls were made. No external paid APIs were called. No production Cloud Run Jobs were triggered. Streamlit runtime behavior was not changed.

## Starting Row Counts

Counts were collected with BigQuery table metadata for physical tables. For views, actual bounded `COUNT(*)` checks were used where needed.

| Table | Starting Rows |
| --- | ---: |
| `backtest_runs` | 0 |
| `backtest_result_player_week` | 0 |
| `backtest_result_summary` | 0 |
| `backtest_calibration_bins` | 0 |
| `market_consensus_sources` | 0 |
| `market_consensus_snapshots` | 0 |
| `market_consensus_player_values` | 0 |
| `market_consensus_baseline_current` | 0 |
| `claim_sources` | 0 |
| `fantasy_claims` | 0 |
| `fantasy_claim_players` | 0 |
| `claim_evaluation_windows` | 0 |
| `claim_grading_runs` | 0 |
| `claim_grades` | 0 |
| `claim_source_scorecards` | 0 |
| `content_brief_runs` | 0 |
| `content_briefs` | 0 |
| `content_brief_items` | 0 |
| `projections_player_weekly` | 0 |
| `projections_player_ros` | 0 |
| `projections_player_dynasty` | 0 |
| `projection_rankings_current` | 0 |
| `compat_trade_assets_current` | 1,383 |
| `fraud_watch_packets` | 0 |
| `sleeper_breakout_packets` | 0 |
| `trade_review_packets` | 0 |

Supporting source context:

| Table | Rows |
| --- | ---: |
| `market_values` | 461 |
| `mart_trade_assets_current` | 1,383 |
| `analytics_pigskin_rankings` | 285 |
| `analytics_fraud_watch` | 3,638 |
| `dim_players_current` | 11,212 |
| `player_identity_bridge` | 11,212 |
| `scoring_profiles` | 3 |
| `analytics_player_weekly_truth` | 50,635 |

## Seed Rows Added

Seed rows were applied through existing MERGE-backed helpers.

### Market Sources

Dry-run command pattern:

```powershell
.\venv\Scripts\python.exe -m src.market_consensus --register-source --source-id <id> --source-name <name> --source-type <type> --access-method <method> --license-notes <notes> --dry-run
```

Applied source rows:

| Source ID | Type | Access | Automated Allowed |
| --- | --- | --- | --- |
| `internal_pigskin_rankings` | `analyst_rank` | `internal` | true |
| `manual_market_values` | `market_value` | `manual` | false |
| `manual_adp` | `adp` | `manual` | false |
| `manual_consensus_rankings` | `ecr` | `manual` | false |

Manual and future-licensed sources remain `automated_allowed=false`.

### Claim Sources

Dry-run command pattern:

```powershell
.\venv\Scripts\python.exe -m src.claim_ledger --create-source --source-id <id> --source-name <name> --source-type <type> --notes <notes> --dry-run
```

Applied source rows:

| Source ID | Type | Notes |
| --- | --- | --- |
| `internal_pigskin` | `internal_pigskin` | Internal Pigskin claims and model-generated positions. |
| `manual_external_claim` | `manual` | Manual external claim placeholder. No scraping authorized. |
| `ai_vs_meatbags_show` | `youtube` | Official AI vs. Meatbags show claims entered manually or generated from governed show workflow. |

No fantasy claims were created. No demo claims were created.

## Market Baseline Materialization

The repo CLI currently supports market source registration and CSV/manual ingestion. It does not expose the requested `--snapshot-source compat_trade_assets_current` CLI flag.

Because `compat_trade_assets_current` had governed rows available, the initial market baseline was materialized through an idempotent BigQuery MERGE script that read only:

```text
fantasy_football_brain.compat_trade_assets_current
```

Dry-run result:

```text
DRY_RUN bytes=1469995
```

Applied materialization:

| Target Table | Rows After |
| --- | ---: |
| `market_consensus_snapshots` | 1 |
| `market_consensus_player_values` | 461 |
| `market_consensus_baseline_current` | 461 |

Snapshot created:

```text
manual_market_values_compat_trade_assets_current_2026_ppr_redraft_one_qb
```

Context:

| Field | Value |
| --- | --- |
| `source_id` | `manual_market_values` |
| `snapshot_date` | `2026-06-13` |
| `season` | `2026` |
| `scoring_profile_id` | `ppr` |
| `league_type_id` | `redraft` |
| `roster_format_id` | `one_qb` |
| `row_count` | 461 |

Top sample rows in `market_consensus_baseline_current`:

| Player | Position | Team | Market Value | Overall Rank |
| --- | --- | --- | ---: | ---: |
| Bijan Robinson | RB | ATL | 10,934 | 1 |
| Jahmyr Gibbs | RB | DET | 10,703 | 2 |
| Ja'Marr Chase | WR | CIN | 9,888 | 3 |
| Jaxon Smith-Njigba | WR | SEA | 9,096 | 4 |
| Puka Nacua | WR | LAR | 8,808 | 5 |

## Backtest And Projection Dry-Runs

Projection dry-run command:

```powershell
.\venv\Scripts\python.exe -m src.projection_engine --horizon weekly --season 2026 --week 1 --scoring-profile ppr --league-type redraft --roster-format one_qb --limit 25 --dry-run
```

Result:

- Command succeeded.
- Produced dry-run weekly projection rows.
- No rows were written.

Backtest dry-run command:

```powershell
.\venv\Scripts\python.exe -m src.backtesting --horizon weekly --season-start 2024 --season-end 2024 --week-start 1 --week-end 1 --scoring-profile ppr --league-type redraft --roster-format one_qb --dry-run
```

Result:

```json
{"projection_rows": 0, "actual_rows": 0, "player_week_rows": 0, "summary_rows": 0, "calibration_rows": 0, "missing_data_flags": ["missing_projection_rows", "missing_actual_rows"], "status": "failed"}
```

Classification: expected empty-state pending projection materialization. No backtest rows were written.

## Claim Ledger And Claim Grading

Claim source rows were seeded. No real external claims were created because no manual claim text was provided. Demo claims were not enabled.

Claim grading dry-run command:

```powershell
.\venv\Scripts\python.exe -m src.claim_grading --season 2026 --week 1 --scoring-profile ppr --league-type redraft --roster-format one_qb --dry-run
```

Result:

```json
{"claim_count": 0, "grade_count": 0, "scorecard_count": 0}
```

Classification: expected empty-state until reviewed manual claims exist.

## Content Brief Dry-Run

Content brief dry-run command:

```powershell
.\venv\Scripts\python.exe -m src.content_briefs --brief-type rankings_debate_show --season 2026 --week 1 --scoring-profile ppr --league-type redraft --roster-format one_qb --dry-run
```

Result:

- Command succeeded.
- Returned a draft empty-state brief with `missing_source_rows`.
- No content brief rows were written.

Classification: expected empty-state until packet/projection/claim sources are materialized.

## Final Row Counts

| Table | Final Rows |
| --- | ---: |
| `backtest_runs` | 0 |
| `backtest_result_player_week` | 0 |
| `backtest_result_summary` | 0 |
| `backtest_calibration_bins` | 0 |
| `market_consensus_sources` | 4 |
| `market_consensus_snapshots` | 1 |
| `market_consensus_player_values` | 461 |
| `market_consensus_baseline_current` | 461 |
| `claim_sources` | 3 |
| `fantasy_claims` | 0 |
| `fantasy_claim_players` | 0 |
| `claim_evaluation_windows` | 0 |
| `claim_grading_runs` | 0 |
| `claim_grades` | 0 |
| `claim_source_scorecards` | 0 |
| `content_brief_runs` | 0 |
| `content_briefs` | 0 |
| `content_brief_items` | 0 |
| `projections_player_weekly` | 0 |
| `projections_player_ros` | 0 |
| `projections_player_dynasty` | 0 |
| `projection_rankings_current` | 0 |
| `compat_trade_assets_current` | 1,383 |
| `fraud_watch_packets` | 0 |
| `sleeper_breakout_packets` | 0 |
| `trade_review_packets` | 0 |

## Validation Results

Commands:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern market
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern backtest
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern claim
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern content_brief
```

Results:

| Pattern | Result |
| --- | --- |
| `market` | 9 passed, 0 failed |
| `backtest` | 8 passed, 0 failed |
| `claim` | 13 passed, 0 failed |
| `content_brief` | 7 passed, 0 failed |

Warnings:

- `113_market_identity_coverage.sql`: informational warning. `market_consensus_player_values` has 461 rows, 64 missing `player_id_internal`, identity missing rate `0.13882863340563992`.
- `120_claims_player_identity_coverage.sql`: informational expected empty-state. `fantasy_claim_players` has 0 rows.

No table-not-found failures remain.

## Remaining Expected Empty-States

- Backtest outputs remain empty because projection output tables are empty.
- Claim outputs remain empty because no reviewed manual claims were provided.
- Claim grading outputs remain empty because no claims are ready to grade.
- Content brief outputs remain empty because source packet/projection/claim sources are not materialized yet.
- Fraud, sleeper breakout, and trade review packet tables remain empty.

## Future Production Materialization Commands

Projection materialization after approval:

```powershell
.\venv\Scripts\python.exe -m src.projection_engine --horizon weekly --season 2026 --week 1 --scoring-profile ppr --league-type redraft --roster-format one_qb --limit 25
```

Backtest after projection rows exist:

```powershell
.\venv\Scripts\python.exe -m src.backtesting --horizon weekly --season-start 2024 --season-end 2024 --week-start 1 --week-end 1 --scoring-profile ppr --league-type redraft --roster-format one_qb --dry-run
.\venv\Scripts\python.exe -m src.backtesting --horizon weekly --season-start 2024 --season-end 2024 --week-start 1 --week-end 1 --scoring-profile ppr --league-type redraft --roster-format one_qb
```

Manual claim entry after a real claim is provided:

```powershell
.\venv\Scripts\python.exe -m src.claim_ledger --create-claim --source-id manual_external_claim --claim-type ranking --claim-direction over --time-horizon weekly --season 2026 --week 1 --text "<manual reviewed claim>" --entered-by "<operator>" --review-status draft --player "<player name>" --dry-run
```

Claim grading after claims are reviewed:

```powershell
.\venv\Scripts\python.exe -m src.claim_grading --season 2026 --week 1 --scoring-profile ppr --league-type redraft --roster-format one_qb --dry-run
```

Content brief after packet/projection/claim rows exist:

```powershell
.\venv\Scripts\python.exe -m src.content_briefs --brief-type rankings_debate_show --season 2026 --week 1 --scoring-profile ppr --league-type redraft --roster-format one_qb --dry-run
```

## Final Decision

GO WITH WARNINGS.

The market consensus path is now operational with governed rows. Backtest, claim grading, and content brief paths remain structurally valid but intentionally empty until projection rows, reviewed claims, and packet sources are materialized.
