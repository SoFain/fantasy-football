# Phase 35.9: Standard QB Weight Refinement

## Final decision

**GUARDED CONSENSUS 75/25 IS A SERIOUS STANDARD QB REPLACEMENT CANDIDATE**

The candidate is ready for a read-only 2026 owner-review board. It is not approved for live ranking writes or production promotion.

No ranking rows were written. No model was trained or activated. No deployment, materialization, LLM call, Pigskin prompt, or Sleeper API call occurred.

## Search design

The bounded search varied the share assigned to existing advanced BQML signals while retaining the current deterministic Pigskin candidate as the control:

- `77.5/22.5`
- `75/25`
- `70/30`
- `65/35`

Both the linear-points and logistic-bust signals were tested individually. Their equal-weight consensus was also tested. The research runner rejects signal weights above 40%.

Two theory-driven QB Fable variants were tested separately:

- `qb_fable_balanced`, with direct rushing-linked weight reduced to about 28%;
- `qb_fable_passing`, with direct rushing-linked weight reduced to about 21%.

These were limited changes intended to address the formula's known rushing bias. They were not an unrestricted parameter search.

## Aggregate guarded-blend results

Combined 2024-2025 sample: 868 player-week observations.

| Candidate | Correlation | Top 12 | Captured points | VOR captured | Regret | Pairwise | Max move | Moves over 3 | Rushing-only risers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Current Pigskin candidate | 0.5217 | 0.6806 | 0.8189 | 0.7597 | 878.58 | 0.6404 | 0 | 0 | 0 |
| Consensus 77.5/22.5 | 0.5375 | 0.6852 | 0.8238 | 0.7640 | 862.90 | 0.6460 | 4 | 1 | 0 |
| **Consensus 75/25** | **0.5383** | **0.6875** | **0.8239** | **0.7641** | **862.76** | **0.6464** | **4** | **1** | **0** |
| Linear 75/25 | 0.5393 | 0.6852 | 0.8238 | 0.7640 | 862.90 | 0.6471 | 4 | 1 | 0 |
| Consensus 70/30 | 0.5427 | 0.6852 | 0.8219 | 0.7614 | 872.30 | 0.6484 | 4 | 7 | 0 |
| Linear 70/30 | 0.5423 | 0.6875 | 0.8235 | 0.7640 | 863.12 | 0.6491 | 4 | 12 | 0 |
| Consensus 65/35 | 0.5476 | 0.6852 | 0.8214 | 0.7592 | 880.52 | 0.6509 | 5 | 21 | 0 |

Increasing BQML weight beyond 25% improves correlation and pairwise ordering but begins to damage regret, VOR capture, or movement stability. The `65/35` result is not acceptable because its regret is worse than control and 21 observations move more than three ranks.

## Season stability

### 2024

| Candidate | Correlation | Top 12 | Captured points | VOR captured | Regret | Pairwise | Max move |
|---|---:|---:|---:|---:|---:|---:|---:|
| Control | 0.4274 | 0.5231 | 0.7639 | 0.5966 | 572.34 | 0.6409 | 0 |
| **Consensus 75/25** | **0.4493** | **0.5370** | **0.7731** | **0.6078** | **556.50** | **0.6483** | **4** |
| Linear 70/30 | 0.4526 | 0.5278 | 0.7693 | 0.5992 | 568.64 | 0.6499 | 4 |

### 2025

| Candidate | Correlation | Top 12 | Captured points | VOR captured | Regret | Pairwise | Max move |
|---|---:|---:|---:|---:|---:|---:|---:|
| Control | 0.4470 | 0.8380 | 0.8855 | 0.8632 | 306.24 | 0.6384 | 0 |
| **Consensus 75/25** | **0.4530** | 0.8380 | 0.8855 | 0.8631 | 306.26 | **0.6392** | **2** |
| Linear 70/30 | 0.4680 | 0.8472 | 0.8894 | 0.8684 | 294.48 | 0.6461 | 3 |

The `70/30` linear blend is the best 2025 result, but its weaker 2024 top-board performance makes it less stable. The `75/25` consensus materially improves 2024 and preserves the strong 2025 control board.

## Fable weight changes

The passing-heavier variants do not solve the holdout failure.

| 2024 -> 2025 candidate | Correlation | Top 5 | Top 12 | Captured points | Mean rank error |
|---|---:|---:|---:|---:|---:|
| Prior-year Standard PPG | 0.3305 | 0.20 | 0.5833 | 0.9308 | 8.00 |
| QB Fable v1 | 0.2901 | 0.20 | 0.5000 | 0.9195 | 8.07 |
| QB Fable balanced | 0.2483 | 0.20 | 0.5000 | 0.8981 | 8.41 |
| QB Fable passing | 0.2158 | 0.40 | 0.5000 | 0.8981 | 8.69 |

QB Fable remains a feature-research lane, not a replacement formula.

## Evidence jobs

- 75/25 combined summary: `f139bf87-31f4-4139-b63f-3893794b4fc4`
- 75/25 combined movement: `0fcb6011-1477-418d-b7e9-ecde34362dfb`
- 75/25 2024 summary: `c122644a-90e6-434a-bdbb-028459779441`
- 75/25 2025 summary: `386bc582-f27f-467b-ac1b-3e3aafe220d2`
- 70/30 combined summary: `3ed67d6a-e219-4373-b450-7d3c225b61b2`
- 70/30 2025 summary: `71bd7f8c-8fd0-4410-93aa-5afc61efdc3d`
- Fable variant comparison: `8ea8f469-be9d-442a-9c1b-ccd9d76a409e`

## Required promotion tripwires

Before any ranking write, generate a read-only 2026 board for `guarded_consensus_75_25` and verify:

- no player moves more than four ranks;
- every move of three or four ranks has passing and projection evidence;
- weak passing EPA and CPOE cannot be overcome by rushing signal alone;
- QB6, QB12, and QB24 crossings are owner-reviewed;
- rookies or players without model inputs remain in a separate deterministic lane;
- injuries remain coded, bounded adjustments rather than unrestricted rank rewriting.

## Recommendation

Advance `guarded_consensus_75_25` to a read-only 2026 Standard QB owner-review board. Keep `guarded_linear_70_30` as the aggressive challenger shown beside it. Do not promote either until the player-level movement review passes.
