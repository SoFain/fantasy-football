# Phase 38.10 GNG Final Audit and Production Package

## Decision

`PRODUCTION PACKAGE DRY-RUN PASSED; LIVE APPLY REQUIRES FINAL OWNER COMMAND`

The final Top 100 player audit found and fixed a cross-source identity defect, re-applied dynamic WR and QB guardrails, and produced a guarded transactional promotion package. Production remains unchanged.

## Canonical Identity Repair

Several fantasy-point rows used Sleeper IDs while advanced features used GSIS IDs. Direct joins left elite players with profile points but no advanced inputs. Null renormalization kept the rows scoreable and hid the feature loss.

The board builder now canonicalizes point-row IDs through `player_identity_bridge` before joining advanced, expected-opportunity, and NGS features.

Examples after repair:

- CeeDee Lamb moved to WR10.
- Justin Jefferson moved from WR48 to formula WR15, then the accepted live-WR guardrail anchored him at WR12.
- DeVonta Smith moved from WR43 to WR29.
- Wan'Dale Robinson moved from WR40 to WR34.
- Christian Watson moved from WR11 to WR46 after receiving his full advanced-feature record.

## Dynamic Guardrails

- Live WR1-WR6 cannot rank below WR12. Final violations: 0.
- Live WR7-WR12 cannot rank below WR24. Final violations: 0.
- QB positional rank 4 cannot enter the top 24. Brock Purdy is the current QB4 and lands outside the top 24.
- Jeremiyah Love remains overall 20.
- All positional queues remain contiguous.

## Final Preflight

| Check | Result |
|---|---:|
| Positional rows | 260 |
| Unified rows | 100 |
| Sleeper hard reviews | 0 |
| Watchlist leaks | 0 |
| Distinct unified players | 100 |

## Promotion Package

Added `scripts/promote_gng_2026_rankings.py`.

The package:

- requires `ALLOW_GNG_2026_PRODUCTION_PROMOTION=true` plus `--apply`;
- creates isolated rollback snapshots of current GNG positional and unified rows;
- deactivates only active `gng_keeper/redraft/one_qb` positional rows;
- inserts exactly 260 deterministic positional rows;
- replaces only the `gng_keeper` unified scope with 100 rows;
- runs positional and unified writes in one BigQuery transaction.

The first dry-run caught an `INT64` versus `STRING` Sleeper ID mismatch. The insert now casts Sleeper IDs explicitly. The second dry-run passed with `1,783,627` bytes processed.

## Validation

- Promotion preflight passed.
- BigQuery transactional dry-run passed.
- Thirteen focused unit tests passed.
- Python compilation passed.
- Production remains `pigskin-llm-20260704072119`.

## Next Command

After explicit final approval:

```powershell
$env:ALLOW_GNG_2026_PRODUCTION_PROMOTION='true'
.\venv\Scripts\python.exe scripts\promote_gng_2026_rankings.py --apply
```

Then verify active row counts, version consistency, unified rank continuity, watchlist exclusion, and production read behavior.
