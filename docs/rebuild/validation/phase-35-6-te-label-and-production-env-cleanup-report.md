# Phase 35.6: TE Label and Production Environment Cleanup

## Final decision

**TE LABELS AND PRODUCTION ENV CLEANUP COMPLETE**

## Root cause

The guarded Pigskin review correctly limited rank movement, but the response contract still allowed Gemini to replace deterministic presentation fields. The active Standard TE board had zero rank changes, yet model-authored `tier` and `pigskin_verdict` values mislabeled several top players as watchlist assets and cited unsupported inactive-roster conclusions.

## Source changes

- `src/generate_pigskin_rankings.py` now accepts only adjustment code, requested delta, evidence, detail, and estimated games missed from the model.
- Tier, verdict, rationale, risk flags, and change criteria are copied from the deterministic candidate row.
- `scripts/promote_te_fable_v1a_standard_te.py` seeds deterministic verdict and change-criteria text.
- `scripts/repair_te_fable_v1a_live_labels.py` provides a gated, version-scoped label repair that cannot update rank or score.
- Focused tests prove the model cannot overwrite deterministic presentation fields and the repair SQL excludes rank, score, and adjustment-code assignments.

Source commit: `170e759 Keep Pigskin presentation deterministic`

## Live board repair

Ranking version: `te-fable-guarded-pigskin-20260711010953`

- Rows repaired: 35
- Tier cutlines: elite TE1-TE5, front-line starter TE6-TE12, starter TE13-TE24, flex or matchup TE25-TE35
- Player/rank/score fingerprint before: `7c44f3d6726506718d5cf30ee6f63d7a`
- Player/rank/score fingerprint after: `7c44f3d6726506718d5cf30ee6f63d7a`
- Pigskin audit codes preserved: 32 `NO_ADJUSTMENT`, 3 `INJURY_UNCERTAIN`
- `INJURY_UNCERTAIN` verdicts now state that unresolved preseason injury information has no rank effect.

The repair ran with `ALLOW_TE_FABLE_V1A_STANDARD_TE_PROMOTION=true` only inside the applying PowerShell process. The gate was removed afterward.

## Validation

- `scripts/check_deployment_safety.py`: pass
- Python compile checks: pass
- Focused guardrail and repair tests: 29 passed
- Full suite: 934 passed
- Live TE35 fingerprint check: pass
- Top-row readback: Trey McBride TE1, `elite`, deterministic TE Fable verdict

## Build and deployment

- Build ID: `693ef499-7faa-4b26-a24f-5de9b3a58d12`
- Source SHA: `170e759664b1`
- Image tag: `prod-candidate-170e759664b1-20260711T020256Z`
- Digest: `sha256:7d6bd157ab5c8a7fa02d0cf1c94320db4b9415e024fccac8e367874f19449ead`
- Previous production revision: `nfl-studio-dashboard-00090-5ps`
- New production revision: `nfl-studio-dashboard-00091-rh5`
- Traffic: 100 percent to `nfl-studio-dashboard-00091-rh5`
- Health: `/_stcore/health` returned 200 `ok`; root returned 200 with the Streamlit shell and no traceback text

Rollback command:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services update-traffic nfl-studio-dashboard --project=fantasy-football-498121 --region=us-central1 --to-revisions=nfl-studio-dashboard-00090-5ps=100
```

Rollback was not needed.

## Environment cleanup

Production had three malformed environment names created from prior auth-value parsing. The deployment removed only those malformed names, preserved all valid environment values, and preserved `GEMINI_API_KEY` as a Secret Manager reference. No auth values or secret values are included in this report.

- Malformed environment names before: 3
- Malformed environment names after: 0
- `DATA_OPS_ALLOW_JOB_TRIGGER=false`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER=false`
- `USE_TRADE_ANALYZER_SCORE_V0=false`
- `USE_COMPAT_TRADE_PLAYER_SCORE=false`
- `USE_COMPAT_TRADE_PLAYER_HISTORY=false`
- Deploy authorization gate after rollout: unset

## Production impact

TE ranks and scores did not change. The dashboard now displays formula-owned TE tiers and verdicts. Pigskin remains an auditable exception layer for current role, rookie context, and injuries rather than a free-form presentation author.

## Standard QB next step

Start a focused Standard QB comparison rather than promote an existing challenger immediately. Current evidence names `adv_standard_qb_logistic_bust` and `bqml_v2_standard_qb_logistic_bust_inverse_v0`, but both carry running-QB bias or noise warnings. The first QB phase should compare those lanes against the live Standard QB input board, the prior BQML linear-points lane, and a simple projection baseline with explicit rushing caps and cutline checks at QB6, QB12, and QB24.
