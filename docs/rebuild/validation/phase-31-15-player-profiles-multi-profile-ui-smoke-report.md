# Phase 31.15 Player Profiles Multi Profile UI Smoke Report

Date: 2026-07-04

Final decision: **PLAYER PROFILES MULTI PROFILE UI READY**

## Scope

Phase 31.15 verified that Player Profiles can select and query all generated scoring-profile ranking boards:

- PPR
- Half PPR
- Standard
- GNG Keeper

No production deploy, staging deploy, Pigskin chat call, LLM-backed ranking generation, ranking regeneration, candidate materialization, active-ranking overwrite, live Sleeper API call, Cloud Run Job trigger, Scheduler job creation, ranking formula/backtest write, or Pigskin formula exposure was performed.

## Git State

Latest commit before this report:

- `02f09b8 Document generated multi-profile Pigskin rankings`

Tracked working tree before the report:

- no tracked source diffs

Untracked historical validation backlog remains present from prior phases and was not staged.

Files changed in this phase:

- `docs/rebuild/validation/phase-31-15-player-profiles-multi-profile-ui-smoke-report.md`

## Active Ranking Board Verification

Read-only BigQuery checks against `analytics_pigskin_rankings` confirmed:

- active final ranking row count: `1,140`
- all rows checked with `is_active=true`
- no null ranks
- no duplicate player IDs within profile/position
- PPR remained intact

| scoring_profile_id | QB | RB | WR | TE |
| --- | ---: | ---: | ---: | ---: |
| `ppr` | 45 | 80 | 100 | 60 |
| `half_ppr` | 45 | 80 | 100 | 60 |
| `standard` | 45 | 80 | 100 | 60 |
| `gng_keeper` | 45 | 80 | 100 | 60 |

Each profile returned `285` active players.

## Trey McBride Verification

Trey McBride was present as TE rank 1 in every generated board:

| scoring_profile_id | player_id | position | rank | ranking_version |
| --- | --- | --- | ---: | --- |
| `ppr` | `00-0037744` | TE | 1 | `pigskin-llm-20260703061257` |
| `half_ppr` | `00-0037744` | TE | 1 | `pigskin-llm-20260704070315` |
| `standard` | `00-0037744` | TE | 1 | `pigskin-llm-20260704071412` |
| `gng_keeper` | `00-0037744` | TE | 1 | `pigskin-llm-20260704072119` |

## Sample Player Smoke

Read-only query checks confirmed Player Profiles can see the requested sample players in all four profiles:

| player | ppr | half_ppr | standard | gng_keeper |
| --- | ---: | ---: | ---: | ---: |
| Trey McBride | TE 1 | TE 1 | TE 1 | TE 1 |
| Brock Bowers | TE 2 | TE 2 | TE 2 | TE 2 |
| Josh Allen | QB 1 | QB 1 | QB 1 | QB 1 |
| Christian McCaffrey | RB 1 | RB 1 | RB 1 | RB 1 |
| Ja'Marr Chase | WR 3 | WR 3 | WR 4 | WR 4 |

The profile-specific differences for Ja'Marr Chase confirm selected profile rows are not silently falling back to PPR.

## Player Profiles Dropdown And Query Verification

Code reviewed:

- `src/player_profile_ranking_profiles.py`
- `app.py`
- `tests/test_player_profile_ranking_profiles.py`

Dropdown options are exactly:

| label | internal value |
| --- | --- |
| PPR | `ppr` |
| Half PPR | `half_ppr` |
| Standard | `standard` |
| GNG Keeper | `gng_keeper` |

Default:

- `ppr`

Query behavior:

- `build_pigskin_rankings_query(...)` filters with `scoring_profile_id = @scoring_profile_id`
- selected profile is passed as a BigQuery parameter
- Half PPR, Standard, and GNG Keeper do not fall back to PPR
- missing-board warning remains explicit: `Rankings for this scoring system have not been generated yet.`

Display behavior:

- selected scoring label appears in the canonical ranking freshness caption
- selected scoring label appears in detailed ranking sections such as `Pigskin Score (Half PPR)` and `Canonical Pigskin Ranking (Half PPR)`
- rank badges and position rank values come from the selected profile merge

## Local Checks

Commands run:

```powershell
.\venv\Scripts\python.exe scripts\check_deployment_safety.py
.\venv\Scripts\python.exe -m py_compile app.py
.\venv\Scripts\python.exe -m compileall -q src scripts
.\venv\Scripts\python.exe -m unittest tests.test_player_profile_ranking_profiles tests.test_pigskin_rankings_model_runs tests.test_pigskin_rankings_materialize_identity
.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run
```

Results:

- safety checker: pass
- `app.py` compile: pass
- `src` and `scripts` compile: pass
- focused tests: `24` tests passed
- pending migrations: none
- validation dry-run discovery: `209` validation files

No full test suite was run because no source code changed.

## Staging Deploy

Staging deploy was not run in this phase.

Reason:

- local helper tests passed
- data/query verification passed
- no UI/source fix was required
- the prompt only required staging deployment if code changed or staging was needed for owner review

Current staging service, read-only describe:

- service: `nfl-studio-dashboard-staging`
- revision: `nfl-studio-dashboard-staging-00031-79n`
- URL: `https://nfl-studio-dashboard-staging-inypcgbx7a-uc.a.run.app`

## Production Deploy Planning

Production deploy was not run.

Current production service, read-only describe:

- service: `nfl-studio-dashboard`
- revision: `nfl-studio-dashboard-00081-bwr`
- URL: `https://nfl-studio-dashboard-inypcgbx7a-uc.a.run.app`
- traffic: `nfl-studio-dashboard-00081-bwr=100`
- service account: `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com`

Current production risk flag state observed:

- `DATA_OPS_ALLOW_JOB_TRIGGER=false`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER=false`
- `USE_BACKTEST_DASHBOARD=false`
- `USE_CLAIM_LEDGER_UI=false`
- `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false`
- `USE_COMPAT_PLAYER_PROFILES=false`
- `USE_COMPAT_SLEEPER_WATCH=false`
- `USE_COMPAT_TRADE_ASSETS=false`
- `USE_COMPAT_TRADE_PLAYER_HISTORY=false`
- `USE_COMPAT_TRADE_PLAYER_SCORE=false`
- `USE_COMPAT_VIEWER_TEAM_CONTEXT=false`
- `USE_CONTENT_BRIEF_REVIEW_UI=false`
- `USE_DATA_OPS_LOCAL_SUBPROCESS_CONTROLS=false`
- `USE_TRADE_ANALYZER_SCORE_V0=false`

Observed production-specific QA flag:

- `USE_PIGSKIN_PACKET_QA_UI=true`

Production recommendation:

- do not deploy production from this phase
- if owner wants the scoring dropdown promoted, run a separate Phase 31.16 staging browser smoke or production deploy phase
- preserve all current production safety flags
- do not enable Pigskin formula/backtest exposure

Rollback command template if a future production deploy is approved:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services update-traffic nfl-studio-dashboard `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --to-revisions=nfl-studio-dashboard-00081-bwr=100
```

Suggested future smoke checklist:

- health endpoint returns ok
- app login gate works
- Player Profiles Directory opens
- scoring dropdown shows PPR, Half PPR, Standard, GNG Keeper
- default is PPR
- switching profiles changes rank rows
- Trey McBride remains TE rank 1 in each profile
- no missing-board message appears for generated profiles
- no traceback

## Ranking Data No-Change Confirmation

Post-check read-only state:

- active final rankings: `1,140`
- all four profile boards present
- candidate table profile purity: `ppr` only
- candidate table row count: `936`

Ranking formula/backtest table counts:

| table | row_count |
| --- | ---: |
| `ranking_formula_candidates` | 12 |
| `ranking_formula_sets` | 1 |
| `ranking_backtest_runs` | 0 |
| `ranking_backtest_results` | 0 |
| `ranking_backtest_candidate_summaries` | 0 |
| `ranking_formula_champions` | 0 |

## Pigskin Formula Exposure Confirmation

Search paths:

- `app.py`
- `src/pigskin_context_tools.py`
- `src/pigskin_packet_guardrails.py`
- `src/pigskin_context_qa.py`

Search terms:

- `ranking_formula`
- `ranking_backtest`
- `ALLOW_RANKING_FORMULA_BACKTEST_WRITE`
- `execute_bigquery_sql`

Result:

- no matches in the searched Pigskin-visible paths
- no arbitrary SQL path added
- no ranking formula/backtest read/write exposure found

## Warnings

- Manual browser smoke was not run because no UI code changed and staging deployment was not required in this phase.
- The Player Profiles detailed scouting report section can still call Gemini if a runtime key is present and a user opens that path. This phase did not exercise that path and did not call LLM-backed actions.
- Historical untracked validation backlog remains in the worktree and was not touched.

## Recommended Next Phase

Recommended next phase:

- **Phase 31.16 — Production deploy Player Profiles scoring dropdown**, only if the owner wants this UI state promoted and accepts the separate deployment gate.

Alternative:

- **Phase 31.16 — Formula comparison dashboard skeleton**, if deployment can wait and the next priority is ranking formula review tooling.
