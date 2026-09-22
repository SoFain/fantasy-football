# Phase 38.22 PPR and Half-PPR Score and Verdict Repair

## Decision

The PPR and Half-PPR positional score and Pigskin verdict defect is repaired and published. Player order and formulas were preserved.

## Production Result

- PPR positional version: `ppr-fable-v1-safety-20260713234954`
- Half-PPR positional version: `half-ppr-fable-v1-safety-20260713235028`
- PPR unified version: `unified-ppr-fable-v1-20260713235323`
- Half-PPR unified version: `unified-half-ppr-fable-v1-20260713235352`
- Standard unified version: `unified-fable-v1-standard-20260713235439`
- Immutable manifest SHA-256: `080157371a26016c10ce35d4a9fa1d293efddac62c27395f140e2d2b649955df`
- Public warnings: `0`

All four profiles are present in `v1/manifest.json`.

## Validation

- PPR and Half-PPR RB/WR/TE score ranges: `50.0-99.0`
- Missing reception-profile verdicts: `0`
- Legacy rank-only reception-profile verdicts: `0`
- Positional rank mismatches against the prior PPR and Half-PPR boards: `0 of 430`
- Unified rows per profile: `100`
- Anonymous board hash mismatches: `0`
- Focused tests: `13` passed
- Unified-table streaming rows after promotion: `0`

## Files Changed

- `scripts/promote_ppr_fable_v1_positional.py`
- `scripts/promote_unified_ppr_fable_v1_top100.py`
- `scripts/promote_unified_fable_v1_standard_top100.py`
- `tests/test_promote_ppr_fable_v1_positional.py`
- `AGENTS.md`
- `docs/PPR_HALFPPR_SCORE_VERDICT_FIX.md`
- `docs/rankings-production-runbook.md`
- `docs/public-rankings-json-feed.md`
- `output/unified-ppr-fable-v1-top100.json`
- `output/unified-half-ppr-fable-v1-top100.json`
- `docs/rebuild/unified-ppr-fable-v1-top100.md`
- `docs/rebuild/unified-half-ppr-fable-v1-top100.md`

## Durable Contract

Reception-profile promotion must normalize public scores to `50-99`, generate metric-backed verdicts, and fail closed on missing or rank-only text. Unified board replacement uses committed load jobs so consecutive profile promotions do not create a BigQuery streaming-buffer lock.
