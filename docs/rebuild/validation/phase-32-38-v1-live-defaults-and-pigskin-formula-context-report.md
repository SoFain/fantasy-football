# Phase 32.38 V1 Live Defaults And Pigskin Formula Context Report

Final decision: V1 LIVE DEFAULTS READY

## Files Changed

- `app.py`
- `Dockerfile`
- `src/player_profile_ranking_profiles.py`
- `src/pigskin_context_tools.py`
- `src/pigskin_live_formula_context.py`
- `tests/test_player_profile_ranking_profiles.py`
- `tests/test_pigskin_context_tools.py`
- `tests/test_pigskin_live_formula_context.py`
- `docs/rebuild/pigskin-live-ranking-formula-context.md`
- `docs/rebuild/formula-ranking-owner-review-index.md`
- `docs/rebuild/ranking-algorithm-scorecard.md`
- `docs/rebuild/ranking-opportunity-metrics-matrix.md`

Code/docs commit:

`a173ed0 phase 32.38 set v1 live ranking defaults`

## Production Defaults Summary

Owner-approved v1.0 policy is now reflected in code and documentation:

- Live ranking source: Current Pigskin active rows from `analytics_pigskin_rankings`.
- Default scoring profile: `standard`.
- Dropdown order: Standard, Half PPR, PPR, GNG Keeper.
- Default position board: `ALL`.
- `ALL` board uses one cross-position order, not position chunks.
- TE production depth remains 35.
- Formula Review remains read-only owner-review evidence.

## Formula Policy

| scoring_profile_id | QB | RB | WR | TE |
|---|---|---|---|---|
| `standard` | Current Pigskin | Current Pigskin | Current Pigskin | Current Pigskin |
| `half_ppr` | Current Pigskin | Current Pigskin | Current Pigskin | Current Pigskin |
| `ppr` | Current Pigskin | Current Pigskin | Current Pigskin | Current Pigskin |
| `gng_keeper` | Current Pigskin | Current Pigskin | Current Pigskin | Current Pigskin |

No profile-position challenger was promoted for v1.0.

Why no challenger was promoted:

- Enriched Logistic Elite is useful review-only evidence, but overall pairwise weakness and missingness block promotion.
- Enriched Linear Points is context only because it is useful but more volatile.
- BQML NGS is context only.
- Stats02, PBP, and NGS are component signals.
- Injury and availability are risk flags only.
- Historical depth remains blocked.

## ALL Tab Fix

Previous behavior grouped the `All` board by position, then position rank.

Phase 32.38 behavior:

- Default board key is `ALL`.
- `ALL` sorts active Current Pigskin rows by `display_score` descending, then position rank, position, and player name.
- `ALL` shows `Board Rank`.
- Position tabs remain `ALL`, `QB`, `RB`, `WR`, `TE`.
- Position-specific boards preserve QB45, RB80, WR100, and TE35.

The app still uses `analytics_pigskin_rankings` for live rankings. It does not use Formula Review Markdown or `analytics_pigskin_rankings_candidates` as live ranking source.

## Pigskin Formula Context

Created static context:

`docs/rebuild/pigskin-live-ranking-formula-context.md`

Runtime helper:

`src/pigskin_live_formula_context.py`

The app loads this context into Pigskin chat system instructions. The context tells Pigskin:

- Current Pigskin is active for all scoring profiles and positions.
- Candidate evidence uses the documented proxy:
  `0.55 * analytical_grade_proxy + 0.15 * opportunity_score_proxy + 0.10 * efficiency_score_proxy + 0.10 * role_stability_score + 0.10 * profile_points_score`
- Live rankings are Current Pigskin final rankings from candidate evidence and final Pigskin adjudication.
- Standard is first.
- Position depth is QB45, RB80, WR100, TE35.
- BQML Logistic is review-only.
- Linear Points and BQML NGS are context only.
- Stats02, PBP, and NGS are component signals.
- Injury and availability are risk flags only.
- `pigskin_context_score` must not be claimed.
- Backtest, tournament, champion, ranking-generation, and write controls must not be exposed.

The Dockerfile packages the static context file into the Cloud Run image.

## Read-Only Warehouse Verification

Active `analytics_pigskin_rankings` shape:

| scoring_profile_id | QB | RB | WR | TE | Total |
|---|---:|---:|---:|---:|---:|
| `standard` | 45 | 80 | 100 | 35 | 260 |
| `half_ppr` | 45 | 80 | 100 | 35 | 260 |
| `ppr` | 45 | 80 | 100 | 35 | 260 |
| `gng_keeper` | 45 | 80 | 100 | 35 | 260 |

Total active rows:

`1,040`

Champion verification:

- `ranking_formula_champions`: `0`
- active champion rows: `0`

No TE35 data fix was needed.

## Checks Run

| Check | Result |
|---|---|
| `.\venv\Scripts\python.exe -m unittest tests.test_formula_review_dashboard tests.test_player_profile_ranking_profiles tests.test_pigskin_live_formula_context tests.test_pigskin_context_tools tests.test_pigskin_chat_schema` | Pass, 32 tests |
| `.\venv\Scripts\python.exe -m py_compile app.py src\compat_flags.py src\formula_review_dashboard.py src\player_profile_ranking_profiles.py src\pigskin_context_tools.py src\pigskin_live_formula_context.py` | Pass |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | Pass |
| `git diff --check` | Pass, line-ending warnings only |

No broad validation patterns were run.

## Build And Deploy

Build tag:

`prod-candidate-a173ed0a0b44-20260706T172355Z`

Build ID:

`b7aa2996-4f0a-45e9-bcb7-52c9817b8b98`

Build status:

`SUCCESS`

Build-log evidence confirmed both static docs were packaged:

- `docs/rebuild/live-2026-ranking-review-boards.md`
- `docs/rebuild/pigskin-live-ranking-formula-context.md`

Previous production revision:

`nfl-studio-dashboard-00085-6v4`

Previous image digest:

`sha256:8bfaee3a2a1e54b5d78ed1ac676ebfeb4b9531e1078b08120f84d7f5b4fbaffb`

New production revision:

`nfl-studio-dashboard-00086-wpx`

New image digest:

`sha256:6f443eb45e42409510885c44592c3b303cdfd0fbba531ba9c61ceec8f1a69ceb`

Traffic:

`nfl-studio-dashboard-00086-wpx=100`

Production URL:

`https://nfl-studio-dashboard-583607027760.us-central1.run.app`

Rollback command:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services update-traffic nfl-studio-dashboard --project=fantasy-football-498121 --region=us-central1 --to-revisions=nfl-studio-dashboard-00085-6v4=100
```

Rollback was not used.

## Production Smoke

| Check | Result |
|---|---|
| Cloud Run revision | `nfl-studio-dashboard-00086-wpx` |
| Traffic | 100 percent to new revision |
| Image | digest-pinned `sha256:6f443eb45e42409510885c44592c3b303cdfd0fbba531ba9c61ceec8f1a69ceb` |
| `/_stcore/health` | `200 ok` |
| `/` | `200`, Streamlit shell present |
| Root response traceback check | No traceback |
| `USE_FORMULA_COMPARISON_DASHBOARD` | `true` |
| `DATA_OPS_ALLOW_JOB_TRIGGER` | `false` |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` | `false` |
| `USE_PIGSKIN_HISTORICAL_PACKET_TOOL` | unset |
| Trade score flags | `false` |

Post-login UI confirmation still needs owner refresh because automated smoke stops at the app login shell.

## Safety Confirmations

Confirmed:

- No BQML training.
- No Gemini call.
- No Pigskin chat call.
- No live Sleeper API call.
- No source ingest.
- No Data Ops job trigger.
- No old Python tournament run.
- No write to `ranking_formula_champions`.
- No overwrite of `analytics_pigskin_rankings_candidates`.
- No LLM ranking regeneration.
- No write to `analytics_pigskin_rankings`.
- No `pigskin_context_score` fabrication.
- No backtest/tournament controls exposed to Pigskin.

## Remaining Warnings

- Owner should refresh the production app and confirm the Player Profiles page opens on Standard plus ALL.
- Owner should verify the `ALL` board reads like one cross-position draft board.
- Pigskin chat context was wired into the system prompt, but Pigskin chat was not called in this phase by design.

## Recommended Next Phase

Recommended next:

Studio use / hold Current Pigskin for v1.0.

Other options:

- Post-studio owner selection by scoring profile.
- Review-only persistence after studio.
- Further ranking research after studio.
