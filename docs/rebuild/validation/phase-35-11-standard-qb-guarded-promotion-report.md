# Phase 35.11: Standard QB Guarded 75/25 Promotion

## Final decision

**STANDARD QB GUARDED 75/25 DEPLOYED WITH DETERMINISTIC ROLE GUARDS**

The active Standard/redraft/one-QB QB board now uses the guarded 75/25 formula. The prior Flash-adjusted board is archived. No dashboard image deploy was needed because the application reads active BigQuery ranking rows directly.

## Owner authorization

The owner approved completing and deploying the Standard QB replacement. The promotion write gate `ALLOW_STANDARD_QB_GUARDED_PROMOTION=true` was set only in the applying PowerShell process and removed in `finally`. Post-run verification showed the gate unset.

## Role guard correction

Sleeper context confirmed Justin Fields is active on Kansas City with `sleeper_depth_chart_order=2`.

The promotion candidate therefore added deterministic role buckets:

- starter or unknown: QB1-32;
- second string: QB33-43;
- third string or lower: QB44-45.

Formula movement remains capped at four ranks inside the correct role bucket. A verified role conflict may override that cap. This places Justin Fields at QB33 instead of the raw model's QB24. Fernando Mendoza moves to QB32 because the current snapshot lists him first on the Las Vegas QB depth chart despite missing historical BQML inputs.

The LLM is not responsible for starter-status correction. Structured Sleeper depth order handles it programmatically.

## Promotion

| Item | Result |
|---|---|
| Prior ranking version | `pigskin-llm-20260704071412` |
| New ranking version | `standard-qb-guarded-75-25-20260711214758` |
| New model run | `standard_qb_guarded_75_25-20260711T214758Z` |
| Candidate | `standard_qb_guarded_bqml_75_25_v1` |
| Formula version | `1.0-phase-35-11` |
| Review query job | `caf8d1b1-712b-475e-b3b7-a11905ae6f3f` |
| Promotion job | `a71637ef-eddd-4af4-aa55-127aa1958b61` |
| Active rows | 45 |
| Unique ranks | 45 |
| Archived prior rows | 45 |

## Live verification

Verification jobs:

- board integrity: `39f9c612-7de0-45c7-b6af-b1ebf6caa7fe`
- selected players: `be31b5c3-b4fa-4b17-9476-b242fb7c31fd`
- champion: `eee5cd73-5b31-4ebd-9708-6629046f18f8`
- history: `14a9020f-a3fa-4e63-91a1-283e3c42f9b4`

| Check | Result |
|---|---:|
| Active Standard QB rows | 45 |
| Distinct ranks | 45 |
| Rank range | 1-45 |
| Depth-2 rows above QB33 | 0 |
| Depth-3 rows above QB44 | 0 |
| Non-deterministic prompt markers | 0 |

Selected live rows:

| Rank | Player | Role | Tier |
|---:|---|---|---|
| 11 | Lamar Jackson | QB1 | front-line starter |
| 14 | Matthew Stafford | QB1 | matchup starter |
| 19 | Jordan Love | QB1 | matchup starter |
| 32 | Fernando Mendoza | QB1 | starter depth |
| 33 | Justin Fields | QB2 | backup or watchlist |

Every selected row uses:

- `rank_source=standard_qb_guarded_75_25`;
- `prompt_version=deterministic-no-llm`;
- `llm_adjustment_code=NO_ADJUSTMENT`.

## Safety

- Only active Standard/redraft/one-QB QB rows were replaced.
- Standard RB, WR, and TE rows were not touched.
- Half PPR, PPR, and GNG Keeper were not touched.
- No Gemini or Pigskin prompt call occurred.
- No Sleeper API call occurred. Existing warehouse context was read.
- No deployment service, Cloud Run Job, Scheduler job, ingestion, or materialization ran.
- The prior Standard QB board remains available in `analytics_pigskin_rankings_history`.

## Checks

- Deployment safety: passed.
- Focused formula, board, and promotion tests: 27 passed before apply.
- Promotion transaction assertions: passed.
- Post-promotion read-only verification: passed.

## Files

- `scripts/run_standard_qb_2026_owner_review.py`
- `scripts/promote_standard_qb_guarded_75_25.py`
- `tests/test_standard_qb_2026_owner_review.py`
- `tests/test_promote_standard_qb_guarded_75_25.py`
- `docs/rebuild/standard-qb-2026-guarded-owner-review-board.md`
- `docs/rebuild/validation/phase-35-11-standard-qb-guarded-promotion-report.md`

## Next work

Keep injury handling separate from formula rank. Sleeper injury status should trigger coded review. Any LLM adjustment must require source evidence, an adjustment code, and estimated regular-season games missed. Preseason `Questionable` alone should not move ranks.

