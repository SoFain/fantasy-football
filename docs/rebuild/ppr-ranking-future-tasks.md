# PPR Ranking Future Tasks

## Automated Current-Context Decisions

Build a deterministic review layer that runs before any positional promotion:

- Exclude unsigned players from ranked boards. Restore eligibility only after an official roster transaction supplies a current team.
- Apply an injury recovery gate for ACL, Achilles, and other long-term injuries. Require activation status, contact clearance, and a credible regular-season availability date before removing the hold.
- Compare Sleeper depth order with official team depth charts. Conflicts must create `OFFICIAL_DEPTH_CONFLICT` and retain both sources instead of silently choosing one.
- Require first-team snap or route evidence before promoting a listed TE2 into the top 12.
- Permit formula rises for healthy official starters, while preserving the formula rank, applied decision code, source evidence, and final rank delta.
- Archive every decision with `player_id`, snapshot date, formula rank, final rank, decision code, evidence URL or source table, and reviewer status.

Initial regression cases:

- Colby Parkinson: TE2 role verification.
- DK Metcalf: healthy WR1 acceptance.
- Zach Charbonnet: ACL recovery hold.
- Kimani Vidal: official-depth/Sleeper conflict.
- Stefon Diggs, Deebo Samuel, Keenan Allen: unsigned exclusion and signing-triggered re-entry.

## PPR Formula Work

- Promote PPR positional formulas only after the current-context exceptions are resolved or explicitly held.
- Fit PPR-specific rank-to-PPG curves. Do not reuse Standard coefficients.
- Calibrate PPR replacement ranks and positional composition with forward folds.
- Build an additive unified PPR top-100 before changing any live consumer.
