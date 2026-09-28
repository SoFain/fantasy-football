# Phase 38.28 Daily Ranking Staleness Repair

## Decision

The ten-day board staleness was a failed coverage gate, not a missing daily schedule. `PigskinDailyPublishImport` ran, but Theo Wease was incorrectly treated as a blocking established starter because Sleeper reported MIA RWR depth order 1. Miami's published depth chart placed him in the third column, and his 2025 sample was 3 games and 10 targets. That exact case is now a bounded review-only owner decision. It expires if his team, experience, games, or targets leave the recorded bounds.

The repair also removed three brittle downstream stops exposed by the fresh context:

- Standard RB grew from 85 to 86 eligible rows when Dare Ogunbowale gained a current LV team. The exact count became a bounded 80-100 integrity contract.
- Ricky Pearsall's SF IR status is now review-only in PPR, Half-PPR, and GNG. It carries injury flags and zero missed-game movement because no verified regular-season games-missed estimate was supplied.
- Teamless candidates remain excluded before promotion. Missing Sleeper identity context still blocks.

The daily wrapper now passes named coverage warnings into fallback manifests, calls `gcloud.cmd` for Windows dataset uploads, and retries the IONOS import once after 10 seconds.

## Production Result

The coordinated chain completed at `2026-08-07T01:57:21-04:00` with board refresh exit 0, publication exit 0, and IONOS import exit 0.

| Profile | Board version | Source generated UTC | Overall | Positional rows |
|---|---|---|---:|---|
| Standard | `unified-fable-v1-standard-20260807055438` | `2026-08-07T05:54:45.626751Z` | 150 | QB 45, RB 86, WR 100, TE 35 |
| PPR | `unified-ppr-fable-v1-20260807055452` | `2026-08-07T05:55:28.638623Z` | 150 | QB 45, RB 80, WR 100, TE 35 |
| Half-PPR | `unified-half-ppr-fable-v1-20260807055532` | `2026-08-07T05:55:37.959116Z` | 150 | QB 45, RB 80, WR 100, TE 35 |
| GNG Keeper | `unified-gng-keeper-2026-20260807055542` | `2026-08-07T05:55:48.223505Z` | 150 | QB 45, RB 80, WR 100, TE 35 |

Immutable manifest: `v1/manifests/sha256-641422bc0b398855915a4623aa08146b15f0f9487b0af6da3ee021fcc65f638a.json`.

IONOS imported 416 Standard rows and 410 rows for each other profile. The live cache-busted manifest had four profiles, empty warnings, and matching SHA-256 bytes for every board.

## Verification

- Focused unit tests: 42 passed for the daily row contract, GNG injury treatment, PPR/Half-PPR safety, Standard promotion, coverage gating, and public-feed contracts.
- Full dry refresh: passed before production writes.
- Coverage audit: zero blocking omissions; Theo Wease listed under `review_only_omissions`.
- GNG preflight: 260 positional rows, 150 unified rows, zero hard reviews, zero teamless rows, zero queue mismatches.
- Final chain log: `output/daily-publish/chain-20260807-014959.log`.

## Remaining Risk

The scheduled task has not yet reached its next 07:30 ET run with this code. The live manual run exercised the same wrapper successfully. A future legitimate roster change can alter the Standard RB pool within 80-100 without intervention; falling outside that range still fails closed.
