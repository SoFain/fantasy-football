# Phase 27.3 Trade Score V1 Source Context Review Report

## Final Decision

TRADE SCORE V1 NEEDS MINOR TUNING

V1 is structurally safe and the bounded dry-run remains non-mutating, but it should not move to staging materialization yet. The blockers are narrow and explainable:

- `role_source_gap` is too noisy because missing role flags come from `compat_trade_player_history.missing_data_flags` even when alternate role context is present.
- team context needs an explicit warning path because some rows combine current-team display context with historical production or projection context.
- projection `as_of_*` metadata is still null in `projection_rankings_current`, while the score source query currently coalesces it to the target week and hides that warning.
- draft picks are still preview-scored, but correctly excluded from materializable player score rows.

Recommended next phase: implement a small Phase 27.4 tuning pass. Do not materialize v1 yet.

## Scope

This phase was review and dry-run only. No score rows were written. No `--write` command was run. No deployment, production feature flag change, Cloud Run Job trigger, Scheduler job, ingestion, score materialization, LLM action, Pigskin prompt, scrape, Firebase artifact, authorization gate, staging change, production change, or commit occurred.

## Safety State

| Gate | State |
| --- | --- |
| `ALLOW_TRADE_SCORE_MATERIALIZATION` | unset |
| `ALLOW_PROJECTION_CONTEXT_REFRESH` | unset |
| `ALLOW_LIMITED_PRODUCTION_DEPLOY` | unset |
| `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST` | unset |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` | unset |

## Checks Run

| Command | Result |
| --- | --- |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | pass |
| `.\venv\Scripts\python.exe -m py_compile app.py` | pass |
| `.\venv\Scripts\python.exe -m py_compile src\trade_player_scores.py` | pass |
| `.\venv\Scripts\python.exe -m compileall -q src scripts` | pass |
| `.\venv\Scripts\python.exe -m unittest tests.test_trade_player_scores` | pass, 30 tests |
| `.\venv\Scripts\python.exe -m unittest discover tests` | pass, 357 tests |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run` | pass |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern trade_player_scores` | pass, 11 of 11 |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern compat_trade_player_scores` | pass, 2 of 2 |

The full test suite prints mocked pipeline and load logs from existing tests. This phase did not run live ingestion.

## V1 Dry-Run Confirmation

Command:

```powershell
.\venv\Scripts\python.exe -m src.trade_player_scores --season 2025 --week 18 --scoring-profile-id ppr --league-type-id redraft --roster-format-id one_qb --model-version trade_score_v1_2025_001 --dry-run
```

Result:

| Metric | Value |
| --- | ---: |
| `dry_run` | true |
| `wrote` | false |
| source rows | 100 |
| score rows | 100 |
| materializable player rows | 77 |
| excluded rows | 23 |
| excluded pick rows | 13 |
| score run id | `trade-score-trade_score_v1_2025_001-2025-w18-d688691f667a` |

Top dry-run examples remain Bijan Robinson, Ja'Marr Chase, and Puka Nacua. Bottom examples remain Chuba Hubbard, Bhayshul Tuten, and David Montgomery.

## Premium Row Identity And Team Review

The score source query uses `compat_trade_assets_current.team` as the displayed score team. Recent production, fantasy profile, Fraud Watch, and projection rows can reflect the player's historical team for the target week. That is not inherently wrong, but the model should expose a team-context warning when those values differ.

Key source context:

| Player | Score team | History team | Fantasy team | Truth team | Truth current team | Projection team | Join status | Review result |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A.J. Brown | NE | PHI | PHI | PHI | NE | PHI | source key | Needs team-context warning. Current display team is NE, but 2025 week 14-18 production and projection context are PHI. |
| Ja'Marr Chase | CIN | CIN | CIN | CIN | CIN | CIN | source key | Clean. |
| Justin Jefferson | MIN | MIN | MIN | MIN | MIN | MIN | source key | Clean. |
| Puka Nacua | LAR | LA | LA | LA | LA | LA | source key | Team alias mismatch only. Needs `LA` to `LAR` normalization, not a player identity issue. |
| Amon-Ra St. Brown | DET | DET | DET | DET | DET | DET | source key | Clean. |
| Josh Allen | BUF | BUF | BUF | BUF | BUF | BUF | source key | Clean. |
| Jalen Hurts | PHI | PHI | PHI | PHI | PHI | PHI | source key | Clean, but v1 still prices the one-QB market lower. |
| Jayden Daniels | WAS | WAS | WAS | WAS | WAS | WAS | source key | Clean identity. Low recent sample explains lower score. |
| Brock Bowers | LV | LV | LV | LV | LV | LV | source key | Clean. |
| Malik Nabers | NYG | none | none | none | none | NYG | source key | Identity is stable, but recent/fantasy/truth context is missing. Keep review-only until source coverage is understood. |
| Marvin Harrison | ARI | ARI | none | none | none | ARI | player_id_internal | Needs identity source review. Asset `source_player_key` is `00-0007024`, while projection weekly rows use `00-0039849`; the join survives through `player_id_internal=sleeper:11628`. |
| Ashton Jeanty | LV | LV | LV | LV | LV | LV | source key | Clean. |
| Bijan Robinson | ATL | ATL | ATL | ATL | ATL | ATL | source key | Clean. |
| Jahmyr Gibbs | DET | DET | DET | DET | DET | DET | source key | Clean. |
| Jaxon Smith-Njigba | SEA | SEA | SEA | SEA | SEA | SEA | source key | Clean. |

### A.J. Brown

A.J. Brown is not an identity join failure:

| Field | Value |
| --- | --- |
| `player_id_internal` | `gsis:00-0035676` |
| `source_player_key` | `00-0035676` |
| `gsis_id` | `00-0035676` |
| score team | `NE` |
| history and fantasy team | `PHI` |
| `analytics_player_weekly_truth.team` | `PHI` |
| `analytics_player_weekly_truth.current_team` | `NE` |
| projection team | `PHI` |
| `projection_join_strategy` | `source_player_key` |
| `fraud_join_strategy` | `source_player_key` |

The mismatch affects display and explainability more than the numeric join. The score combines current team display with historical PHI production and PHI projection context. Recommended fix: add a `team_context_mismatch_warning` in `component_json` or `missing_flags_json` when `asset_team` differs from history, truth, fantasy, projection, or fraud team while `current_team` supports the asset team.

## Role Source Gap Root Cause

`role_source_gap` appears on every row because role flags flow in from `compat_trade_player_history.missing_data_flags`, not from the asset row or fantasy profile row:

| Source flag column | Role flag counts |
| --- | --- |
| `asset_missing_data_flags` | none |
| `fantasy_missing_data_flags` | none |
| `history_missing_data_flags` | `missing_routes_proxy=71`, `missing_snaps=71`, `missing_snap_share=3` |

The top 100 candidate source context shows role alternatives are often present:

| Position | Rows | history sample present | snap context present | target context present | rush context present | truth role quality present |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| QB | 13 | 13 | 13 | 13 | 13 | 0 |
| RB | 29 | 25 | 25 | 25 | 25 | 0 |
| WR | 36 | 27 | 25 | 27 | 27 | 0 |
| TE | 9 | 6 | 5 | 6 | 6 | 0 |
| PICK | 13 | 0 | 0 | 0 | 0 | 0 |

Examples where the gap is probably harmless:

| Player | Role flags | Available context |
| --- | --- | --- |
| Bijan Robinson | `missing_routes_proxy`, `missing_snaps` | history snap share `0.780`, target/rush context present |
| Ja'Marr Chase | `missing_routes_proxy`, `missing_snaps` | history snap share `0.922`, target context present |
| Puka Nacua | `missing_routes_proxy`, `missing_snaps` | history snap share `0.642`, target context present |

Examples where the gap is meaningful:

| Player | Role flags | Why it matters |
| --- | --- | --- |
| Malik Nabers | `missing_snaps_last_3` | no recent history, fantasy profile, truth, or Fraud Watch source rows found in the target window |
| Jeremiyah Love | `missing_snaps_last_3` | high market row with missing model run and recent-history gaps |
| Draft picks | `missing_snaps_last_3` | not player rows; pick score lane is pending |

Decision: reduce or bypass role-source penalties when `snap_share`, `target_share`, `rush_share`, or truth role metrics are present. Keep `missing_snaps_last_3` meaningful for rows with no recent source coverage.

## Recent History And Fallback Gaps

Counts from the v1 dry-run:

| Gap | Rows |
| --- | ---: |
| `missing_recent_trade_history` | 29 |
| `role_usage_fallback_used` | 29 |
| `efficiency_fallback_used` | 29 |

High-market, low-confidence examples:

| Player | Position | Market score | V1 score | Confidence | Cause |
| --- | --- | ---: | ---: | ---: | --- |
| Jeremiyah Love | RB | 87.93 | 76.05 | 57.00 | missing model run, missing recent history, role and efficiency fallbacks |
| Malik Nabers | WR | 84.72 | 63.92 | 46.86 | missing recent history, missing fraud context, role and efficiency fallbacks |
| 2026 Pick 1.01 | PICK | 96.15 | 63.75 | 51.00 | pick lane pending, no player identity, missing model run, no recent history |

Decision: recent-history and fallback penalties are broadly correct. They should stay materialization warnings for player rows. Draft picks should not be compared with player rows.

## Projection Freshness Review

`projection_rankings_current` target slice:

| Metric | Value |
| --- | ---: |
| rows | 600 |
| distinct model runs | 2 |
| `as_of_season` null rows | 600 |
| `as_of_week` null rows | 600 |
| min `created_at` | 2026-06-18 04:40:46 UTC |
| max `created_at` | 2026-06-18 15:21:51 UTC |

`projections_player_weekly` target slice:

| Metric | Value |
| --- | ---: |
| rows | 600 |
| distinct model runs | 2 |
| missing `source_freshness_json` | 0 |
| missing or empty `missing_data_flags` | 0 |

Current issue: the source query does `COALESCE(r.as_of_week, r.week) AS projection_as_of_week`, which masks null `as_of_*` metadata. That means v1 does not currently emit `projection_freshness_metadata_missing` even though the raw projection rows have null `as_of_season` and `as_of_week`.

Decision: null `as_of_*` should remain a warning only for now, not a materialization blocker, because `created_at`, `model_run_id`, and weekly source freshness exist. The next tuning phase should preserve raw `as_of_*` fields separately or fill them from model run metadata.

## Draft Pick Treatment

The dry-run includes 13 draft pick rows for preview, but materialization policy excludes them:

| Metric | Value |
| --- | ---: |
| preview pick rows | 13 |
| materializable pick rows | 0 |
| excluded pick rows | 13 |

Decision: leave picks excluded until a separate lane exists. For UI, prefer either `score unavailable` with market-only context or a separate future `trade_pick_scores` object. Do not materialize draft picks into player score rows.

## Materialization Readiness Decision

V1 should not proceed to bounded staging materialization yet.

Classification: `V1 NEEDS MINOR TUNING FIRST`

Reasons:

- hard safety gates pass;
- the score shape is useful enough to keep developing;
- identity joins are mostly stable, but team context needs explicit warning metadata;
- role-source penalties are too broad and should not penalize rows that already have usable snap, target, rush, or role context;
- projection freshness metadata needs warning visibility restored;
- draft picks need to stay out of player materialization.

## Recommended Phase 27.4

Proposed tuning scope:

1. Add `team_context_mismatch_warning` when asset display team differs from history, truth, fantasy, projection, or Fraud Watch team, while preserving current-team context.
2. Normalize known team aliases such as `LA` and `LAR` before flagging a mismatch.
3. Change `role_source_gap` so `missing_snaps` and `missing_routes_proxy` from history flags are warning-only when alternate role fields exist.
4. Keep `missing_snaps_last_3` as a real penalty when no recent history, fantasy profile, or truth context exists.
5. Preserve raw projection `as_of_season` and `as_of_week` separately from fallback week values, then emit `projection_freshness_metadata_missing` when raw metadata is null.
6. Hide pick preview scores from the Trade Lab score panel, or label them score-unavailable until a separate pick lane exists.

Do not run a write path until that tuning is reviewed with another bounded dry-run.
