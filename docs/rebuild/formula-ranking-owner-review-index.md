# Formula Ranking Owner Review Index

Last updated: 2026-07-06

## Current Decision

Current Pigskin stays live.

No formula champion is active. No BigQuery ML, NGS, injury, PBP, or Stats02 lane should replace current Pigskin without a separate owner-approved champion-selection phase and a separate live ranking generation phase.

Phase 32.38 v1.0 studio defaults:

- Live scoring default: `standard`.
- Live board default: `ALL`.
- Live ranking source: `analytics_pigskin_rankings` active Current Pigskin rows.
- Live depth: QB45, RB80, WR100, TE35 per scoring profile.
- Formula Review remains read-only owner-review evidence.
- Pigskin chat has static read-only formula context for defending Current Pigskin ranks.

## Live Baseline

| Lane | Status | Use |
|---|---|---|
| Current Pigskin candidate score v1 plus LLM final rankings | live baseline | Keep as the production ranking source. Active rankings currently cover PPR, Half PPR, Standard, and GNG Keeper. |

Active ranking state:

- `analytics_pigskin_rankings`: 1,040 active rows.
- Positions per profile: QB 45, RB 80, WR 100, TE 35.
- Active scoring profiles: `ppr`, `half_ppr`, `standard`, `gng_keeper`.
- Latest active generation timestamp: `2026-07-04T07:29:22.569631Z`.
- Current live TE depth is now 35 rows per scoring profile after the owner-approved Phase 32.37 active-row update.

## Challenger Lanes

| Lane | Classification | Owner-read |
|---|---|---|
| Simple projection | owner-review signal | Strong basic benchmark. It remains useful as a sanity check, not a replacement. |
| Enriched BQML logistic elite v1 | owner-review signal | Best top-N, VOR, NDCG, and bust-control review lane from the enriched family. Overall pairwise weakness blocks promotion. |
| Enriched BQML linear points v1 | owner-review signal | Best board-ordering BQML lane. Good pairwise and overall board read, but not enough to replace current Pigskin. |
| BQML NGS logistic elite v1 | context only | Essentially flat to enriched logistic. Keep as NGS context, not a new challenger leader. |
| BQML NGS linear points v1 | context only | Did not improve materially over enriched linear points. |
| BQML boosted tree VOR lanes | context only | NGS boosted tree improved 2025 holdout VOR/NDCG but regressed on 2024 validation and cost more to train. |
| Stats02 WR/TE | component signal | Useful ideal-stat component evidence. Do not let it own rankings. |
| PBP RB/WR | component signal | RB has useful high-value opportunity signal. WR movement still needs protection. |
| NGS direct diagnostics | component signal | RB rushing NGS is the clearest additive component. WR/TE receiving NGS helps explain movement. |

## Risk Flags

| Lane | Classification | Owner-read |
|---|---|---|
| Injury availability | risk flag only | Keep as low-weight context. It is not a default formula. |
| Injury burden | risk flag only | Useful warning field, not a ranking driver. |
| Missed-time risk | risk flag only | Display as context when source freshness is clear. |

## Rejected Or Blocked

| Lane | Classification | Reason |
|---|---|---|
| Generic 5 percent availability blend | rejected | Over-penalization risk and weak cutline proof. |
| v2 trend-aware champion path | rejected | Underperformed after the full backtest expansion. |
| Broad ensembles | rejected | Did not clear the owner-review threshold. |
| Injury-only candidates | rejected | Too sparse and not causally strong enough. |
| Historical depth context | blocked | Source still lacks the required historical season/week context. |
| Sleeper current context as historical input | blocked | Sleeper current context is live display context only. It cannot be historical truth. |

## Source Status

| Source | Status | Use |
|---|---|---|
| `analytics_pigskin_rankings` | active | Live Player Profiles ranking output. |
| `analytics_pigskin_rankings_candidates` | active 2026 PPR candidate slice | Baseline candidate evidence only. Future review boards must not call Gemini or write live rankings. |
| `ranking_backtest_feature_mart` | active through target season 2025 | Historical BQML/backtest feature source. No 2026 feature slice exists yet. |
| `ranking_backtest_candidate_summaries` | active summary evidence | Contains enriched BQML v1 and BQML NGS v1 summaries. |
| `player_week_ngs_metrics` | active | Direct NGS component source. |
| `sleeper_player_context_current` | active | Live-current display context only. Latest snapshot: `2026-07-05T17:52:48.174830Z`. |

## Live 2026 Review Board Requirements

A safe live 2026 review board needs:

- Player identity and position eligibility.
- Scoring profile.
- Current Pigskin rank and score.
- Review-only BQML logistic score and rank, if generated from a 2026 prediction input.
- Review-only BQML linear points score and rank, if generated from a 2026 prediction input.
- Risk flags for availability, injury burden, and missed-time risk.
- NGS feature signals where source-backed.
- Sleeper current team, status, depth position, depth order, and freshness as display-only fields.
- Source freshness and missing flags shown beside model outputs.

Review-board target shape:

| Position | Owner-review board depth |
|---|---:|
| QB | 45 |
| RB | 80 |
| WR | 100 |
| TE | 35 |

TE owner-review output rules:

- Cap TE position boards, TE movement tables, display limits, and owner-facing summaries at TE35.
- Still include TE6, TE12, and TE18 cutline crossings.
- Do not generate owner-review TE tables beyond TE35 unless a missingness or debug note requires it.
- Phase 32.37 reduced active `analytics_pigskin_rankings` TE rows from 60 to 35 per scoring profile.

Current constraints:

- Phase 32.32 generated CTE-only 2026 review inputs for Standard, Half PPR, PPR, and GNG Keeper. The production candidate table remains PPR-only by design.
- The review universe is not persisted. Phase 32.33 uses the committed Markdown review boards as the dashboard source.
- Live ranking generation, champion activation, and TE depth reduction still need separate owner approval.

## Sleeper Live-Context Guardrails

- Use Sleeper current context only for live 2026 display and review.
- Do not use Sleeper current context as historical backtest input.
- Show `snapshot_at` or equivalent freshness.
- If `sleeper_current_team` is null, show null or unknown.
- Do not silently fall back to stale identity team as current team. The Tyreek-style stale-team guardrail still applies.

## Latest Evidence

- [Phase 32.37 emergency Formula Review owner-review enablement](validation/phase-32-37-v1-owner-review-enable-report.md)
- [Phase 32.36 owner inspection checklist](validation/phase-32-36-owner-inspection-checklist.md)
- [Phase 32.36 dashboard owner inspection support](validation/phase-32-36-dashboard-owner-inspection-support-report.md)
- [Phase 32.35 Formula Review dashboard enablement](validation/phase-32-35-formula-review-dashboard-enable-report.md)
- [Phase 32.32 non-PPR review candidate universe](validation/phase-32-32-non-ppr-review-candidate-universe-report.md)
- [Phase 32.34 Formula Review dashboard smoke](validation/phase-32-34-formula-review-dashboard-smoke-report.md)
- [Phase 32.33 formula comparison dashboard](validation/phase-32-33-formula-comparison-dashboard-report.md)
- [Phase 32.31 scoring-profile review input audit](validation/phase-32-31-scoring-profile-review-inputs-report.md)
- [Phase 32.30 live 2026 review boards](validation/phase-32-30-live-2026-review-board-report.md)
- [Phase 32.28 BQML NGS retrain](validation/phase-32-28-bqml-ngs-retrain-report.md)
- [Phase 32.27 direct NGS metrics](validation/phase-32-27-ngs-direct-metrics-report.md)
- [Phase 32.26 BQML candidate rankings](validation/phase-32-26-bqml-candidate-rankings-owner-review-report.md)
- [Phase 32.25 BQML owner-review cutlines](validation/phase-32-25-bqml-owner-review-cutlines-report.md)
- [Ranking algorithm scorecard](ranking-algorithm-scorecard.md)
- [Ranking opportunity metrics matrix](ranking-opportunity-metrics-matrix.md)

## Recommended Next Action

Recommended: studio use with Current Pigskin held for v1.0.

The owner can now review the Formula Review tab. Any next phase should stay profile-specific and avoid one global winner across scoring systems.

Alternate: create review-only table persistence if sortable, durable dashboard data is needed. Do not make it a production ranking source.

Owner action choices:

- Inspect the Formula Review tab after enabling `USE_FORMULA_COMPARISON_DASHBOARD=true`.
- Hold current Pigskin.
- Select a review-only challenger separately by scoring profile.
- Request review-only table persistence if Markdown-backed dashboard data is not enough.
- Approve live ranking generation only after explicit champion selection.

## Phase 32.38 V1.0 Live Defaults

Owner-approved v1.0 policy:

| scoring_profile_id | QB | RB | WR | TE |
|---|---|---|---|---|
| `standard` | Current Pigskin | Current Pigskin | Current Pigskin | Current Pigskin |
| `half_ppr` | Current Pigskin | Current Pigskin | Current Pigskin | Current Pigskin |
| `ppr` | Current Pigskin | Current Pigskin | Current Pigskin | Current Pigskin |
| `gng_keeper` | Current Pigskin | Current Pigskin | Current Pigskin | Current Pigskin |

No profile-position challenger was promoted for v1.0. Enriched Logistic Elite remains review-only challenger evidence. Enriched Linear Points and BQML NGS remain context only. Stats02, PBP, and NGS remain component signals. Injury and availability remain risk flags.

Player Profiles defaults:

- Scoring system: `standard`.
- Position board: `ALL`.
- `ALL` sorts active Current Pigskin rows as one cross-position board by Pigskin score, then position rank, position, and player name.

Pigskin chat formula context:

- Static source: `docs/rebuild/pigskin-live-ranking-formula-context.md`.
- Context is read-only and packaged into the Cloud Run image.
- It does not expose backtest, champion, ranking-generation, or write controls.

Production deploy:

- Revision: `nfl-studio-dashboard-00086-wpx`.
- Image digest: `sha256:6f443eb45e42409510885c44592c3b303cdfd0fbba531ba9c61ceec8f1a69ceb`.
- Health endpoint: `200 ok`.
- Rollback baseline: `nfl-studio-dashboard-00085-6v4`.

## Phase 32.37 Emergency Formula Review Packaging Fix

The owner screenshot showed the `Formula Review` tab was visible in production, but the tab could not load the review boards because the deployed image did not contain:

`/app/docs/rebuild/live-2026-ranking-review-boards.md`

Emergency fix:

- Commit: `428edf8 package formula review board source`.
- New production revision: `nfl-studio-dashboard-00085-6v4`.
- New image digest: `sha256:8bfaee3a2a1e54b5d78ed1ac676ebfeb4b9531e1078b08120f84d7f5b4fbaffb`.
- `USE_FORMULA_COMPARISON_DASHBOARD=true` remains enabled.
- Data Ops trigger flags remain false.
- Trade Analyzer score flags remain false.
- Production Pigskin historical packet tool remains unset.
- Health endpoint returned `200 ok`.

Owner decision choices:

- Hold Current Pigskin for all scoring profiles.
- Select a challenger by scoring profile in a separate Phase 32.38.
- Request more review before any champion-selection or ranking-generation work.

V1.0 default recommendation:

- Current Pigskin for `standard`.
- Current Pigskin for `half_ppr`.
- Current Pigskin for `ppr`.
- Current Pigskin for `gng_keeper`.
- Enriched Logistic Elite remains review-only challenger.

No formula champion was activated. No live ranking generation ran. No live ranking tables were written in the emergency packaging fix.

## Phase 32.37 Production Dashboard And TE35 Result

Phase 32.37 deployed a new production revision with the Formula Review dashboard code and applied the owner-approved TE35 production depth change.

Runtime state:

- Service: `nfl-studio-dashboard`.
- Revision: `nfl-studio-dashboard-00084-9z5`.
- URL: `https://nfl-studio-dashboard-inypcgbx7a-uc.a.run.app`.
- Image digest: `sha256:d0af08ee49858ab6230fea9b0ab6504a12043cc7066d0f76c79fb84f8b723f7d`.
- Flag: `USE_FORMULA_COMPARISON_DASHBOARD=true`.
- Data Ops trigger flags remain false.
- Trade Analyzer score flags remain false.
- Production Pigskin historical packet tool remains unset.
- Health endpoint returned `200 ok`.

TE depth state:

- Active total rows: 1,040.
- Active shape per scoring profile: QB45, RB80, WR100, TE35.
- TE ranks 36 through 60 were marked inactive for `standard`, `half_ppr`, `ppr`, and `gng_keeper`.
- No rows were deleted.
- No ranking generation ran.
- No formula champion is active.

Owner action choices:

- Inspect the Formula Review tab.
- Inspect TE35 Player Profiles depth for each scoring profile.
- Hold Current Pigskin.
- Select a challenger by scoring profile in a separate phase.
- Request review-only table persistence.
- Approve live ranking generation only after explicit champion selection.

## Phase 32.36 Owner Inspection Support

Phase 32.36 committed the Phase 32.35 enablement docs as `a6c3ae4 phase 32.35 enable formula review dashboard`.

Read-only production verification:

- Service: `nfl-studio-dashboard`.
- Revision: `nfl-studio-dashboard-00083-tlr`.
- URL: `https://nfl-studio-dashboard-inypcgbx7a-uc.a.run.app`.
- Flag: `USE_FORMULA_COMPARISON_DASHBOARD=true`.
- Data Ops trigger flags remain false.
- Trade Analyzer score flags remain false.
- Production Pigskin historical packet tool remains unset.
- Health endpoint returned `200 ok`.

Owner checklist:

- [Phase 32.36 owner inspection checklist](validation/phase-32-36-owner-inspection-checklist.md)

The owner should inspect the Formula Review tab while signed in, then choose one action per scoring profile: hold Current Pigskin, continue owner review, request challenger selection, request more evidence, or reject the BQML challenger for that profile.

Separate decisions remain separate: review-only table persistence, production TE depth change from TE60 to TE35, and live ranking generation after explicit champion selection.

## Phase 32.35 Dashboard Enablement Result

Phase 32.35 enabled the read-only Formula Review dashboard in the production Cloud Run service.

Runtime state:

- Service: `nfl-studio-dashboard`.
- Revision: `nfl-studio-dashboard-00083-tlr`.
- URL: `https://nfl-studio-dashboard-inypcgbx7a-uc.a.run.app`.
- Flag: `USE_FORMULA_COMPARISON_DASHBOARD=true`.
- Image digest unchanged from the prior production revision.
- Data Ops trigger flags remain false.
- Production Pigskin historical packet tool remains unset.
- Trade Analyzer score flags remain false.

Owner inspection:

- Sign in to the production app.
- Open the `Formula Review` tab.
- Review each scoring profile separately in this order: `standard`, `half_ppr`, `ppr`, `gng_keeper`.
- Treat all-profile aggregate as context only.
- Do not select one global winner averaged across scoring systems.

Next owner choices:

- Hold current Pigskin.
- Select a review-only challenger separately by scoring profile.
- Request review-only table persistence.
- Request production TE depth change as a separate phase.
- Approve live ranking generation only in a separate explicit phase.

## Phase 32.34 Dashboard Smoke Result

Phase 32.34 committed the Phase 32.33 dashboard package and smoke-tested the local dashboard contract.

Activation:

- Exact flag: `USE_FORMULA_COMPARISON_DASHBOARD`.
- Default: off when unset or false.
- Enabled value: `true`.
- Local smoke set the flag only inside the command process and removed it afterward.
- Cloud Run or Streamlit runtime activation requires setting the environment variable and restarting/redeploying the app process.

Smoke result:

- Standard is first.
- Half PPR, PPR, and GNG Keeper are visible after Standard.
- Current Pigskin remains the live baseline.
- Enriched Logistic Elite is review-only challenger for every scoring profile.
- Enriched Linear Points is context only.
- No global winner is displayed.
- TE owner-review output remains capped at TE35 with TE6, TE12, and TE18 cutlines present.
- Missingness warnings remain visible.

## Phase 32.33 Dashboard Result

Phase 32.33 added a read-only Formula Review tab behind `USE_FORMULA_COMPARISON_DASHBOARD`.

Dashboard source:

- Static committed Markdown: `docs/rebuild/live-2026-ranking-review-boards.md`.
- No BigQuery runtime query is required by the dashboard.
- No live ranking table, candidate table, champion table, backtest detail table, Gemini path, Pigskin chat path, Sleeper API call, or production ranking generator path is invoked.

Owner-review state:

| Scoring profile | Dashboard status | Best review-only challenger | Current decision |
|---|---|---|---|
| `standard` | ready with warnings | `ranking_bqml_enriched_logistic_elite_v1` | Current Pigskin holds. |
| `half_ppr` | ready with warnings | `ranking_bqml_enriched_logistic_elite_v1` | Current Pigskin holds. |
| `ppr` | ready with warnings | `ranking_bqml_enriched_logistic_elite_v1` | Current Pigskin holds. |
| `gng_keeper` | ready with warnings | `ranking_bqml_enriched_logistic_elite_v1` | Current Pigskin holds. |

The dashboard defaults to Standard first, caps owner-review TE output at TE35, keeps TE6, TE12, and TE18 cutlines visible, and labels Enriched Linear Points as context only. Missingness warnings remain visible beside model scores.

## Phase 32.30 Review Result

Phase 32.30 generated PPR-only live 2026 review boards:

- [Phase 32.30 report](validation/phase-32-30-live-2026-review-board-report.md)
- [Live 2026 ranking review boards](live-2026-ranking-review-boards.md)

Owner-review scoring profile order:

1. `standard`
2. `half_ppr`
3. `ppr`
4. `gng_keeper`

Do not choose one global challenger by averaging all scoring profiles. Pick or reject challengers separately by scoring profile. All-profile aggregate reads are stability/context only.

Phase 32.30 profile status:

| Scoring profile | Board status | Best review-only challenger |
|---|---|---|
| `standard` | blocked in Phase 32.30 | none |
| `half_ppr` | blocked in Phase 32.30 | none |
| `ppr` | generated with warnings | `ranking_bqml_enriched_logistic_elite_v1` |
| `gng_keeper` | blocked in Phase 32.30 | none |

Main warning: the available 2026 candidate slice is PPR-only, so Standard, Half PPR, and GNG Keeper review boards were not generated and must not silently fall back to PPR.

## Champion Activation Requirements

Before any champion activation:

- Owner selects the challenger lane.
- A separate champion-selection phase writes `ranking_formula_champions`.
- A separate live ranking phase generates rankings.
- Production exposure, if any, gets its own gate and rollback plan.
