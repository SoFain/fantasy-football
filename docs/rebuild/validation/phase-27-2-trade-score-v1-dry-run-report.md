# Phase 27.2 Trade Score V1 Dry-Run Report

## Final Decision

TRADE SCORE V1 DRY-RUN PASS WITH WARNINGS

V1 is implemented as a deterministic, version-routed path and the bounded 2025 week 18 dry-run completed without writing score rows. The hard safety gates passed. The model quality is materially better than v0 because elite assets are no longer crushed by the old confidence multiplier, confidence penalties are categorized, and risk is explained through `component_json.risk_breakdown`.

This is not an approval to materialize v1. Remaining warnings need owner review before a write phase.

## Scope

This phase changed only local code, tests, and this validation report. No deployment, production flag change, Cloud Run Job trigger, Scheduler job, ingestion, score materialization, LLM action, Pigskin prompt, scrape, Firebase artifact, authorization gate, or commit occurred.

## Files Changed

| File | Change |
| --- | --- |
| `src/trade_player_scores.py` | Added v1 model routing, formula, source stability score, categorized confidence penalties, risk breakdown output, and projection freshness warning support. |
| `tests/test_trade_player_scores.py` | Added v1 unit coverage for formula routing, confidence categories, generic flag grouping, position-aware penalties, and missing fraud context treatment. |
| `docs/rebuild/validation/phase-27-2-trade-score-v1-dry-run-report.md` | Added this dry-run evidence report. |

## Safety State

All checked gates were unset after implementation:

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
| `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending` | pass, no pending migrations |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run` | pass |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern trade_player_scores` | pass, 11 of 11 |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern compat_trade_player_scores` | pass, 2 of 2 |

The full test suite emits mocked pipeline and load logs from existing tests. No live ingestion was run by this phase.

## V1 Formula Summary

V1 keeps the same bounded component scale, but changes how the final score is assembled:

```text
base_value_score =
  0.35 * market_score
  + 0.25 * projection_score
  + 0.15 * recent_production_score
  + 0.10 * role_usage_score
  + 0.05 * positional_scarcity_score
  + 0.05 * efficiency_score
  + 0.05 * source_stability_score

trade_score = clamp(base_value_score + risk_adjustment, 0, 100)
```

The old v0 confidence multiplier is not applied to v1. `component_json.confidence_multiplier` remains `1.0` for compatibility and explainability.

## Source Stability

`source_stability_score` is bounded from 0 to 100 and uses low-weight source completeness signals:

| Signal | Weight |
| --- | ---: |
| stable identity present | 20 |
| model run present | 20 |
| projection context present | 20 |
| recent production or history present | 20 |
| market context present | 15 |
| no stale projection context | 5 |

Dry-run distribution:

| Metric | Value |
| --- | ---: |
| min | 40.00 |
| max | 100.00 |
| avg | 87.00 |
| stddev | 21.98 |

## Confidence Category Summary

V1 replaces the generic missing-flag count penalty with named penalty categories in `component_json.confidence_breakdown.penalty_categories`.

Dry-run category counts:

| Category | Rows |
| --- | ---: |
| `role_source_gap` | 100 |
| `generic_scoring_source_warning` | 71 |
| `position_specific_scoring_gap` | 71 |
| `missing_fraud_context_warning` | 45 |
| `sample_size_warning` | 30 |
| `fallback_used` | 29 |
| `recent_production_gap` | 29 |
| `core_value_gap` | 23 |
| `identity_blocker` | 13 |

Generic scoring flags such as 2-point conversion fields, return touchdowns, and grouped scoring flags collapse into a single warning category rather than stacking one full penalty per field.

## Risk Breakdown Summary

V1 stores explicit risk contribution detail under `component_json.risk_breakdown`:

| Field | Meaning |
| --- | --- |
| `fraud_risk_contribution` | Fraud Watch or Pigskin fraud source contribution, capped when uncorroborated. |
| `projection_risk_contribution` | Weak or missing projection context risk. |
| `role_fragility_contribution` | Role, route, snap, and fallback source fragility. |
| `identity_risk_contribution` | Missing or temporary identity risk. |
| `missing_source_unknown_risk_notes` | Notes where missing context is not treated as automatic high risk. |
| `risk_cap` | Maximum negative risk adjustment for the row context. |
| `risk_adjustment` | Final score impact. |

Dry-run risk adjustment distribution:

| Metric | Value |
| --- | ---: |
| min | -6.00 |
| max | 0.00 |
| avg | -2.75 |
| stddev | 1.30 |

Risk notes:

| Note | Rows |
| --- | ---: |
| `missing_fraud_context_treated_as_unknown_not_high_risk` | 45 |
| `fraud_only_risk_capped_without_corroboration` | 24 |

## Dry-Run Command

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

No `--write` flag was passed.

## V0 Versus V1 Comparison

Same bounded 2025 week 18 PPR redraft one-QB candidate universe:

| Metric | V0 dry-run | V1 dry-run |
| --- | ---: | ---: |
| source rows | 100 | 100 |
| score rows | 100 | 100 |
| materializable player rows | 77 | 77 |
| excluded rows | 23 | 23 |
| excluded pick rows | 13 | 13 |
| trade score min | 7.94 | 15.93 |
| trade score max | 60.07 | 88.93 |
| trade score avg | 33.78 | 51.55 |
| trade score stddev | 11.26 | 15.53 |
| confidence min | 28.66 | 46.86 |
| confidence max | 51.41 | 78.53 |
| confidence avg | 46.36 | 66.48 |
| confidence stddev | 4.83 | 9.95 |

Confidence buckets:

| Bucket | V0 | V1 |
| --- | ---: | ---: |
| `>=80` | 0 | 0 |
| `70-79` | 0 | 46 |
| `60-69` | 0 | 21 |
| `50-59` | 22 | 32 |
| `<50` | 78 | 1 |

Tier distribution:

| Tier | V0 | V1 |
| --- | ---: | ---: |
| elite | 0 | 1 |
| strong | 0 | 10 |
| starter | 1 | 15 |
| flex | 16 | 38 |
| depth | 41 | 31 |
| avoid | 42 | 5 |

V1 score spread is more usable. V0 clustered premium assets in low starter, flex, and depth bands because confidence was multiplied into the final score.

## Player Sanity Examples

Top v1 examples:

| Player | Pos | Team | Score | Confidence | Tier | Note |
| --- | --- | --- | ---: | ---: | --- | --- |
| Bijan Robinson | RB | ATL | 88.93 | 78.53 | elite | Premium market and source stability now survive confidence warnings. |
| Ja'Marr Chase | WR | CIN | 83.35 | 74.35 | strong | Correctly no longer flex-tier from generic scoring gaps. |
| Puka Nacua | WR | LAR | 82.96 | 68.72 | strong | Still carries Pigskin context warning, but not a hard score crush. |
| Jahmyr Gibbs | RB | DET | 81.91 | 78.53 | strong | Better absolute tier than v0. |
| Jaxon Smith-Njigba | WR | SEA | 79.88 | 75.53 | strong | Generic scoring flags do not push confidence below 60. |
| Brock Bowers | TE | LV | 67.01 | 69.23 | starter | TE appears in the top 25 without TE overpromotion. |
| Josh Allen | QB | BUF | 74.86 | 66.97 | strong | One-QB QB context no longer buries every elite QB. |

Remaining warnings:

| Player | V1 result | Warning |
| --- | --- | --- |
| `2026 Pick 1.01` | starter in dry-run preview | Draft picks remain excluded from materializable player rows. A separate pick score lane is still needed. |
| A.J. Brown | 57.11, team `NE` | Source identity or team context still needs review before relying on this row. |
| Malik Nabers | 63.92, confidence 46.86 | High market value with low confidence due recent history and fallback gaps. This is explainable but still a tuning candidate. |
| Marvin Harrison | 23.50, avoid | Low score appears driven by projection and recent source context. Needs source review before judging as true downside. |
| Chuba Hubbard | 15.93, avoid | Low score is plausible from current component mix. |

## Acceptance Gate Results

Hard gates:

| Gate | Result |
| --- | --- |
| scores are 0 to 100 | pass |
| no duplicate grain rows in dry-run rows | pass, 0 duplicates |
| no PICK rows in materializable player score set | pass, 0 materializable pick rows |
| no unresolved identity rows in materializable set | pass, 0 |
| every row has component, missing flags, and freshness JSON | pass, 0 missing required JSON rows |
| no score rows written | pass, `wrote=false` |
| production flags remain false or unset | pass |

Quality gates:

| Gate | Result |
| --- | --- |
| useful confidence spread | pass with warning, 46 rows at 70-79, 21 rows at 60-69, one row below 50 |
| complete source rows can reach confidence >= 70 | pass |
| top 25 includes plausible RB, WR, TE, and one-QB QB context | pass |
| bottom 25 avoids unexplained elite false negatives | pass with warning, Marvin Harrison needs source-context review |
| high market score >= 85 below trade_score < 45 | pass, none found |
| generic scoring flags do not individually drive confidence below 60 | pass |
| missing fraud context is not a hard blocker | pass |
| risk_breakdown explains full or near-full risk penalties | pass |

## Remaining Warnings

- V1 improves scoring shape, but the target source slice still contains identity and team context oddities. A.J. Brown showing team `NE` is the clearest example.
- Draft picks are scored for preview explainability, but excluded from materializable player rows. A dedicated pick lane remains needed.
- `role_source_gap` appears on every row, which suggests the route, snap, or role source contract still needs tightening before v1 should be treated as production quality.
- Some high-market rows still have low confidence from recent-history and fallback gaps. That is now visible instead of hidden inside a generic missing-flag count.
- Projection freshness warning support was added for v1, but projection metadata coverage should still be handled in a later source contract phase.

## Recommended Next Phase

Proceed to a v1 review or tuning phase before materialization. The next phase should focus on source context and calibration, not warehouse plumbing:

- verify identity and current team context for premium rows;
- separate the draft-pick scoring lane from player scoring;
- tune role-source penalties so missing role detail is not universal;
- decide whether v1 is good enough for a bounded staging materialization with `ALLOW_TRADE_SCORE_MATERIALIZATION=true` in a separate authorized phase.
