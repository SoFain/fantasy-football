# Phase 38.1 GNG Formula Hypothesis Research Log

## Status

`COMPLETE — FIVE HYPOTHESES BACKTESTED, NO PRODUCTION PROMOTION`

This log is the restart point for GNG formula research. The five-way screen is complete. Do not promote a GNG board until the position-specific challengers pass the player-level audit.

The original H3-H5 values below used BigQuery's null percentile ordering. Phase 38.2 supersedes those advanced values with weight renormalization over present inputs and contains the final shortlist decisions.

## Authoritative Scoring

Source: `docs/scoring/gng-keeper-sleeper-scoring-2026.md`, league `1369406895588143104`.

Important differences from Standard/PPR:

- 0.02 passing points per yard, 5 per passing TD, -2 interceptions, -1 sacks.
- Completion, long-TD, and 300/400-yard passing bonuses.
- 0.04 rushing/receiving points per yard.
- 0.1 base reception, plus 0.1 WR and 0.2 TE bonuses.
- Rushing and receiving first downs score 0.1.
- Long-play, attempt, and yardage bonuses apply.
- Return yards score.

Historical `gng_keeper` player outcomes are populated for 2022-2025. The live positional boards remain `pigskin-llm-20260704072119` until this research finishes.

## Five Predeclared Hypotheses

### H1 — Locked Fable Transfer

Use the locked Standard Fable positional score unchanged and retarget evaluation to next-season GNG points. Purpose: establish how much existing opportunity/efficiency structure transfers before adding GNG-specific terms.

### H2 — Low-Reception RB Shift

Shift 1-5% from non-garbage-time touches to target share while preserving total weight. Expected winner: 1-2%, because GNG receptions are worth less than PPR but receiving first downs and positional reception bonuses still matter.

### H3 — GNG Weighted Opportunity

Use `adv_weighted_opportunity_gng_keeper_3yr` as the primary opportunity signal, combined with standard production history. This metric prices red-zone targets, other targets, red-zone carries, and other carries with GNG-specific coefficients.

### H4 — Bonus and First-Down Efficiency

Add source-backed first-down rate, explosive/long-play opportunity, red-zone/goal-line usage, passing efficiency, and profile-specific points. Test separately by position. Do not fabricate unsupported bonus events.

### H5 — Stability Hybrid

Blend GNG profile points and weighted opportunity with offensive snap share, role stability, availability, and position-specific advanced efficiency. This is the broad all-metric hypothesis and must report missingness by feature family.

## Metric Families In Scope

Standard/profile metrics:

- prior GNG points and PPG
- games played and availability
- carries, targets, receptions, yards, touchdowns
- WOPR, target share, carry share
- red-zone and goal-line opportunities

Advanced metrics:

- `adv_weighted_opportunity_gng_keeper_3yr`
- passing EPA, EPA/attempt, EPA/dropback, CPOE
- QB rushing baseline and rushing EPA
- rushing EPA/carry and available NGS rushing fields
- receiving EPA/target and receiving first-down rate
- air-yards share, RACR, aDOT, red-zone targets
- offensive snap share and snap-role stability
- availability context

Every hypothesis must preserve null/missing flags. Zero-filling is allowed only where the existing feature contract explicitly does so and the missingness audit remains visible.

## Completed Transfer Results

| Candidate | Spearman | Pairwise | Top 12 | Top 24 | Points@12 | Points@24 | NDCG@24 | Elite misses | Busts |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| RB H1 base | 0.708 | 0.759 | 0.611 | 0.722 | 0.812 | 0.863 | 0.823 | 6 | 3 |
| **RB H2 1% shift** | **0.709** | **0.759** | **0.611** | **0.722** | 0.819 | **0.863** | **0.825** | **6** | **2** |
| RB H2 2% shift | 0.709 | 0.759 | 0.611 | 0.722 | **0.821** | **0.863** | 0.824 | 6 | 2 |
| WR H1 base | 0.719 | 0.761 | 0.583 | 0.625 | **0.906** | 0.883 | 0.839 | 10 | 2 |
| TE H1 base | 0.670 | 0.741 | 0.528 | **0.792** | 0.808 | **0.886** | **0.879** | 6 | **0** |

RB damage begins at 3%: top-24 precision falls to 0.708, points@24 to 0.847, and elite misses rise to seven. H2 currently selects 1% because it has the best NDCG and pairwise result while preserving the broad board. The 2% variant is the top-12-points challenger.

## Advanced Hypothesis Results

Three leakage-safe folds were evaluated: 2022 to 2023, 2023 to 2024, and 2024 to 2025. The values below are fold averages. Misses and busts are three-fold totals.

| Pos | Candidate | Spearman | Pairwise | Top 12 | Top 24 | Points@12 | Points@24 | NDCG@24 | Misses | Busts |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| QB | H1 profile | 0.566 | 0.703 | **0.667** | **0.861** | **0.852** | 0.901 | 0.904 | 4 | **0** |
| QB | H2 standard opportunity | 0.551 | 0.706 | **0.667** | **0.861** | 0.821 | **0.922** | **0.919** | **3** | **0** |
| QB | H4 bonus/first down | **0.571** | **0.713** | 0.639 | 0.847 | 0.828 | 0.899 | 0.910 | 4 | **0** |
| RB | H1 profile | **0.720** | **0.778** | **0.639** | 0.750 | **0.863** | 0.876 | **0.854** | 6 | **1** |
| RB | H4 bonus/first down | 0.703 | 0.764 | 0.583 | **0.778** | 0.857 | **0.897** | 0.851 | **5** | 3 |
| WR | H3 GNG opportunity | **0.723** | **0.767** | **0.611** | 0.583 | 0.875 | 0.885 | 0.857 | 8 | 3 |
| WR | H5 stability | 0.709 | 0.757 | 0.528 | **0.639** | 0.845 | **0.916** | **0.869** | **5** | 2 |
| TE | H2 standard opportunity | **0.726** | **0.769** | **0.639** | 0.750 | 0.827 | 0.857 | 0.862 | 7 | 1 |
| TE | H5 stability | 0.704 | 0.758 | 0.583 | **0.778** | **0.827** | **0.910** | **0.891** | **3** | 1 |

Full results, including H1-H5 for every position and each individual fold, are in `output/gng-advanced-hypotheses.json`.

## Coverage Audit

All 826 player-season rows produced scores. Core profile, opportunity, role, and snap fields were effectively complete. GNG weighted opportunity covered 98.0% of RB, 96.1% of WR, and 98.4% of TE rows. Position-relevant first-down coverage was 99.0% for QB rushing, 93.1% for RB rushing and receiving, 94.7% for WR receiving, and 97.4% for TE receiving.

Availability is the weak family: QB 60.8%, RB 44.3%, WR 53.1%, TE 53.4%. NGS coverage was 79.8% RB, 89.9% WR, and 78.3% TE. The percentile implementation assigns missing raw values to the bottom of a fold rather than deleting the row. H5 therefore needs missingness indicators or weight renormalization before it can be a production formula.

## Findings and Current Recommendation

- **QB:** keep H1 profile points as the elite-board incumbent. H2 is the broad-board challenger because it captured 92.2% of top-24 points and had three elite misses. H4 proved GNG bonus and first-down information helps rank order, but it did not improve player capture enough to win.
- **RB:** select H1 profile points. It is the best balanced result. H4 captured more top-24 points, but its lower correlation and three busts make it a supporting term, not the formula. Test a narrow 80% H1 plus 20% H4 blend next. The earlier 1% reception shift remains safe but is no longer the leading formula.
- **WR:** do not force one global winner. H3 is the elite-tier challenger. H5 is the broad-board leader with 91.6% points@24, 0.869 NDCG, and five misses. Test a tiered formula that uses H3 near WR1 territory and H5 below it.
- **TE:** select H5 for the broad board, subject to null handling. It cut misses to three and captured 91.0% of top-24 points. H2 remains the elite-tier challenger.
- **Production:** hold the existing Pigskin GNG boards. The next gate is a player-level miss/bust review plus explicit missing-value treatment, followed by current-board generation and unified VORP testing.

## Next Commands

1. Add missingness indicators or renormalize weights over present H5 inputs.
2. Run a player-level review of elite misses and top-12 busts, with the untouched 2024-to-2025 fold shown separately.
3. Test only the narrow challengers named above. Avoid another broad weight search.
4. Build current positional boards after those gates pass.
5. Backtest a unified GNG VORP interleaver before any production promotion.

## Safety

- No GNG live ranking changed.
- No champion was activated.
- No model was trained.
- No 2026 outcome was used.
- No Gemini, Pigskin chat, or market target was used.

## Artifacts and Checks

- Added `scripts/run_gng_advanced_hypotheses.py`.
- Wrote detailed results to `output/gng-advanced-hypotheses.json`.
- Updated this phase decision record.
- Reran the BigQuery-backed runner successfully on July 11, 2026.
- `python -m py_compile scripts/run_gng_advanced_hypotheses.py` passed in the project virtual environment.
- `git diff --check` passed for the runner and phase log.
- Focused pytest execution was unavailable because the project virtual environment does not contain `pytest`.
