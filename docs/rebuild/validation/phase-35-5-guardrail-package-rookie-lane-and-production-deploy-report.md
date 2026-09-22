# Phase 35.5 Guardrail Package, Rookie Lane, And Production Deploy Report

## Final Decision

`GUARDED TE FABLE PACKAGE DEPLOYED; ROOKIE REVIEW LANE READY`

## Release Package

- Commit: `c268868 Promote guarded TE Fable rankings`.
- Commit SHA: `c2688689a006`.
- Package files: 27.
- Package includes TE Fable formula/views, deterministic promotion, guarded Pigskin adjudication, adjustment audit migration, Player Profiles code/evidence display, focused tests, owner-review index, and Phase 35.2 through 35.4 reports.
- Historical Phase 33 backlog, WR/RB research backlog, output files, browser artifacts, logs, secrets, and unrelated job work were excluded.
- Pre-existing staged Phase 33 files remained outside the commit.

## Verification

- Deployment safety checker: pass.
- App and changed Python compilation: pass.
- Full suite: 929 tests passed.
- Clean-worktree focused suite: 46 tests passed.
- Pending migrations: none.
- Validation discovery: pass through validation 245.
- Firebase and tracked-secret checks: pass.

One stale full-suite safety failure was found and corrected before commit. Formula Review help text named internal formula warehouse tables even though it did not expose them as tools. The copy now states the boundary without naming those tables.

## Clean Build

- Clean detached worktree: commit `c2688689a006`.
- Image tag: `prod-candidate-c2688689a006-20260711T014716Z`.
- Build ID: `93e45918-6930-4faa-81cc-52adab9bdbf4`.
- Build status: `SUCCESS`.
- Digest: `sha256:dcf096d06c446844d7b8f22763749dc3c62beda1bfb51574d38de053c27d7506`.
- Digest-pinned image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:dcf096d06c446844d7b8f22763749dc3c62beda1bfb51574d38de053c27d7506`.

## Production Deploy

- Service: `nfl-studio-dashboard`.
- Region: `us-central1`.
- Prior revision: `nfl-studio-dashboard-00088-dhk`.
- Final revision: `nfl-studio-dashboard-00090-5ps`.
- Traffic: 100% to `nfl-studio-dashboard-00090-5ps`.
- Service account: `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com`.
- URL: `https://nfl-studio-dashboard-583607027760.us-central1.run.app`.

The first local deploy wrapper timed out after Cloud Run accepted its request, creating healthy revision `00089-wjv`. A controlled retry created `00090-5ps`, which is the only revision receiving traffic. Both use the same digest.

The deploy changed only the image and service account declaration. Existing environment variables, Secret Manager bindings, and service access policy were preserved.

## Postdeploy Checks

- `/_stcore/health`: HTTP 200, `ok`.
- `/`: HTTP 200.
- Streamlit shell: present.
- Traceback in response: absent.
- `APP_AUTH_ENABLED=true`.
- Formula Review dashboard remains enabled.
- Data Ops Cloud Run trigger flags: false.
- Data Ops local subprocess trigger: false.
- Trade score flags: false.
- Trade History compatibility: false.
- Deploy authorization gate after run: unset.

Rollback command:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services update-traffic nfl-studio-dashboard --project=fantasy-football-498121 --region=us-central1 --to-revisions=nfl-studio-dashboard-00088-dhk=100
```

No rollback was needed.

## Rookie TE Lane

View: `fantasy-football-498121.fantasy_football_advanced_metrics.v_te_fable_v1a_rookie_candidates`.

- Total candidates: 49.
- Current-role TE1: 1.
- Current-role TE2: 5.
- Deeper current role: 16.
- Incomplete current role: 27.
- Formula scores: all null by contract.
- Live TE35 writes: none.

Kenyon Sadiq is first in the review queue because Sleeper currently lists him as NYJ TE1. He remains unranked by formula because GSIS identity, approved draft capital, and college-production inputs are missing. Questionable status has zero preseason ranking effect.

## Warning

Production baseline inspection found malformed legacy auth-related environment entries alongside the intended `APP_AUTH_USERS` setting. Secret values are not reproduced here. They were preserved to avoid changing authentication during this deploy. A separate authentication cleanup phase should remove malformed keys and implement the signed-cookie session design already recorded in the deployment checklist.
