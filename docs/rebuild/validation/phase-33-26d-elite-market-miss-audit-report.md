# Phase 33.26D Elite Market-Miss Audit

Final decision: `RB POSITIONAL BOARD NEEDS REFINEMENT`

Secondary decision: `TOP-100 HELD BEHIND CURRENT PIGSKIN`

## Scope

This phase audited severe player-level misses in the Phase 33.26C `prototype_v3_balanced` top-100 review boards. It did not train models, write live rankings, activate champions, deploy, call Gemini, call Pigskin chat, use 2026 outcomes, or fabricate route metrics.

## Files Changed

- Created `docs/rebuild/validation/phase-33-26d-elite-market-miss-audit-report.md`.
- Appended Phase 33.26D decision notes to:
  - `docs/rebuild/position-locked-top-100-interleaver-plan.md`
  - `docs/rebuild/ranking-algorithm-scorecard.md`
  - `docs/rebuild/bqml-v2-ranking-architecture.md`
  - `docs/rebuild/ranking-opportunity-metrics-matrix.md`
- Generated local evidence file `output/phase-33-26d-audit-evidence.json` for this audit. It is local review evidence, not a release artifact.
- No live ranking tables were changed.
- No champion tables were changed.

Preexisting git state before this report included staged/modified Phase 33 docs and `src/bqml_v2_feature_contract.py`, plus untracked Phase 33 review artifacts. This report does not revert or overwrite that work.

## Read-Only Evidence

Read-only BigQuery sources inspected:

| Source | Row Count | Use |
| --- | ---: | --- |
| `analytics_pigskin_rankings` | 1,140 | Current Pigskin active ranks and ranking scores |
| `market_consensus_baseline_current` | 461 | External market tripwire, PPR snapshot only |
| `player_season_advanced_metrics` | 57,730 | RB feature and source-status audit |

Docs inspected:

- `docs/rebuild/position-locked-top-100-prototype-review.md`
- `docs/rebuild/validation/phase-33-26c-top-100-weighting-calibration-report.md`
- `docs/rebuild/advanced-bqml-v2-owner-review-boards.md`
- `docs/rebuild/bqml-v2-positional-formula-finalists.md`
- `docs/rebuild/ranking-algorithm-scorecard.md`
- `docs/rebuild/bqml-v2-ranking-architecture.md`
- `docs/rebuild/ranking-opportunity-metrics-matrix.md`

Current Pigskin overall rank below is derived from active `analytics_pigskin_rankings` by sorting `ranking_score` within scoring profile because the table stores position rank, not an explicit overall rank.

## Jahmyr Gibbs Root-Cause Audit

Jahmyr Gibbs is not an identity miss, missingness miss, or top-100-only interleaver miss. The guarded RB queue already ranks him too low before the interleaver pulls from position queues.

| Profile | Current Pigskin Overall | Current Pigskin RB | Market Overall | Market RB | Raw RB Rank | Guarded RB Rank | Prototype Overall | Prototype RB | VOR | Scarcity | Missingness | Labels |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| standard | 16 | 3 | 2 | 2 | 18 | 18 | 48 | 18 | 1.06 | 1.00 | 0% | NONE |
| half_ppr | 13 | 3 | 2 | 2 | 19 | 19 | 58 | 19 | 0.59 | 1.00 | 0% | MANUAL_REVIEW_REQUIRED |
| ppr | 14 | 3 | 2 | 2 | 9 | 9 | 27 | 9 | 9.37 | 1.00 | 0% | NONE |
| gng_keeper | 12 | 3 | 2 | 2 | 18 | 18 | 60 | 18 | 0.74 | 1.00 | 0% | NONE |

Verdict: RB18/RB19 is not defensible for review. Gibbs should be treated as a positional-board failure with an elite market/current anchor tripwire until the RB board is refined.

## Gibbs Feature Audit

The feature table stores Gibbs as `J.Gibbs`. His 2025 season is present and not undercounted in the inspected feature mart rows.

Key 2025 feature values:

| Field | Value |
| --- | ---: |
| Games | 17 |
| Carries | 243 |
| Rushing yards | 1,223 |
| Targets | 94 |
| Receptions | 77 |
| Receiving yards | 616 |
| Red-zone opportunities | 67 |
| Goal-line opportunities | 12 |
| Weighted opportunity, Standard | 231.31 |
| Weighted opportunity, Half PPR | 264.28 |
| Weighted opportunity, PPR | 313.84 |
| Weighted opportunity, GNG Keeper | 238.19 |
| Availability score | 100.0 |
| Offensive snap share | 0.67 |
| Snap role stability | 58.996 |
| Route metrics source status | BLOCKED |
| NGS source status | AVAILABLE |
| Participation source status | AVAILABLE |

Feature-bug findings:

- Receiving usage is present: 94 targets, 77 receptions, 616 receiving yards in 2025.
- 2025 is present: 17-game 2025 rows exist.
- Availability is not suppressing him: availability score is 100.0 on the complete 2025 row.
- Route metrics remain blocked. `routes_run`, `yprr`, `tprr`, pressure EPA, and covered-receiver EPA are blocked in the feature flags and were not used as populated facts.
- Rushing and receiving touchdown split fields are not present in `player_season_advanced_metrics`. Total touchdowns are available in Current Pigskin ranking output, but split touchdown diagnostics cannot be taken from this feature mart.
- The model appears to underweight receiving-back value and current role expansion outside PPR. The PPR board moves Gibbs to RB9, while Standard, Half PPR, and GNG leave him RB18/RB19 despite Current Pigskin RB3 and market rank 2 overall.
- The split-backfield history is the likely qualitative suppressor. Gibbs' 2025 role has elite weighted opportunity, but the positional finalist still favors traditional rush/goal-line profiles in non-PPR contexts.

## Elite RB Comparison

PPR market snapshot is used only as a tripwire. It is not used for training.

| Player | Market Overall | Market Pos | Current Pigskin Pos, PPR | Guarded RB, PPR | Prototype Overall, PPR | 2025 PPR Weighted Opp Rank In Sample | Note |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Bijan Robinson | 1 | RB1 | 2 | 1 | 1 | 2 | Model and market aligned |
| Jahmyr Gibbs | 2 | RB2 | 3 | 9 | 27 | 3 | Severe elite miss |
| Ashton Jeanty | 6 | RB3 | 11 | 4 | 10 | 6 | Prospect guarded but still high |
| De'Von Achane | 12 | RB5 | 4 | 13 | 35 | 5 | Elite speed/receiving profile suppressed outside PPR |
| Jonathan Taylor | 18 | RB7 | 5 | 3 | 4 | 4 | Traditional volume profile lifted |
| Christian McCaffrey | 25 | RB9 | 1 | 5 | 14 | 1 | Current Pigskin and features support high placement |
| Breece Hall | 26 | RB10 | 18 | 8 | 26 | 11 | Model above Current Pigskin |
| Saquon Barkley | 32 | RB13 | 8 | 2 | 3 | 7 | Model aggressively above market/current |
| Kyren Williams | 42 | RB16 | 9 | 7 | 18 | 8 | Reasonable model lift |
| Derrick Henry | 61 | RB22 | 20 | 6 | 17 | 9 | Goal-line/rushing profile lifted |
| Josh Jacobs | 69 | RB23 | 13 | 14 | 36 | 10 | Reasonable middle tier |

The PPR feature slice shows Gibbs third in sample weighted opportunity, third in targets, third in receiving yards, and sixth in rushing yards. His PPR board still ranks him RB9. Standard, Half PPR, and GNG fall much harder. That points at model weighting and anchor policy, not missing source data.

## Severe Miss Table

Thresholds used:

- Market top 5 outside prototype top 24.
- Market top 12 outside prototype top 36.
- Market top 24 outside prototype top 60.
- Current Pigskin top 12 outside prototype top 36.
- Current Pigskin top 24 outside prototype top 60.

| Player | Profiles Flagged | Evidence | Classification |
| --- | --- | --- | --- |
| Jahmyr Gibbs | standard, half_ppr, ppr, gng_keeper | Market 2 overall and Current Pigskin RB3, but prototype ranks 48, 58, 27, 60 | `positional_board_miss`, `market_anchor_needed`, `manual_review_required` |
| De'Von Achane | standard, half_ppr, gng_keeper | Market 12 overall, Current Pigskin RB4/RB5, prototype ranks 46, 57, 59 | `positional_board_miss`, `market_anchor_needed`, `manual_review_required` |
| Rashee Rice | all profiles | Current Pigskin overall 15 to 22, prototype ranks 89 to 98 | `positional_board_miss`, `manual_review_required` |
| Chris Olave | standard | Current Pigskin overall 13, prototype 75 | `top100_interleaver_miss`, `manual_review_required` |
| Brock Purdy | half_ppr, ppr | Current Pigskin top 24, prototype 75 to 77, but market QB13 overall 77 | `legitimate_model_disagreement`, `manual_review_required` |
| Trevor Lawrence | ppr | Current Pigskin overall 21, prototype 77, market overall 71 | `legitimate_model_disagreement`, `manual_review_required` |
| Chase Brown | standard, half_ppr, ppr, gng_keeper | Current Pigskin RB6, guarded RB25 to RB32 | `positional_board_miss`, `manual_review_required` |
| Tetairoa McMillan | half_ppr, ppr, gng_keeper | Market 21 overall/WR9, prototype 99 to 100 | `market_anchor_needed`, `guardrail_overreaction`, `manual_review_required` |
| Wan'Dale Robinson | half_ppr, ppr, gng_keeper | Current Pigskin WR16/WR17, market overall 107, prototype 91 to 99 | `legitimate_model_disagreement`, `manual_review_required` |
| Nico Collins | gng_keeper | Market 27 overall/WR12, Current Pigskin WR15, prototype 88 | `top100_interleaver_miss`, `manual_review_required` |
| Jaylen Waddle | half_ppr, ppr, gng_keeper | Current Pigskin WR22/WR23 area, prototype near 90s | `top100_interleaver_miss`, `manual_review_required` |
| Jaylen Warren | half_ppr, ppr | Current Pigskin RB19, market RB30, prototype 87 to 88 | `legitimate_model_disagreement`, `manual_review_required` |
| Cam Skattebo | half_ppr, gng_keeper | Low-history player, market 46 overall/RB18, prototype 75/81 | `guardrail_overreaction`, `market_anchor_needed`, `manual_review_required` |
| Marvin Harrison Jr. | multiple profiles | Prior identity issue fixed, market WR24, prototype outside early review bands | `manual_review_required` |
| Breece Hall | no severe tripwire in PPR | Market 26, prototype 26, guarded RB8 | `no_hard_miss` |
| Josh Jacobs | no severe tripwire | Market 69, prototype 36 | `no_hard_miss` |

## Root-Cause Classification

For Gibbs:

- RB18/RB19 is not defensible.
- The primary failure is the RB positional board. The top-100 interleaver is faithfully pulling from a guarded RB queue that already buried him.
- The current RB model underweights receiving/role expansion, especially outside PPR.
- Gibbs should be manually anchored in review prototypes until the RB board is fixed.
- The RB positional board should be sent back for refinement before any owner-facing top-100 can be called reliable.

System root causes:

- `positional_board_miss`: primary for Gibbs, Achane, Chase Brown, Rashee Rice.
- `top100_interleaver_miss`: secondary for some WRs where guarded positional rank is plausible but overall position mix buries the player.
- `market_anchor_needed`: primary review safety gap for Gibbs, Achane, Tetairoa McMillan, Cam Skattebo.
- `guardrail_overreaction`: likely for prospect/low-history players with strong current or market signals.
- `legitimate_model_disagreement`: possible for one-QB QBs where market and format do not justify top-36 overall protection.

## Review-Only Elite Anchor Guardrails

These are review safety rails. They are not live ranking rules and must not write to `analytics_pigskin_rankings`.

Current Pigskin anchor:

- Current Pigskin top 6 overall cannot fall outside top 18 without manual override.
- Current Pigskin top 12 overall cannot fall outside top 30 without manual override.
- Current Pigskin top 24 overall cannot fall outside top 50 without manual override.
- Current Pigskin top 50 overall cannot fall outside top 80 without manual override.

External market tripwire, when market data exists:

- Market top 5 cannot fall outside top 18 without explicit model evidence and manual review.
- Market top 12 cannot fall outside top 30 without explicit model evidence and manual review.
- Market top 24 cannot fall outside top 50 without explicit model evidence and manual review.

Position-specific review anchors:

- Consensus or current top 3 RB cannot fall outside top 18.
- Consensus or current top 6 RB cannot fall outside top 30.
- Consensus or current top 3 WR cannot fall outside top 18.
- Consensus or current top 6 WR cannot fall outside top 30.
- Top 3 TE cannot enter top 8 overall unless both Current Pigskin and VOR support it.
- One-QB QB should not flood the top 24.

Required override record fields:

- player
- original prototype rank
- anchor-adjusted review rank
- reason
- source of anchor
- manual review required
- positional board needs correction

## Prototype v4 Decision

`prototype_v4_elite_anchor` was not created in this phase.

Reason: a safe v4 would need to move Gibbs inside the RB positional queue, not just change the interleaver. The Phase 33.26D rules prohibit reordering inside position queues unless it is explicitly documented as a positional-board correction proposal. Creating a v4 overlay without fixing the RB queue would hide the root problem.

Top-100 remains blocked behind Current Pigskin and positional-only review until the RB board is refined or the owner explicitly approves review-only manual anchors.

## No-Live-Change Confirmation

- No model training occurred.
- No BigQuery writes occurred.
- No live ranking writes occurred.
- No champions were activated.
- No production or staging deploy occurred.
- No Gemini, Pigskin chat, or LLM-backed action occurred.
- No 2026 outcomes were used.
- Route metrics remain blocked. `routes_run`, `yprr`, `tprr`, pressure EPA, and covered-receiver EPA remain blocked/null policy fields.

## Checks

Required checks were run after creating this report.

| Check | Result |
| --- | --- |
| `.\venv\Scripts\python.exe -m unittest tests.test_bqml_v2_feature_contract` | PASS, 26 tests |
| `.\venv\Scripts\python.exe -m py_compile src\bqml_v2_feature_contract.py` | PASS |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | PASS |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run` | PASS, validation discovery completed |
| Focused top-100 prototype checks | PASS, parsed prototype ranks, VOR, source queue, scarcity, and identity status |
| Focused elite-miss checks | PASS, verified Gibbs tripwire breach, guarded RB ranks, market rank, and 2025 feature availability |
| `git diff --check` | PASS with Git LF-to-CRLF warnings on preexisting docs |

## Warnings

- The market table is a PPR snapshot. It is valid as a review tripwire, not as a training target.
- Current Pigskin overall rank was derived from `ranking_score`; the active ranking table stores position rank directly.
- `player_season_advanced_metrics` stores compact names such as `J.Gibbs`, so player-name joins need careful identity handling in future diagnostics.
- Touchdown splits by rushing and receiving are not available in `player_season_advanced_metrics`; only total touchdown support is available from ranking output.
- The worktree had preexisting staged, modified, and untracked files before this audit.

## Recommended Next Phase

Recommended next phase: Phase 33.27, refine RB positional board.

Minimum goals:

- Build RB-specific diagnostics for receiving role, weighted opportunity per game, 2025 role expansion, and split-backfield context.
- Add review-only market/current tripwire reporting before owner-facing top-100 boards are regenerated.
- Do not use market data as training input.
- Do not activate a champion.
- Do not write live rankings.
