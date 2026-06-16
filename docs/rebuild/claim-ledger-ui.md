# Claim Ledger UI

Phase 13.4 adds a default-off Streamlit workflow for manual Meatbag Claim Ledger entry and CSV import.

## Feature Flag

`USE_CLAIM_LEDGER_UI=false` by default.

When false, the existing Streamlit tab list is unchanged. When true, a `Claim Ledger` tab is appended after the existing admin tabs.

## Scope

The UI supports:

- claim source search and upsert
- manual claim entry
- CSV import preview and write
- player name resolution through the canonical identity bridge helper
- claim review board filtering
- claim detail inspection
- status actions for reviewed, ready to grade, and archived
- grading dry-run command preview

The UI does not:

- scrape external sources
- fetch source URLs
- call LLMs
- auto-grade claims
- expose raw warehouse tables to Pigskin
- run long warehouse jobs from request-time Streamlit code

## Helper Layer

CSV and admin helper: [src/claim_import.py](../../src/claim_import.py)

Write path:

- `claim_ledger.register_claim_source()`
- `claim_ledger.create_fantasy_claim()`
- `claim_ledger.update_claim_status()`

Read path:

- `claim_sources`
- `fantasy_claims`
- `fantasy_claim_players`
- `claim_evaluation_windows`

These are claim-ledger/admin metadata tables, not raw football source tables.

## Status Behavior

Draft claims may be incomplete. Claims marked `reviewed`, `ready_to_grade`, or `graded` must include source metadata, claim text, claim type, claim direction, horizon, season, and at least one resolved player or team subject.

Ambiguous or unresolved CSV player rows can be imported only as `draft`. The UI surfaces the resolution status and stores missing-data context in `context_json`.

## Rollback

Rollback is env-only:

1. Remove `USE_CLAIM_LEDGER_UI` or set it to `false`.
2. Restart or redeploy the Streamlit service.
3. Confirm the Claim Ledger tab is absent.

No migration rollback is required.

## Manual QA

Run locally with:

```powershell
.\venv\Scripts\python.exe -m streamlit run app.py
```

Checklist:

1. With the flag unset, confirm the Claim Ledger tab is absent.
2. Set `USE_CLAIM_LEDGER_UI=true`.
3. Add or update a manual source.
4. Preview a manual draft claim.
5. Write a manual draft claim.
6. Upload a valid CSV and confirm preview rows are shown before writing.
7. Confirm ambiguous and unresolved players are flagged.
8. Confirm invalid rows can be exported as an error CSV.
9. Confirm status actions reject incomplete reviewed or ready claims.
10. Confirm grading is a command preview only.

## Validation

Claim UI validation SQL:

- [142_claim_ledger_ui_sources_exist.sql](../../bigquery/validations/142_claim_ledger_ui_sources_exist.sql)
- [143_claim_ledger_ui_draft_claims_allowed_missing_fields.sql](../../bigquery/validations/143_claim_ledger_ui_draft_claims_allowed_missing_fields.sql)
- [144_claim_ledger_ui_ready_claims_required_fields.sql](../../bigquery/validations/144_claim_ledger_ui_ready_claims_required_fields.sql)
- [145_claim_ledger_ui_player_resolution_flags.sql](../../bigquery/validations/145_claim_ledger_ui_player_resolution_flags.sql)

Use:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern claim_ledger_ui
```
