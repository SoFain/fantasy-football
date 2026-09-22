# Phase 27.1 Trade Score Quality Audit Report

## Final Decision

TRADE SCORE V1 PLAN READY WITH WARNINGS

The v0 score layer is structurally safe and validated, but it is not production-ready trade advice. The main blocker is quality, not warehouse safety: every materialized v0 row is below the confidence threshold, and the confidence model is too sensitive to generic missing flags that do not carry equal meaning by position or source.

## Scope

This phase was read-only analysis and design. No score rows were written. No `--write` command was run. No deployment, production flag change, Cloud Run Job trigger, Scheduler creation, ingestion, score materialization, LLM action, Pigskin prompt, scrape, Firebase artifact creation, authorization gate, or commit occurred.

## Safety State

Authorization gates were checked first:

| Gate | State |
| --- | --- |
| ALLOW_TRADE_SCORE_MATERIALIZATION | unset |
| ALLOW_PROJECTION_CONTEXT_REFRESH | unset |
| ALLOW_LIMITED_PRODUCTION_DEPLOY | unset |
| ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST | unset |
| DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER | unset |

## Local Checks

| Check | Result |
| --- | --- |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | pass |
| `.\venv\Scripts\python.exe -m py_compile app.py` | pass |
| `.\venv\Scripts\python.exe -m compileall -q src scripts` | pass |
| `.\venv\Scripts\python.exe -m unittest discover tests` | pass, 352 tests |
| `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending` | pass, no pending migrations |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run` | pass |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern trade_player_scores` | pass, 11 of 11 |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern compat_trade_player_scores` | pass, 2 of 2 |

Safety checker passed no-Firebase, no tracked secret files, no secret content, default-off feature flags, Pigskin SQL safety, and compile checks.

## Target Slice

| Field | Value |
| --- | --- |
| model_version | `trade_score_v0_2025_001` |
| season | `2025` |
| week | `18` |
| scoring_profile_id | `ppr` |
| league_type_id | `redraft` |
| roster_format_id | `one_qb` |

## Current v0 Quality Summary

| Metric | Value |
| --- | ---: |
| `trade_player_scores` target rows | 77 |
| `compat_trade_player_scores_current` target rows | 77 |
| duplicate grain rows | 0 |
| trade score min | 7.9352 |
| trade score max | 60.0659 |
| trade score avg | 33.2663 |
| trade score stddev | 11.9112 |
| confidence min | 28.66 |
| confidence max | 51.41 |
| confidence avg | 46.3644 |
| confidence stddev | 4.8333 |
| confidence >= 70 | 0 |
| confidence 60 to 69 | 0 |
| confidence 50 to 59 | 22 |
| confidence 40 to 49 | 48 |
| confidence < 40 | 7 |

Score tiers:

| Tier | Rows |
| --- | ---: |
| avoid | 34 |
| depth | 30 |
| flex | 12 |
| starter | 1 |

Position distribution:

| Position | Rows |
| --- | ---: |
| WR | 30 |
| RB | 26 |
| QB | 13 |
| TE | 8 |

Source object coverage for the target slice:

| Source | Rows or status |
| --- | ---: |
| compat_trade_assets_current | 1383 |
| compat_trade_player_history, 2025 week 18 | 3201 |
| analytics_player_weekly_truth, 2025 week 18 | 1067 |
| analytics_player_fantasy_points_by_profile, 2025 week 18 PPR | 1067 |
| analytics_fraud_watch, 2025 week 18 | 57 |
| projection_rankings_current, 2025 week 18 PPR redraft one-QB | 600 |

Projection rows exist for the target week, and all 77 score rows have a `model_run_id`. The projection table has `as_of_season` and `as_of_week` columns, but the current rows for the target had null `as_of_*` values. That should become a v1 freshness warning or source contract fix.

## Component Distribution

| Component | Min | Max | Avg | Stddev |
| --- | ---: | ---: | ---: | ---: |
| market_score | 1.39 | 98.61 | 52.1183 | 28.3880 |
| projection_score | 1.39 | 96.15 | 44.4295 | 25.8167 |
| recent_production_score | 1.85 | 98.15 | 49.2208 | 27.7867 |
| role_usage_score | 14.31 | 82.18 | 50.1144 | 14.1979 |
| positional_scarcity_score | 85.60 | 100.00 | 98.9195 | 3.2262 |
| efficiency_score | 37.96 | 100.00 | 67.3827 | 15.0746 |
| fraud_score | 0.00 | 100.00 | 50.2597 | 38.4125 |
| normalized_risk_score | 0.4957 | 1.0000 | 0.7866 | 0.1714 |

The strongest structural issue is not component range. The ranges pass. The issue is interpretation: `positional_scarcity_score` is compressed near the top, `normalized_risk_score` is high for most rows, and the confidence multiplier suppresses every final score.

## Confidence Root Cause Analysis

The code path in `src/trade_player_scores.py` does this:

- starts confidence at `92.0`;
- blends in projection confidence if present;
- blends in Pigskin asset confidence if present;
- subtracts `8.0` when sample size is below 2;
- subtracts `4.0` per unique missing flag, capped at `35.0`;
- computes final confidence from the reduced value;
- uses `confidence_score / 100`, clamped from `0.70` to `1.00`, as the final score multiplier.

Fresh query results:

| Confidence field | Min | Max | Avg |
| --- | ---: | ---: | ---: |
| starting_confidence | 92.00 | 92.00 | 92.00 |
| missing_flag_count | 4.00 | 11.00 | 9.0260 |
| missing_flag_penalty | 16.00 | 35.00 | 33.6753 |
| sample_size | 0.00 | 5.00 | 3.9740 |
| sample_size_penalty | 0.00 | 8.00 | 0.7273 |
| final confidence_score | 28.66 | 51.41 | 46.3644 |

The missing-flag penalty is the dominant reason confidence is low. Most rows are at or near the `35.0` cap.

Top missing flags:

| Flag | Rows | v1 treatment |
| --- | ---: | --- |
| missing_fumbles_lost | 71 | Position-specific warning, not a full confidence penalty for every position |
| missing_interceptions | 71 | Position-specific, mostly QB relevant |
| missing_passing_2pt_conversions | 71 | Explainability warning only unless scoring settings need it |
| missing_receiving_2pt_conversions | 71 | Explainability warning only |
| missing_return_tds | 71 | Explainability warning only |
| missing_routes_proxy | 71 | Position-specific WR/TE role warning |
| missing_rushing_2pt_conversions | 71 | Explainability warning only |
| missing_snaps | 71 | Source coverage warning, not a repeated per-row hard penalty when alternate role fields exist |
| scoring_missing_data_flags_present | 71 | Collapse into one scoring-source warning |
| missing_fraud_context | 22 | Keep as missing-data flag, reduce confidence only when risk component depends on fraud |
| missing_snaps_last_3 | 9 | Position and role-specific warning |
| efficiency_fallback_used | 6 | Low weight, explainability warning |
| missing_recent_trade_history | 6 | Keep as real source gap |
| role_usage_fallback_used | 6 | Keep as real source gap |
| missing_pigskin_ranking_context | 4 | Source-specific warning |
| missing_snap_share | 3 | Role-source warning |

### Penalty Classification

| Penalty class | v0 behavior | v1 recommendation |
| --- | --- | --- |
| Real missing source data | Penalized like all other flags | Keep penalty for missing market, projection, recent history, model run, unresolved identity |
| Stale or incomplete projection context | Blocks materialization if stale, but `as_of_*` null is not separately punished | Require projection freshness metadata or emit a source freshness warning |
| Identity instability | Penalized when source key is used or missing identity appears | Keep as-is for unresolved identity, reduce only after stable identity join is proven |
| Missing scoring fields | Each scoring flag counts separately | Collapse to one source-level scoring warning unless the field is position-critical |
| Missing snaps/routes fields | Counts like other flags | Make position-specific and reduce when role alternatives exist |
| Missing fraud context | Counts as generic missing flag | Keep as warning; do not reduce confidence heavily unless fraud component is used for that row |
| Missing recent trade history | Counts as generic missing flag | Keep penalty, but separate from market-value confidence |
| Temporary name join identity | Current policy can clear it with stable projection join | Keep as-is |
| Sample-size penalty | `8.0` below 2 samples | Keep, but make it source-specific and position-aware |
| Generic missing flag count | `4.0` per flag, cap `35.0` | Replace with weighted categories and caps per category |

## Component And Weight Audit

v0 formula:

```text
base_score =
  0.40 * market_score
  + 0.20 * projection_score
  + 0.15 * recent_production_score
  + 0.10 * role_usage_score
  + 0.10 * positional_scarcity_score
  + 0.05 * efficiency_score

risk_adjustment = -10 * normalized_risk_score

trade_score = clamp((base_score + risk_adjustment) * confidence_multiplier, 0, 100)
```

Findings:

- Market weight is defensible for v0, but the final confidence multiplier is so low that high market rows are suppressed into flex or depth territory.
- Projection and recent production are heavily week-sensitive. Week 18 creates skew for elite players whose current-week production, rank, or usage context is not representative of trade value.
- Risk is double counted. Missing flags increase `normalized_risk_score` by up to `0.25`, and the same flags reduce confidence by up to `35.0`.
- Fraud risk is too blunt. Several elite rows have `fraud_score = 100`, which forces `normalized_risk_score = 1.0` and a full `-10` adjustment.
- Positional scarcity is almost maxed for everyone. The average is `98.9195`, so it adds points without meaningful separation.
- The one-QB context correctly prevents all QBs from dominating, but elite QBs are probably too suppressed when fraud and week-specific projection signals are poor.
- Draft picks are correctly excluded from player materialization. v1 still needs a separate pick lane.

## Player Sanity Checks

| Player | v0 result | Audit classification | Reason |
| --- | --- | --- | --- |
| Bijan Robinson | 60.0659, starter, confidence 50.53 | plausible rank, too low absolute | Top row is reasonable, but low confidence caps an elite asset |
| Ja'Marr Chase | 55.7722, flex, confidence 49.35 | too low | Elite WR should not be flex-tier unless risk and data warning is explicit |
| Justin Jefferson | 42.4340, depth, confidence 50.53 | too low | High market score but weak recent and projection signals appear week-skewed |
| Amon-Ra St. Brown | 51.6068, flex, fraud 100 | too low | Full risk penalty suppresses a premium asset |
| Puka Nacua | 54.3830, flex, fraud 100 | too low but explained | Strong market and production, full risk penalty and low confidence |
| Josh Allen | 49.2100, flex, fraud 100 | too low for elite QB | One-QB discount is fine, full fraud risk is too punitive |
| Jalen Hurts | 18.4702, avoid | too low or data gap | Elite QB appears crushed by week/projection/risk context |
| Jayden Daniels | 22.9821, avoid, confidence 30.04 | too low or data gap | Projection and recent scores are extremely low for likely market profile |
| Brock Bowers | 43.8011, depth | too low | High market TE suppressed by recent production and fraud risk |
| Malik Nabers | 44.3408, depth | unclear due to data gap | Missing recent history, role fallback, efficiency fallback |
| Marvin Harrison | 14.5610, avoid | likely too low, data gap | Very low projection and recent production suggest week/context skew |
| Ashton Jeanty | 49.2474, flex | plausible with warning | Rookie/future asset needs a dedicated lane |
| Christian McCaffrey | 51.2452, flex | plausible with warning | Age/risk may justify suppression, but confidence remains low |
| Chuba Hubbard | 7.9352, avoid | plausible | Low market, low projection, low recent production |
| Kyle Pitts | 25.0302, avoid | plausible but risk-heavy | Recent production helps, fraud risk and low market suppress it |
| A.J. Brown | 35.4137, depth, fraud 100 | needs identity/team review | Team/source context should be verified before relying on score |

## Source Gap Findings

The current source state is good enough for dry-run and staging review, but not enough for production advice.

Key gaps:

- Generic scoring missing-data flags appear on 71 of 77 rows and dominate confidence.
- Fraud context is present for many rows but covers only 57 rows in `analytics_fraud_watch` for the target slice, while 22 score rows still carry `missing_fraud_context`.
- Projection rows exist for 2025 week 18, but `as_of_season` and `as_of_week` were null in the current projection rows. v1 needs reliable freshness metadata.
- Recent history exists broadly, but 6 rows still have missing recent trade history.
- Snap and route coverage should be treated by position and source. The current all-row penalty overstates the problem.
- Week 18 is a poor sole evaluation week for trade advice because playing time, injuries, benching, playoff rest, and end-of-season context can distort recent production.

## v1 Recommendations

### Formula Changes

Keep the component family, but split value and confidence more cleanly:

```text
base_value_score =
  market_weight * market_score
  + projection_weight * projection_score
  + production_weight * recent_production_score
  + role_weight * role_usage_score
  + scarcity_weight * positional_scarcity_score
  + efficiency_weight * efficiency_score

risk_adjustment = position_specific_risk_cap(normalized_risk_score, risk_sources)

trade_score = clamp(base_value_score + risk_adjustment, 0, 100)

display_confidence = confidence_score
```

Do not multiply the final score by confidence in v1. Confidence should be displayed prominently and used for UI warnings, filtering, and acceptance gates. It should not automatically crush every elite player score. If a multiplier is retained, cap its downside at `0.85` for rows with market, projection, identity, and recent production present.

### Suggested v1 Weights

For `redraft`:

| Component | v0 | v1 recommendation |
| --- | ---: | ---: |
| market_score | 0.40 | 0.35 |
| projection_score | 0.20 | 0.25 |
| recent_production_score | 0.15 | 0.15 |
| role_usage_score | 0.10 | 0.10 |
| positional_scarcity_score | 0.10 | 0.05 |
| efficiency_score | 0.05 | 0.05 |
| stability or source confidence component | none | 0.05, optional, not a harsh multiplier |

For `dynasty` or keeper contexts, create a separate profile later. Do not force dynasty/future value into the redraft v1 model.

### Confidence Changes

Replace the single missing flag count with weighted categories:

| Category | Example flags | v1 penalty |
| --- | --- | --- |
| Identity blocker | missing player id, unresolved identity | 25 to 40 or block materialization |
| Core value gap | missing market value, missing projection context, missing model run | 12 to 25 |
| Recent production gap | missing recent history | 8 to 12 |
| Role source gap | missing snaps/routes when no target/rush/share alternatives exist | 4 to 10 |
| Position-specific scoring field | interceptions for QB, routes for WR/TE | 2 to 6 |
| Generic scoring field | 2-point conversions, return TDs, broad scoring flags | warning only or 1 grouped penalty |
| Missing fraud context | missing_fraud_context | warning only unless risk model depends on it |
| Fallback used | role or efficiency fallback | 2 to 6 based on component weight |

Specific changes:

- Collapse `scoring_missing_data_flags_present` and its child scoring flags into one grouped warning.
- Do not count non-applicable fields against every position.
- Keep missing flags visible in `missing_flags_json`.
- Add `confidence_breakdown.penalty_categories`.
- Add `confidence_grade`, such as `high`, `usable`, `review`, and `low`.
- Gate production on confidence distribution and explanation quality, not on a blind threshold alone.

Expected impact on the current 77 rows: confidence should gain roughly 20 to 30 points for rows whose only major issue is generic scoring flags. That estimate comes from replacing an average missing-flag penalty of `33.6753` with a smaller grouped penalty. Exact impact requires a v1 dry-run.

### Risk Adjustment Changes

- Remove generic missing flag count from `normalized_risk_score`.
- Keep risk tied to explicit risk sources: fraud, projection risk, injury, volatility, role fragility.
- Cap fraud-only risk impact unless corroborated by projection risk or role fragility.
- Treat `missing_fraud_context` as unknown risk, not low confidence and not high risk.
- Store `risk_breakdown` in `component_json`.
- Consider a smaller max adjustment in one-QB redraft, such as `-6` unless severe risk is supported.

### Positional Rules

- Rebuild positional scarcity from replacement gap by roster format.
- In `one_qb`, QB scarcity should rarely push a player above elite RB or WR assets.
- TE scarcity should help true difference-makers, but it should not make every TE near-max scarcity.
- Role and scoring fields should be position-specific:
  - QB: attempts, dropbacks, rushing role, interceptions, sacks if available.
  - RB: carries, targets, snap share, goal-line or red-zone role.
  - WR and TE: target share, routes, air yards or route proxy, red-zone role.

### Rookie And Future-Asset Handling

- Create a rookie or future-asset lane for players with strong market value but sparse production.
- Do not punish rookies the same way as veterans for missing recent production.
- Use market rank, projection rank, draft capital if available from curated objects, and source freshness.
- Keep v1 player table free of `PICK` rows.

### Pick Lane Recommendation

Draft picks should stay out of `trade_player_scores`.

Recommended separate object:

```text
trade_pick_scores
compat_trade_pick_scores_current
```

Pick lane inputs should include class year, round, expected slot, league format, historical pick hit rates, and market value. Do not overload `position = PICK` inside player scores.

### Source Coverage Requirements

Before v1 materialization:

- projection rows for target week must include useful freshness metadata;
- market source must have stable identity keys;
- fraud coverage should either reach a set threshold or be treated as optional context;
- role usage needs a clear fallback hierarchy by position;
- current-season source rows should be refreshed for a non-skewed target week, or Week 18 should be explicitly labeled as staging-only.

## v1 Acceptance Gates

Hard gates:

- score rows remain 0 to 100;
- no duplicate grain rows;
- no `PICK` rows in `trade_player_scores`;
- no unresolved identity rows in materialized player scores;
- every row has `component_json`, `missing_flags_json`, and `source_freshness_json`;
- compatibility view has no raw/source table dependency;
- production feature flags remain false;
- staging rollout happens before production consideration.

Quality gates:

- confidence distribution has useful spread;
- at least 25 percent of rows with market, projection, identity, and recent production present should reach confidence 70 or higher;
- no high-market row with `market_score >= 85` should fall below `trade_score < 45` unless `component_json` shows a true risk or source explanation;
- top 25 by score should include obvious elite assets across RB, WR, TE, and one-QB QB context;
- bottom 25 should not contain obvious elite false negatives without an explicit data gap;
- generic scoring flags should not individually drive confidence below 60;
- missing fraud context should not be a hard quality blocker by itself;
- `risk_breakdown` must explain every full or near-full risk penalty;
- source freshness must show projection model run and target week context.

Review gates:

- v1 dry-run must compare old v0 and new v1 side by side for the same 77 rows;
- v1 report must include changed ranks for top market assets;
- v1 must be browser QAed in staging only;
- production score flags stay false until a separate approval phase.

## Recommended Next Phase

Recommended next phase:

```text
Phase 27.2: Implement Trade Analyzer score v1 dry-run only
```

Scope for 27.2:

- add `model_version=trade_score_v1_2025_001`;
- keep all writes disabled by default;
- add weighted confidence categories;
- remove generic missing flag double counting from risk;
- add `risk_breakdown` and `confidence_breakdown.penalty_categories`;
- add tests for confidence category weights and position-specific penalties;
- run bounded dry-run for 2025 week 18 only;
- compare v0 and v1 output without writing rows.

Production remains out of scope for v1 until dry-run, materialization, validation, and staging UI review pass separately.
