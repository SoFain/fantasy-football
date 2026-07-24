# Phase 34.6 RB Fable v1 Sleeper Current-Context Report

## Final Decision

`RB FABLE V1 OWNER REVIEW BOARD READY` and `CURRENT PIGSKIN STILL HOLDS LIVE`

The Sleeper current-team context layer is built, identity-clean, and joined to the full Fable-vs-Standard comparison universe. Every player matched by ID; zero name-fallback matches were needed. Sleeper independently confirms the Standard board's team assignments in all cases, so the Phase 34.5 stale-team warnings are now precisely scoped: four Fable top-30 scores rest on prior-team usage and require owner role review, and two Standard top-40 players have no qualified Fable row at all. Nothing in this phase changed the formula, weights, ranks, or any live object.

## Sleeper Fetch And Cache Details

- Client: reused `fetch_sleeper_players` from the existing `src/sleeper_player_snapshot.py` lane; no new HTTP code was written.
- Endpoint: `https://api.sleeper.app/v1/players/nfl`, fetched exactly once at `2026-07-10T05:25:40Z`.
- Cache: full raw payload stored at `output/sleeper_current_players_cache.json`; the loader prefers the cache, so re-runs never re-fetch (`--refresh` is required to hit the network again). This respects Sleeper's rate guidance for the full player map.
- Volume: 12,200 players, 926 RBs.
- Each row preserves a SHA-256 `raw_payload_hash` of its player payload plus the `fetched_at` timestamp.

## BigQuery Objects Created (research dataset only)

- `fantasy_football_advanced_metrics.sleeper_current_player_context` — table, one row per Sleeper player ID (12,200 rows), WRITE_TRUNCATE load, review evidence only. No production feature mart, identity table, or brain-dataset object was touched.
- `fantasy_football_advanced_metrics.v_rb_fable_v1_current_context_review` — view over the union of Fable v1 top 40 (2025 source metrics) and Current Standard top 40 (`pigskin-llm-20260704071412`, the same single active board confirmed in Phase 34.5).

## Join Coverage And Identity

| Measure | Result |
|---|---|
| Universe rows (union of both top 40s) | 43 |
| Matched via Standard-board Sleeper ID | 43 (100%) |
| Matched via GSIS bridge fallback | 0 |
| Matched via normalized name+team fallback | 0 |
| No Sleeper match | 0 |
| Standard-vs-Sleeper team mismatches | 0 |

Identity warnings: none. Every joined player's Fable identity remains `EXACT_SLUG_MATCH`; the Sleeper join adds no ambiguity because the Standard board already carries verified Sleeper IDs.

Fable source team codes were normalized (HST→HOU, BLT→BAL, CLV→CLE, ARZ→ARI, LA→LAR) before comparison so no false team-change flags fire.

## Context Flag Summary

| Flag | Count | Players |
|---|---:|---|
| FABLE_SCORE_TRUSTED | 26 | everyone not listed below |
| INJURY_STATUS_WARNING | 5 | Devon Achane (Q), Cam Skattebo (Q), Bucky Irving (Q), Zach Charbonnet (Q), Quinshon Judkins (Q) |
| CURRENT_ROLE_REVIEW_REQUIRED | 4 | Travis Etienne (JAX→NO), Rico Dowdle (CAR→PIT), Kenneth Walker (SEA→KC), Kenneth Gainwell (PIT→TB) |
| STALE_TEAM_CONTEXT (Fable 31-40) | 3 | Chris Rodriguez (WAS→JAX), David Montgomery (DET→HOU), Rachaad White (TB→WAS) |
| SLEEPER_DEPTH_CHART_WARNING | 3 | Tyrone Tracy (order 2), Rhamondre Stevenson (order 2), Woody Marks (order 2) |
| NO_QUALIFIED_FABLE_ROW | 2 | James Conner (Std 29), Trey Benson (Std 36) |

## Top-30 Comparison With Context Flags

| Fable | Std | Player | Sleeper team | Flag |
|---:|---:|---|---|---|
| 1 | 1 | Christian McCaffrey | SF | FABLE_SCORE_TRUSTED |
| 2 | 4 | Jonathan Taylor | IND | FABLE_SCORE_TRUSTED |
| 3 | 2 | Bijan Robinson | ATL | FABLE_SCORE_TRUSTED |
| 4 | 3 | Jahmyr Gibbs | DET | FABLE_SCORE_TRUSTED |
| 5 | 5 | Devon Achane | MIA | INJURY_STATUS_WARNING (Questionable) |
| 6 | 7 | James Cook | BUF | FABLE_SCORE_TRUSTED |
| 7 | 9 | Javonte Williams | DAL | FABLE_SCORE_TRUSTED |
| 8 | 20 | Derrick Henry | BAL | FABLE_SCORE_TRUSTED |
| 9 | 13 | Josh Jacobs | GB | FABLE_SCORE_TRUSTED |
| 10 | 6 | Kyren Williams | LAR | FABLE_SCORE_TRUSTED |
| 11 | 8 | Chase Brown | CIN | FABLE_SCORE_TRUSTED |
| 12 | 10 | Saquon Barkley | PHI | FABLE_SCORE_TRUSTED |
| 13 | 14 | Travis Etienne | NO | CURRENT_ROLE_REVIEW_REQUIRED |
| 14 | 11 | Omarion Hampton | LAC | FABLE_SCORE_TRUSTED |
| 15 | 12 | Ashton Jeanty | LV | FABLE_SCORE_TRUSTED |
| 16 | 18 | Cam Skattebo | NYG | INJURY_STATUS_WARNING (Questionable) |
| 17 | 15 | D'Andre Swift | CHI | FABLE_SCORE_TRUSTED |
| 18 | 19 | Jaylen Warren | PIT | FABLE_SCORE_TRUSTED |
| 19 | 22 | Rico Dowdle | PIT | CURRENT_ROLE_REVIEW_REQUIRED (Sleeper depth order 2 behind Warren) |
| 20 | 17 | Bucky Irving | TB | INJURY_STATUS_WARNING (Questionable) |
| 21 | 30 | Zach Charbonnet | SEA | INJURY_STATUS_WARNING (Questionable; depth order 2) |
| 22 | 16 | Breece Hall | NYJ | FABLE_SCORE_TRUSTED |
| 23 | 21 | Quinshon Judkins | CLE | INJURY_STATUS_WARNING (Questionable) |
| 24 | 25 | Kenneth Walker | KC | CURRENT_ROLE_REVIEW_REQUIRED |
| 25 | 31 | Kenneth Gainwell | TB | CURRENT_ROLE_REVIEW_REQUIRED (depth order 2) |
| 26 | 28 | TreVeyon Henderson | NE | FABLE_SCORE_TRUSTED |
| 27 | 23 | J.K. Dobbins | DEN | FABLE_SCORE_TRUSTED |
| 28 | 33 | Tyrone Tracy | NYG | SLEEPER_DEPTH_CHART_WARNING (order 2) |
| 29 | 24 | Rhamondre Stevenson | NE | SLEEPER_DEPTH_CHART_WARNING (order 2) |
| 30 | 34 | Woody Marks | HOU | SLEEPER_DEPTH_CHART_WARNING (order 2) |
| 34 | 26 | Aaron Jones | MIN | FABLE_SCORE_TRUSTED |
| 35 | 27 | Tony Pollard | TEN | FABLE_SCORE_TRUSTED |
| n/a | 29 | James Conner | ARI | NO_QUALIFIED_FABLE_ROW (Questionable; depth order 3) |

## Stale-Team Audit (the Phase 34.5 five, plus disagreement players)

| Player | Fable team | Std team | Sleeper team | Status / injury | Depth | Verdict |
|---|---|---|---|---|---|---|
| Travis Etienne | JAX | NO | NO | Active | RB1 | **Manually review.** Team changed, but Sleeper lists him RB1 in New Orleans; volume assumption plausibly carries. Fable 13 vs Standard 14 agree anyway — low-stakes review. |
| Rico Dowdle | CAR | PIT | PIT | Active | **RB2 behind Jaylen Warren** | **Discount.** Fable 19 is built on a Carolina lead role he no longer holds; Sleeper depth chart contradicts the volume assumption directly. |
| Kenneth Walker | SEA | KC | KC | Active | RB1 | **Manually review.** New team, but listed RB1 in Kansas City; Fable 24 vs Standard 25 agree, so the stale context is not driving a disagreement. |
| Kenneth Gainwell | PIT | TB | TB | Active | RB2 | **Discount.** His Fable case was receiving usage in Pittsburgh; in Tampa behind Irving, the role that generated the score is gone. |
| James Conner | none | ARI | ARI | Active, Questionable | RB3 | **Incomplete.** No qualified 2025 row, and Sleeper now lists him RB3 in Arizona behind Trey Benson — the gap matters less than Phase 34.5 feared. |
| Derrick Henry | BAL | BAL | BAL | Active, RB1, no injury | RB1 | **Trusted.** The board's biggest disagreement (Fable 8 vs Standard 20) survives the context check completely clean — same team, healthy, unchallenged on the depth chart. |
| Breece Hall | NYJ | NYJ | NYJ | Active | RB1 | **Trusted.** The Fable discount (22 vs Standard 16) is a formula opinion about red-zone usage, not stale context. |
| Zach Charbonnet | SEA | SEA | SEA | Active, Questionable | RB2 | **Manually review.** Fable 21 vs Standard 30, but with Walker gone the SEA depth chart lists Charbonnet RB2 (behind a new RB1) and he is Questionable — the rise case needs owner eyes. |
| Aaron Jones | MIN | MIN | MIN | Active | RB1 | **Trusted (as a formula opinion).** Context is current; the Fable fade is the age/volume penalty working as designed. |
| Tony Pollard | TEN | TEN | TEN | Active | RB1 | **Trusted (as a formula opinion).** Context is current; the fade is red-zone/TD-driven. |

## Are The Fable Disagreements Trustworthy?

The headline disagreements survive: Henry (context fully clean), Hall, Jones, and Pollard are all current-team, healthy-roster formula opinions. The disagreements that do NOT survive cleanly are Dowdle (+3, but Sleeper shows him RB2), Gainwell (+6, role gone), and Charbonnet (+9, Questionable and behind a new RB1). Notably, all three untrustworthy disagreements are Fable *risers* — the context layer removes optimistic errors, not the formula's fades.

## Readiness

- Ready for owner review: **yes** — the board plus flags is exactly the evidence package the owner needs.
- Ready for live Standard RB replacement: **no**. Four top-30 scores need role review, two Standard players are unrankable, and Fable has still never beaten a historical baseline (none exists).
- Current Pigskin holds live: **yes, by default.**

## Files Changed

- `scripts/build_sleeper_current_player_context.py` (new)
- `bigquery/views/v_rb_fable_v1_current_context_review.sql` (new)
- `tests/test_sleeper_current_player_context.py` (new)
- `docs/rebuild/validation/phase-34-6-rb-fable-sleeper-context-report.md` (this report)
- `docs/rebuild/rb-fable-v1-owner-review-board.md`

Local evidence (not commit candidates): `output/sleeper_current_players_cache.json`.

## Safety Confirmation

- RB Fable v1 formula weights, views, and scores are unchanged; the context layer never enters `rb_fable_01_score`.
- No live ranking write occurred; the only writes were the research table and review view in the isolated advanced-metrics dataset.
- No champion was activated. No model was trained. No deployment occurred.
- No Gemini or Pigskin chat call occurred.
- No 2026 outcomes were used. Sleeper current context was not joined to any historical backtest object; `v_rb_fable_01_backtest_prep` is untouched.
- No market data entered any formula input.
- Existing identity tables and production feature marts were not modified.

## Checks

- `venv\Scripts\python.exe -m py_compile scripts\build_sleeper_current_player_context.py`: pass.
- `venv\Scripts\python.exe -m unittest tests.test_sleeper_current_player_context`: 5 tests passed (fetch-row contract, cache-preferred-over-network, flag coverage, join-method coverage, review-only/no-2026 contamination guard).
- Focused identity join check: 43/43 rows matched by Sleeper ID, 0 fallback matches, 0 misses.
- Focused review query checks: flag distribution and audit-player rows verified read-only.
- Focused no-live-write check: table/view writes confined to `fantasy_football_advanced_metrics`; all board queries via the read-only endpoint.
- Focused no-2026-outcome and no-historical-contamination check: view definition contains no 2026 references and reads only `season = 2025` Fable rows; backtest views unchanged.
- `scripts/check_deployment_safety.py`: all checks passed.
- `scripts/run_bigquery_validations.py --dry-run`: discovery passed through validation 245.
- `git diff --check`: pass; existing line-ending warnings informational.

## Recommended Next Phase

Phase 34.7: owner review session over `docs/rebuild/rb-fable-v1-owner-review-board.md`. If the owner wants a context-aware display board, build it as a separate, clearly-labeled overlay (see the modifier design note in the owner board doc) — never inside the validated Fable score, because Sleeper current context has no historical snapshots and therefore can never be backtested honestly. Begin retaining dated Sleeper snapshots now so a future season can validate any context modifier properly.
