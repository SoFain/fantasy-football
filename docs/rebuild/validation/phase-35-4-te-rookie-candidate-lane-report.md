# Phase 35.4 TE Rookie Candidate Lane Report

## Final Decision

`TE ROOKIE REVIEW LANE READY; PERFORMANCE RANKING BLOCKED ON SOURCE GAPS`

A separate 2026 rookie TE review lane now exists at:

`fantasy-football-498121.fantasy_football_advanced_metrics.v_te_fable_v1a_rookie_candidates`

It does not alter the active TE35 board. It does not assign fantasy ranks or formula scores.

## Contract

Eligibility requires the latest Sleeper snapshot, `position='TE'`, `years_exp=0`, active status, and a current NFL team. The deterministic `review_order` uses current depth-chart category, Sleeper search rank, then player name.

This order is an owner-review queue, not a fantasy ranking.

Every row exposes:

- Sleeper identity and team.
- Current status, injury tag, depth position, and depth order.
- Snapshot freshness.
- Rookie lane status.
- `formula_score=NULL`.
- Missing flags for GSIS identity, college production, draft capital, and depth order.

## Current Snapshot

| Status | Candidates |
|---|---:|
| Current-role TE1 | 1 |
| Current-role TE2 | 5 |
| Deeper current role | 16 |
| Incomplete current role | 27 |
| Total | 49 |

Top review candidates:

| Review order | Player | Team | Depth | Search rank | Injury |
|---:|---|---|---:|---:|---|
| 1 | Kenyon Sadiq | NYJ | 1 | 109 | Questionable |
| 2 | Eli Stowers | PHI | 2 | 140 | Questionable |
| 3 | Eli Raridon | NE | 2 | 999 | none |
| 4 | Marlin Klein | HOU | 2 | 999 | Questionable |
| 5 | Nate Boerkircher | JAX | 2 | 999 | none |
| 6 | Will Kacmarek | MIA | 2 | 9999999 | none |

## Source Gaps

All current rookie TE records lack GSIS IDs in the Sleeper snapshot. The warehouse does not yet provide an approved 2026 rookie draft-capital and college-production contract for this lane. Those fields are required before producing a deterministic rookie fantasy score.

Pigskin may use `ROOKIE_CONTEXT` only after source-backed rookie evidence is supplied. It cannot invent college production, draft capital, or role certainty.

## Safety

- No live ranking rows written.
- No champion change.
- No Gemini call.
- No rookie inserted into TE35.
- Preseason Questionable remains display-only.
