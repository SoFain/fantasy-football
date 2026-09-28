# Phase 16.5 Real Claim Data Report

Date: 2026-06-16

Final status: BLOCKED PENDING OPERATOR-SUPPLIED REAL CLAIMS

## Goal

Move beyond demo draft claims by adding a small set of real, human-entered reviewed claims for future claim grading and Meatbag Accountability content.

## Result

No real claims were imported in this phase because no operator-supplied real claim rows were provided.

This is intentional. The phase rules require exact source names and exact claim text supplied by the operator. No claim text was scraped, inferred, generated, or fabricated.

## Real Claim Intake CSV

Created header-only intake template:

```text
data/real_claim_import_template.csv
```

Template columns:

```csv
source_name,source_type,person_name,show_name,source_url,episode_or_video_title,published_at,claimed_at,claim_text,claim_type,claim_direction,time_horizon,season,week,scoring_profile_id,league_type_id,roster_format_id,player_names,team_names,claimed_rank,claimed_projection,claimed_value,notes,review_status
```

The template contains no data rows.

## Import Preview

Command equivalent:

```powershell
.\venv\Scripts\python.exe -c "from pathlib import Path; from src.claim_import import build_claim_import_preview; print(len(build_claim_import_preview(Path('data/real_claim_import_template.csv').read_text())))"
```

Result:

```text
preview_rows=0
display_rows=[]
```

Interpretation:

- CSV header parsed.
- No claims were written.
- No external URLs were fetched.
- No scraping occurred.
- No LLM calls occurred.

## Current Claim Table Counts

Read-only BigQuery counts:

```text
claim_sources: 3
fantasy_claims: 3
fantasy_claim_players: 3
claim_evaluation_windows: 3
claim_grades: 0
```

Current sources:

```text
AI vs. Meatbags Show, source_type=youtube
Internal Pigskin, source_type=internal_pigskin
Manual External Claim, source_type=manual
```

Current claims:

```text
manual_external_claim-waiver-2026-w1-20260616T124942Z-c0466f99
status=draft
claim_type=waiver
claim_text=DEMO CLAIM - DO NOT USE FOR PUBLIC CONTENT: Totally Madeup Demo Player is a waiver stash.

ai_vs_meatbags_show-buy-2026-season-20260616T124937Z-4d0f691c
status=draft
claim_type=buy
claim_text=DEMO CLAIM - DO NOT USE FOR PUBLIC CONTENT: Justin Jefferson is still a buy if the room discounts him.

manual_external_claim-ranking-2026-season-20260616T124931Z-af4bc2e3
status=draft
claim_type=ranking
claim_text=DEMO CLAIM - DO NOT USE FOR PUBLIC CONTENT: Ja'Marr Chase will finish as a top three PPR wide receiver.
```

Demo claims remain draft-only.

## Claim Helper QA

Targeted tests:

```powershell
.\venv\Scripts\python.exe -m unittest tests.test_claim_import tests.test_claim_ledger
```

Result:

```text
Ran 26 tests
OK
```

Read helpers:

- `list_claim_sources(limit=10)` returned 3 active sources.
- `search_claims(limit=10)` returned 3 draft demo claims.

## Staging Claim Ledger UI Check

Temporarily enabled in staging:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services update nfl-studio-dashboard-staging `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --update-env-vars=USE_CLAIM_LEDGER_UI=true `
  --quiet
```

Temporary revision:

```text
nfl-studio-dashboard-staging-00005-q65
```

Health result:

```text
GET /_stcore/health
status=200
body=ok
```

Then removed the staging flag:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services update nfl-studio-dashboard-staging `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --remove-env-vars=USE_CLAIM_LEDGER_UI `
  --quiet
```

Final staging revision:

```text
nfl-studio-dashboard-staging-00006-w68
```

Final staging health:

```text
GET /_stcore/health
status=200
body=ok
```

Final staging flags:

```text
USE_COMPAT_TRADE_PLAYER_HISTORY=true
USE_CLAIM_LEDGER_UI=<unset/default false>
USE_COMPAT_PLAYER_PROFILES=false
USE_COMPAT_SLEEPER_WATCH=false
USE_COMPAT_TRADE_ASSETS=false
USE_COMPAT_VIEWER_TEAM_CONTEXT=false
USE_BACKTEST_DASHBOARD=false
USE_CONTENT_BRIEF_REVIEW_UI=false
USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false
DATA_OPS_ALLOW_JOB_TRIGGER=false
```

Browser-click Claim Ledger UI QA was not completed because the private staging service requires an authenticated browser session and this phase did not authorize using the user Chrome profile. The backend helpers and staging health path were validated.

## Claim Validation

Command run:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern claim
```

Result:

```text
17 passed, 0 failed
```

Expected informational warnings:

```text
120_claims_player_identity_coverage.sql
identity_missing_rate = 0.3333333333333333
```

This warning is expected because the demo unresolved row is still draft-only.

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

Safety validation:

```text
145_claim_ledger_ui_player_resolution_flags.sql
non_draft_unresolved_player_rows = 0
```

Unresolved player rows cannot be promoted incorrectly under the current validation posture.

## What Remains Before Grading

The operator must provide at least one real claim row with:

- source name
- source type
- person or show metadata when available
- source URL as metadata only
- exact claim text
- claim type
- claim direction
- time horizon
- season and week
- scoring profile, league type, and roster format when available
- player names or team names
- claimed rank, projection, or value when applicable

Then:

1. Run import preview.
2. Resolve ambiguous or unresolved players manually.
3. Import rows as `draft`.
4. Human review the claim detail.
5. Promote to `reviewed`.
6. Promote to `ready_to_grade` only when evaluation windows and required fields are present.
7. Run claim validations again.

## Safety Confirmation

- No scraping occurred.
- No URLs were fetched.
- No LLM calls occurred.
- No claims were fabricated.
- No claims were auto-graded.
- No Firebase artifacts were created.
- No production service was changed.
- Demo claims remain draft-only.

## Decision

BLOCKED PENDING OPERATOR-SUPPLIED REAL CLAIMS

The import path, helper reads, staging health check, and validation suite are ready. The only blocker is missing real human-supplied claim data.
