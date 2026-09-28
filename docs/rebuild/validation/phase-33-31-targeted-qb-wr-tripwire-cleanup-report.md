# Phase 33.31 Targeted QB/WR Tripwire Cleanup Report

Final decision: **PROSPECT LANE REQUIRED BEFORE TOP-100 ADVANCES**

Phase 33.31 tested targeted review-only cleanup candidates for the remaining Phase 33.30 top-100 blockers. The cleanup candidates reduce some QB/WR pressure, but they do not create a live-safe replacement for Current Pigskin. Jeremiyah Love remains a market-only prospect with no official top-100 lane, and Breece Hall still needs a targeted Half PPR context refresh before live use.

## Scope Confirmation

- No live rankings were written.
- No champion was activated.
- No models were trained.
- No deployment occurred.
- No Gemini, Pigskin chat, or Sleeper API calls were made.
- No 2026 outcomes were used.
- Route metrics remain blocked/null. YPRR, TPRR, true route share, first-read share, and fabricated route fields were not used.
- Current Sleeper context was not used as historical input.
- Market data was not used as a training target.

## Files Changed

- `docs/rebuild/validation/phase-33-31-targeted-qb-wr-tripwire-cleanup-report.md`
- `docs/rebuild/position-locked-top-100-interleaver-plan.md`
- `docs/rebuild/advanced-bqml-v2-owner-review-boards.md`
- `docs/rebuild/ranking-algorithm-scorecard.md`
- `docs/rebuild/bqml-v2-ranking-architecture.md`
- `docs/rebuild/ranking-opportunity-metrics-matrix.md`

Evidence artifact:

- `output/phase-33-31-targeted-qb-wr-cleanup-evidence.json`

## Git State

The worktree was already dirty before this phase. Phase 33.31 did not stage, commit, deploy, or revert prior work. Existing modified and untracked Phase 33 files remain owner-review material.

## Cleanup Candidate Comparison

Average across Standard, Half PPR, PPR, and GNG Keeper proxy slices:

| Variant | Top-100 hit | VOR captured | Pairwise draft win | Tripwire breaches | QB breaches | WR breaches | RB breaches | Extreme movement |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `current_proxy` | 0.680 | 0.818 | 0.571 | 8.62 | 2.38 | 3.25 | 3.00 | 0.00 |
| `refined_proxy` | 0.670 | 0.782 | 0.596 | 8.62 | 2.50 | 3.25 | 2.88 | 3.50 |
| `prototype_33_31_qb_anchor_only` | 0.670 | 0.809 | 0.589 | 8.88 | 2.75 | 3.25 | 2.88 | 2.62 |
| `prototype_33_31_wr_anchor_only` | 0.675 | 0.785 | 0.584 | 8.75 | 2.50 | 3.38 | 2.88 | 1.25 |
| `prototype_33_31_qb_wr_anchor` | 0.675 | 0.812 | 0.577 | 9.00 | 2.75 | 3.38 | 2.88 | 0.38 |
| `prototype_33_31_conservative_current_pigskin_heavy` | 0.673 | 0.806 | 0.579 | 8.50 | 2.25 | 3.38 | 2.88 | 0.12 |

Interpretation: `refined_proxy` still has the best pairwise draft win rate, but it carries high extreme movement. The conservative Current Pigskin-heavy cleanup has the lowest aggregate tripwire count and almost no extreme movement, but it gives back VOR and top-100 capture. Current Pigskin remains the safest live baseline.

## QB Audit

| Player | Main finding | Manual review |
|---|---|---|
| Patrick Mahomes | Half PPR falls from Current Pigskin QB3/O11 to prototype O64, an interleaver breach. Standard and PPR one-QB discounts are defensible but still close to the cap. | Yes for Half PPR |
| Drake Maye | Current Pigskin QB2 remains inside O6-O9. Prototype O16-O39 is defensible in one-QB but needs QB2 pull-floor monitoring. | No |
| Matthew Stafford | Missing from several guarded queues or lands outside top 100. Current Pigskin rank varies heavily by profile. | No, unless owner wants veteran-QB preservation |
| Brock Purdy | Standard, Half PPR, and PPR fall to O75-O78 despite Current Pigskin QB4-QB7 pressure. This is an interleaver issue. | Yes |
| Trevor Lawrence | Standard, Half PPR, and PPR fall to O77-O79. Interleaver issue, not a WR/RB scarcity issue. | Yes |
| Jalen Hurts | Prototype O33-O38 for non-GNG profiles is defensible despite Current Pigskin top-5 QB pressure. | No |
| Justin Herbert | Outside top 100 in most profiles, but Current Pigskin pressure is lower than Mahomes/Maye. | No |
| Caleb Williams | Standard, Half PPR, and PPR fall to O78-O82. Interleaver issue. | Yes |
| Jordan Love | GNG falls to O80 despite Current Pigskin QB8. Other profiles fall outside top 100 because guarded queue does not select him. | Yes for GNG |

### QB Cleanup Test Result

The QB-only anchor improves some pairwise score, but it does not reduce aggregate QB breaches. The recommended QB cleanup is not a full QB queue replacement. Use explicit review caps:

- Current Pigskin QB1-QB3 cannot fall outside top 36 overall without manual review.
- Current Pigskin QB4-QB6 cannot fall outside top 60 overall without manual review.
- QB1 must appear by top 24.
- QB2 must appear by top 50 if Current Pigskin has QB2 inside top 24.
- Do not force more than three QBs into top 24.

Recommended QB action: **QB anchor/cap rule plus interleaver pull-floor review**, not live promotion.

## WR Audit

| Player | Current/guarded/prototype finding | Source-backed context | Manual review |
|---|---|---|---|
| Rashee Rice | Current WR7-WR8, guarded WR29-WR36, prototype O88-O96. | WOPR 0.531, target share 0.290, receiving EPA 2.002, market WR22. No source-backed concerns were found. | Yes |
| Jaxon Smith-Njigba | Current WR1-WR2, guarded WR7-WR8, prototype O12-O21. | WOPR 0.905, target share 0.368, receiving EPA 5.334, market WR2. | No |
| Chris Olave | Current WR6-WR9, guarded WR17-WR22, prototype O37-O75. | WOPR 0.725, target share 0.292, receiving EPA 2.227, market WR16. | Yes for Standard |
| Tetairoa McMillan | Current WR16-WR18, guarded WR37-WR39, prototype O97-O99. | Prospect/low-history label, market WR9. | Prospect review |
| Wan'Dale Robinson | Guarded missing in Standard and prototype O90-O101 elsewhere. | WOPR 0.653, target share 0.303, receiving EPA 1.216, market WR48. | No |
| Nico Collins | Current WR14-WR15, guarded WR20-WR27, prototype O49-O88. | WOPR 0.609, target share 0.242, receiving EPA 2.621, market WR12. | No |
| Jaylen Waddle | Current WR22, guarded WR29-WR32, prototype O89-O94. | WOPR 0.648, target share 0.233, receiving EPA 2.153, market WR28. | No |
| Rome Odunze | Guarded missing in all four profiles and prototype O101. | WOPR 0.602, target share 0.236, receiving EPA 1.741, market WR20. | Yes if retained in top-100 review |
| George Pickens | Current WR11-WR13, guarded WR12-WR16, prototype O28-O44. | WOPR 0.563, target share 0.225, receiving EPA 5.220, market WR10. | No |
| DeVonta Smith | Current WR20, guarded WR18-WR22, prototype O38-O78. | WOPR 0.594, target share 0.246, receiving EPA 3.198, market WR21. | No |
| Marvin Harrison Jr. | The exact requested audit row was absent from Phase 33.31 evidence. Treat this as an identity/display warning before owner review. | Not accepted as a clean Jr. audit row in this phase. | Yes |

### WR Cleanup Test Result

The WR-only and QB/WR anchor variants did not reduce WR breach count. The recommended WR cleanup is a source-backed demotion rule:

- Current Pigskin WR1-WR6 cannot fall outside WR12 without manual review.
- Current Pigskin WR7-WR12 cannot fall outside WR24 without manual review.
- Current Pigskin top-24 overall WR cannot fall outside top 60 overall without manual review.
- A Current Pigskin top-12 WR may only fall more than 12 WR spots if at least two source-backed concerns are present.

Recommended WR action: **elite WR anchor plus source-backed demotion requirement**, not live promotion.

## Rashee Rice Decision

Rashee Rice's WR30-ish queue demotion is not defensible from the Phase 33.31 evidence. His WOPR, target share, receiving EPA, and market WR22 context do not provide two source-backed concerns. Current Pigskin may be aggressive at WR7-WR8, but the guarded queue demotion to WR29-WR36 is too severe for live use.

Rashee Rice blocks live top-100 use unless the WR elite anchor is enforced or the owner explicitly accepts that demotion.

## Breece Hall Stale-Context Decision

Half PPR Breece Hall still needs a targeted refresh before live use:

- Current active Half PPR Pigskin rank: RB6.
- Phase 33.27 evidence rank: RB18.
- Phase 33.28/33.29 prototype rank: RB16.
- Decision: targeted refresh required before live use.

This does not block review-only experimentation, but it blocks live replacement.

## Jeremiyah Love Prospect Policy

Jeremiyah Love is classified as a market-only prospect in this phase.

Policy recommendation: keep him as a manual placeholder outside the official top-100 until a prospect watch lane exists or the owner explicitly rejects market-only prospects.

- Blocks owner-review board work: no.
- Blocks live top-100 use: yes.

Recommended prospect policy:

- Do not force market-only prospects into official live rankings without source support.
- Require a source-backed active ranking row before official inclusion, or create a separate prospect watch lane.
- Owner may reject market-only prospects entirely for v1.0 live top-100.

## Owner-Review Validity

Owner review can continue if the next board is clearly labeled review-only and includes the QB/WR tripwire warnings, the Breece refresh warning, and the Jeremiyah prospect-lane block.

Live use remains blocked. Current Pigskin holds as the production-safe baseline.

## Checks

Passed:

- `.\venv\Scripts\python.exe -m unittest tests.test_bqml_v2_feature_contract`: 26 tests passed.
- `.\venv\Scripts\python.exe -m py_compile src\bqml_v2_feature_contract.py`: passed.
- `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`: passed.
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run`: passed, 251 validation files discovered.
- Focused QB tripwire evidence check: passed.
- Focused WR tripwire evidence check: passed with the expected `Marvin Harrison Jr.` exact-row warning.
- Focused Breece Hall stale-context evidence check: passed.
- Focused Jeremiyah Love prospect-lane evidence check: passed.
- `git diff --check`: passed with CRLF warnings on existing docs.

## Remaining Warnings

- Phase 33.31 evidence uses a proxy backtest on target seasons 2024 and 2025. It is not live proof.
- Current Pigskin-heavy variants reduce movement risk but do not clearly improve top-100 capture.
- `Marvin Harrison Jr.` requires exact identity/display verification because the exact audit row was absent from Phase 33.31 evidence.
- Breece Hall Half PPR context remains stale against earlier RB evidence.
- Jeremiyah Love needs a prospect-lane decision before any official top-100 advancement.
- `git diff --check` reported CRLF conversion warnings for existing docs, with no whitespace errors.

## Recommended Next Phase

Phase 33.32 should either:

- Build a prospect watch lane and rerun the owner-review top-100 with QB/WR tripwire caps, or
- Hold top-100 behind Current Pigskin and document that the refined interleaver remains research-only.

Do not advance to live activation from Phase 33.31.
