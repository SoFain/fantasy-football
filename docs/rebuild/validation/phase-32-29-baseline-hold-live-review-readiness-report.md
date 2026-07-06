# Phase 32.29: Baseline Hold And Live 2026 Review Readiness

Final decision: **CURRENT PIGSKIN BASELINE HELD**

## Scope

Phase 32.29 closes the current ranking-research loop and prepares the owner path for live 2026 review boards.

This phase did not deploy, regenerate live rankings, activate champions, train BQML models, ingest sources, call Sleeper, call Pigskin chat, call Gemini, run the old Python tournament, write detail rows, write live rankings, or globally truncate tables.

## Files Changed

| File | Change |
|---|---|
| `docs/rebuild/formula-ranking-owner-review-index.md` | Added stable owner decision index for ranking lanes and live 2026 review prerequisites. |
| `docs/rebuild/ranking-algorithm-scorecard.md` | Added Phase 32.29 baseline-hold decision and final lane classifications. |
| `docs/rebuild/ranking-opportunity-metrics-matrix.md` | Added final source status after NGS and BQML NGS retrain. |
| `docs/rebuild/validation/phase-32-29-baseline-hold-live-review-readiness-report.md` | This report. |

Commit hash: Phase 32.29 package commit recorded by `git log -1 --oneline` after packaging.

## Git State

Before Phase 32.29:

- Latest commit: `038a6c8 phase 32.28 retrain bqml ngs challengers`.
- Working tree contained the known untracked historical validation backlog.
- No Phase 32.28 tracked changes were left uncommitted.

After documentation edits:

- New/modified files are limited to the Phase 32.29 docs listed above.
- Historical validation backlog files remain untracked and were not staged.

## Final Classification Table

| Lane | Classification | Decision |
|---|---|---|
| Current Pigskin candidate score v1 plus LLM final rankings | live baseline | Keep live. |
| Simple projection | owner-review signal | Use as a basic challenger and sanity check. |
| Enriched BQML logistic elite v1 | owner-review signal | Best top-N, VOR, NDCG, and bust-control review signal. |
| Enriched BQML linear points v1 | owner-review signal | Best BQML board-ordering review signal. |
| BQML NGS logistic elite v1 | context only | Flat to enriched logistic. Not a promotion lane. |
| BQML NGS linear points v1 | context only | Did not improve materially over enriched linear points. |
| BQML boosted tree VOR lanes | context only | Useful nonlinear check, but unstable and costlier. |
| Stats02 WR/TE | component signal | Useful position-specific context, not a default formula. |
| PBP RB/WR | component signal | RB high-value opportunity is useful. WR movement remains fragile. |
| NGS direct diagnostics | component signal | RB rushing NGS is the clearest additive NGS component. |
| Injury and availability | risk flag only | Display as low-weight risk context. Do not promote as a formula. |
| Historical depth | blocked | Source still lacks historical season/week role context. |
| Sleeper current context | live-only display/context | Use for live display only. Never use as historical backtest input. |

## Current Baseline Hold Decision

Current Pigskin remains live.

Reasons:

- No champion formula is active.
- No current evidence supports replacing current Pigskin.
- BQML and NGS remain review signals, not production defaults.
- Availability remains a risk flag only.
- WR movement risk still blocks automatic model promotion.

## No-Change Verification

Read-only BigQuery checks:

| Object | Result |
|---|---:|
| `analytics_pigskin_rankings` active rows | 1,140 |
| Active scoring profiles | 4 |
| Active model runs | 4 |
| Latest active ranking timestamp | `2026-07-04T07:29:22.569631Z` |
| `ranking_formula_champions` rows | 0 |
| Active champion rows | 0 |
| Enriched BQML v1 summary rows | 128 |
| BQML NGS v1 summary rows | 128 |
| `sleeper_player_context_current` rows | 12,200 |
| Sleeper latest snapshot timestamp | `2026-07-05T17:52:48.174830Z` |

Active ranking shape:

| Scoring profile | QB | RB | WR | TE |
|---|---:|---:|---:|---:|
| `ppr` | 45 | 80 | 100 | 60 |
| `half_ppr` | 45 | 80 | 100 | 60 |
| `standard` | 45 | 80 | 100 | 60 |
| `gng_keeper` | 45 | 80 | 100 | 60 |

Latest active ranking versions:

| Scoring profile | Ranking version |
|---|---|
| `ppr` | `pigskin-llm-20260703061257` |
| `half_ppr` | `pigskin-llm-20260704070315` |
| `standard` | `pigskin-llm-20260704071412` |
| `gng_keeper` | `pigskin-llm-20260704072119` |

## Live 2026 Review-Board Readiness

Current repo path:

- Player Profiles read active rankings through `src/player_profile_ranking_profiles.py`.
- Current production ranking generation reads `analytics_pigskin_rankings_candidates` in `src/generate_pigskin_rankings.py`, calls Gemini, and writes `analytics_pigskin_rankings` plus history.
- That production generator is not the right path for review-only boards.
- Existing BQML prediction helpers in `src/ranking_formula_backtests.py` are historical-evaluation helpers and require labeled rows with outcomes.

Current warehouse state:

| Source | State |
|---|---|
| `analytics_pigskin_rankings_candidates` | 936 PPR candidate rows for 2026. |
| `ranking_backtest_feature_mart` | 2025 target slices exist for all four scoring profiles. No 2026 target slice returned. |
| Review-only ranking table | Not present. |
| Sleeper current context | Available for display-only live context. |

Readiness decision:

- Baseline side is partially ready because `analytics_pigskin_rankings` and `analytics_pigskin_rankings_candidates` have current 2026 ranking/candidate evidence.
- BQML challenger side is not ready until a 2026 outcome-free prediction input exists.
- Review boards can be generated safely only by a separate read-only path that avoids Gemini, avoids live ranking writes, and avoids champion writes.

## Required Inputs For Live 2026 Review Boards

Required fields:

- Player identity.
- Position eligibility.
- Scoring profile.
- Current Pigskin baseline rank and score.
- BQML logistic score and rank, if produced from a safe 2026 input.
- BQML linear points score and rank, if produced from a safe 2026 input.
- Availability, injury burden, and missed-time risk flags.
- NGS feature signals where source-backed.
- Sleeper current team, status, depth position, and depth order as display-only fields.
- Source freshness timestamps.
- Missing flags.

Required implementation work:

1. Build an outcome-free 2026 prediction input for `ML.PREDICT`.
2. Ensure that input uses only pre-2026 historical features plus current display context that is explicitly marked display-only.
3. Generate review-only BQML ranks without writing to `analytics_pigskin_rankings`.
4. Join current Pigskin baseline ranks and scores.
5. Join Sleeper current context as display-only fields with freshness.
6. Output Markdown or a dedicated owner-review table only after owner approval.

## Sleeper Live-Context Guardrails

Sleeper current context:

- Can be used only for live 2026 display/context.
- Must not be used as historical backtest truth.
- Must show freshness.
- Must not silently fall back to stale identity team when `sleeper_current_team` is null.
- Must preserve the Tyreek-style stale-team guardrail.

## Rejected And Default-No Lanes

| Lane | Decision |
|---|---|
| Generic 5 percent availability blend | Rejected as default. |
| v2 trend-aware champion path | Rejected. |
| Broad ensembles | Rejected for now. |
| Injury-only candidates | Rejected. |
| Historical depth | Blocked. |
| Sleeper current context as historical input | Blocked. |

## Owner Decision Summary

Hold current Pigskin.

Keep enriched BQML logistic elite and enriched BQML linear points as the two useful challenger lanes for owner review. Treat NGS, Stats02, PBP, and availability as component or risk context. Do not activate a champion.

## Recommended Next Phase

Recommended: **Phase 32.30 - Live 2026 review-board generation, review-only**.

That phase should build the outcome-free 2026 review input and produce owner-readable review boards without touching live rankings or champions.

Alternate next phases:

- Phase 32.30 - Formula comparison dashboard in app, read-only.
- Phase 32.30 - Hold current Pigskin baseline.

## Checks Run

Read-only and doc-only checks:

```powershell
git status --short
git log -5 --oneline
rg -n -m 30 "analytics_pigskin_rankings|scoring_profile_id|Player Profiles|pigskin_rankings|ranking" app.py src docs\rebuild
```

Read-only BigQuery checks:

- `analytics_pigskin_rankings` active counts by scoring profile and position.
- `ranking_formula_champions` total and active counts.
- `ranking_backtest_candidate_summaries` enriched BQML and BQML NGS summary counts.
- `sleeper_player_context_current` freshness and row count.
- `ranking_backtest_feature_mart` 2025/2026 target-season availability.
- `analytics_pigskin_rankings_candidates` current candidate slice availability.

Final markdown check to run before packaging:

```powershell
git diff --check
```

## Confirmations

- No live ranking table writes occurred.
- No champion activation occurred.
- No `ranking_backtest_results` detail rows were written.
- No BQML models were trained.
- No source ingest occurred.
- No deployment occurred.
- No Sleeper API call occurred.
- No Pigskin chat call occurred.
- No Gemini or LLM call occurred.

## Remaining Warnings

- There is no 2026 `ranking_backtest_feature_mart` target slice.
- The existing BQML prediction helper expects historical outcome labels, so it cannot directly serve live 2026 review boards.
- `analytics_pigskin_rankings_candidates` is PPR-only for the 2026 candidate slice observed in this phase.
- Sleeper current context has many null current-team values; the UI or report must show unknown/null instead of falling back to stale identity team.
- Historical validation backlog files remain untracked for owner review.
