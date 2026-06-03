# AI vs Vibes Analytics Plan

## Product Intent

This dashboard is the analytical backbone for the AI vs Vibes fantasy football show.

The goal is not a generic fantasy chatbot. The goal is a debate engine that can:

- punish weak fantasy reasoning
- separate points from process
- expose touchdown chasing
- grade player takes against real usage
- arm the show with receipts before every segment
- criticize our own takes and public analyst takes with the same standard

## First Principle

Every strong answer needs a player truth table.

The AI should not reason directly from raw play-by-play every time. Raw data is the evidence base, but the show needs a derived weekly table that encodes fantasy meaning:

- opportunity
- usage stability
- target earning
- rushing role
- red zone role
- fantasy output
- expected regression
- injury drag
- recent trend
- final analytical verdict

## Current Foundation

The repo already has the right foundation:

- `src.pipeline` ingests NFL data into BigQuery.
- `weekly_metrics` provides player fantasy production, volume, EPA, target share, air yards share, and WOPR.
- `play_by_play` provides granular football context.
- `src.materialize` is the right place to build derived analytical tables.
- `app.py` already has a Gemini co-host that can query BigQuery.

The main gap is that the derived analytics layer is too thin.

## Immediate Build Order

1. Build `analytics_player_weekly_truth`.
2. Make the Gemini assistant default to that table.
3. Add show segment views on top of the truth table.
4. Add take grading after the truth table is stable.

## Player Truth Table

Primary table name:

`fantasy_football_brain.analytics_player_weekly_truth`

The table should produce one row per player, season, and week.

Core columns:

- identity: season, week, player_id, player_name, position, team, opponent_team
- production: fantasy_points, fantasy_points_ppr, touchdowns
- volume: targets, receptions, carries, attempts
- receiving role: target_share, air_yards_share, wopr
- efficiency: total_epa, yards_per_touch, fantasy_points_per_touch
- red zone: red_zone_targets, red_zone_carries, red_zone_touches
- trend: prior_week_ppr, ppr_delta, rolling_3_week_ppr, rolling_3_week_targets, rolling_3_week_carries
- flags: touchdown_dependent, empty_volume, target_earner, usage_warning, box_score_trap
- scores: opportunity_score, efficiency_score, analytical_grade
- verdict: concise criticism-ready classification

## Show Segments

Initial dashboard views should be:

- Player Autopsy: why a player smashed or failed
- Fraud Watch: players whose fantasy points are masking weak usage
- Waiver Wire Court: add/drop cases with evidence
- Start/Sit Trial: compare two players by role, floor, ceiling, and risk
- Talking Head Accountability: grade claims against data
- AI vs Vibes Pick Battle: compare our picks against the AI
- Buy/Sell/Panic Index: identify market overreaction

## Assistant Rules

The co-host should follow these rules:

- query data before giving analytical answers
- default to `analytics_player_weekly_truth`
- cite the exact metrics behind criticism
- call out box-score chasing
- call out stale rankings
- separate confidence from entertainment
- explain what would change its mind

## Next Milestone

Make `analytics_player_weekly_truth` trustworthy, then build the first show segment:

`Fraud Watch`

That segment is the best first proof of concept because it matches the show identity and forces the system to distinguish fantasy points from real role quality.
