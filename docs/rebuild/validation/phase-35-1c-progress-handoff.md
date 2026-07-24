# Phase 35.1C Progress Handoff — WR Fable v1.1 Upgrade (Session Ended Mid-Phase)

Status: **BUILD ARTIFACTS WRITTEN, NOTHING DEPLOYED OR VALIDATED.** All Phase 35.1C code exists on disk but no tests have been run, no views deployed, no backtest executed, and no report produced. Nothing live was touched at any point. The final phase report (`phase-35-1c-wr-fable-v1-1-upgrade-report.md`) does NOT exist yet.

## Completed (files written to disk, unvalidated)

### Part A/B — Two-season blend + availability separation
- `bigquery/views/v_wr_fable_v11_metric_inputs.sql` — reads `v_wr_fable_v1_situational_splits` with a **relaxed pool** (games >= 3 OR routes >= 75 OR targets >= 40), recomputes the v1 derivations, self-joins the prior season, and produces blended `b_*` rate metrics.
  - Dynamic latest-season weight: `routes/(routes+200)` clamped [0.35, 0.70]; opportunity/TD weight = `LEAST(raw, 0.70)`, efficiency weight = `LEAST(raw, 0.60)` — full seasons reproduce the static 70/30 and 60/40 blends exactly; injury seasons scale down to the 0.35 floor. No prior qualified season -> weight 1.0 (latest-only, nothing invented).
  - aDOT regression and league RZ TD conversion are computed on the **qualified subset only** (games >= 6 OR targets >= 40) but applied to all included rows.
  - Carry-forward eligibility: `latest_qualified OR (NOT season_qualified AND prev_qualified AND (games >= 3 OR routes >= 75))` — this is the Nabers fix.
  - `two_year_availability_rate = 0.70*latest_gpr + 0.30*prev_gpr` (latest-only if no prior).
  - Shrinkage samples include weighted prior-season routes/targets: `n_eff = latest + (1 - eff_weight)*prev`.
- `bigquery/views/v_wr_fable_v11_scored_seasons.sql` — v1 weights unchanged over `b_*` inputs; `z_games_rate` replaced by `z_two_year_availability`; output column `wr_fable_v11_score`.

### Part C — Team environment
- `bigquery/views/v_wr_team_environment.sql` — team-season score, seasons 2022-2025, z within season:
  `0.35*z(QB passing EPA/dropback [qb_week_environment_metrics, weighted by dropbacks]) + 0.20*z(pass EPA/play [team_week_context_metrics, weighted by plays]) + 0.20*z(pass att/gm [stg_team_week_stats]) + 0.15*z(off PPG) + 0.10*z(win%)`.
  PPG and win% come from `raw_nflverse_schedules.raw_payload_json` (home_score/away_score verified present). Exposes `team_environment_z` (z of the composite) — situation buckets use deltas of THIS column at +/-0.50. Team codes canonicalized to LAR-style (`LA->LAR`; situational `HST/BLT/CLV/ARZ->HOU/BAL/CLE/ARI`).
- `bigquery/views/v_wr_fable_v11_backtest_prep.sql` — folds 2022-2024 -> 2023-2025 WR Standard PPG. Historical destination team = **target-season Week 1 roster** from `raw_nflverse_rosters_weekly` (known before Week 1; leakage-safe). Environment always from the input season. Outputs both `wr_fable_v11_score` and `wr_fable_v11_env_score` (= score + 0.05*bucket for team-changers). No Sleeper/depth-chart references (unit-test enforced).

### Part D — Current board with alpha-role adjustment
- `bigquery/views/v_wr_fable_v11_current_board.sql` — season 2025 scored rows joined to `sleeper_current_player_context` (WR, by gsis_id) and 2025 team environment. Team-changers get `0.05*bucket` plus alpha adjustment (Sleeper depth order 1: +0.03; 2: 0; >=3: -0.03; missing: 0 + `alpha_role_review_flag`). Total context adjustment capped [-0.08, +0.08] into `wr_fable_v11_current_score`. Unchanged-team players get zero adjustments. Current-board only — never in folds.

### Part E — Weekly Sleeper archive
- `scripts/build_sleeper_current_player_context.py` extended with: `archive_snapshot()` (creates/appends `fantasy_football_advanced_metrics.sleeper_player_snapshot_history`, grain snapshot_date + sleeper_player_id, idempotent via DELETE-then-load per date), `deploy_status_changes_view()` (`v_sleeper_player_status_changes`, newest vs previous snapshot), and an `--archive` CLI flag composing with `--apply --refresh`.

### Support
- `scripts/build_wr_fable_v11_layer.py` — deploys the five v1.1 views (dry-run/apply).
- `scripts/run_wr_fable_v11_backtest.py` — evaluates `v11_blend` and `v11_blend_env` variants by aliasing each score into the v1 fold machinery (imports `fold_summary` from `scripts/run_wr_fable_v1_backtest.py`); also reports carry-forward counts per fold.
- `tests/test_wr_fable_v11.py` — ~10 assertions: template render, dynamic weight caps, rates-not-totals blending, carry-forward rule, availability separation, environment weights, backtest leakage safety (no Sleeper/depth/2026 in prep), board caps and flags, no fabricated metrics, archive idempotency.

## NOT started / remaining work (in execution order)

1. `venv\Scripts\python.exe -m unittest tests.test_wr_fable_v11 tests.test_wr_fable_v1 tests.test_sleeper_current_player_context` — **never run; expect possible SQL-string assertion mismatches to fix.**
2. `venv\Scripts\python.exe scripts\build_wr_fable_v11_layer.py --dry-run` then `--apply` — **views not deployed; BigQuery may surface SQL errors (the v11 metric-inputs view is large and untested).** Risk spots: correlated `dates` CTE pattern in the status-changes view, JSON extraction perf on schedules, `prev_qualified IS NOT NULL` semantics (prev join already filters `prev.season_qualified`, so `prev_qualified` is TRUE or NULL — intended).
3. Run `scripts\run_wr_fable_v11_backtest.py --json-output output\phase-35-1c-wr-fable-v11-results.json` and compare against v1 baselines from Phase 35.1B (aggregate: Spearman 0.738, top-12 0.639, pts@12 0.917, NDCG@24 0.849, pairwise 0.769, regret 0.266, 8 elite misses, 2 busts — full numbers in `docs/rebuild/validation/phase-35-1b-wr-fable-v1-build-backtest-report.md`). Decision test: does v1.1 fix role-change/injury misses (Godwin, Higgins, Olave, Watson, Collins, Evans, Deebo, McLaurin) without materially degrading aggregates; does the env modifier help or hurt (Keenan Allen/Pittman busts are the target cases).
4. Sleeper archive first run: `scripts\build_sleeper_current_player_context.py --apply --refresh --archive` (creates history table + status-changes view; also refreshes the current context table). Then prepare weekly scheduling per the project's job pattern (only documentation/config — do not deploy).
5. Current board: query `v_wr_fable_v11_current_board` top 40 by `wr_fable_v11_current_score`, joined to v1 ranks (`v_wr_fable_v1_scored_seasons` 2025) and the active Standard WR board (`analytics_pigskin_rankings`, is_active, WR, standard) with rank deltas, blend/availability/situation/alpha columns, and Sleeper context.
6. Player audits required by the phase: **Malik Nabers** (the carry-forward test case — verify he now scores; show latest games/routes/targets, on-field rates, prior-season rates, blended inputs, availability deduction, resulting rank), **A.J. Brown** (PHI->NE: env scores both teams, bucket, Sleeper depth order, alpha adj, final rank), plus Diggs, Deebo, Keenan Allen, Adams, Metcalf, Rice, Olave, Higgins.
7. Final checks: deployment safety, `run_bigquery_validations.py --dry-run`, `git diff --check`.
8. Write the single compact report `docs/rebuild/validation/phase-35-1c-wr-fable-v1-1-upgrade-report.md` (formula deltas, backtest comparison table v1 vs v1.1 vs v1.1+env, current top-40 with movement reasons, audits, recommendation from: READY FOR OWNER APPROVAL / V1 STILL BETTER / NEEDS ONE SIMPLE TWEAK / NOT READY).

## Constraints still in force
No promotion, no live rankings, no champion, no deployment, no 2026 outcomes, no market inputs, no fabricated metrics (especially end-zone targets), no Sleeper current context in historical folds (env modifier only is historical; alpha modifier is current-board-only), no silent zero-fills.

## Context from earlier in the session (for continuity)
- RB Fable v1 was promoted live as the Standard RB champion in Phase 34.7 (`rb-fable-v1-standard-20260710054940`); WR work is research-only so far.
- WR Fable v1 baseline artifacts: views `v_wr_fable_v1_*`, runner `scripts/run_wr_fable_v1_backtest.py`, report `phase-35-1b-wr-fable-v1-build-backtest-report.md`, readable summary `docs/rebuild/wr-fable-v1-results.md`.
- Known v1 board issues 35.1C exists to fix: Malik Nabers unrankable (Std 18), A.J. Brown stale (PHI->NE, Fable 15), Diggs/Deebo/Keenan Allen Fable-only with no Sleeper match, role-change misses in all three folds.
