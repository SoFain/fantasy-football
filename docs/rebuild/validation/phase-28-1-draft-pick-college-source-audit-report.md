# Phase 28.1 Draft Pick And College Source Audit Report

Generated: 2026-06-27

## Final Decision

DRAFT PICK AND COLLEGE SOURCE AUDIT READY WITH WARNINGS

## Scope Confirmation

This phase was read-only source audit and design only. No production deploy, staging deploy, BigQuery write, migration creation, migration apply, score materialization, ingestion, Cloud Run Job trigger, Scheduler job, LLM-backed action, Pigskin prompt, Data Ops local-control click, scrape, Firebase artifact, commit, or authorization-gate change occurred.

Authorization gates were checked before the audit and were unset:

| Gate | State |
| --- | --- |
| `ALLOW_TRADE_SCORE_MATERIALIZATION` | unset |
| `ALLOW_PROJECTION_CONTEXT_REFRESH` | unset |
| `ALLOW_LIMITED_PRODUCTION_DEPLOY` | unset |
| `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST` | unset |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` | unset |

## Local Checks

| Check | Result |
| --- | --- |
| `scripts/check_deployment_safety.py` | PASS |
| `py_compile app.py` | PASS |
| `py_compile src\trade_player_scores.py` | PASS |
| `compileall -q src scripts` | PASS |
| `run_bigquery_validations.py --dry-run` | PASS, 160 validations discovered |

No test, validation, or inspection command wrote warehouse data.

## Source And Object Inventory

Dataset audited: `fantasy-football-498121.fantasy_football_brain`.

| Object | Type | Row count | Audit use |
| --- | --- | ---: | --- |
| `compat_trade_assets_current` | view | n/a | Safe current trade asset view. Contains pick assets. |
| `mart_trade_assets_current` | base table | 1,383 | Curated trade asset source behind the compatibility view. |
| `market_consensus_player_values` | base table | 461 | Current market value input. |
| `market_consensus_baseline_current` | base table | 461 | Market baseline input. |
| `draft_picks` | base table | 257 | Raw/source NFL draft pick table. Useful for draft identity and loose historical priors, not UI-safe directly. |
| `college_player_stats` | base table | 11,046 | Raw/source CFBD college stat rows. Not UI-safe directly. |
| `rookie_scouting_metrics` | base table | 4 | Manual scouting/source rows. Not UI-safe directly. |
| `player_identity_bridge` | base table | 11,212 | NFL identity bridge. Strong for NFL players, weak for college-only identities. |
| `dim_players_current` | base table | 11,212 | Current player dimension. |
| `player_rosters` | base table | 25,040 | Source table with player college/draft metadata. |
| `player_contracts` | base table | 51,629 | Source table with player contract, college, and draft metadata. |
| `trade_player_scores` | base table | 154 | Existing player score table. Contains v0 and v1 player score rows. |
| `trade_player_scores_current` | view | n/a | Current player score view. |
| `compat_trade_player_scores_current` | view | n/a | UI-safe current player score compatibility view. |

Repo classification docs confirm `draft_picks`, `college_player_stats`, and `rookie_scouting_metrics` are source or staging objects and should not be exposed directly to Pigskin or Streamlit score UI. The requested `docs/source/classification` path was not present; the active classification records are `docs/rebuild/current-warehouse-inventory.md` and `docs/rebuild/table-classification.md`.

## Existing Trade Score Boundary

Trade Score v1 is staging-quality for player rows only. Phase 27.11 states that draft picks need a separate score lane before pick assets can receive comparable scores. Current code enforces that boundary:

- `src/trade_player_scores.py` adds `draft_pick_asset` and `draft_pick_score_lane_pending` for `position = 'PICK'`.
- `materialization_exclusion_reasons()` excludes pick rows with `pick_row` and `draft_pick_score_lane_pending`.
- `tests/test_trade_player_scores.py` covers pick exclusion, unavailable UI reason, and materialization policy counts.
- Phase 27.5R materialized 77 player rows and excluded 13 pick rows from the v1 target slice.

The correct next move is a pick-specific lane. Do not force picks through `trade_player_scores` as fake players.

## Draft-Pick Asset Audit

Current pick assets are available in `compat_trade_assets_current`.

| Metric | Value |
| --- | ---: |
| `position = 'PICK'` rows | 192 |
| distinct pick labels | 64 |
| scoring contexts | 3, `ppr`, `half_ppr`, `standard` |
| exact-slot rows | 144 |
| exact-slot labels | 48 |
| round-only rows | 48 |
| round-only labels | 16 |
| min market value | 774 |
| max market value | 7,084 |
| average market value | 1,681.98 |
| source freshness present | 192 |
| missing flags present | 192 |

Pick asset values currently repeat across the three scoring profiles. That is acceptable for a first market-led pick score, but the UI should label the pick lane as pick-market based until scoring-specific pick adjustments exist.

Top PPR pick examples:

| Label | Source key | Market value | Risk-adjusted value |
| --- | --- | ---: | ---: |
| `2026 Pick 1.01` | `fantasycalc:2026pick101:PICK:UNK` | 7,084 | 6,729.80 |
| `2026 Pick 1.02` | `fantasycalc:2026pick102:PICK:UNK` | 4,233 | 4,021.35 |
| `2026 Pick 1.03` | `fantasycalc:2026pick103:PICK:UNK` | 3,751 | 3,563.45 |
| `2026 Pick 1.04` | `fantasycalc:2026pick104:PICK:UNK` | 3,574 | 3,395.30 |
| `2026 Pick 1.05` | `fantasycalc:2026pick105:PICK:UNK` | 3,376 | 3,207.20 |
| `2026 1st` | `fantasycalc:20261st:PICK:UNK` | 3,073 | 2,919.35 |
| `2027 1st` | `fantasycalc:20271st:PICK:UNK` | 2,843 | 2,700.85 |
| `2028 1st` | `fantasycalc:20281st:PICK:UNK` | 2,085 | 1,980.75 |

## Pick Parsing Findings

Pick parsing is feasible with deterministic labels and source keys.

Supported label classes:

| Pick class | Rows | Labels | Market min | Market max | Market avg |
| --- | ---: | ---: | ---: | ---: | ---: |
| exact slot, such as `2026 Pick 1.01` | 144 | 48 | 774 | 7,084 | 1,765.31 |
| round only, such as `2026 1st` | 48 | 16 | 780 | 3,073 | 1,432.00 |

Parsing rule:

- Use `position = 'PICK'` as the primary classifier.
- Treat `:PICK:` in `source_player_key` as a secondary classifier.
- Do not use display-name substring matching alone. Player names such as George Pickens and Kenny Pickett create false positives.
- Parse exact slots with `^(20[0-9]{2}) Pick ([0-9]+)\.([0-9]+)$`.
- Parse round-only picks with `^(20[0-9]{2}) ([1-7])(st|nd|rd|th)$`.

Round-only picks should carry lower confidence than exact-slot picks because the actual slot distribution is unresolved.

## Draft-Pick Table Audit

`draft_picks` exists and is populated, but it should be treated as a source table.

| Metric | Value |
| --- | ---: |
| rows | 257 |
| distinct player names | 257 |
| season min | 2025 |
| season max | 2025 |
| rows with `gsis_id` | 256 |
| rows matched to `player_identity_bridge` by `gsis_id` | 254 |
| rows with unmatched non-null `gsis_id` | 2 |
| rows with `cfb_player_id` | 249 |

The table is useful for:

- pick/player identity after an NFL draft;
- draft capital features by round and overall pick;
- later college-to-NFL identity bridging through `cfb_player_id`.

It is not enough by itself to calibrate long-term pick value. It only covers 2025 in the current warehouse, and 2025 outcomes are immature for dynasty-style pick value. Do not use 2025 `w_av`, games, or outcome stats as a hard fantasy pick value curve.

## College-Stat Table Audit

`college_player_stats` has broad row coverage but thin identity and source metadata.

| Metric | Value |
| --- | ---: |
| rows | 11,046 |
| distinct player names | 7,863 |
| season min | 2024 |
| season max | 2025 |
| null `games` rows | 11,046 |

Position coverage:

| Season | Position | Rows | Distinct names |
| ---: | --- | ---: | ---: |
| 2025 | WR | 3,919 | 3,901 |
| 2025 | QB | 1,071 | 1,071 |
| 2025 | RB | 677 | 677 |
| 2024 | WR | 3,764 | 3,746 |
| 2024 | QB | 1,021 | 1,020 |
| 2024 | RB | 594 | 594 |

Current schema fields:

- identity/context: `season`, `player_name`, `position`, `team`, `conference`;
- volume/production: `games`, `passing_yards`, `passing_tds`, `rushing_yards`, `rushing_tds`, `receptions`, `receiving_yards`, `receiving_tds`.

Warnings:

- `games` is null for every row, so per-game normalization is not safe from this table alone.
- No TE rows appeared in the audited `college_player_stats` position distribution.
- The table does not include `cfb_player_id`, source fetch timestamp, source provider, source stat category, or confidence/provenance fields.
- `src/ingest_college_data.py` supports a `mock` mode. Any production scoring path must distinguish real CFBD rows from mock/test rows before using this table.
- The ingest script deletes an existing season before append. That is outside this phase, but future source refreshes need the same explicit write gate discipline used elsewhere.

## Rookie Scouting Table Audit

`rookie_scouting_metrics` is useful as manual scouting context, but coverage is tiny.

| Metric | Value |
| --- | ---: |
| rows | 4 |
| distinct players | 4 |
| season min | 2024 |
| season max | 2024 |

Covered positions:

| Season | Position | Rows |
| ---: | --- | ---: |
| 2024 | RB | 1 |
| 2024 | TE | 1 |
| 2024 | WR | 2 |

The table includes useful traits such as yards after contact per attempt, yards per route run, target share, catch radius grade, success rates, average separation, and `data_source`. It should be optional context only until there is a real operator-maintained coverage process.

## College-To-NFL Identity Join Findings

Read-only join diagnostics:

| Join | Source rows | Any match | Unambiguous | Ambiguous | No match |
| --- | ---: | ---: | ---: | ---: | ---: |
| `college_player_stats` to `player_identity_bridge` by normalized name and position | 11,046 | 425 | 425 | 0 | 10,621 |
| `rookie_scouting_metrics` to `player_identity_bridge` by normalized name and position | 4 | 3 | 3 | 0 | 1 |
| `draft_picks` to `player_identity_bridge` by `gsis_id` | 257 | 254 | n/a | n/a | 3 total unmatched or missing |
| `college_player_stats` to `draft_picks` by normalized name and position | 11,046 | 33 | 33 | 0 | 11,013 |

Interpretation:

- NFL draft rows have strong identity coverage once a player exists in NFL identity sources.
- College stat rows do not have enough reliable identity coverage for direct scoring.
- Name and position joins are too sparse to support public pick or rookie scores without a college identity bridge.
- `cfb_player_id` exists in `draft_picks`, but not in `college_player_stats`. Adding or materializing that bridge is the highest-value source contract improvement.

## Can College Stats Support Pick Scoring?

Not as a required input for the first pick score lane.

Current college stats can provide optional class-strength context later, but they cannot safely score generic picks now because:

- current pick assets represent future abstract picks, not known college players;
- exact future pick labels such as `2026 Pick 1.01` do not map to a player before the draft;
- college identity joins are weak;
- `college_player_stats` has no `cfb_player_id`;
- `games` is entirely null, which blocks clean per-game normalization;
- no TE rows exist in the current college stat table;
- `draft_picks` only has 2025 rows, so it cannot produce a stable historical pick-value curve.

The first pick score should be market-led and pick-structure-led. College context should be a neutral component with a visible missing flag until a pick becomes a known player or class-strength features are contracted.

## Can College Stats Support Rookie Or Future-Player Scoring?

Partially.

College stats can support rookie/future-player scoring only after identity hardening. The best near-term shape is a curated `rookie_player_context` or similar intermediate mart that resolves:

- `player_id_internal`;
- `gsis_id` when available;
- `cfb_player_id` when available;
- normalized college name;
- position;
- draft year, round, and overall pick;
- college production summary;
- scouting metrics summary;
- source freshness;
- missing flags;
- identity join method and confidence.

Until that exists, college stats should remain warning-level context. They should not drive a public score.

## Formula Proposal

Proposed first lane: `trade_pick_score_v0`.

Grain:

one row per `model_version`, `pick_year`, `pick_class`, `pick_round`, `pick_slot`, `source_pick_key`, `scoring_profile_id`, `league_type_id`, and `roster_format_id`.

Score range: `0` to `100`.

Recommended components:

| Component | Weight | Input | Notes |
| --- | ---: | --- | --- |
| market score | 0.50 | `market_value` or `risk_adjusted_trade_value` from `compat_trade_assets_current` | Normalize within pick assets for the same scoring, league, and roster context. |
| slot capital score | 0.20 | parsed round and slot | Exact slots get direct slot curve. Round-only picks get round midpoint or range baseline. |
| time discount score | 0.15 | pick year relative to current league year | Nearer picks score higher. Future years get explicit discount. |
| liquidity/certainty score | 0.10 | exact slot vs round-only, source freshness, missing flags | Exact-slot and fresh market context score higher. |
| college or class context score | 0.05 | future optional class-strength or mapped rookie context | Start neutral at 50 with `college_context_unavailable` until a safe mart exists. |

Suggested score:

```text
pick_score =
  0.50 * market_score
  + 0.20 * slot_capital_score
  + 0.15 * time_discount_score
  + 0.10 * liquidity_certainty_score
  + 0.05 * college_context_score
  + risk_adjustment
```

Suggested risk adjustment:

- exact-slot pick: `0` to `-2`;
- round-only pick: `-4` to `-8`;
- stale or missing market freshness: up to `-10`;
- unparsed label or missing year/round: blocker for score row, not a low score.

Do not use `projected_3_year_value` for picks in v0 unless a pick-specific projection source is created. It is not present on `compat_trade_assets_current`.

## Confidence Proposal

Confidence should be separate from score value.

Suggested starting confidence:

| Case | Starting confidence |
| --- | ---: |
| exact-slot pick with parsed year, round, slot, market value, freshness, and source key | 88 |
| round-only pick with parsed year and round | 74 |
| future-year pick beyond the next draft year | 66 to 72 |
| pick with missing freshness or missing flags | subtract 5 to 15 |
| pick with unparsed label | no score row |

Suggested confidence flags:

- `pick_round_only_uncertainty`;
- `pick_future_year_discount`;
- `pick_market_source_only`;
- `college_context_unavailable`;
- `draft_outcome_prior_insufficient`;
- `pick_label_unparsed`;
- `pick_source_key_missing`;
- `pick_market_freshness_missing`;
- `pick_score_staging_only`.

## Warehouse Contract Proposal

No migrations were created in this phase. Proposed objects for the next implementation phase:

- `trade_pick_scores`;
- `trade_pick_scores_current`;
- `compat_trade_pick_scores_current`.

Proposed `trade_pick_scores` fields:

| Field | Purpose |
| --- | --- |
| `model_version` | Pick score model version, such as `trade_pick_score_v0_2026_001`. |
| `score_run_id` | Deterministic run identifier. |
| `source_pick_key` | Existing pick source key, such as `fantasycalc:2026pick101:PICK:UNK`. |
| `pick_label` | Display label from market source. |
| `pick_year` | Parsed pick year. |
| `pick_class` | `exact_slot` or `round_only`. |
| `pick_round` | Parsed draft round. |
| `pick_slot` | Parsed slot within round when available. |
| `estimated_overall_pick` | Derived for exact-slot picks. Nullable for round-only. |
| `scoring_profile_id` | Context. |
| `league_type_id` | Context. |
| `roster_format_id` | Context. |
| `current_market_value` | Market input. |
| `risk_adjusted_trade_value` | Existing adjusted market proxy. |
| `market_score` | Normalized market component. |
| `slot_capital_score` | Parsed slot/round component. |
| `time_discount_score` | Pick year discount component. |
| `liquidity_certainty_score` | Exactness and source quality component. |
| `college_context_score` | Neutral in v0 unless a safe class/rookie context exists. |
| `confidence_score` | Separate confidence. |
| `pick_score` | Final 0 to 100 score. |
| `score_tier` | UI tier label. |
| `source_freshness_json` | Source freshness. |
| `missing_flags_json` | Missing or warning flags. |
| `component_json` | Full explainability payload. |
| `created_by` | Builder identifier. |
| `created_at` | Load timestamp. |

The compatibility view must read only from curated pick score and market/pick marts. It must not expose `draft_picks`, `college_player_stats`, or `rookie_scouting_metrics` directly.

## UI Behavior Proposal

When score flags are enabled in staging:

- Player score cards continue to use `compat_trade_player_scores_current`.
- Pick assets use `compat_trade_pick_scores_current` if present.
- If no pick score row exists, show the existing market summary plus a clear message: `draft pick score lane pending`.
- Label pick scores as `Pick Score`, not `Pigskin Trade Score`, until product decides whether player and pick scores should share one label.
- Show pick score components: market value, draft slot or round, time discount, confidence, missing flags, and source freshness.
- Keep market totals separate from score totals.
- Do not show college-player context for generic future picks.
- For round-only picks, show the range/uncertainty explicitly.

Production remains default-off until a separate production rollout is approved.

## Validation Proposal

Add validation files in a future implementation phase:

- `trade_pick_scores` object exists;
- `trade_pick_scores` grain uniqueness;
- `pick_score` range 0 to 100;
- component ranges 0 to 100;
- confidence range 0 to 100;
- parsed pick year, round, and class present;
- exact-slot rows have slot and estimated overall pick;
- round-only rows do not pretend to have exact slots;
- source freshness JSON present;
- missing flags JSON present;
- no duplicate current rows;
- compatibility view exists;
- compatibility view has no raw/source dependencies on `draft_picks`, `college_player_stats`, or `rookie_scouting_metrics`;
- no `PICK` rows materialized into `trade_player_scores`;
- identity coverage validation for any future rookie/college context mart;
- warning threshold for unparsed pick labels.

## Implementation Phases

Recommended next phases:

1. Phase 28.2: Add pick parser and dry-run builder tests. No migrations or writes.
2. Phase 28.3: Add additive BigQuery contracts and validations for `trade_pick_scores` and current compatibility views. Do not apply without authorization.
3. Phase 28.4: Implement bounded dry-run pick score builder using `compat_trade_assets_current`.
4. Phase 28.5: Apply migration and materialize a small staging-only pick score run only after explicit authorization.
5. Phase 28.6: Wire staging UI to show pick scores when staging flags are enabled, preserving current unavailable behavior when disabled.
6. Phase 28.7: Design a college identity bridge or rookie context mart before using college stats in public scores.

## Blockers

No blocker prevents starting a market-led draft-pick score lane.

Blockers for college-driven rookie/future-player scoring:

- no durable `cfb_player_id` on `college_player_stats`;
- weak direct college-to-NFL identity coverage;
- `games` null across `college_player_stats`;
- no TE coverage in `college_player_stats`;
- `rookie_scouting_metrics` has only 4 rows;
- no source provenance fields on `college_player_stats`;
- no mature historical draft-outcome table beyond 2025.

## Warnings

- Pick score v0 should be labeled market-led and staging-only until it has product review.
- Round-only picks have material uncertainty and should carry lower confidence.
- Current market pick values are not scoring-profile differentiated.
- Current `draft_picks` outcomes are too recent to calibrate long-term fantasy value.
- College source tables are not UI-safe directly.
- Future college ingest work must keep source writes behind explicit gates.
- Historical Phase 17 through Phase 27 validation backlog remains untracked by owner decision.

## Recommended Next Phase

Proceed to Phase 28.2: implement a read-only pick parser and pick score dry-run planner with tests. Keep college stats out of the first required scoring formula, except as neutral and visibly missing optional context.
