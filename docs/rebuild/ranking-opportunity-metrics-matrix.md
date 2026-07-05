# Ranking Opportunity Metrics Matrix

Phase 32.12 added an explicit opportunity and role metrics lane for ranking research. The lane is additive and does not change live Pigskin rankings, ranking champions, or formula/backtest tables.

## Source Availability

| Feature family | Source tables | 2014-2025 status | Implemented field |
| --- | --- | --- | --- |
| QB rushing leverage | `player_week_advanced_metrics`, `stg_player_week_stats` | Available from carries, carry share, red-zone carries, inside-five carries | `qb_rushing_leverage_index` |
| RB high-value opportunity | `player_week_advanced_metrics` | Available from red-zone touches, high-value touches, target share, opportunity share | `rb_high_value_opportunity_score` in the feature mart |
| WR dominance | `player_week_advanced_metrics` | Available from target share, air-yards share, WOPR, red-zone targets | `receiving_role_dominance_score` for WR rows |
| TE receiving role dominance | `player_week_advanced_metrics` | Available from target share, air-yards share, WOPR, red-zone targets, snap share proxy | `receiving_role_dominance_score` for TE rows |
| Red-zone usage | `player_week_advanced_metrics`, `stg_team_week_stats` | Available from red-zone targets, carries, touches, and team red-zone rates | `red_zone_usage_score` |
| Goal-line usage | `player_week_advanced_metrics` | Available from inside-ten and inside-five carries | `goal_line_usage_score` |
| Team environment | `stg_team_week_stats` | Available from plays, EPA per play, neutral pass rate | `team_environment_score` |
| Ceiling and bust history | `analytics_player_fantasy_points_by_profile` | Available from PPR weekly point thresholds by position | `spike_week_rate_3yr`, `bust_week_rate_3yr`, `elite_week_rate_3yr` |
| True route share | `stg_participation_context` | Source flag exists, true route source is not consistently available | Missing flag only |
| First-read share | No approved source | Unavailable | Missing flag only |
| YPRR | No approved route source | Unavailable | Missing flag only |
| End-zone targets | No approved source field | Unavailable | Missing flag only |

## Warehouse Objects

`player_week_opportunity_metrics` is one row per:

- `opportunity_metric_version`
- `season`
- `week`
- `player_id_internal`
- `position`

Backfill result:

- Seasons: 2014-2025
- Rows: 70,356
- Season-weeks: 257
- Metric version: `opportunity_metrics_v0`

`ranking_backtest_feature_mart` now carries opportunity features for target seasons 2017-2025. Predictors still use historical source windows only. Target-season outcomes remain separate.

## Guardrails

- Blocked advanced metrics are not fabricated.
- Missing metrics remain flagged in `missing_flags_json`.
- Feature-mart enrichment does not write live rankings.
- Diagnostic tournament smoke is read-only and summary-only.
- No Python full result-row tournament path was used.
