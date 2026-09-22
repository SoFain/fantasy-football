# Phase 38.2 GNG Shortlist, Null, and Player Audit

## Decision

`PASS FOR 2026 POSITIONAL BOARD GENERATION, NOT APPROVED FOR PRODUCTION`

The null-safe rerun selects QB H2, RB H1, WR H5, and TE H5. The proposed RB blend and WR tier split did not improve the board enough to retain.

## Missing-Value Treatment

Raw nulls now remain null through percentile creation. Each composite score divides by the sum of weights for inputs actually present. A missing availability or NGS field no longer receives a bottom-percentile value and no longer reduces the player's score indirectly.

Every one of the 826 player-season rows retained a composite score. This is expected because the core profile and opportunity fields are present. The incomplete optional fields now affect only the denominator used for that row.

## Shortlist Results

Three folds were evaluated: 2022 to 2023, 2023 to 2024, and 2024 to 2025.

| Position | Candidate | Spearman | Top 12 | Top 24 | Points@12 | Points@24 | NDCG@24 | Misses | Busts | Decision |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| QB | H1 profile | 0.566 | 0.667 | 0.861 | **0.851** | 0.901 | 0.904 | 4 | 0 | Reject |
| QB | **H2 opportunity** | 0.553 | 0.667 | 0.861 | 0.821 | **0.922** | **0.919** | **3** | 0 | **Select** |
| RB | **H1 profile** | 0.720 | 0.639 | **0.750** | 0.863 | **0.875** | **0.854** | 6 | 1 | **Select** |
| RB | 80% H1 / 20% H4 | **0.724** | 0.639 | 0.736 | 0.863 | 0.873 | 0.853 | 6 | 1 | Reject |
| WR | H3 opportunity | **0.733** | 0.583 | 0.597 | 0.868 | 0.888 | 0.858 | 8 | 3 | Reject |
| WR | **H5 stability** | 0.720 | 0.583 | **0.653** | **0.884** | 0.910 | **0.883** | **6** | **0** | **Select** |
| WR | H3 top 12 / H5 rest | 0.722 | 0.583 | **0.653** | 0.868 | **0.911** | 0.874 | 6 | 3 | Reject |
| TE | H2 opportunity | 0.726 | **0.639** | 0.750 | 0.827 | 0.857 | 0.862 | 7 | 1 | Reject |
| TE | **H5 stability** | **0.731** | 0.611 | **0.778** | **0.851** | **0.904** | **0.891** | **3** | **0** | **Select** |

## Player Audit

### QB H2

- 2023 outcome: Jordan Love, predicted 39, actual 5.
- 2024 outcome: Sam Darnold, predicted 27, actual 7. Jordan Love, predicted 33, actual 10.
- No top-12 busts.

### RB H1

- 2023 outcome misses: Saquon Barkley 30 to 9, Isiah Pacheco 39 to 12, Raheem Mostert 43 to 3, Kyren Williams 71 to 2.
- 2024 outcome misses: James Cook 38 to 7, Chuba Hubbard 42 to 12.
- Bust: Dalvin Cook, predicted 3 and actual 75 in the 2023 outcome.

The rejected 80/20 blend retained every miss and the Dalvin Cook bust. It moved none of them inside the top 24.

### WR H5

- 2023 outcome misses: Deebo Samuel 26 to 6, Nico Collins 74 to 8.
- 2024 outcome misses: Terry McLaurin 28 to 8, Tee Higgins 34 to 3, Drake London 38 to 12, Nico Collins 39 to 7.
- No top-12 busts.

The tiered candidate retained all six misses and added three busts inherited from H3: Chris Godwin in the 2023 outcome, then Calvin Ridley and Amari Cooper in the 2024 outcome.

### TE H5

- 2023 outcome misses: Trey McBride 37 to 12, Jake Ferguson 56 to 9.
- 2024 outcome miss: Jonnu Smith 29 to 5.
- No top-12 busts.

H2 produced seven misses and one bust. Its higher top-12 precision does not offset the damage below the elite tier.

## Interpretation

Most remaining misses are role changes, breakouts, or team-context changes that a prior-season statistical formula cannot reliably identify. They should feed a current-context review queue. They do not justify another broad historical weight search.

The 2025 outcome fold produced no elite misses or top-12 busts for any selected formula. It remains only one fold and is not enough by itself to approve production.

## Artifacts and Checks

- Updated `scripts/run_gng_advanced_hypotheses.py` with null-safe weighted scores, shortlist evaluation, and named player audits.
- Added `tests/test_gng_advanced_hypotheses.py`.
- Rewrote `output/gng-advanced-hypotheses.json` with raw coverage, all folds, shortlist results, and player audit rows.
- BigQuery-backed rerun completed successfully on July 11, 2026.
- Python compilation passed.
- Focused unittest passed.
- No ranking table, champion, or production row changed.

## Next Phase

Generate isolated 2026 QB, RB, WR, and TE candidate boards from the selected formulas. Preserve the existing Pigskin GNG boards until the new boards pass identity, current-team, injury, rookie, and rank-distribution review.
