# Phase 28.2 Draft Pick Parser And Dry-Run Report

Generated: 2026-06-27

## Final Decision

DRAFT PICK PARSER AND DRY-RUN READY WITH WARNINGS

## Scope Confirmation

This phase implemented local parser and dry-run planner code only. No migration, BigQuery table creation, BigQuery write, score materialization, production deploy, staging deploy, production feature flag change, Trade Analyzer production flag enablement, Cloud Run Job trigger, Scheduler job, ingestion, LLM-backed action, Pigskin prompt, scrape, external fetch, Firebase artifact, commit, or authorization-gate change occurred.

Authorization gates were checked before work and were unset:

| Gate | State |
| --- | --- |
| `ALLOW_TRADE_SCORE_MATERIALIZATION` | unset |
| `ALLOW_PROJECTION_CONTEXT_REFRESH` | unset |
| `ALLOW_LIMITED_PRODUCTION_DEPLOY` | unset |
| `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST` | unset |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` | unset |

## Files Changed

| File | Change |
| --- | --- |
| `src/trade_pick_scores.py` | New read-only draft-pick parser, scorer, BigQuery dry-run reader, summary builder, and CLI. |
| `tests/test_trade_pick_scores.py` | New parser, scoring, dry-run, no-write, false-positive, and component JSON tests. |
| `docs/rebuild/validation/phase-28-2-draft-pick-parser-and-dry-run-report.md` | This report. |

## Parser Behavior

Pick classification is intentionally strict:

- accepts rows with `position = 'PICK'`;
- accepts rows whose `source_player_key` contains `:PICK:`;
- does not classify rows by display-name substring alone.

False positives covered by tests:

- `George Pickens`;
- `Kenny Pickett`.

Supported labels:

| Label shape | Example | Parsed output |
| --- | --- | --- |
| exact slot | `2026 Pick 1.01` | `pick_year=2026`, `pick_class=exact_slot`, `pick_round=1`, `pick_slot=1`, `estimated_overall_pick=1`, `pick_bucket=exact`, `parse_confidence=high` |
| exact later slot | `2026 Pick 1.12` | `pick_round=1`, `pick_slot=12`, `estimated_overall_pick=12` |
| round only | `2026 1st` | `pick_year=2026`, `pick_class=round_only`, `pick_round=1`, `pick_slot=null`, `estimated_overall_pick=null`, `pick_bucket=round_only`, `parse_confidence=medium` |
| round only future | `2027 2nd` | `pick_year=2027`, `pick_class=round_only`, `pick_round=2` |

Malformed labels do not create score candidates. They are reported with `pick_label_unparsed`.

## Formula Implementation

Implemented model version target: `trade_pick_score_v0_2026_001`.

Formula:

```text
pick_score =
  0.50 * market_score
  + 0.20 * slot_capital_score
  + 0.15 * time_discount_score
  + 0.10 * liquidity_certainty_score
  + 0.05 * college_context_score
  + risk_adjustment
```

Rules implemented:

- every component score is clamped to `0` through `100`;
- final `pick_score` is clamped to `0` through `100`;
- market score uses min/max normalization inside the same scoring profile, league type, and roster format;
- college context is neutral at `50`;
- `college_context_unavailable` is always present for v0;
- no `college_player_stats` table is read;
- no `draft_picks` outcome fields are used;
- no `projected_3_year_value` is used.

Score tier naming:

| Threshold | Tier |
| ---: | --- |
| `>= 88` | `elite` |
| `>= 74` | `premium` |
| `>= 60` | `solid` |
| `>= 45` | `speculative` |
| `>= 30` | `deep` |
| otherwise | `avoid` |

I used neutral pick labels instead of player-specific `starter` or `flex`.

## Confidence Behavior

Confidence is separate from `pick_score`.

Rules implemented:

- exact-slot starts at `88`;
- round-only starts at `74`;
- future classes lose `4` confidence points per year beyond the nearest available pick year, capped at `12`;
- missing source key, missing market value, and missing market freshness reduce confidence;
- unparsed labels receive no score row.

Warning flags implemented:

- `pick_round_only_uncertainty`;
- `pick_future_year_discount`;
- `pick_market_source_only`;
- `college_context_unavailable`;
- `draft_outcome_prior_insufficient`;
- `pick_label_unparsed`;
- `pick_source_key_missing`;
- `pick_market_freshness_missing`;
- `pick_score_staging_only`.

The dry-run also preserves existing asset missing flags from `compat_trade_assets_current`.

## Dry-Run Commands

All-context dry-run:

```powershell
.\venv\Scripts\python.exe -m src.trade_pick_scores --model-version trade_pick_score_v0_2026_001 --dry-run
```

PPR dry-run:

```powershell
.\venv\Scripts\python.exe -m src.trade_pick_scores --model-version trade_pick_score_v0_2026_001 --scoring-profile-id ppr --dry-run
```

No write command was run. The `--write` path fails closed with:

```text
write mode is not implemented in Phase 28.2
```

## Dry-Run Metrics

All contexts:

| Metric | Value |
| --- | ---: |
| source pick asset rows | 192 |
| parsed pick rows | 192 |
| unparsed pick rows | 0 |
| exact-slot rows | 144 |
| round-only rows | 48 |
| score min | 18.0143 |
| score max | 96.7000 |
| score avg | 43.6848 |
| score stddev | 13.8831 |
| confidence min | 62.0000 |
| confidence max | 88.0000 |
| confidence avg | 83.0000 |
| confidence stddev | 8.9443 |

Rows by scoring profile:

| Scoring profile | Rows |
| --- | ---: |
| `half_ppr` | 64 |
| `ppr` | 64 |
| `standard` | 64 |

Rows by pick year:

| Pick year | Rows |
| ---: | ---: |
| 2026 | 156 |
| 2027 | 12 |
| 2028 | 12 |
| 2029 | 12 |

Tier distribution:

| Tier | Rows |
| --- | ---: |
| `elite` | 3 |
| `solid` | 21 |
| `speculative` | 48 |
| `deep` | 96 |
| `avoid` | 24 |

PPR-only:

| Metric | Value |
| --- | ---: |
| source pick asset rows | 64 |
| parsed pick rows | 64 |
| unparsed pick rows | 0 |
| exact-slot rows | 48 |
| round-only rows | 16 |
| score min | 18.0143 |
| score max | 96.7000 |
| score avg | 43.6848 |
| score stddev | 13.8831 |
| confidence min | 62.0000 |
| confidence max | 88.0000 |
| confidence avg | 83.0000 |
| confidence stddev | 8.9443 |

PPR rows by pick year:

| Pick year | Rows |
| ---: | ---: |
| 2026 | 52 |
| 2027 | 4 |
| 2028 | 4 |
| 2029 | 4 |

PPR tier distribution:

| Tier | Rows |
| --- | ---: |
| `elite` | 1 |
| `solid` | 7 |
| `speculative` | 16 |
| `deep` | 32 |
| `avoid` | 8 |

## Warning Flag Counts

PPR warning flags:

| Flag | Count |
| --- | ---: |
| `college_context_unavailable` | 64 |
| `draft_outcome_prior_insufficient` | 64 |
| `missing_age` | 64 |
| `missing_fraud_context` | 64 |
| `missing_gsis_id` | 64 |
| `missing_pigskin_ranking_context` | 64 |
| `missing_player_id_internal` | 64 |
| `missing_recent_trade_history` | 64 |
| `missing_sleeper_player_id` | 64 |
| `pick_future_year_discount` | 12 |
| `pick_market_source_only` | 64 |
| `pick_round_only_uncertainty` | 16 |
| `pick_score_staging_only` | 64 |

The inherited player-centric missing flags are expected for pick assets in the current trade asset view. Future pick-specific contracts should replace those with pick-native missing flags.

## PPR Top 25

| Rank | Pick | Class | Market | Score | Confidence | Tier |
| ---: | --- | --- | ---: | ---: | ---: | --- |
| 1 | `2026 Pick 1.01` | exact_slot | 7,084 | 96.7000 | 88 | elite |
| 2 | `2026 Pick 1.02` | exact_slot | 4,233 | 73.7989 | 88 | solid |
| 3 | `2026 Pick 1.03` | exact_slot | 3,751 | 69.6696 | 88 | solid |
| 4 | `2026 Pick 1.04` | exact_slot | 3,574 | 67.9570 | 88 | solid |
| 5 | `2026 Pick 1.05` | exact_slot | 3,376 | 66.0781 | 88 | solid |
| 6 | `2026 Pick 1.06` | exact_slot | 3,183 | 64.2388 | 88 | solid |
| 7 | `2026 Pick 1.07` | exact_slot | 2,963 | 62.1855 | 88 | solid |
| 8 | `2026 Pick 1.08` | exact_slot | 2,772 | 60.3620 | 88 | solid |
| 9 | `2026 Pick 1.09` | exact_slot | 2,604 | 58.7208 | 88 | speculative |
| 10 | `2026 Pick 1.10` | exact_slot | 2,455 | 57.2302 | 88 | speculative |
| 11 | `2026 Pick 1.11` | exact_slot | 2,322 | 55.8663 | 88 | speculative |
| 12 | `2026 1st` | round_only | 3,073 | 55.7121 | 74 | speculative |
| 13 | `2026 Pick 1.12` | exact_slot | 2,203 | 54.6133 | 88 | speculative |
| 14 | `2026 Pick 2.01` | exact_slot | 2,095 | 53.4475 | 88 | speculative |
| 15 | `2026 Pick 2.02` | exact_slot | 1,998 | 52.3689 | 88 | speculative |
| 16 | `2026 Pick 2.03` | exact_slot | 1,909 | 51.3537 | 88 | speculative |
| 17 | `2027 1st` | round_only | 2,843 | 51.0896 | 70 | speculative |
| 18 | `2026 Pick 2.04` | exact_slot | 1,828 | 50.4018 | 88 | speculative |
| 19 | `2026 Pick 2.05` | exact_slot | 1,753 | 49.4976 | 88 | speculative |
| 20 | `2026 Pick 2.06` | exact_slot | 1,684 | 48.6408 | 88 | speculative |
| 21 | `2026 Pick 2.07` | exact_slot | 1,621 | 47.8316 | 88 | speculative |
| 22 | `2026 Pick 2.08` | exact_slot | 1,562 | 47.0541 | 88 | speculative |
| 23 | `2026 Pick 2.09` | exact_slot | 1,507 | 46.3083 | 88 | speculative |
| 24 | `2026 Pick 2.10` | exact_slot | 1,456 | 45.5941 | 88 | speculative |
| 25 | `2026 Pick 2.11` | exact_slot | 1,408 | 44.9038 | 88 | deep |

## PPR Bottom 25

| Bottom rank | Pick | Class | Market | Score | Confidence | Tier |
| ---: | --- | --- | ---: | ---: | ---: | --- |
| 1 | `2029 4th` | round_only | 784 | 18.0143 | 62 | avoid |
| 2 | `2028 4th` | round_only | 780 | 20.7826 | 66 | avoid |
| 3 | `2029 3rd` | round_only | 954 | 23.0813 | 62 | avoid |
| 4 | `2027 4th` | round_only | 818 | 23.8836 | 70 | avoid |
| 5 | `2028 3rd` | round_only | 957 | 25.9051 | 66 | avoid |
| 6 | `2026 4th` | round_only | 859 | 27.0085 | 74 | avoid |
| 7 | `2029 2nd` | round_only | 1,206 | 28.7981 | 62 | avoid |
| 8 | `2027 3rd` | round_only | 1,022 | 29.2201 | 70 | avoid |
| 9 | `2026 Pick 4.12` | exact_slot | 774 | 32.1300 | 88 | deep |
| 10 | `2028 2nd` | round_only | 1,289 | 32.2558 | 66 | deep |
| 11 | `2026 Pick 4.11` | exact_slot | 788 | 32.5510 | 88 | deep |
| 12 | `2026 3rd` | round_only | 1,130 | 32.8759 | 74 | deep |
| 13 | `2026 Pick 4.10` | exact_slot | 803 | 32.9798 | 88 | deep |
| 14 | `2026 Pick 4.09` | exact_slot | 818 | 33.4087 | 88 | deep |
| 15 | `2026 Pick 4.08` | exact_slot | 834 | 33.8454 | 88 | deep |
| 16 | `2026 Pick 4.07` | exact_slot | 850 | 34.2822 | 88 | deep |
| 17 | `2026 Pick 4.06` | exact_slot | 868 | 34.7349 | 88 | deep |
| 18 | `2026 Pick 4.05` | exact_slot | 885 | 35.1795 | 88 | deep |
| 19 | `2026 Pick 4.04` | exact_slot | 904 | 35.6401 | 88 | deep |
| 20 | `2026 Pick 4.03` | exact_slot | 924 | 36.1086 | 88 | deep |
| 21 | `2026 Pick 4.02` | exact_slot | 944 | 36.5770 | 88 | deep |
| 22 | `2027 2nd` | round_only | 1,532 | 36.9813 | 70 | deep |
| 23 | `2026 Pick 4.01` | exact_slot | 965 | 37.0535 | 88 | deep |
| 24 | `2026 Pick 3.12` | exact_slot | 987 | 37.5378 | 88 | deep |
| 25 | `2026 Pick 3.11` | exact_slot | 1,010 | 38.0301 | 88 | deep |

## Component Examples

`2026 Pick 1.01`:

```json
{
  "formula": {
    "model": "trade_pick_score_v0",
    "risk_adjustment": 0.0,
    "market_normalization": "min_max_within_scoring_league_roster_context"
  },
  "parse": {
    "pick_year": 2026,
    "pick_class": "exact_slot",
    "pick_round": 1,
    "pick_slot": 1,
    "estimated_overall_pick": 1,
    "parse_confidence": "high"
  },
  "confidence_breakdown": {
    "starting_confidence": 88.0,
    "deductions": [],
    "confidence_score": 88.0
  },
  "risk_breakdown": {
    "risk_adjustment": 0.0,
    "details": [
      {
        "reason": "exact_slot_known",
        "adjustment": 0.0
      }
    ]
  },
  "college_context": {
    "score": 50.0,
    "status": "neutral_unavailable",
    "source_tables_used": []
  }
}
```

`2026 1st`:

```json
{
  "formula": {
    "model": "trade_pick_score_v0",
    "risk_adjustment": -5.0,
    "market_normalization": "min_max_within_scoring_league_roster_context"
  },
  "parse": {
    "pick_year": 2026,
    "pick_class": "round_only",
    "pick_round": 1,
    "pick_slot": null,
    "estimated_overall_pick": null,
    "parse_confidence": "medium"
  },
  "confidence_breakdown": {
    "starting_confidence": 74.0,
    "deductions": [],
    "confidence_score": 74.0
  },
  "risk_breakdown": {
    "risk_adjustment": -5.0,
    "details": [
      {
        "reason": "round_only_uncertainty",
        "adjustment": -5.0
      }
    ]
  },
  "college_context": {
    "score": 50.0,
    "status": "neutral_unavailable",
    "source_tables_used": []
  }
}
```

## Market Ordering Review

The dry-run broadly follows market ordering:

- `2026 Pick 1.01` ranks first with score `96.7`.
- `2026 Pick 1.02` and `2026 Pick 1.03` rank second and third.
- `2026 1st` ranks below the known top 11 exact first-round slots because it is round-only and carries uncertainty.
- Later-year round-only firsts decline: `2027 1st` rank 17, `2028 1st` rank 30, `2029 1st` rank 39.
- Low-value future round-only picks sit at the bottom.

This is sane enough for contracts and staging-only review. It is not final product calibration.

## Test Results

| Check | Result |
| --- | --- |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | PASS |
| `.\venv\Scripts\python.exe -m py_compile app.py` | PASS |
| `.\venv\Scripts\python.exe -m py_compile src\trade_player_scores.py` | PASS |
| `.\venv\Scripts\python.exe -m py_compile src\trade_pick_scores.py` | PASS |
| `.\venv\Scripts\python.exe -m compileall -q src scripts` | PASS |
| `.\venv\Scripts\python.exe -m unittest tests.test_trade_pick_scores` | PASS, 13 tests |
| `.\venv\Scripts\python.exe -m unittest discover tests` | PASS, 380 tests |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run` | PASS, 160 validations discovered |

The full test suite emitted existing mocked pipeline, load, and job-run logs. No live ingestion or score materialization command was run.

## Remaining Warnings

- Pick scores are dry-run only. No warehouse contract exists yet.
- The score uses current market value and pick structure, not college production.
- `college_context_score` is neutral and explicitly flagged unavailable.
- `draft_outcome_prior_insufficient` is present because current `draft_picks` history is not mature enough for long-term fantasy pick calibration.
- Existing pick asset missing flags are player-centric. A future pick contract should use pick-native flags.
- Tier thresholds need product review. Example: `2026 Pick 1.02` scores `73.7989`, just below `premium`.
- Production score flags remain false and were not touched.

## Recommended Next Phase

Proceed to Phase 28.3: add additive warehouse contracts, current views, and validations for `trade_pick_scores`, `trade_pick_scores_current`, and `compat_trade_pick_scores_current`. Do not apply migrations until explicitly authorized.
