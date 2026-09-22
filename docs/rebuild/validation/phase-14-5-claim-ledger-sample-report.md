# Phase 14.5 Claim Ledger Sample Report

Final status: PASS WITH EXPECTED DEMO/DRAFT INFORMATIONAL WARNINGS

Validation date: 2026-06-16

Project: `fantasy-football-498121`

Dataset: `fantasy_football_brain`

## Purpose

Phase 14.5 exercised the Meatbag Claim Ledger import and review path with bounded sample/manual data. The goal was to make the default-off Claim Ledger UI testable without scraping websites, calling LLMs, or fabricating production claims.

## Sample Data Scope

Sample file:

- `tests/fixtures/sample_claim_import.csv`

Rules used:

- Demo claims are labeled with `DEMO CLAIM - DO NOT USE FOR PUBLIC CONTENT`.
- Demo claims are draft-only.
- Demo rows are for workflow testing, not public show content.
- One intentionally unresolved player row is included to test draft-only unresolved behavior.

## Warehouse Counts

Bounded BigQuery checks reported:

| Item | Count |
| --- | ---: |
| `claim_sources` | 3 |
| `fantasy_claims` | 3 |
| `fantasy_claim_players` | 3 |
| `claim_evaluation_windows` | 3 |
| `claim_grades` | 0 |
| Demo claims | 3 |
| Draft demo claims | 3 |
| Non-draft demo claims | 0 |
| Unresolved claim-player rows | 1 |

## Unresolved Demo Row

The unresolved row is intentional. It uses a made-up sample player to prove the import and UI workflow can carry unresolved player context without accidentally making the claim review-ready.

This is acceptable because:

- the claim remains `draft`;
- `144_claim_ledger_ui_ready_claims_required_fields.sql` passed;
- `145_claim_ledger_ui_player_resolution_flags.sql` passed;
- unresolved rows are blocked from non-draft review states;
- the row is clearly marked as demo data.

## Safety

- No scraping was performed.
- No LLM calls were made.
- No production claims were fabricated.
- No automatic grading was run.
- No Firebase artifacts were created.

## Validation

Command:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern claim
```

Result:

- 17 validations passed.
- 0 validations failed.

Expected informational warnings:

- `120_claims_player_identity_coverage.sql`: 3 claim-player rows, 1 intentionally unresolved draft demo row, identity missing rate `0.3333333333333333`.
- `142_claim_ledger_ui_sources_exist.sql`: 3 active claim sources.
- `143_claim_ledger_ui_draft_claims_allowed_missing_fields.sql`: 1 draft claim missing review fields.

## Decision

PASS WITH EXPECTED DEMO/DRAFT INFORMATIONAL WARNINGS.

The Claim Ledger can be exercised with sample/manual data. The unresolved player warning is intentional and remains draft-only.
