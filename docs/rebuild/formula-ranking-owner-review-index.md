# Formula Ranking Owner Review Index

Last updated: 2026-07-06

## Current Decision

Current Pigskin stays live.

No formula champion is active. No BigQuery ML, NGS, injury, PBP, or Stats02 lane should replace current Pigskin without a separate owner-approved champion-selection phase and a separate live ranking generation phase.

## Live Baseline

| Lane | Status | Use |
|---|---|---|
| Current Pigskin candidate score v1 plus LLM final rankings | live baseline | Keep as the production ranking source. Active rankings currently cover PPR, Half PPR, Standard, and GNG Keeper. |

Active ranking state:

- `analytics_pigskin_rankings`: 1,140 active rows.
- Positions per profile: QB 45, RB 80, WR 100, TE 60.
- Active scoring profiles: `ppr`, `half_ppr`, `standard`, `gng_keeper`.
- Latest active generation timestamp: `2026-07-04T07:29:22.569631Z`.
- Current live TE depth remains 60 rows per scoring profile. Keep that as read-only verification until an owner-approved live-ranking depth change exists.

## Challenger Lanes

| Lane | Classification | Owner-read |
|---|---|---|
| Simple projection | owner-review signal | Strong basic benchmark. It remains useful as a sanity check, not a replacement. |
| Enriched BQML logistic elite v1 | owner-review signal | Best top-N, VOR, NDCG, and bust-control review lane from the enriched family. Overall pairwise weakness blocks promotion. |
| Enriched BQML linear points v1 | owner-review signal | Best board-ordering BQML lane. Good pairwise and overall board read, but not enough to replace current Pigskin. |
| BQML NGS logistic elite v1 | context only | Essentially flat to enriched logistic. Keep as NGS context, not a new challenger leader. |
| BQML NGS linear points v1 | context only | Did not improve materially over enriched linear points. |
| BQML boosted tree VOR lanes | context only | NGS boosted tree improved 2025 holdout VOR/NDCG but regressed on 2024 validation and cost more to train. |
| Stats02 WR/TE | component signal | Useful ideal-stat component evidence. Do not let it own rankings. |
| PBP RB/WR | component signal | RB has useful high-value opportunity signal. WR movement still needs protection. |
| NGS direct diagnostics | component signal | RB rushing NGS is the clearest additive component. WR/TE receiving NGS helps explain movement. |

## Risk Flags

| Lane | Classification | Owner-read |
|---|---|---|
| Injury availability | risk flag only | Keep as low-weight context. It is not a default formula. |
| Injury burden | risk flag only | Useful warning field, not a ranking driver. |
| Missed-time risk | risk flag only | Display as context when source freshness is clear. |

## Rejected Or Blocked

| Lane | Classification | Reason |
|---|---|---|
| Generic 5 percent availability blend | rejected | Over-penalization risk and weak cutline proof. |
| v2 trend-aware champion path | rejected | Underperformed after the full backtest expansion. |
| Broad ensembles | rejected | Did not clear the owner-review threshold. |
| Injury-only candidates | rejected | Too sparse and not causally strong enough. |
| Historical depth context | blocked | Source still lacks the required historical season/week context. |
| Sleeper current context as historical input | blocked | Sleeper current context is live display context only. It cannot be historical truth. |

## Source Status

| Source | Status | Use |
|---|---|---|
| `analytics_pigskin_rankings` | active | Live Player Profiles ranking output. |
| `analytics_pigskin_rankings_candidates` | active 2026 PPR candidate slice | Baseline candidate evidence only. Future review boards must not call Gemini or write live rankings. |
| `ranking_backtest_feature_mart` | active through target season 2025 | Historical BQML/backtest feature source. No 2026 feature slice exists yet. |
| `ranking_backtest_candidate_summaries` | active summary evidence | Contains enriched BQML v1 and BQML NGS v1 summaries. |
| `player_week_ngs_metrics` | active | Direct NGS component source. |
| `sleeper_player_context_current` | active | Live-current display context only. Latest snapshot: `2026-07-05T17:52:48.174830Z`. |

## Live 2026 Review Board Requirements

A safe live 2026 review board needs:

- Player identity and position eligibility.
- Scoring profile.
- Current Pigskin rank and score.
- Review-only BQML logistic score and rank, if generated from a 2026 prediction input.
- Review-only BQML linear points score and rank, if generated from a 2026 prediction input.
- Risk flags for availability, injury burden, and missed-time risk.
- NGS feature signals where source-backed.
- Sleeper current team, status, depth position, depth order, and freshness as display-only fields.
- Source freshness and missing flags shown beside model outputs.

Review-board target shape:

| Position | Owner-review board depth |
|---|---:|
| QB | 45 |
| RB | 80 |
| WR | 100 |
| TE | 35 |

TE owner-review output rules:

- Cap TE position boards, TE movement tables, display limits, and owner-facing summaries at TE35.
- Still include TE6, TE12, and TE18 cutline crossings.
- Do not generate owner-review TE tables beyond TE35 unless a missingness or debug note requires it.
- Do not reduce active `analytics_pigskin_rankings` TE rows in the review-board phase.
- Future owner-approved live-ranking depth change: reduce TE from 60 to 35.

Current blockers:

- `ranking_backtest_feature_mart` has 2025 target slices, not 2026.
- The existing BQML prediction helper is built for historical rows with known outcome labels. A 2026 review path needs an outcome-free prediction input.
- There is no dedicated review-only ranking table yet.
- `analytics_pigskin_rankings_candidates` currently has only the 2026 `ppr` slice. Standard, Half PPR, and GNG Keeper review boards are blocked until a non-mutating profile-specific candidate input exists.

## Sleeper Live-Context Guardrails

- Use Sleeper current context only for live 2026 display and review.
- Do not use Sleeper current context as historical backtest input.
- Show `snapshot_at` or equivalent freshness.
- If `sleeper_current_team` is null, show null or unknown.
- Do not silently fall back to stale identity team as current team. The Tyreek-style stale-team guardrail still applies.

## Latest Evidence

- [Phase 32.31 scoring-profile review input audit](validation/phase-32-31-scoring-profile-review-inputs-report.md)
- [Phase 32.30 live 2026 review boards](validation/phase-32-30-live-2026-review-board-report.md)
- [Phase 32.28 BQML NGS retrain](validation/phase-32-28-bqml-ngs-retrain-report.md)
- [Phase 32.27 direct NGS metrics](validation/phase-32-27-ngs-direct-metrics-report.md)
- [Phase 32.26 BQML candidate rankings](validation/phase-32-26-bqml-candidate-rankings-owner-review-report.md)
- [Phase 32.25 BQML owner-review cutlines](validation/phase-32-25-bqml-owner-review-cutlines-report.md)
- [Ranking algorithm scorecard](ranking-algorithm-scorecard.md)
- [Ranking opportunity metrics matrix](ranking-opportunity-metrics-matrix.md)

## Recommended Next Action

Recommended: Phase 32.30, live 2026 review-board generation, review-only.

That phase should build an outcome-free 2026 prediction input and generate owner-review outputs without writing `analytics_pigskin_rankings`, `ranking_formula_champions`, or `ranking_backtest_results`.

Alternate: build a read-only formula comparison UI if the owner wants visual review before any 2026 board output.

## Phase 32.30 Review Result

Phase 32.30 generated PPR-only live 2026 review boards:

- [Phase 32.30 report](validation/phase-32-30-live-2026-review-board-report.md)
- [Live 2026 ranking review boards](live-2026-ranking-review-boards.md)

Owner-review scoring profile order:

1. `standard`
2. `half_ppr`
3. `ppr`
4. `gng_keeper`

Do not choose one global challenger by averaging all scoring profiles. Pick or reject challengers separately by scoring profile. All-profile aggregate reads are stability/context only.

Phase 32.30 profile status:

| Scoring profile | Board status | Best review-only challenger |
|---|---|---|
| `standard` | blocked | not selected |
| `half_ppr` | blocked | not selected |
| `ppr` | generated with warnings | `ranking_bqml_enriched_logistic_elite_v1` |
| `gng_keeper` | blocked | not selected |

Main warning: the available 2026 candidate slice is PPR-only, so Standard, Half PPR, and GNG Keeper review boards were not generated and must not silently fall back to PPR.

## Champion Activation Requirements

Before any champion activation:

- Owner selects the challenger lane.
- A separate champion-selection phase writes `ranking_formula_champions`.
- A separate live ranking phase generates rankings.
- Production exposure, if any, gets its own gate and rollback plan.
