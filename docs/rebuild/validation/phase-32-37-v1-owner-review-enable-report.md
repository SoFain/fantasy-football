# Phase 32.37 V1 Owner Review Enable Report

Final decision: FORMULA REVIEW DEPLOYED FOR V1 OWNER REVIEW

## Prompt Delta

The emergency prompt overrode the earlier Phase 32.37 priority. Formula Review owner access became the top priority. TE35 production-depth work must not block owner review.

The owner screenshot changed the diagnosis. Production already showed the `Formula Review` tab and `USE_FORMULA_COMPARISON_DASHBOARD=true`, but the tab failed because the container did not include:

`/app/docs/rebuild/live-2026-ranking-review-boards.md`

## Root Cause

The production image copied app code, `src/`, validations, scripts, and data, but did not copy the static Formula Review board source:

`docs/rebuild/live-2026-ranking-review-boards.md`

The dashboard code reads that Markdown file at runtime, so the tab rendered an unavailable-board warning even though the tab and feature flag were enabled.

## Files Changed

- `Dockerfile`
- `tests/test_formula_review_dashboard.py`

The Docker image now copies the board source to:

`/app/docs/rebuild/live-2026-ranking-review-boards.md`

Regression coverage now checks that the source file exists in the repo and that the Dockerfile packages it.

Code commit:

- `428edf8 package formula review board source`

## Checks Run

| Check | Result |
|---|---|
| `.\venv\Scripts\python.exe -m unittest tests.test_formula_review_dashboard` | Pass, 8 tests |
| `.\venv\Scripts\python.exe -m py_compile app.py src\compat_flags.py src\formula_review_dashboard.py` | Pass |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | Pass |
| `git diff --check` | Pass |

No broad warehouse validations were run. The phase was scoped to emergency app packaging and deployment.

## Build Result

Build command used the repo Cloud Build path with explicit immutable tag:

`prod-candidate-428edf884581-20260706T164724Z`

Build ID:

`9ab6407e-5583-49a8-b2d1-3514cfeb1ba2`

Build status:

`SUCCESS`

Build-log evidence:

`COPY docs/rebuild/live-2026-ranking-review-boards.md ./docs/rebuild/live-2026-ranking-review-boards.md`

New digest-pinned image:

`us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:8bfaee3a2a1e54b5d78ed1ac676ebfeb4b9531e1078b08120f84d7f5b4fbaffb`

## Production Deploy Result

Service:

`nfl-studio-dashboard`

Production URL:

`https://nfl-studio-dashboard-583607027760.us-central1.run.app`

Previous production revision:

`nfl-studio-dashboard-00084-9z5`

Previous image digest:

`sha256:d0af08ee49858ab6230fea9b0ab6504a12043cc7066d0f76c79fb84f8b723f7d`

New production revision:

`nfl-studio-dashboard-00085-6v4`

New image digest:

`sha256:8bfaee3a2a1e54b5d78ed1ac676ebfeb4b9531e1078b08120f84d7f5b4fbaffb`

Traffic:

`nfl-studio-dashboard-00085-6v4=100`

Rollback command:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services update-traffic nfl-studio-dashboard --project=fantasy-football-498121 --region=us-central1 --to-revisions=nfl-studio-dashboard-00084-9z5=100
```

Rollback was not used.

## Production Flags

| Flag | State |
|---|---|
| `USE_FORMULA_COMPARISON_DASHBOARD` | `true` |
| `DATA_OPS_ALLOW_JOB_TRIGGER` | `false` |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` | `false` |
| `USE_TRADE_ANALYZER_SCORE_V0` | `false` |
| `USE_COMPAT_TRADE_PLAYER_SCORE` | `false` |
| `USE_PIGSKIN_HISTORICAL_PACKET_TOOL` | unset |

No write/export controls were added to Formula Review.

## Smoke Results

| Check | Result |
|---|---|
| `/_stcore/health` | `200 ok` |
| `/` | `200`, Streamlit shell present |
| Root response traceback check | No traceback |
| Headless browser smoke | Reached app-level login screen |
| Post-login Formula Review content | Owner refresh required |

The headless browser could not complete post-login inspection because it reached the app login screen and no credentials were used in this phase. The owner screenshot already confirmed the tab was visible before the packaging fix. The new image now contains the board file that was missing in that screenshot.

Owner should refresh production, sign in, and open `Formula Review`.

## Owner Inspection Checklist

Confirm after refresh:

- `Formula Review` tab opens without the missing-file warning.
- Standard appears first.
- Half PPR, PPR, and GNG Keeper follow.
- Current Pigskin is labeled as the live baseline.
- Enriched Logistic Elite is labeled as review-only challenger.
- Enriched Linear Points is context only.
- No single global winner is shown.
- Missingness warnings remain visible.
- TE owner-review output is capped at TE35.
- No write, export, deploy, ranking-generation, or champion controls appear.

## Recommended V1.0 Formula Policy

Recommended hold:

- Current Pigskin for Standard.
- Current Pigskin for Half PPR.
- Current Pigskin for PPR.
- Current Pigskin for GNG Keeper.
- Enriched Logistic Elite remains review-only challenger for every scoring profile.

If the owner wants to override any profile, use:

`Phase 32.38 - owner champion selection by scoring profile`

## No Live Ranking Mutation

Confirmed:

- No live ranking generation ran.
- `src/generate_pigskin_rankings.py` was not invoked.
- No Gemini call was made.
- No Pigskin chat call was made.
- No live Sleeper API call was made.
- No BQML training ran.
- No source ingest ran.
- No champion formula was activated.
- No write to `analytics_pigskin_rankings`.
- No overwrite of `analytics_pigskin_rankings_candidates`.
- No write to `ranking_formula_champions`.
- No write to `ranking_backtest_results`.
- No global table truncate.

## Remaining Warning

Automated browser verification stopped at the app login screen. The owner needs to refresh the authenticated browser session and confirm the board content renders. The missing runtime file is now packaged in the deployed image.

## Recommended Next Phase

Recommended next:

`Phase 32.38 - Hold Current Pigskin for v1.0`

Alternative next phases:

- `Phase 32.38 - Owner champion selection by scoring profile`
- `Phase 32.38 - Live ranking generation only after explicit champion selection`
