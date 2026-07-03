# Phase 31.8 Ranking Integrity, Formula, and Scoring Profile Report

Final decision: **RANKING INTEGRITY AND SCORING PROFILE PLAN READY**

Date: 2026-07-03

Scope:
- Audit current Pigskin rankings after the Trey McBride identity fix.
- Confirm whether other players are missing because of the same Sleeper-to-GSIS identity class.
- Document the exact current ranking variables and formulas.
- Define the path for Standard, PPR, and GNG Keeper ranking profiles in Player Profiles.

Non-actions:
- No deployment.
- No materialization.
- No Pigskin chat prompt.
- No LLM-backed ranking generation.
- No live Sleeper API call.
- No Cloud Run Job or Scheduler trigger.
- No ranking formula champion selection.
- No ranking formula or backtest table writes.

## Ranking Integrity Audit

Current final ranking version: `pigskin-llm-20260703061257`

Current model run: `pigskin_rankings-2026-na-20260703T061304Z-f923f2f9`

Final active ranking counts:

| Position | Candidate count | Final-pool count | Final active count | Missing final-pool candidates | Missing high-score candidates |
| --- | ---: | ---: | ---: | ---: | ---: |
| QB | 128 | 45 | 45 | 0 | 0 |
| RB | 202 | 80 | 80 | 0 | 0 |
| WR | 393 | 100 | 100 | 0 | 0 |
| TE | 213 | 60 | 60 | 0 | 0 |

Trey McBride regression status:
- `player_id`: `00-0037744`
- `sleeper_player_id`: `8130`
- `current_team`: `ARI`
- `position`: `TE`
- final rank: `1`
- tier: `elite`
- status: active ranking row present
- result: fixed and still present after Phase 31.7.

No Trey-style final-pool omission was found in the current final rankings. Every candidate selected for the LLM final pool is present in `analytics_pigskin_rankings`.

## Identity-Risk Review Cases

The audit found candidates with identity or current-roster risk signals, but the important part is that the high-ranking final-pool examples are included, not omitted.

| Position | Example | Status |
| --- | --- | --- |
| QB | Jameis Winston, Josh Johnson | Included in final pool. Both carry backup-QB role warnings. |
| RB | James Conner | Included in final pool. Current-source review recommended because the row has only 3 recent weekly rows but a high candidate score. |
| TE | Albert Okwuegbunam, Shane Zylstra, Will Mallory, Ben Sims | Included in final pool. Mostly fragile-role or low-sample warnings, not missing-player defects. |

Top historical PPR players absent from current candidates:

| Position | Examples | Classification |
| --- | --- | --- |
| QB | M.Penix | Candidate rank 46, just below the QB final-pool cutoff of 45. Current depth warning present. |
| RB | K.Hunt | Not in current candidate board. Treat as current-source or active-roster eligibility review, not LLM omission. |
| WR | S.Diggs, D.Samuel, K.Allen | Not in current candidate board. Treat as current-source or active-roster eligibility review. |
| TE | D.Waller, Z.Ertz | Not in current candidate board. Treat as current-source or active-roster eligibility review. |

Conclusion: the current issue class is not another McBride-style final-pool omission. The remaining review targets are source-currentness and eligibility questions.

## Current Ranking Formula

The current production ranking path has two stages.

Stage 1: deterministic candidate board from `src/materialize.py`.

Source inputs:
- `sleeper_players_current`
- `player_identity_bridge`
- `player_rosters`
- `analytics_player_weekly_truth`

Eligibility and identity:
- Current Sleeper players are the root population.
- Supported positions are `QB`, `RB`, `WR`, and `TE`.
- Identity is resolved by Sleeper player ID through `player_identity_bridge`, direct GSIS ID match, or a fallback normalized-name plus position plus current-team match.
- `player_id` is selected from roster GSIS ID, Sleeper GSIS ID, bridge GSIS ID, bridge internal ID, or a `sleeper:` fallback.
- `metrics_player_id` is roster GSIS ID, Sleeper GSIS ID, or bridge GSIS ID.

Candidate features:
- `weekly_rows`
- `avg_ppr`
- `avg_opportunity`
- `avg_efficiency`
- `avg_total_epa`
- `season_total_epa`
- `avg_epa_per_opportunity`
- `avg_passing_epa`, `season_passing_epa`
- `avg_rushing_epa`, `season_rushing_epa`
- `avg_receiving_epa`, `season_receiving_epa`
- `avg_role_quality`
- `avg_role_fragility`
- `avg_grade`
- `avg_wopr`
- `avg_target_share`
- `avg_carry_share`
- `avg_player_run_opportunity_pct`
- `avg_player_pass_opportunity_pct`
- `total_ppr`
- `total_targets`
- `total_carries`
- `total_red_zone_touches`
- `total_touchdowns`
- multi-season WOPR, target-share, carry-share, PPR, and EPA history.

Current deterministic candidate formula:

```text
raw_ranking_score =
  0.55 * avg_grade
  + 0.15 * avg_opportunity
  + 0.10 * avg_efficiency
  + 0.10 * max(0, 100 - avg_role_fragility)
  + 0.10 * min(100, avg_ppr * 4)
```

Depth-chart penalty:

```text
QB depth_chart_order > 1: 18.0
QB depth_chart_order is null: 10.0
RB/WR/TE depth_chart_order > 5: 5.0
else: 0.0
```

Candidate ranking score:

```text
ranking_score = max(0, raw_ranking_score - depth_chart_penalty)
```

Candidate rank ordering:

```text
ORDER BY ranking_score DESC, avg_ppr DESC, player_name
```

Confidence score:

```text
confidence_score =
  min(100, max(0,
    35
    + weekly_rows * 2
    + 20 if avg_grade is present
    - 10 if avg_role_fragility >= 60
  ))
```

Tier rules:
- QB backup depth overrides to `backup or handcuff`.
- QB ranks 1 to 3: `elite QB1`.
- QB ranks 4 to 8: `QB1`.
- QB ranks 9 to 18: `QB2 or streamer`.
- Other QB: `bench or watchlist`.
- RB/WR/TE ranks 1 to 3: `elite`.
- RB/WR/TE ranks 4 to 8: `front-line starter`.
- RB/WR/TE ranks 9 to 16: `starter`.
- RB/WR/TE ranks 17 to 30: `flex or matchup`.
- Other RB/WR/TE: `deep or watchlist`.

Risk flags:
- missing recent weekly sample
- not current QB1 on own NFL depth chart
- not on a current Sleeper NFL team
- fragile role
- box-score support outruns role quality
- target profile is thin for price
- backfield share is thin for price

Stage 2: LLM adjudicated final ranking from `src/generate_pigskin_rankings.py`.

Position pool sizes:
- QB: 45
- RB: 80
- WR: 100
- TE: 60

Evidence fields passed into final adjudication:
- ID, name, team, Sleeper team, active flag, status, depth chart position, depth order
- candidate rank, candidate score, raw score, depth penalty
- PPR per game, grade, opportunity, efficiency
- EPA per opportunity, season EPA, split passing/rushing/receiving EPA
- role quality, role fragility
- WOPR and WOPR history
- target-share and target-share history
- carry-share and carry-share history
- PPR history
- risk flags

Hard final rules:
- Rank every listed candidate exactly once.
- Preserve each provided player ID.
- No gaps or ties.
- Current Sleeper role is a hard constraint.
- Backup QBs must not be ranked as normal QB1s.
- Penalize stale roster status, fragile role, bad EPA, unstable volume, and touchdown spikes.
- Do not invent facts outside the evidence.

Current write behavior:
- Final table: `analytics_pigskin_rankings`, `WRITE_TRUNCATE`.
- History table: `analytics_pigskin_rankings_history`, `WRITE_APPEND`.
- This means the current writer supports one active final board at a time. Multi-profile active rankings need a profile-aware write path before Player Profiles can safely show multiple scoring-profile boards.

## Draft Formula Candidate Tables

The Phase 31 ranking formula candidate tables are separate from the current production ranking generation path.

Current seeded formula status:
- `ranking_formula_candidates`: seeded draft candidates.
- `ranking_formula_sets`: seeded draft formula set.
- `ranking_backtest_runs`, `ranking_backtest_results`, and `ranking_backtest_candidate_summaries`: backtest scaffolding.
- `ranking_formula_champions`: no champion should be selected yet.

Write gate:
- `ALLOW_RANKING_FORMULA_BACKTEST_WRITE=true` is required for ranking formula writes.
- Trade score materialization gates do not authorize ranking formula writes.

Seeded draft formula families:

| Position | Candidate | Formula |
| --- | --- | --- |
| QB | Balanced Baseline | `recent_points_avg 0.30`, `passing_epa_per_play 0.25`, `passing_success_rate 0.20`, `cpoe 0.10`, `pigskin_context_score 0.15` |
| QB | Volume Opportunity | `recent_points_avg 0.25`, `dropbacks 0.30`, `rushing_attempts 0.15`, `usage_volume 0.15`, `pigskin_context_score 0.15` |
| QB | Efficiency Upside | `passing_epa_per_play 0.35`, `passing_success_rate 0.25`, `cpoe 0.20`, `team_epa_per_play 0.10`, `pigskin_context_score 0.10` |
| RB | Balanced Baseline | `recent_points_avg 0.30`, `usage_volume 0.25`, `rush_success_rate 0.15`, `receiving_usage 0.15`, `pigskin_context_score 0.15` |
| RB | Volume Opportunity | `carries 0.30`, `targets 0.20`, `goal_line_opportunities 0.20`, `usage_volume 0.20`, `pigskin_context_score 0.10` |
| RB | Efficiency Upside | `rush_success_rate 0.30`, `receiving_usage 0.20`, `epa_per_play 0.20`, `success_rate 0.15`, `pigskin_context_score 0.15` |
| WR | Balanced Baseline | `recent_points_avg 0.30`, `targets 0.25`, `air_yards 0.15`, `receiving_epa 0.15`, `pigskin_context_score 0.15` |
| WR | Volume Opportunity | `targets 0.35`, `air_yards 0.25`, `red_zone_targets 0.15`, `usage_volume 0.15`, `pigskin_context_score 0.10` |
| WR | Efficiency Upside | `receiving_epa 0.30`, `receiving_yards 0.20`, `epa_per_play 0.20`, `success_rate 0.15`, `pigskin_context_score 0.15` |
| TE | Balanced Baseline | `recent_points_avg 0.30`, `targets 0.25`, `receiving_yards 0.15`, `team_pass_rate 0.15`, `pigskin_context_score 0.15` |
| TE | Volume Opportunity | `targets 0.35`, `red_zone_targets 0.20`, `air_yards 0.15`, `usage_volume 0.15`, `pigskin_context_score 0.15` |
| TE | Efficiency Upside | `receiving_epa 0.30`, `receiving_yards 0.20`, `team_pass_rate 0.15`, `epa_per_play 0.15`, `pigskin_context_score 0.20` |

All seeded formulas use:
- `score_expression`: `weighted_linear`
- `normalization`: `position_percentile`
- target: `top_12_position`
- status: `draft`

Blocked metric status:
- No seeded formula requires route share, YPRR, first-read share, true pressure, contact yards, or alignment.
- The validation catalog includes `ranking_formula_candidates_blocked_metrics_guard`.

## Scoring Profile Support

Current `scoring_profiles` rows:
- `standard`, active, 0.0 reception points.
- `half_ppr`, active, 0.5 reception points.
- `ppr`, active, 1.0 reception points.

Current code support:
- `src/fantasy_scoring.py` supports Standard, Half PPR, and PPR local defaults.
- Basic Sleeper keys are mapped: `pass_yd`, `pass_td`, `pass_int`, `pass_2pt`, `rush_yd`, `rush_td`, `rush_2pt`, `rec`, `rec_yd`, `rec_td`, `rec_2pt`, `fum_lost`, `st_td`.
- Bonus, kicker, DST, and unmapped settings are preserved structurally but are not fully applied to current Player Profiles ranking generation.

Missing GNG source file:
- `keeper-sleeper-scoring-report-2026.md` was not present in the repo.
- No live Sleeper API call was made in this phase.
- GNG Keeper settings in this report are therefore based only on the Phase 31.8 prompt-supplied source fields, not a live league fetch.

GNG Keeper support assessment:
- The existing `scoring_profiles` table can store a first `gng_keeper` profile through `scoring_json`.
- No migration is strictly required for a first dropdown implementation if metadata can live inside `scoring_json`.
- A later additive migration would be useful if the owner wants first-class columns for `source`, `source_league_id`, `supported_positions`, or `notes`.

Critical blocker for multi-profile rankings:
- `src/materialize.py` hardcodes the candidate board as `PPR`.
- `src/generate_pigskin_rankings.py` hardcodes the prompt as `official 2026 PPR`.
- `analytics_pigskin_rankings` is overwritten with `WRITE_TRUNCATE`.
- `app.py` reads active rankings without filtering by `scoring_profile_id`.

So the dropdown is not just a UI control. The ranking generation and final active table need profile-aware behavior first.

## Player Profiles Dropdown Plan

Recommended dropdown options:
- `PPR`
- `Standard`
- `GNG Keeper`

Do not show `Half PPR` in the first requested dropdown unless the owner wants it. The data exists, but the explicit ask is Standard, PPR, and GNG Keeper.

Implementation sequence:

1. Seed or verify `gng_keeper` in `scoring_profiles`.
2. Extend ranking candidate materialization to accept `scoring_profile_id`.
3. Source fantasy points from `analytics_player_fantasy_points_by_profile` or calculate profile-aware points through `src/fantasy_scoring.py`.
4. Replace hardcoded PPR labels in the candidate board and final prompt.
5. Replace `WRITE_TRUNCATE` active-table behavior with a profile-aware upsert or delete-insert for one profile slice.
6. Add validation that each active ranking profile has complete QB/RB/WR/TE counts.
7. Add Player Profiles dropdown state.
8. Filter `fetch_pigskin_rankings_data()` by selected `scoring_profile_id`.
9. Display the selected profile in the ranking card and ranking freshness copy.
10. Fail clearly if a selected profile has no ranking board. Do not silently fall back to PPR.

GNG Keeper scoring details to preserve:
- Standard fantasy positions should use the league's player scoring settings.
- TE premium fields must be retained if present.
- Bonus keys should remain visible, even if not applied in v0 ranking math.
- Kicker and defense settings should be stored but should not affect QB/RB/WR/TE ranking formulas.

## Safety Checks

Commands run:

```powershell
.\venv\Scripts\python.exe scripts\check_deployment_safety.py
.\venv\Scripts\python.exe -m compileall -q src scripts
.\venv\Scripts\python.exe -m unittest tests.test_pigskin_rankings_materialize_identity tests.test_pigskin_rankings_model_runs tests.test_ranking_formula_backtests
.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run
```

Results:
- Safety checker passed.
- `src` and `scripts` compile passed.
- Focused ranking tests passed: 34 tests.
- Pending migrations: none.
- Validation discovery passed: 209 validation files discovered.

## Warnings

- `keeper-sleeper-scoring-report-2026.md` is not present in the repo, so GNG Keeper values need an owner-supplied source file or explicit approved JSON before implementation.
- Current ranking generation is PPR-specific despite accepting `--scoring-profile-id` metadata.
- Active final ranking writes use `WRITE_TRUNCATE`, which is not safe for multiple simultaneous scoring-profile boards.
- James Conner should get a small source-currentness review because he appears as an active final-pool RB with a strong score but only 3 recent weekly rows.
- K.Hunt, S.Diggs, D.Samuel, K.Allen, D.Waller, and Z.Ertz are not candidate-board bugs until current Sleeper/source status is verified.

## Blockers

None for this audit/report phase.

Implementation blockers before Player Profiles dropdown:
- Generate or seed the `gng_keeper` profile.
- Make ranking candidate generation profile-aware.
- Make final ranking writes profile-aware.
- Add app filtering by selected `scoring_profile_id`.

## Recommended Phase 31.9 Work

Recommended next phase: **Player Profiles scoring-profile dropdown implementation plan and non-mutating tests**.

Specific work:
- Add `gng_keeper` profile seed input from an owner-approved source.
- Add profile-aware candidate materialization dry-run tests.
- Add profile-aware active ranking write design, but do not run LLM generation yet.
- Add Player Profiles dropdown UI behind a safe default path.
- Add tests proving PPR remains the default and no silent fallback occurs for missing profile boards.
