# Meatbag Claim Ledger

The Meatbag Claim Ledger is a manual-entry BigQuery layer for tracking analyst claims before future grading. It is designed for receipts, content prep, and eventual Pigskin versus Meatbag evaluation.

## Scope

This phase adds:

- BigQuery tables for sources, claims, claim players, and evaluation windows.
- A manual backend helper in [src/claim_ledger.py](../../src/claim_ledger.py).
- CLI dry-run entry paths.
- Validation SQL for table grain, required review fields, identity coverage, model-run joins, and evaluation-window grain.
- Contracts under [bigquery/contracts](../../bigquery/contracts).

This phase does not:

- Call LLMs.
- Scrape YouTube, TV, podcasts, or articles.
- Create Firebase artifacts.
- Alter Pigskin chat.
- Apply migrations automatically.

Phase 13.4 adds a default-off Streamlit admin UI. See [claim-ledger-ui.md](claim-ledger-ui.md) and [claim-import-format.md](claim-import-format.md).

## Tables

| Table | Purpose | Grain |
| --- | --- | --- |
| `claim_sources` | Manual source registry | one row per `source_id` |
| `fantasy_claims` | Claim-level ledger | one row per `claim_id` |
| `fantasy_claim_players` | Player participants | one row per claim and player role |
| `claim_evaluation_windows` | Grading window metadata | one row per claim and window |

## Manual CLI Examples

Create or update a source without writing:

```powershell
python -m src.claim_ledger --create-source --source-id analyst_x --source-name "Analyst X" --source-type youtube --dry-run
```

Create a draft claim without writing:

```powershell
python -m src.claim_ledger --create-claim --source-id analyst_x --claim-type breakout --player "Player Name" --season 2025 --week 4 --text "Player X is a league winner" --dry-run
```

Use the repo venv on Windows:

```powershell
.\venv\Scripts\python.exe -m src.claim_ledger --create-source --source-id analyst_x --source-name "Analyst X" --source-type youtube --dry-run
```

## Streamlit UI

The Claim Ledger UI is behind `USE_CLAIM_LEDGER_UI=false`.

When enabled, it supports source management, manual claim entry, CSV import preview and write, player resolution review, claim board filtering, claim detail inspection, and safe status actions. It does not scrape URLs, call LLMs, or auto-grade claims.

CSV imports are validated before writing and use [src/claim_import.py](../../src/claim_import.py), which writes through the existing `src.claim_ledger` helper functions.

Phase 14.5 added a small draft-only demo import set for workflow testing. See [phase-14-5-claim-ledger-sample-report.md](validation/phase-14-5-claim-ledger-sample-report.md).

## Status Workflow

1. `draft`: quick manual entry. Only basic fields are required.
2. `reviewed`: metadata has been checked and must include direction plus player or team context.
3. `ready_to_grade`: the evaluation window has matured.
4. `graded`: protected from normal edits.
5. `correction`: explicit audited correction path for graded claims.
6. `archived`: no longer active.

## Identity Handling

Claims resolve players through `player_identity_bridge` when identity rows are supplied or a live BigQuery client is used. The helper:

- Resolves exact `player_id_internal` first.
- Resolves known external IDs second.
- Uses name, team, and position fallback when available.
- Returns disambiguation for ambiguous matches.
- Retains unmatched players with missing identity flags.

## Model and Market Context

The claim row can store:

- `model_run_id_at_claim`
- `pigskin_rank_at_claim`
- `market_rank_at_claim`

These fields are optional for draft claims. Future entry tools should populate them from curated ranking and market outputs when available.

The helper can opportunistically snapshot ranks from:

- `projection_rankings_current`
- `market_consensus_baseline_current`

Those lookups are bounded by player, season, optional week, scoring profile, league type, roster format, and optional model run. Missing tables or empty results should not block draft claim entry.

## Future Grading Direction

Future grading jobs should:

- Read only ledger tables plus curated projection, market, and actual-result marts.
- Produce versioned grading outputs with clear scoring profiles and league context.
- Keep corrections auditable.
- Generate show-ready evidence packets without exposing raw warehouse tables to Pigskin.
