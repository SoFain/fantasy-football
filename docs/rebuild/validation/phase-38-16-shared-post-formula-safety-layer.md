# Phase 38.16 Shared Post-Formula Safety Layer

## Decision

The shared current-context layer is deployed in the research dataset and is now used by the Standard WR Fable review board, the GNG candidate builder, and future PPR/Half-PPR Fable promotions.

Historical formulas and backtests remain unchanged. No active ranking row, unified board, champion, or public JSON feed changed.

## Contract

Canonical view: `fantasy_football_advanced_metrics.v_ranking_post_formula_safety`.

- Current roster eligibility requires `active=TRUE`, a current team, `Active` or `ACT` status, and a Sleeper snapshot no older than 72 hours.
- Current depth order 1 receives `+0.020` after formula scoring.
- RB, WR, or TE depth order 3 or worse receives `-0.040` after formula scoring.
- Depth order 2 receives no score movement.
- Injury status produces `INJURY_UNCERTAIN` only. It never changes the score without a source-backed games-missed decision.
- Rookies receive no automatic role movement and enter `ROOKIE_CONTEXT_REQUIRED` review.
- Teamless, inactive, stale, missing-context, and backup-QB states block promotion until reviewed. They do not alter the historical formula.

The view resolves missing Sleeper GSIS IDs through `player_identity_bridge`, first by Sleeper ID and then by a unique normalized name plus position.

## Fresh Snapshot

Sleeper was fetched once from the network at `2026-07-13T17:31:53.167379Z`.

- Current context rows: 12,200.
- Core-position safety identities: 4,004.
- Duplicate core-position identities: 0.
- Invalid adjustment values: 0.
- Hard-review rows with a nonzero adjustment: 0.

## Repaired Standard WR Review

The post-formula review contains 100 unique WRs.

- Missing Sleeper context: 0.
- Rows with a bounded role adjustment: 69.
- Hard promotion reviews: 6.
- Total owner-review flags: 16.
- Injury review flags: 11.
- Largest formula-to-safety movement: 7 ranks.
- Largest active-Standard-to-candidate movement: 31 ranks.

Current hard-review rows:

| Candidate rank | Player | Reason |
|---:|---|---|
| 36 | Stefon Diggs | Teamless |
| 38 | Deebo Samuel | Teamless |
| 39 | Keenan Allen | Teamless |
| 67 | Hunter Renfrow | Teamless |
| 76 | Gabe Davis | Teamless, injury status present |
| 85 | Sterling Shepard | Teamless |

The first three already have owner-approved unranked-watchlist decisions. Renfrow, Davis, and Shepard need the same decision or a verified roster update before promotion.

## Elite WR Order Warning

The shared safety layer does not resolve the earlier A.J. Brown ordering concern:

| Player | Active Standard WR rank | Repaired Fable rank | Post-safety rank | Current depth |
|---|---:|---:|---:|---:|
| A.J. Brown | 7 | 15 | 15 | 1 |
| Justin Jefferson | 9 | 13 | 13 | 1 |
| Garrett Wilson | 10 | 14 | 14 | 1 |

All three receive the same `+0.020`, so their order is unchanged. Promoting this board would put Brown below Jefferson and Wilson. That conflicts with the owner's prior positional-order decision and remains a promotion blocker.

## PPR and Half-PPR Guard

`promote_ppr_fable_v1_positional.py` now joins the shared view, ranks on formula score plus the bounded role adjustment, stores raw and adjusted score provenance, refreshes current Sleeper fields, and fails closed on selected hard-review rows.

Default candidate rows no longer freeze `recommended_rank` to the pre-safety formula rank. Explicit owner decisions remain fixed.

Both PPR and Half-PPR promotion SQL dry-runs passed. Neither board was republished or promoted.

## Checks

- `python -m unittest tests.test_gng_advanced_hypotheses tests.test_ranking_post_formula_safety tests.test_promote_ppr_fable_v1_positional tests.test_publish_ppr_fable_v1_candidate_boards`: 21 passed.
- Python compilation passed for all edited builders and promotion scripts.
- Shared safety view BigQuery dry-run and deployment validation passed.
- Standard WR safety review produced 100 unique rows.
- GNG candidate rebuild completed without `--apply`.
- PPR and Half-PPR promotion SQL dry-runs passed without `--apply`.

## Next Gate

Do not promote the repaired Standard WR board yet. Resolve the three new teamless watchlist decisions and the A.J. Brown elite-order conflict first. Injury flags can remain review-only unless a source-backed games-missed estimate is approved.
