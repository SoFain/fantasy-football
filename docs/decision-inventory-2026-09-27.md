# Pipeline Decision Inventory (2026-09-27)

Every decision the Pigskin ranking pipeline makes about a player or a board, compiled read-only on 2026-09-27 for the AI decision layer work (`docs/ai-decision-layer.md`). Sources: the files listed at the end, the chain logs in `output/daily-publish/chain-*.log` (26 runs, 2026-09-14 to 09-27), the local feed in `output/public-rankings/*.json`, and git history. BigQuery was not queried; current values come from the local JSON written 2026-09-27 20:24.

**Chain health, 2026-09-14 to 09-27:** 2 of 26 runs succeeded (`chain-20260921-233946`, `chain-20260927-201604`).
- 21 failed at the coverage gate on MarShawn Lloyd (blocking omission).
- 2 failed at stage 9, after writes had begun (exit 3): `standard overall board contains teamless players: Darius Slayton`.
- 2 failed at the GNG promote on Caleb Williams (`hard_reviews: 1`).
- 1 failed on a concurrent-transaction abort in the stats refresh.
- 1 failed on a STRUCT supertype error in the Standard QB promote.

**"Text?" column:** NUM = pure numbers or enumerated codes; TXT = a judgment over text or an unstructured signal; MIX = numbers whose meaning depends on text or role interpretation. Paths are relative to this repo unless marked `site:` (`E:\cbs-league-history\site\app\`).

## A. Data ingest and identity

| # | Decision / outputs | Inputs | How decided today | Where | Consumers | Text? | Known failure modes |
|---|---|---|---|---|---|---|---|
| A1 | Sleeper snapshot fresh enough to run (pass / fail) | `sleeper_current_player_context.fetched_at` | Age between -5 min and 26 h; safety view separately flags over 72 h as `SLEEPER_CONTEXT_STALE` | `scripts/run_daily_board_refresh.py::assert_context_fresh`; `bigquery/views/v_ranking_post_formula_safety.sql` | Whole chain | NUM | The coverage gate makes its own live `/players` call twice per run, so one run can judge players against two Sleeper snapshots. Ingest uses `?active=true`, so a player leaving the active set disappears instead of being flagged. |
| A2 | Accept this season's weekly stats (apply / fail, list of completed games missing stats) | nflverse weekly, schedule, existing `weekly_metrics` keys | One season, no null keys or duplicates, weeks 1 to 22, ASSERT no existing key lost, then a transactional replace | `scripts/refresh_current_season_stats.py` | `weekly_metrics` for the in-season model, feed `current_season`, Studio | NUM | 2026-09-21 23:23 concurrent-update abort; NYG-LA Week 2 upstream pending. |
| A3 | Canonical player identity (internal ID, `match_method`, confidence) | Sleeper, rosters, rankings, weekly truth, depth charts, market; `player_identity_overrides` | Priority plus confidence: manual 1.0, exact ID 0.95, name+team+position 0.82, name+position 0.65, new 0.55; below 0.8 gets `low_confidence_match` | `src/build_player_identity.py` | Every join | MIX | Same-name players; names normalized differently in different places (coverage audit strips jr/sr/ii, safety view does not). |
| A4 | Situational metric source to GSIS link (VERIFIED / EXACT_SLUG_MATCH / NAME_TEAM_SEASON_MATCH / MULTIPLE_CANDIDATES / UNMAPPED, collision flag) | Identity candidates, bridge, `stg_player_identity` | One exact-name GSIS, or one name+team+season match with confidence at least 0.90; hard-coded Marvin Harrison Jr override (`d96487d` to `00-0039849`) | `bigquery/views/v_wr_fable_v1_identity_bridge.sql`; `situational_identity_bridge_review` | Fable qualification (C1, C3, C5) | MIX | Father/son collision needed a manual override; a collision drops the player (`IDENTITY_BRIDGE_COLLISION`). |
| A5 | Sleeper row to GSIS in the safety view | Sleeper `gsis_id`, bridge by Sleeper ID, unique normalized name+position | SQL coalesce; dedupe per gsis/position, latest wins | `v_ranking_post_formula_safety.sql` | Every promoter, publisher | MIX | Missing from the snapshot means no safety row: RB/TE/PPR drop him silently; Standard WR marks `SLEEPER_CONTEXT_MISSING` plus hard review. |
| A6 | GNG pool to Sleeper join | Bridge keys, three hard-coded pairs (`00-0037157`/`8122`, `00-0039373`/`11579`, `00-0036988`/`7670`), unique-name fallback | SQL | `scripts/build_gng_2026_candidate_boards.py::build_query` (`aliases`) | GNG boards and context | MIX | The three aliases are undocumented; a miss defaults to `SLEEPER_CONTEXT_MISSING` plus hard review. |
| A7 | Team and eligibility at publish time | Unified and positional rows, safety view | Safety team when a safety row matches, else board team; `current_board_rank_eligible` defaults FALSE without a match | `scripts/publish_public_rankings.py::fetch_overall_rows/fetch_positional_rows` | Gate H3 | NUM | Darius Slayton "teamless" failures 2026-09-14 and 09-21 07:30, both after writes; any failed join reads as teamless. |
| A8 | Situation facts: `team_changed`, `qb_to`, QB quality delta, `hc_changed`, flags (NEW_TEAM, QB_CHANGED, QB_UPGRADE/DOWNGRADE(_MAJOR) at 1.5/4.0 PPG, QB_NO_PRIOR_SEASON, NEW_HC, AGE_CLIFF) | Profile points, Sleeper current, active Standard QB board, coaching staff, birth dates | SQL; `qb_to` is the best-ranked active Standard QB on the current team; HC change is `STRPOS` name containment; LAR/LA alias | `src/situation_layer.py::build_situation_sql` | D5, feed `situation`, `player_situation`, owner review queue | MIX | LAR/LA once produced 13 false Rams movers (fixed); `qb_to` inherits Standard QB board errors. |
| A9 | Current coaching staff by team and role | Wikipedia staff templates | Wikitext parse into a reviewed CSV | `scripts/populate_coaching_staff_csv.py`, `src/ingest_coaching_staff.py` | A8 | TXT | Roles missing from the template stay vacant. |
| A10 | Who changed today; which team news mentions them | Two latest Sleeper snapshots; team RSS | Field diff; news by full-name substring | `src/detect_player_changes.py`, `src/player_status_changes.py`, `src/team_news_feeds.py::match_players` | Written to `player_status_changes`, `team_news_items`, `player_news_matches` only | TXT | Nothing reads the output. |
| A11 | Queue injury review events (new OUT/IR, `PENDING`, `NO_AUTOMATIC_RANK_CHANGE`) | Sleeper injury status now vs before | Rule | `src/sleeper_injury_reviews.py` via `src/ingest_news.py` to `sleeper_injury_review_queue` | None found | TXT (the real decision is time missed) | Never resolved. |
| A12 | Market rank for rookies | `market_consensus_baseline_current` (`manual_market_values`) | Hand-loaded | `src/market_consensus.py`; C11, coverage audit | GNG rookie ranks | NUM (human-supplied) | `v_market_rankings_context.sql` says market data "must never feed a formula", yet the GNG rookie overlay uses it as a rank input. |

## B. Eligibility and safety

| # | Decision / outputs | Inputs | How decided | Where | Consumers | Text? | Failure modes |
|---|---|---|---|---|---|---|---|
| B1 | `roster_context_eligible` | Sleeper active, team, status, age | active AND team AND status in (`Active`, `ACT`) AND at most 72 h old | `v_ranking_post_formula_safety.sql` | B3, B4, role adjustment | NUM | IR and other statuses fall out. |
| B2 | `current_board_rank_eligible`, `ranking_eligibility` | Sleeper team | team IS NOT NULL | same | Every promoter, publisher | NUM | Depends on A5. |
| B3 | Review flags: SLEEPER_ROSTER_REVIEW, SLEEPER_INACTIVE, SLEEPER_TEAMLESS, SLEEPER_STATUS_REVIEW, SLEEPER_CONTEXT_STALE, DEPTH_CHART_UNKNOWN, QB_BACKUP_ROLE_REVIEW (QB depth over 1), INJURY_UNCERTAIN (any tag), ROOKIE_CONTEXT_REQUIRED | Sleeper fields | Rules | same (`flagged`) | `risk_flags`, verdict wording, Studio rookie label | MIX | Every injury tag looks the same (Questionable vs Out vs PUP); `injury_notes` and `injury_body_part` are carried but never read; QB depth taken literally even when the drop is temporary. |
| B4 | `sleeper_hard_review` | B1 plus exceptions | (not eligible AND not rostered-injury exception) OR (QB AND depth over 1) | same | Enforced only in the Standard WR preflight and the GNG preflight (Top 150 only) | MIX | Caleb Williams (Out, depth 3) blocked the GNG promote twice on 09-27. |
| B5 | Rostered-injury exception (Inactive with an injury tag stays review-only) | active, team, status, tag | Rule, duplicated in SQL and Python | same; `src/gng_sleeper_safety.py::is_rostered_injury_review_only` | B4 | MIX | Only `status='Inactive'` with a tag. |
| B6 | Clear a GNG hard review for an injured starter | Row fields; `GNG_INJURED_STARTER_HARD_REVIEW_DECISIONS` | Owner exception with bounds | `src/gng_sleeper_safety.py::is_owner_approved_injured_starter` | GNG candidates | TXT (injured starter vs genuine backup) | New case each time. The approval text cites an availability discount, but the GNG availability multiplier is a per-position constant (0.8937 for every GNG QB), not per player. |
| B7 | Teamless players to watchlist or drop | team, flags | GNG and Standard WR: watchlists; RB/TE/PPR: silent filter | GNG builder; `scripts/build_standard_wr_fable_v1_safety_review.py`; promoters | Boards | NUM | Inconsistent by position. |
| B8 | GNG owner watchlist | `GNG_WATCHLIST_NAMES` | Exception list, applied only with a hard review | `src/ranking_owner_decisions.py` | GNG | TXT (signed or not) | Stale: Diggs (WAS), Deebo (SF), Allen (IND), Ertz (PHI) are ranked on GNG today; Tyreek Hill is on no board. |
| B9 | PPR/Half candidate eligibility and pins (`promotion_eligible`, `recommended_rank`, `decision_code`, `decision_note`) | July review board plus hand-written `DECISIONS` | Owner list dated 2026-07-11 in static tables the daily chain does not rebuild | `scripts/publish_ppr_fable_v1_candidate_boards.py::DECISIONS`; `scripts/build_ppr_fable_v1_review_boards.py` | `promote_ppr_fable_v1_positional.py` | TXT (role, injury, signing) | Diggs, Deebo, Allen still `EXCLUDE_UNSIGNED`, so they are missing from PPR and Half while Standard has them WR38/39/41 and GNG has Allen WR22, Diggs WR29. The PPR pool is effectively frozen at 2026-07-11. |
| B10 | Coverage gate: frontline universe, trace codes, blocking vs review-only | Live Sleeper, bridge, boards, formula views, candidates, market | Rule classifier plus `COVERAGE_GATE_REVIEW_ONLY_DECISIONS` | `scripts/audit_current_player_ranking_coverage.py` | Chain stages 2 and 5 | TXT/MIX | Lloyd blocked 21 runs 09-15 to 09-27; Wease earlier. `EXPECTED_COUNTS` differ from the runbook contracts (QB 44 reported FAIL but not blocking). |
| B11 | Rookie placement on redraft boards | none | Nothing decides it (`ROOKIE_SYSTEM_REQUIRED` is non-blocking; no redraft rookie lane) | none | none | MIX | Rookies are absent from Standard, PPR, Half (Jeremiyah Love GNG RB5 / market RB4, Sadiq, Tate, Price, Boston). |
| B12 | Injury or suspension absence (games missed, rank movement) | Injury designation, news | Nothing in production; promoters write `llm_estimated_games_missed = NULL`, zero movement; only the unscheduled Gemini path has INJURY codes | `src/generate_pigskin_rankings.py` (unscheduled) | none | TXT | Every injured player keeps full formula value, except July pins (Charbonnet `INJURY_ANCHOR`). |

## C. Formula scoring per position and profile

| # | Decision / outputs | Inputs | How decided | Where | Consumers | Text? | Failure modes |
|---|---|---|---|---|---|---|---|
| C1 | RB qualification | games, touches, identity | games at least 6 OR touches at least 50; identity accepted, no collision | `v_rb_fable_01_metric_inputs.sql` | C2 | NUM | No 2025 sample means no row (Lloyd). |
| C2 | RB Fable 0.1 score | Season z-scores 2022 to 2025 | Weights 0.30/0.13/0.12 opportunity; 0.08/0.06/0.05/0.04/0.04 efficiency with shrink; 0.10 TD; 0.05 age with 60% forgiveness for high-volume backs; 0.03 games | `v_rb_fable_01_scored_seasons.sql` | Standard RB; PPR/Half after C6 | NUM | |
| C3 | WR qualification and carry-forward | games, targets, routes, rookie flag, prior score | games at least 6 OR targets at least 40; else prior-season carry-forward for qualified non-rookie veterans (games at least 3 OR routes at least 75); variant I4 blends prior weight by games | `v_wr_fable_v1d_*`, `v_wr_fable_v1_current_candidates.sql` | WR boards | NUM | Never admits rookies. |
| C4 | WR Fable v1 score | WOPR, targets, RZ, YPRR, EPA/target, YAC, aDOT-adjusted catch, TD, breakout/decline/games | 0.30/0.12/0.10; 0.12/0.06/0.05/0.05 with shrink; 0.10; 0.04/0.03/0.03 | `v_wr_fable_v1_scored_seasons.sql` | Same | NUM | |
| C5 | TE qualification and v1.0a score | routes, games, TPRR, YPRR, EPA, RZ, age | games at least 4 AND routes at least 100; weights 0.22/0.16/0.12; 0.12/0.13/0.05; 0.10; 0.04/0.03/0.03 | `v_te_fable_v1a_*` | TE boards | NUM | Six valid TEs sit below the TE35 cutoff (Isaiah Likely, market TE11). |
| C6 | PPR/Half RB transform (WR, TE unchanged) | RB score, z-scores | score + 0.02 z_target_share - 0.02 z_ngt_tpg, computed once into the static table | `scripts/build_ppr_fable_v1_review_boards.py` | B9 table | NUM | Frozen at 2026-07-11; Half uses the same transform. |
| C7 | Standard QB guarded 75/25 | Anchor `COALESCE(candidate_rank, rank)`; BQML predictions; EPA, CPOE, rushing; depth from the ranking row | Min-cost-flow assignment: within 4 of anchor; weak-passing rule; role buckets by depth; rookies and missing-history locked to anchor; QB6/QB24 crossings fail without `--acknowledge-crossings` | `scripts/run_standard_qb_2026_owner_review.py`; `scripts/promote_standard_qb_guarded_75_25.py::validate_board` | Standard QB; C8 | MIX | Anchor references the previous promotion (self-referential day to day); depth comes from `rankings.sleeper_depth_chart_order`, never refreshed (Caleb Williams reads "depth order 1" while Sleeper shows 3, in `MISSING_HISTORY_DETERMINISTIC_LANE`); pool limited to the prior board; 09-21 STRUCT failure; 44 rows. |
| C8 | PPR/Half QB = copy of Standard | Active Standard QB | Copy, no dry mode | `scripts/promote_guarded_qb_to_reception_profiles.py` | PPR/Half QB | NUM | Inherits C7. |
| C9 | GNG position formulas | 2023 to 25 GNG PPG, at least 4 games in 2025; advanced, PBP, NGS | Percentiles then `weighted_average` over `FORMULAS`; null inputs dropped and weights renormalized | `build_gng_2026_candidate_boards.py::FORMULAS`; `run_gng_advanced_hypotheses.py`; `run_gng_position_candidate_expansion.py` | GNG boards | NUM | Sparse-data players can score on only a few inputs. |
| C10 | GNG role adjustment | Safety `post_formula_adjustment` | +0.02 depth 1; -0.04 depth 3 or more (RB/WR/TE); 0 for rookies and ineligible | SQL view | GNG order | MIX | The Python `apply_sleeper_safety()` is a second implementation that differs (any position, rookies not zeroed); used only in tests. |
| C11 | GNG rookie overlay | Sleeper rookies, manual market rank, depth | priority = market rank + depth penalty (0/3/10/20) | GNG builder | GNG boards | MIX | Depends on hand-loaded A12. |
| C12 | GNG WR continuity protection | Prior-day live GNG WR rank | Live rank 6 or better caps priority at 6 + rank; 12 or better at 12 + rank | GNG builder | GNG WR | NUM | Anchored to yesterday's board. |
| C13 | Board sizes | none | QB 40 to 45, RB 80 to 100 or 80, WR 100, TE 35; GNG 45/80/100/35 and exactly 260 | Promoters; `ROW_CONTRACTS`; GNG preflight | Gates | NUM | Standard RB count moves when a player gains or loses a team. |

## D. Post-formula adjustments and guardrails

| # | Decision / outputs | Inputs | How decided | Where | Consumers | Text? | Failure modes |
|---|---|---|---|---|---|---|---|
| D1 | Depth-chart role adjustment | Sleeper depth order | +0.020 / -0.040 on the raw score before re-ranking | Safety view; Standard and PPR promoters | Standard/PPR/Half RB/WR/TE | MIX (what the slot means) | Theo Wease was RWR depth 1 but third column on Miami's chart; Charbonnet and Vidal currently take -0.04. |
| D2 | Standard WR elite order (Brown > Jefferson > Wilson) | `STANDARD_WR_ELITE_ORDER` | Owner exception plus a promoter ASSERT | `build_standard_wr_fable_v1_safety_review.py`; `promote_standard_fable_v1_positional.py` | Standard WR | TXT (owner judgment) | Situation v1 runs afterwards and broke the order: Jefferson WR13, Brown WR14, Wilson WR16. The ASSERT runs only before stage 5.5; PPR/Half have no guard. |
| D3 | PPR/Half pins (Metcalf 19, Charbonnet 31, Vidal 32, Parkinson 22) | B9 table | `recommended_rank` overrides the formula unless `FORMULA_DEFAULT` | `promote_ppr_fable_v1_positional.py` | PPR/Half | TXT | July notes still in `rank_rationale` ("ACL recovery; require PUP clearance"). |
| D4 | PPR/Half live fallback | Prior active rows not in the candidate table | Ranked after candidates (1000 + rank) | same | PPR/Half | NUM | Carries stale rows forward. |
| D5 | Situation v1 rank moves (up to 4 slots) | A8; pinned `EFFECTS`; `WINPCT_2025`; PPG density | delta_ppg formula, dead band 0.10, density floor 0.05, cap 4; mirrored to GNG; refuses to re-run on the same board | `scripts/apply_situation_adjustments.py` | Standard and GNG WR/RB/TE | NUM (inputs from A8) | Not applied to PPR or Half; overrides D2. |
| D6 | Coverage and identity provenance text | C3 fields | SQL templates | Standard and PPR promoters | `rank_rationale`, evidence | NUM | Harrison branch hard-coded by ID. |
| D7 | Acknowledge a QB cutline crossing | CLI reason | Manual `--acknowledge-crossings` | `promote_standard_qb_guarded_75_25.py` | Standard QB | TXT (human) | Never passed by automation, so a crossing fails the chain until someone intervenes. |
| D8 | Public score and tier | Rank, adjusted score | RB/WR/TE min-max to 50 to 99; QB 100 - (rank-1) 50/44; GNG 100 - 0.5 rank; tiers by rank thresholds | Promoters | Feed, site | NUM | |

## E. Unified Top 150

| # | Decision / outputs | Inputs | How decided | Where | Consumers | Text? | Failure modes |
|---|---|---|---|---|---|---|---|
| E1 | Cross-position order (VORP interleave) | Positional queues; 2022 to 25 PPG by positional rank | Log-curve fit per position; replacement ranks per profile; per-position availability multiplier; onesie multipliers QB 0.85, TE 0.90 | `build_unified_fable_v1_top100.py::interleave` and PPR/GNG variants | `unified_draft_rankings_current` | NUM | Availability is not player-specific. |
| E2 | GNG hard-coded floors | Names | Jeremiyah Love no higher than overall 20; QB4 no higher than 25 | `build_unified_gng_2026_top100.py::apply_position_locked_floors` | GNG unified | TXT (owner valuation) | Keyed by name. |
| E3 | Unified integrity checks | Board, active ranks | 150 unique, contiguous, version match, teamless check | `promote_unified_*` | Gate | NUM | Standard unified has no teamless check (Slayton surfaced only at stage 9); Standard `BOARD_VERSION` is a fixed string. |
| E4 | GNG promote preflight | GNG tables | Exact dict: 260 positional, 150 unified, 0 hard reviews, 0 teamless, 0 non-contiguous, 0 queue mismatches | `scripts/promote_gng_2026_rankings.py` | Gate | NUM | Where B4 cases block; dry run validates tables left by the last apply. |

## F. In-season projections

| # | Decision / outputs | Inputs | How decided | Where | Consumers | Text? | Failure modes |
|---|---|---|---|---|---|---|---|
| F1 | As-of week or season complete | nflverse schedule scores | Latest fully scored week | `scripts/inseason_rankings.py::main` | Chain | NUM | |
| F2 | Shrinkage k and release gate | Frozen `docs/inseason-shrinkage-v1-calibration.json` | MAE on 2016 to 24, gated on the 2025 holdout | `choose_models`, `main` | Artifact | NUM | Validates per-appearance rate only, not availability. |
| F3 | Projected rate and points; flags | Observed points and games, prior rate or position median, schedule | (points + k prior)/(games + k), floored at 0, times remaining games or 0/1 | `predicted_rate`, `remaining_team_schedule` | In-season dataset, site, Studio | MIX (injury only as a flag) | An injured player is projected as if healthy. |
| F4 | Universe | Safety view | Includes IR and inactive; excludes teamless | `main` | same | NUM | |
| F5 | GNG exact score per game, or null when ambiguous | nflverse stats and PBP; GNG settings | Tier and bonus rules; ambiguous plays make the score null | `scripts/inseason_gng_scoring.py` | In-season GNG | MIX | Excludes 17 to 68 player-seasons per year; four current players unavailable. |
| F6 | Draft-board `current_season` block | `weekly_metrics`, schedule | Observed totals plus coverage caveat | `publish_public_rankings.py::attach_current_season_stats` | Feed, Studio | NUM | |

## G. Rationale and context text

| # | Decision / outputs | Inputs | How decided | Where | Consumers | Text? | Failure modes |
|---|---|---|---|---|---|---|---|
| G1 | Standard RB/WR/TE `pigskin_verdict` | Metrics, flags | SQL templates with numeric branches | `promote_standard_fable_v1_positional.py` | Feed, site, Studio | NUM to text | Templated repetition. |
| G2 | PPR/Half verdict and `risk_flags` | Candidate table and views | Templates; flags concatenated from July flags, context flags, decision code | `promote_ppr_fable_v1_positional.py` | same | TXT (legacy phrases) | Duplicated flags; legacy LLM-era phrases persist. |
| G3 | QB verdict | Rank | "Deterministic guarded Standard formula ranks X at QBn. No LLM reordering was applied." | `promote_standard_qb_guarded_75_25.py` | same | NUM | The rank-only sentence AGENTS.md forbids; the rank-only regex checks only the old Fable pattern. |
| G4 | GNG verdict, rationale, `context` | Percentiles, `rank_source` | `FORMULA_LOCKED`; context names driver, support, limiter metrics; 320 chars max | `promote_gng_2026_rankings.py`; `scripts/build_gng_rank_context.py` | Feed, site, Studio | NUM to template | Context never mentions injury or Sleeper review state. |
| G5 | `what_would_change_mind` | none | Fixed strings | Promoters | Feed, Studio | | Generic. |
| G6 | Adjustment provenance | D1 to D7 | Templates, appended | Promoters; `apply_situation_adjustments.py` | Feed, Studio | NUM | Codes pile up (`NO_ADJUSTMENT+SITUATION_V1`). |
| G7 | In-season rationale | F3 | Template | `inseason_rankings.py` | Site, Studio | NUM | |
| G8 | LLM verdict rewrite / TE adjudication | Metrics | Gemini | `scripts/rewrite_standard_pigskin_verdicts.py`; `scripts/adjudicate_te_fable_v1a_standard_te.py` | Not in the daily chain; overwritten daily | TXT (LLM) | |
| G9 | Human review queues | Situation flags; GNG top-30 deltas | `situation-review-YYYYMMDD.md` (156 flagged 2026-09-28); `gng_2026_top30_review.review_reasons` | `run_daily_board_refresh.py::write_situation_review`; GNG builder | Owner only | TXT (human) | No recorded disposition. |

## H. Publication gates

| # | Decision | How / where | Text? | Failure modes |
|---|---|---|---|---|
| H1 | Positional invariants | `run_daily_board_refresh.py::validate_positional` | NUM | Does not check verdict quality (G3). |
| H2 | Unified 150 unique contiguous rows | `::validate_unified` | NUM | |
| H3 | Local feed validation, zero warnings across four profiles | `src/public_rankings_feed.py::validate_profile_rows`; `validate_local_publish` | NUM | Slayton failures after writes. |
| H4 | Exit class (1 no writes, 3 writes began), retries | `run_daily_board_refresh.py`; `scripts/daily_pigskin_chain.ps1` | NUM | An exit-3 day leaves live positional rows changed and the feed unpublished. |
| H5 | Dataset uploads, SHA readback, carry-forward | `daily_pigskin_chain.ps1`; `publish_public_rankings.py::fetch_current_datasets` | NUM | |
| H6 | Live verification | `scripts/verify_live_rankings.py` | NUM | |
| H7 | Site import | site: `pigskin_rankings.php::pigskin_rankings_import`; site: `pigskin_inseason_rankings.php` | NUM | |

## I. Site and Pigskin consumption

| # | Decision | How / where | Text? | Notes |
|---|---|---|---|---|
| I1 | Site blurb: verdict, or `context` when `FORMULA_LOCKED` | site: `pigskin_rankings.php::pigskin_verdict_is_take`, `pigskin_display_text` | NUM | |
| I2 | Risk code to plain English | `pigskin_risk_flag_phrases` (4 entries) | TXT (fixed map) | An article once printed `INJURY_UNCERTAIN` verbatim. |
| I3 | Board health | site: `pigskin_studio.php::pigskin_studio_build_rankings_health` | NUM | The 6-day stale period would show as warning, not critical. |
| I4 | Which rows get rich detail in the Studio prompt | `pigskin_studio_prepare_rankings_context` and helpers | TXT | Nicknames and partial names missed. |
| I5 | Rookie label | `pigskin_studio_cross_profile_rank_lines` | NUM | |
| I6 | Horizon context | `pigskin_inseason_studio_context` | NUM | |
| I7 | Availability label on Sleeper roster players | `pigskin_inseason_availability_map`, `pigskin_studio_sleeper_player_label` | MIX | Name fallback. |
| I8 | Does an article topic need a source | `pigskin_studio_article_topic_needs_source` | TXT | Keyword heuristics. |
| I9 | Pigskin prose | Generative model | TXT (LLM) | |

## Owner exceptions in force, and the automated decision each stands in for

1. `STANDARD_WR_ELITE_ORDER`: owner-vs-formula disagreement on elite WR order. Currently undone by Situation v1.
2. `GNG_WATCHLIST_NAMES`: signed or unsigned status. Stale.
3. Coverage exception, Theo Wease (MIA, 2026-08-07): depth-chart slot meaning.
4. Coverage exception, MarShawn Lloyd (GB, 2026-09-27): a legitimate no-prior-sample case; a no-sample or promoted-backup lane.
5. `GNG_INJURED_STARTER_HARD_REVIEW_DECISIONS`, Caleb Williams (2026-09-27): injured starter vs genuine backup, and a per-player games-missed discount the code does not apply.
6. PPR/Half `DECISIONS` (2026-07-11): role verification, injury availability, signing status, still applied daily.
7. Marvin Harrison Jr identity override: same-name disambiguation.
8. Three GNG identity aliases: undocumented identity repairs.
9. GNG unified floors (Love at least 20, QB4 at least 25): rookie valuation and QB scarcity.
10. GNG WR continuity protection: current-star coverage.
11. QB cutline acknowledgement: automated acceptance of QB6/QB24 movement.
12. Situation v1 `EFFECTS` and `WINPCT_2025` (2026-07-24/25): pinned policy numbers.
13. Hand-curated inputs: `manual_market_values`, `player_identity_overrides`, `data/coaching_staff.csv`.

## Decisions that most often need manual intervention

1. Coverage-gate blocks when a depth-order-1 player has no formula row (Lloyd, 21 runs; Wease earlier).
2. Hard reviews from QB depth over 1 or an injury-driven depth drop (Caleb Williams); the Standard QB board uses stale depth instead.
3. Teamless or identity mismatches at publish time (Darius Slayton, 09-14 and 09-21, after writes).
4. Injury and availability: no games-missed decision exists (B12); tags are flags only.
5. Veteran signing status: July exclusions and the watchlist are stale; Diggs, Deebo, Allen missing from PPR/Half.
6. Rookie placement: no redraft rookie lane; GNG relies on hand-loaded market values and a name-keyed floor.
7. QB cutline crossings, which need a manual command-line reason.

## Uncertainty

- The Darius Slayton root cause is inferred from the publisher's join logic, not documented.
- Current values come from the local JSON artifacts, not BigQuery.
