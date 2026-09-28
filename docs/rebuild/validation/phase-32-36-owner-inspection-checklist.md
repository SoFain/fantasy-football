# Phase 32.36 Owner Inspection Checklist

Use this checklist while reviewing the production Formula Review tab.

Production URL:

- `https://nfl-studio-dashboard-inypcgbx7a-uc.a.run.app`

Expected runtime state:

- Service: `nfl-studio-dashboard`
- Revision: `nfl-studio-dashboard-00083-tlr`
- Flag: `USE_FORMULA_COMPARISON_DASHBOARD=true`
- Dashboard tab: `Formula Review`
- Source: `docs/rebuild/live-2026-ranking-review-boards.md`

## Access

- [ ] Log in successfully.
- [ ] Confirm the app opens without traceback.
- [ ] Confirm the `Formula Review` tab is visible.

## Profile Order

- [ ] Standard appears first.
- [ ] Half PPR appears after Standard.
- [ ] PPR appears after Half PPR.
- [ ] GNG Keeper appears after PPR.

Do not choose one global winner averaged across the scoring systems. Review each scoring profile separately.

## Required Labels

- [ ] Current Pigskin is labeled as the live baseline.
- [ ] Enriched Logistic Elite is labeled as review-only challenger.
- [ ] Enriched Linear Points is labeled as context only.
- [ ] BQML NGS is context only.
- [ ] Injury and availability fields are risk flags only.
- [ ] Sleeper current context is display-only.
- [ ] Historical depth is blocked.

## Guardrails

- [ ] No global winner is shown.
- [ ] Missingness warnings are visible.
- [ ] WR movement warnings are visible.
- [ ] `pigskin_context_score` is not required or fabricated.
- [ ] No write, export, deploy, ranking-generation, champion-selection, Gemini, Pigskin chat, Sleeper API, or Cloud Run Job controls appear in the tab.

## TE Review Depth

- [ ] TE board output is capped at TE35.
- [ ] TE6 cutline is visible.
- [ ] TE12 cutline is visible.
- [ ] TE18 cutline is visible.
- [ ] Live TE60 ranking rows are not described as changed.

## Owner Decision Form

For each scoring profile, choose one:

| Scoring profile | Hold Current Pigskin | Continue owner review | Request challenger selection phase | Request more evidence | Reject BQML challenger |
|---|---|---|---|---|---|
| `standard` | [ ] | [ ] | [ ] | [ ] | [ ] |
| `half_ppr` | [ ] | [ ] | [ ] | [ ] | [ ] |
| `ppr` | [ ] | [ ] | [ ] | [ ] | [ ] |
| `gng_keeper` | [ ] | [ ] | [ ] | [ ] | [ ] |

Separate owner decisions:

- [ ] Hold all changes.
- [ ] Request review-only table persistence.
- [ ] Request production TE depth change from TE60 to TE35 as a separate phase.
- [ ] Request live ranking generation only after explicit champion selection.

## Next Phase Options

- Phase 32.37, hold Current Pigskin baseline.
- Phase 32.37, owner selection by scoring profile.
- Phase 32.37, review-only table persistence.
- Phase 32.37, production TE depth change only after explicit owner approval.
- Phase 32.37, live ranking generation only after explicit champion selection.
