# Current Player Ranking Coverage Audit

## Final Decision

PASS. The repaired candidate universe contains no blocking established-player pipeline omissions. Positional promotion may proceed through its normal dry-run and write gates.

This phase was read-only against BigQuery and the public rankings. It made no live ranking, formula, candidate-table, unified-board, or JSON-feed changes.

## Checks

| Profile | Position | Rows | Expected | Result |
|---|---|---|---|---|
| standard | QB | 45 | 45 | PASS |
| standard | RB | 85 | 85 | PASS |
| standard | WR | 100 | 100 | PASS |
| standard | TE | 35 | 35 | PASS |
| ppr | QB | 45 | 45 | PASS |
| ppr | RB | 80 | 80 | PASS |
| ppr | WR | 100 | 100 | PASS |
| ppr | TE | 35 | 35 | PASS |
| half_ppr | QB | 45 | 45 | PASS |
| half_ppr | RB | 80 | 80 | PASS |
| half_ppr | WR | 100 | 100 | PASS |
| half_ppr | TE | 35 | 35 | PASS |

- Live Sleeper fetch: `2026-07-22T06:07:06.383643+00:00`.
- BigQuery Sleeper snapshot: `2026-07-20 01:59:58.860146+00:00` (52 hours old).
- BigQuery 72-hour safety status: `CURRENT`.
- PPR versus Half-PPR presence mismatches: `0`.
- Depth-order-1 current players missing at least one redraft board: `10`.
- High-signal omissions supported by GNG or market rank: `6`.
- Blocking veteran pipeline omissions: `0`.

## What The Current Omissions Mean

- `5` are rookies. GNG admits them through its market overlay; redraft intentionally has no approved rookie path yet.
- `0` established player falls below a one-season Fable threshold: Malik Nabers.
- `0` established player is blocked by an identity collision: Marvin Harrison.
- `5` tight ends have valid formula and candidate rows but land below the active TE35 cutoff. Isaiah Likely is the only high-signal market disagreement in that group.

## High-Signal Omissions

| Player | Pos | Team | Exp | Standard | PPR | Half | GNG | Market Pos | PPR Candidate | Trace |
|---|---|---|---|---|---|---|---|---|---|---|
| Jeremiyah Love | RB | ARI | 0 | missing | missing | missing | 5 | 4 | n/a | ROOKIE_SYSTEM_REQUIRED |
| Kenyon Sadiq | TE | NYJ | 0 | missing | missing | missing | 10 | 9 | n/a | ROOKIE_SYSTEM_REQUIRED |
| Carnell Tate | WR | TEN | 0 | missing | missing | missing | 14 | 13 | n/a | ROOKIE_SYSTEM_REQUIRED |
| Jadarian Price | RB | SEA | 0 | missing | missing | missing | 19 | 17 | n/a | ROOKIE_SYSTEM_REQUIRED |
| Isaiah Likely | TE | NYG | 4 | missing | missing | missing | 33 | 11 | 39 | POSITIONAL_PROMOTION_OR_BOARD_CUTOFF |
| KC Concepcion | WR | CLE | 0 | missing | missing | missing | 34 | 30 | n/a | ROOKIE_SYSTEM_REQUIRED |

## PPR And Half-PPR Presence Differences

None. The two reception-profile positional boards contain the same players.

## Why GNG Behaves Differently

| Stage | GNG Keeper | Standard, PPR, and Half-PPR |
|---|---|---|
| Veteran source pool | Averages 2023-2025 and requires at least four 2025 weekly scoring rows. | Position-specific Fable views use 2025. WR veterans below six games or 40 targets may use a prior qualified v1 score with a refreshed availability component. RB and TE thresholds are unchanged. |
| Missing advanced inputs | `weighted_average()` drops null inputs and renormalizes the remaining weights. | A player must survive the position view's identity, qualification, regression, and scoring joins. Failure produces no candidate row. |
| Identity | The GNG point pool starts from canonical internal player IDs and then joins Sleeper context. | Fable situational data uses a name-based identity bridge. Same-name collisions can block an otherwise complete source row. |
| Current Sleeper layer | Formula score is calculated first. A bounded depth-order adjustment is added; teamless players move to the watchlist. | The same post-formula safety view is joined after scoring. It cannot restore a player who never reached a Fable candidate table. |
| Rookie handling | Explicit market-ranked rookie overlay with depth-chart penalties. | No equivalent rookie overlay in the current shared redraft promotion path. |
| WR continuity | Existing live GNG top-six and top-12 WRs receive bounded merge-priority protection. | Standard has the approved A.J. Brown elite-order guardrail, but no general current-star coverage floor. |
| Unified board | Position-locked interleaving plus the approved Jeremiyah Love and QB4 floors. | Position-locked interleaving preserves only players already present on active positional boards. |

## Malik Nabers Trace

Malik Nabers was not found in the live depth-order-1 universe.

## Marvin Harrison Trace

Marvin Harrison was not found in the live depth-order-1 universe.

## Sleeper Safety Status

The BigQuery Sleeper context is current and may be used by the shared post-formula safety layer.

## Files Changed

- `scripts/audit_current_player_ranking_coverage.py`
- `output/current-player-ranking-coverage-audit.json`
- `docs/rebuild/validation/phase-38-25-current-player-coverage-audit.md`

## Next Phase

Run positional promotion dry-runs, apply only through the named write gates, rerun this coverage gate against active boards, then regenerate unified boards.
