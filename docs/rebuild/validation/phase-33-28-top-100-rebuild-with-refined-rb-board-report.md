# Phase 33.28 Top-100 Rebuild With Refined RB Board Report

Final decision: `TOP-100 PROTOTYPE READY FOR OWNER REVIEW WITH TRIPWIRES`.

The rebuilt board fixes the Jahmyr Gibbs positional miss and keeps all changes review-only. Top-100 remains blocked from live use because Current Pigskin and market tripwires still require owner review.

## Files Changed

- `docs/rebuild/position-locked-top-100-prototype-review.md`
- `docs/rebuild/position-locked-top-100-interleaver-plan.md`
- `docs/rebuild/advanced-bqml-v2-owner-review-boards.md`
- `docs/rebuild/ranking-algorithm-scorecard.md`
- `docs/rebuild/bqml-v2-ranking-architecture.md`
- `docs/rebuild/ranking-opportunity-metrics-matrix.md`
- `docs/rebuild/validation/phase-33-28-top-100-rebuild-with-refined-rb-board-report.md`
- `output/phase-33-28-top100-rebuild-evidence.json`

`output/phase-33-28-top100-rebuild-evidence.json` is generated evidence and should be reviewed before any package decision.

## Git State

Existing working tree was already dirty with Phase 33 artifacts and source changes. Phase 33.28 did not revert or stage unrelated work.

```text
MM docs/rebuild/bqml-v2-positional-formula-finalists.md
MM docs/rebuild/bqml-v2-ranking-architecture.md
MM docs/rebuild/ranking-algorithm-scorecard.md
MM docs/rebuild/ranking-opportunity-metrics-matrix.md
A  docs/rebuild/validation/phase-33-18b-advanced-bqml-scorecard-completion-report.md
A  docs/rebuild/validation/phase_33_18_report.md
M  src/bqml_v2_feature_contract.py
?? docs/rebuild/advanced-bqml-v2-owner-approval-packet.md
?? docs/rebuild/advanced-bqml-v2-owner-review-boards.md
?? docs/rebuild/position-locked-top-100-interleaver-plan.md
?? docs/rebuild/position-locked-top-100-prototype-review.md
?? docs/rebuild/top-100-identity-preflight.md
?? docs/rebuild/validation/phase-33-18c-advanced-bqml-finalist-comparison-correction-report.md
?? docs/rebuild/validation/phase-33-19-advanced-bqml-owner-review-boards-report.md
?? docs/rebuild/validation/phase-33-20-owner-review-of-advanced-positional-boards.md
?? docs/rebuild/validation/phase-33-21-advanced-board-guardrails-report.md
?? docs/rebuild/validation/phase-33-21b-guardrail-identity-history-fix-report.md
?? docs/rebuild/validation/phase-33-22-owner-approval-packet-report.md
?? docs/rebuild/validation/phase-33-23-owner-decision-guarded-positional-boards.md
?? docs/rebuild/validation/phase-33-24-position-locked-top-100-planning-report.md
?? docs/rebuild/validation/phase-33-25-top-100-identity-preflight-report.md
?? docs/rebuild/validation/phase-33-26-position-locked-top-100-prototype-report.md
?? docs/rebuild/validation/phase-33-26b-top-100-positional-mix-calibration-report.md
?? docs/rebuild/validation/phase-33-26c-top-100-weighting-calibration-report.md
?? docs/rebuild/validation/phase-33-26d-elite-market-miss-audit-report.md
?? docs/rebuild/validation/phase-33-27-rb-positional-board-refinement-report.md
```

## Input Queue Summary

| Profile | QB | RB | WR | TE |
| --- | --- | --- | --- | --- |
| Standard | Guarded BQML v2 | Phase 33.27 anchored_blend_tripwire | Guarded BQML v2 | Guarded BQML v2 |
| Half PPR | Guarded BQML v2 | Phase 33.27 anchored_blend_tripwire | Guarded BQML v2 | Held Current Pigskin |
| PPR | Guarded BQML v2 | Phase 33.27 anchored_blend_tripwire | Guarded BQML v2 | Held Current Pigskin |
| GNG Keeper | Held Current Pigskin | Phase 33.27 anchored_blend_tripwire | Guarded BQML v2 | Held Current Pigskin |

## RB Queue Replacement Summary

- Selected RB queue: `anchored_blend_tripwire`.
- Replacement scope: RB queue only, all profiles.
- Non-RB queues: unchanged from accepted or held Phase 33 owner-review decisions.
- Internal position queue ordering: preserved. The interleaver chose position slots using the Phase 33.26C calibrated sequence, then pulled the next player from each position queue.

## Top-100 Rebuild Summary

- Baseline: Option 2, QB12/RB30/WR42/TE12.
- Interleaver: Phase 33.26C calibrated weighted hybrid pull sequence.
- Live writes: none.
- Champion activation: none.
- Training: none.
- Deployment: none.
- Route metrics: blocked/null. No route share, YPRR, TPRR, first-read share, pressure EPA, covered-receiver EPA, or `pigskin_context_score` was used.

## Positional Mix Summary

| Profile | Top N | QB | RB | WR | TE |
| --- | --- | --- | --- | --- | --- |
| Standard | 12 | 1 | 5 | 4 | 2 |
| Standard | 24 | 3 | 8 | 10 | 3 |
| Standard | 50 | 5 | 20 | 18 | 7 |
| Standard | 100 | 13 | 38 | 35 | 14 |
| Half PPR | 12 | 1 | 5 | 5 | 1 |
| Half PPR | 24 | 1 | 7 | 12 | 4 |
| Half PPR | 50 | 5 | 16 | 21 | 8 |
| Half PPR | 100 | 13 | 34 | 38 | 15 |
| PPR | 12 | 0 | 4 | 7 | 1 |
| PPR | 24 | 1 | 7 | 12 | 4 |
| PPR | 50 | 5 | 16 | 21 | 8 |
| PPR | 100 | 13 | 33 | 40 | 14 |
| GNG Keeper | 12 | 1 | 5 | 5 | 1 |
| GNG Keeper | 24 | 3 | 8 | 10 | 3 |
| GNG Keeper | 50 | 8 | 15 | 19 | 8 |
| GNG Keeper | 100 | 15 | 33 | 38 | 14 |

## Gibbs Placement By Profile

| Profile | Previous Overall | New Overall | New RB Rank | Pass |
| --- | --- | --- | --- | --- |
| Standard | 48 | 7 | 3 | Yes |
| Half PPR | 58 | 6 | 3 | Yes |
| PPR | 27 | 4 | 3 | Yes |
| GNG Keeper | 60 | 6 | 3 | Yes |

## Elite RB Tripwire Results

| Profile | Player | Tripwire | Source Rank | Review RB Rank | Threshold | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Standard | Jeremiyah Love | Market top 6 RB | 4 | 999 | 12 | Owner review required |
| Half PPR | Breece Hall | Current Pigskin top 6 RB | 6 | 16 | 12 | Owner review required |
| Half PPR | Jeremiyah Love | Market top 6 RB | 4 | 999 | 12 | Owner review required |
| PPR | Jeremiyah Love | Market top 6 RB | 4 | 999 | 12 | Owner review required |
| GNG Keeper | Jeremiyah Love | Market top 6 RB | 4 | 999 | 12 | Owner review required |

Notes: Breece Hall is a live Current Pigskin drift warning in Half PPR. The Phase 33.27 evidence had him outside the Current Pigskin top six, while the current active table lists him RB6. Jeremiyah Love is a market-only RB4 signal and is not present in the active Current Pigskin board or selected RB feature queue.

## Market And Current Tripwire Results

- Current Pigskin tripwire warnings: `39`.
- RB-specific tripwire warnings: `5`.
- All current tripwire warnings have manual-review explanations in the generated evidence file.
- No market data was used as a training target. Market data was used only as a review tripwire.

## Before And After Severe Miss Table

| Profile | Player | Pos | Current Overall | Previous | New | Threshold | Before | After |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Standard | Patrick Mahomes | QB | 10 | 53 | 53 | 50 | True | True |
| Standard | Rashee Rice | WR | 15 | 96 | 95 | 80 | True | True |
| Standard | Matthew Stafford | QB | 22 | 101 | 101 | 80 | True | True |
| Half PPR | Patrick Mahomes | QB | 11 | 64 | 64 | 50 | True | True |
| Half PPR | Rashee Rice | WR | 16 | 92 | 91 | 80 | True | True |
| PPR | Patrick Mahomes | QB | 9 | 56 | 56 | 50 | True | True |
| PPR | Rashee Rice | WR | 17 | 89 | 88 | 80 | True | True |
| GNG Keeper | Jahmyr Gibbs | RB | 12 | 60 | 6 | 50 | True | False |
| GNG Keeper | Rashee Rice | WR | 22 | 98 | 96 | 80 | True | True |

## Board Quality

| Profile | Top-24 Current Overlap | Top-50 Current Overlap | Top-100 Current Overlap | Extreme Movement Count |
| --- | --- | --- | --- | --- |
| Standard | 15 | 34 | 99 | 34 |
| Half PPR | 17 | 37 | 99 | 30 |
| PPR | 17 | 35 | 99 | 31 |
| GNG Keeper | 18 | 40 | 99 | 27 |

Historical points captured, VOR captured, NDCG, pairwise draft win rate, and pick-band regret were not recomputed as live evidence in this phase. The position-pull sequence is inherited from Phase 33.26C, while the RB queue is review-only and uses no 2026 outcomes. Those metrics need a separate bounded backtest before any champion or live top-100 decision.

## Remaining Concerns

- Jeremiyah Love remains a market-only prospect tripwire until a source-backed active ranking or approved prospect lane includes him.
- Half PPR Breece Hall requires owner review because the current active ranking table now treats him as RB6, while the selected RB evidence used an older lower Current Pigskin rank.
- Current Pigskin overall tripwires still produce 39 owner-review warnings. Most are QB/WR movement warnings inherited from the Phase 33.26C position-pull sequence, not new RB errors.
- Top-100 is not ready for live ranking writes or champion activation.

## Checks Run

| Check | Result |
| --- | --- |
| .\venv\Scripts\python.exe -m unittest tests.test_bqml_v2_feature_contract | PASS, 26 tests |
| .\venv\Scripts\python.exe -m py_compile src\bqml_v2_feature_contract.py | PASS |
| .\venv\Scripts\python.exe scripts\check_deployment_safety.py | PASS |
| .\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run | PASS, discovered 251 validation files |
| focused top-100 checks | PASS |
| focused RB tripwire checks | PASS with 5 owner-review warnings |
| focused elite miss checks | PASS with 39 owner-review warnings |
| git diff --check | PASS with existing LF-to-CRLF warning on docs/rebuild/bqml-v2-positional-formula-finalists.md |

## Safety Confirmations

- No live ranking table touched.
- No champion table touched.
- No model training run.
- No Gemini call.
- No Pigskin chat call.
- No deployment.
- No Sleeper current context used as historical input.
- No route metrics populated.

## Recommended Next Phase

Phase 33.29: Owner review of refined top-100 prototype with tripwires, including explicit decisions on Jeremiyah Love, Half PPR Breece Hall, and the remaining Current Pigskin QB/WR movement warnings.
