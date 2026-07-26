# Phase 33.33 - RB STD GPT 5.5 v1.0 Standard RB Formula Test

## Final Decision

`RB STD GPT 5.5 v1.0 BLOCKED BY MISSING METRICS`

The required metric audit failed the prompt's stop condition. The current warehouse has zero source-backed RB rows for receiving YAC above expectation in every leakage-safe source window for target seasons 2023, 2024, and 2025. The direct NGS receiving source contains WR and TE rows only for the audited seasons. The formula reference explicitly requires `avg_yac_above_expectation` and forbids replacing it with raw YAC without owner approval.

No formula was calculated. No backtest or top-25 board was generated. Current Pigskin remains the Standard RB baseline by default, not because it won a Phase 33.33 comparison.

## Files Changed

- `docs/rebuild/validation/phase-33-33-rb-std-gpt-5-5-v1-formula-test-report.md`
- `docs/rebuild/rb-std-gpt-5-5-v1-top25-board.md`
- `docs/rebuild/ranking-algorithm-scorecard.md`
- `docs/rebuild/bqml-v2-ranking-architecture.md`
- `docs/rebuild/ranking-opportunity-metrics-matrix.md`
- `docs/rebuild/advanced-bqml-v2-owner-review-boards.md`

No Python, SQL, migration, model, ranking, or application file changed.

## Git State

The worktree was already dirty before Phase 33.33. Existing modified, staged, and untracked Phase 33 files were preserved. This phase did not stage or commit files.

## Formula Reference Review

Reviewed `D:\So Fain\Downloads\RB STD GPT 5.5 v1.0 Scoring Formula.pdf`, 9 pages. The PDF agrees with the prompt:

- projected role value is the base;
- efficiency is a small multiplier;
- availability is always applied;
- subjective rankings are excluded;
- receiving YAC above expectation is preferred over raw YAC;
- team environment should be omitted when team RB xFP pools already drive the base, to avoid double counting.

The PDF was rendered and visually checked. It does not authorize a raw-YAC substitute.

## Leakage-Safe Audit Windows

| Target season | Source seasons |
|---|---|
| 2023 | 2020-2022 |
| 2024 | 2021-2023 |
| 2025 | 2022-2024 |

All BigQuery checks were read-only. No 2026 outcomes were queried or used.

## Metric Availability Audit

Coverage is shown in target-season order: 2023 / 2024 / 2025.

| Formula input | Source table and column | Coverage | Missingness | Leakage-safe | Decision |
|---|---|---:|---:|---|---|
| Rushing xFP | `raw_ffopportunity_weekly.rush_fantasy_points_exp` | 4,533/4,533; 4,516/4,516; 4,450/4,450 player-weeks | 0%; 0%; 0% | Yes | Approved source input |
| Receiving xFP | `raw_ffopportunity_weekly.rec_fantasy_points_exp` | 4,533/4,533; 4,516/4,516; 4,450/4,450 | 0%; 0%; 0% | Yes | Available, but source scoring semantics need explicit Standard adjustment documentation |
| Projected receptions input | `player_season_advanced_metrics.receptions` | 603/603; 596/596; 575/575 player-seasons | 0%; 0%; 0% | Yes | Available for a leakage-safe projection |
| Team RB rushing xFP pool | `raw_ffopportunity_weekly.rush_fantasy_points_exp_team` | 4,533/4,533; 4,516/4,516; 4,450/4,450 | 0%; 0%; 0% | Yes | Available |
| Team RB receiving xFP pool | `raw_ffopportunity_weekly.rec_fantasy_points_exp_team` | 4,533/4,533; 4,516/4,516; 4,450/4,450 | 0%; 0%; 0% | Yes | Available |
| Player rushing xFP share | Player xFP divided by team xFP, or `player_week_pbp_opportunity_metrics.rushing_xfp_share` | Direct ratio inputs 100%; persisted PBP share 89.8%; 91.0%; 92.0% | 0% when derived from direct xFP inputs | Yes | Approved derivation |
| Player receiving xFP share | Player xFP divided by team xFP, or `player_week_pbp_opportunity_metrics.receiving_xfp_share` | Direct ratio inputs 100%; persisted PBP share 78.7%; 78.6%; 77.3% | 0% when derived from direct xFP inputs | Yes | Approved derivation |
| Offensive snap share | `player_season_advanced_metrics.offensive_snap_share` | 603/603; 596/596; 575/575 | 0%; 0%; 0% | Yes | Approved |
| High-value opportunity share | `player_season_advanced_metrics.weighted_opportunity_standard`, plus team aggregation | 603/603; 596/596; 575/575 base values | 0%; 0%; 0% | Yes | Derivable; share is not persisted directly |
| Red-zone opportunity share | `player_season_advanced_metrics.red_zone_opportunities`, plus team aggregation | 603/603; 596/596; 575/575 | 0%; 0%; 0% | Yes | Approved derivation |
| Goal-line opportunity share | `player_season_advanced_metrics.goal_line_opportunities`, plus team aggregation | 603/603; 596/596; 575/575 | 0%; 0%; 0% | Yes | Approved derivation |
| Rush yards over expected per attempt | `player_season_advanced_metrics.ngs_rush_yards_over_expected_per_att` | 319/603; 305/596; 295/575 | 47.1%; 48.8%; 48.7% | Yes where present | Partial coverage warning |
| NGS rushing efficiency | `player_season_advanced_metrics.ngs_rushing_efficiency` | 319/603; 305/596; 295/575 | 47.1%; 48.8%; 48.7% | Yes where present | Partial coverage warning; lower is better |
| NGS box resilience | `player_season_advanced_metrics.ngs_box_count_rate` | 319/603; 305/596; 295/575 | 47.1%; 48.8%; 48.7% | Yes where present | Partial coverage warning |
| RB receiving YAC above expectation | `player_season_advanced_metrics.ngs_yac_above_expectation` | 0/603; 0/596; 0/575 | 100%; 100%; 100% | No usable rows | **Blocked core metric** |
| Direct NGS RB receiving source | `raw_nflverse_ngs_receiving.avg_yac_above_expectation` | 0 RB rows for 2020-2024 | 100% | N/A | Source lane contains WR and TE only |
| Team RB xFP per game | Team aggregation of `raw_ffopportunity_weekly` xFP | Direct xFP inputs 100% | 0% before aggregation | Yes | Available, but redundant with team-pool base |
| Team red-zone RB xFP | `player_week_pbp_opportunity_metrics.red_zone_rush_xfp` | 4,070/4,533; 4,110/4,516; 4,094/4,450 | 10.2%; 9.0%; 8.0% | Yes | Partial; skip team multiplier in v1 to avoid double counting |
| Team goal-line RB xFP | `player_week_pbp_opportunity_metrics.goal_line_rush_xfp` | 4,070/4,533; 4,110/4,516; 4,094/4,450 | 10.2%; 9.0%; 8.0% | Yes | Partial; skip team multiplier in v1 |
| Team play volume | `stg_team_week_stats.plays` | 1,676/1,676; 1,708/1,708; 1,708/1,708 team-weeks | 0%; 0%; 0% | Yes | Available |
| Age or birth date | `dim_players_current.birth_date`, joined by GSIS ID | 231/234; 229/232; 224/226 RB identities | 1.3%; 1.3%; 0.9% | Stable attribute; derive age as of target season | Approved with small identity warning |
| Games with offensive snaps | `player_week_advanced_metrics.offensive_snaps` | 4,757/4,761; 4,793/4,793; 4,808/4,808 player-weeks non-null | 0.08%; 0%; 0% | Yes | Approved; count rows with snaps greater than zero |
| Historical availability factor | Derived from prior-season games with offensive snaps | Inputs above | At most 0.08% source-row missingness | Yes | Approved derivation |
| Fumbles lost | `analytics_player_fantasy_points_by_profile.source_stat_json.fumbles_lost` | 1,459/1,459; 1,511/1,511; 1,587/1,587; 1,487/1,487; 1,524/1,524 for source seasons 2020-2024 | 0% by source season | Yes | Available |
| Opportunities for fumble rate | `player_week_advanced_metrics.carries`, `targets`, or `opportunities` | Source-backed historical rows available | Requires cross-source identity join | Yes | Derivable; implementation still needed |

## Stop Decision

The phase stopped before formula construction and backtesting because `Receiving_YAC_Above_Expectation_Modifier` cannot be calculated for RBs. This blocks the required `Efficiency_Multiplier` exactly as specified.

The following actions were intentionally not taken:

- raw YAC was not substituted;
- the YAC component was not dropped and weights were not redistributed;
- missing values were not zero-filled;
- Current Pigskin was not used as a formula input;
- the prior episode formula was not rerun;
- no 2023, 2024, or 2025 top-25 board was produced.

## Formula Implementation Status

No executable formula implementation was added. The exact proposed formula remains:

```text
Final_RB_Standard_Points =
(
  Base_RB_Standard_xFP
  * Role_Stability_Multiplier
  * Efficiency_Multiplier
  * Availability_Multiplier
)
- Fumble_Lost_Penalty
```

The no-team-multiplier form is the correct first variant because the preferred base uses projected team RB xFP pools. The exact variant with a separate team multiplier was not tested because it would risk double counting and the phase had already hit a core stop condition.

## Backtest And Player Reports

| Required output | Status |
|---|---|
| 2023 backtest | Not run: core metric blocker |
| 2024 backtest | Not run: core metric blocker |
| 2025 backtest | Not run: core metric blocker |
| Current Pigskin comparison | Not run |
| Prior episode formula comparison | Not run |
| Top-25 RBs by season | Not generated |
| Player-level explanation table | Not generated |

There is no evidence from Phase 33.33 that RB STD GPT 5.5 v1.0 beats Pigskin. It is not episode-ready or owner-review ready. Current Pigskin still holds for Standard RB.

## Excluded Metrics

- Raw YAC: excluded because the prompt and PDF require YAC above expectation.
- YPRR, TPRR, true route share, first-read share: blocked route metrics.
- Broken tackles: no approved source was established.
- `pigskin_context_score`: explicitly prohibited.
- Market data and subjective rankings: comparison context only, never formula input or training target.
- Sleeper current context: excluded from historical features.

## Checks

| Check | Result |
|---|---|
| `.\venv\Scripts\python.exe -m unittest tests.test_bqml_v2_feature_contract` | PASS, 26 tests |
| `.\venv\Scripts\python.exe -m py_compile src\bqml_v2_feature_contract.py` | PASS |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | PASS, all checks true |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run` | PASS, 251 validation files discovered |
| Focused metric availability query | PASS, `rb_yac_oe_nonnull=0`; stop condition confirmed |
| Focused leakage query | PASS, `leaked_row_count=0` for Standard RB targets 2023-2025 |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern route_metrics` | PASS, 2 validations passed |
| `git diff --check` | PASS with preexisting LF-to-CRLF warnings on four tracked research docs |

The focused formula check was the fail-closed stop assertion. No score computation was allowed after the required efficiency input returned zero coverage.

## No-Live-Change Confirmation

- No live ranking writes.
- No champion activation.
- No model training.
- No deployment.
- No Gemini or Pigskin chat calls.
- No Sleeper API calls.
- No 2026 outcomes used.
- No BigQuery mutations.

## Warnings

- NGS rushing efficiency, RYOE per attempt, and box-context coverage is only about 51-53% across the tested source windows. A future exact formula needs an explicit missing-data policy even after the RB receiving YAC lane is fixed.
- ffopportunity receiving xFP scoring semantics must be documented before subtracting projected receptions for Standard.
- The formula PDF was supplied outside the repository and was reviewed locally; it was not copied into the repo.

## Recommended Next Phase

`Phase 33.34 - build missing RB receiving YAC-above-expectation metric lane`

The next phase should determine whether nflverse NGS receiving can provide RB rows from a different source or whether the formula must be owner-revised. Do not substitute raw YAC without explicit owner approval.
