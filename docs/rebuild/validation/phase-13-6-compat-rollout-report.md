# Phase 13.6 Compatibility Rollout Report

## Decision

GO WITH WARNINGS

The compatibility readiness checker exists, all five candidate paths were assessed, and only `USE_COMPAT_TRADE_PLAYER_HISTORY` is selected for staged enablement. Production defaults were not changed.

## What Changed

- Added [src/compat_rollout.py](../../../src/compat_rollout.py).
- Added [tests/test_compat_rollout.py](../../../tests/test_compat_rollout.py).
- Added [docs/rebuild/compat-rollout-status.md](../compat-rollout-status.md).
- Updated [docs/rebuild/streamlit-compat-rollout.md](../streamlit-compat-rollout.md).
- Updated [docs/rebuild/ui-query-debt-register.md](../ui-query-debt-register.md).

No legacy Streamlit paths were removed.

## Readiness Summary

| Flag | Object | Ready | Rows | Validation files | Selected |
| --- | --- | --- | ---: | ---: | --- |
| `USE_COMPAT_TRADE_PLAYER_HISTORY` | `compat_trade_player_history` | yes | 55,617 | 6 | yes |
| `USE_COMPAT_TRADE_ASSETS` | `compat_trade_assets_current` | yes | 1,383 | 8 | no |
| `USE_COMPAT_PLAYER_PROFILES` | `compat_player_profiles_current` | yes | 27,864 | 7 | no |
| `USE_COMPAT_SLEEPER_WATCH` | `compat_sleeper_watch_candidates` | yes | 1,652 | 8 | no |
| `USE_COMPAT_VIEWER_TEAM_CONTEXT` | `compat_viewer_team_context` | yes | 10 | 8 | no |

All required rollout columns were present. Bounded samples showed 0.0 missing rates for `source_freshness_json` and `missing_data_flags`.

## Selected Flag

`USE_COMPAT_TRADE_PLAYER_HISTORY`

Reason:

- It is first in the documented rollout order.
- It is the lowest-risk UI surface.
- It replaces the Trade Lab `weekly_metrics` history query with `compat_trade_player_history`.
- Its helper already uses parameterized queries.
- Live validation passed.

## Validation Results

Command:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern compat_trade_player_history
```

Result:

- 6 passed
- 0 failed
- 1 informational warning from identity coverage with `missing_identity_rate = 0.0`

## Rollback

Unset `USE_COMPAT_TRADE_PLAYER_HISTORY` and restart Streamlit or Cloud Run. Legacy Trade Lab history remains available.

## Warnings

- The flag was not enabled in production code or committed defaults. Enable it through environment only for staging or local QA.
- Manual browser QA has not been run.
- All other candidate paths passed automated readiness, but they remain disabled until this first rollout is observed.

## Final Status

Ready for staged `USE_COMPAT_TRADE_PLAYER_HISTORY=true` rollout.
