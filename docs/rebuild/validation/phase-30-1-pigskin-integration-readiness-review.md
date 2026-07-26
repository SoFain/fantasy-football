# Phase 30.1 Pigskin Integration Readiness Review

Final decision: **PIGSKIN INTEGRATION NEEDS RETRIEVAL LAYER**

The completed 2014-2025 nflverse packet warehouse is validated and useful as historical player context. It should not be exposed directly to Pigskin yet. The next step is a Pigskin-safe retrieval layer that enforces season/window filters, player ID disambiguation, historical-vs-current wording, source freshness, missing-data flags, and blocked-metric presentation.

## Gate State

All checked gates were empty or unset:

- `ALLOW_PIGSKIN_PACKET_REFRESH`
- `ALLOW_ADVANCED_METRICS_MATERIALIZATION`
- `ALLOW_NFLVERSE_STAGING_MATERIALIZATION`
- `ALLOW_NFLVERSE_HISTORICAL_BACKFILL`
- `ALLOW_NFLVERSE_WEEKLY_REFRESH`
- `ALLOW_NFLVERSE_WAREHOUSE_MIGRATION_APPLY`
- `ALLOW_TRADE_PICK_SCORE_MATERIALIZATION`
- `ALLOW_TRADE_SCORE_MATERIALIZATION`
- `ALLOW_LIMITED_PRODUCTION_DEPLOY`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER`

No authorization gate was set in this phase.

## Git State

- latest commit: `acdb92c Expand nflverse Pigskin packets through 2025`
- staged files: none
- untracked backlog remains separate, including historical validation reports and `phase-29-50-2025-expansion-commit-report.md`
- no expected source modifications were present before this report was created

## Baseline Check Results

Baseline checks passed:

- safety checker: pass
- `py_compile` for nflverse packet, advanced metrics, staging, backfill, backfill plan, and `app.py`: pass
- `compileall -q src scripts`: pass
- `tests.test_nflverse_pigskin_packets`: pass, 15 tests
- `tests.test_nflverse_advanced_metrics`: pass, 12 tests
- `tests.test_nflverse_staging`: pass, 11 tests
- `tests.test_nflverse_backfill_executor`: pass, 18 tests
- `tests.test_nflverse_backfill_plan`: pass, 15 tests
- `unittest discover tests`: pass, 487 tests
- migrations: no pending migrations
- validation dry-run: catalog discovered through `200_no_pressure_metrics_without_source.sql`

## Final Warehouse State

Packet surfaces:

| Object | Row count | 2026+ rows |
| --- | ---: | ---: |
| `pigskin_player_context_packet_current` | 4,084 | 0 |
| `compat_pigskin_player_context_current` | 4,084 | 0 |

Packets by season:

| Season | Packet count |
| --- | ---: |
| 2014 | 482 |
| 2015 | 498 |
| 2016 | 128 |
| 2017 | 479 |
| 2018 | 111 |
| 2019 | 113 |
| 2020 | 525 |
| 2021 | 107 |
| 2022 | 131 |
| 2023 | 508 |
| 2024 | 492 |
| 2025 | 510 |

Packet health:

| Check | Result |
| --- | ---: |
| duplicate packet grain count | 0 |
| missing packet JSON count | 0 |
| missing packet text count | 0 |
| missing source freshness count | 0 |
| missing blocked metric flags count | 0 |

2026+ separation:

- raw nflverse 2026+ rows: 0
- staging 2026+ rows: 0
- advanced metric 2026+ rows: 0
- packet 2026+ rows: 0

Score lanes are unchanged and out of scope for this review:

- `trade_player_scores`: 154 rows
- `trade_pick_scores`: 64 rows

## Packet Schema And Surface Audit

`compat_pigskin_player_context_current` exposes:

- `as_of_season`
- `as_of_week`
- `player_id_internal`
- `player_name`
- `position`
- `team`
- scoring, league, and roster profile IDs
- `packet_version`
- `feature_run_id`
- `packet_text`
- `packet_json`
- `source_freshness_json`
- `missing_data_flags`
- `created_at`

Safe for Pigskin retrieval after guardrails:

- `as_of_season`, `as_of_week`, `player_id_internal`, scoring context, `packet_version`, `feature_run_id`
- `packet_text` as compact historical context
- parsed `packet_json` as structured evidence
- parsed `source_freshness_json` and `missing_data_flags`

Use with caution:

- `player_name` is a compact display name such as `T.Hill`, not always a full name
- `team` is historical as-of packet context, not current team
- `position` is historical as-of packet context
- `created_at` is provenance, not freshness of current roster state

Keep internal:

- base table component columns such as `identity_json`, `advanced_metrics_json`, `recent_form_json`, `team_context_json`, ranking/projection/trade/risk JSON
- base table `pigskin_player_context_packet_current` itself should remain an internal/output object behind a retrieval layer

Packet JSON top-level fields observed in representative rows:

- `identity`
- `usage_summary`
- `receiving_air_yards`
- `efficiency_summary`
- `qb_context`
- `team_context`
- `blocked_metrics`
- `source_freshness`
- `source_metric_version`
- `warnings`

The JSON payloads are stored as strings. A retrieval layer should parse them before passing structured context to Pigskin.

## Source Isolation Audit

`compat_pigskin_player_context_current` view SQL reads only:

- `pigskin_player_context_packet_current`

It does not directly read:

- `raw_nflverse_*`
- `stg_*`
- `play_by_play`
- `weekly_metrics`
- `player_rosters`
- LLM output tables
- content brief tables

Validation `198_compat_pigskin_context_no_raw_dependencies.sql` passed with `raw_source_dependency_count = 0`.

Repository tests also enforce that compatibility views do not read raw/source tables and that app code does not directly reference `pigskin_player_context_packet_current` at request time.

## Repository Integration Point Audit

Current Pigskin tool path:

- `src/pigskin_context_tools.py` declares named tools only. It does not expose `execute_bigquery_sql`.
- `get_player_context_packet` and `search_players` currently call `src.llm_context_packets`.
- `src.llm_context_packets` reads `llm_player_context_packet`, a separate compatibility view over `mart_llm_player_context_packet`.
- The new nflverse packet surface is not yet wired into `src.pigskin_context_tools.py` or app prompt retrieval.

Current prompt guardrail:

- `app.py` already tells Pigskin: "For offseason or current roster context, use current team and roster-status fields from the tools. Never describe a historical stat-week team as a player's current team."

Current roster sources:

- Sleeper global current player snapshot writes to `sleeper_players_current`.
- Viewer-team/current league context uses `sleeper_roster_players`, `sleeper_available_players`, and related snapshot tables through existing Data Ops paths.
- Those sources should remain behind controlled materializers or compatibility functions, not direct Pigskin raw-table access.

Risk:

- If `compat_pigskin_player_context_current` is added as a model-visible tool without a retrieval layer, Pigskin could confuse historical packet team with current roster/team/free-agent state.
- Compact display names create wrong-player risk without player ID or team/position disambiguation.

## Pigskin-Safe Retrieval Rules

1. Always require an explicit historical season or as-of window. No default "current" answer from nflverse packets.
2. Never answer 2026 roster, free-agent, dynasty availability, or current-team questions from nflverse packets.
3. Use Sleeper/current roster source for 2026 roster/team/free-agent status.
4. Require `player_id_internal` when available. For name lookup, require full-name resolution plus `team` and `position` when compact names collide.
5. Preserve packet warnings and include them in Pigskin context.
6. Surface blocked metrics as unavailable, not zero.
7. Treat Week 22 as historical/postseason context.
8. Keep raw/staging tables out of Pigskin prompts.
9. Use a compatibility view or purpose-built Pigskin-safe retrieval function. Do not expose the base table directly.
10. Include source freshness/provenance when the packet is used for analysis.
11. If historical packet team and current roster team differ, state both explicitly.
12. If current roster source says free agent, say the historical packet shows prior usage, not current team status.
13. If Sleeper and nflverse identity mappings disagree, stop at an ambiguity warning and require player ID confirmation.

## Display-Name Ambiguity Review

Across 2014-2025, compact packet display names have substantial ambiguity:

- ambiguous display names: 693
- max distinct player IDs for one display name: 6
- max team count for one display name: 8
- max position count for one display name: 4

High-risk examples:

| Display name | Risk |
| --- | --- |
| `D.Johnson` | 6 distinct player IDs, 8 teams, 3 positions |
| `J.Williams` | multiple RB/WR identities across BUF, DAL, DEN, DET, GB, NO, TB, WAS |
| `K.Williams` | Kyren Williams plus older RB/WR collisions |
| `A.Brown` | A.J. Brown, Antonio Brown, and another QB collision |
| `J.Jefferson` | Justin Jefferson WR/MIN and Jermar Jefferson RB/DET |
| `T.Hill` | Tyreek Hill WR/MIA/KC and Taysom Hill TE/NO |

Specific note:

- `Tyreek Hill` full-name lookup does not directly match `compat_pigskin_player_context_current` because the view stores compact `player_name` values such as `T.Hill`.
- `T.Hill` returns both Tyreek Hill and Taysom Hill rows.
- Tyreek Hill historical packet resolution requires player ID or `T.Hill` plus `team=MIA` and `position=WR` for the 2025 Miami historical row.

Recommendation: public UI and Pigskin tool calls should prefer player ID. If only a name is provided, the retrieval layer should return candidates instead of selecting automatically when more than one player/team/position identity exists.

## Historical-vs-Current Player-State Separation

nflverse historical packets can answer:

- what a player did in a completed season/week
- usage, target share, weighted opportunity, WOPR, EPA/opportunity, QB environment, team context for that historical slice
- historical comparison across completed seasons
- whether source freshness and missing-data warnings apply to the packet

Sleeper/current roster source must answer:

- current team
- current free-agent status
- current roster availability
- current fantasy availability
- current dynasty/keeper availability
- current injury/status fields where sourced from Sleeper snapshots

When a user asks about a player going into 2026:

- retrieve current Sleeper/current roster state first for roster/team/status
- retrieve nflverse packets only as historical performance evidence
- label the historical packet by `as_of_season` and `as_of_week`
- do not overwrite current status with packet team

Tyreek Hill example:

- 2025 nflverse packet context: Miami historical evidence for completed-season usage.
- 2026 roster/free-agent state: must come from Sleeper/current roster data.
- Pigskin should say: "The 2025 packet is Miami context. Current 2026 status comes from the current roster source."

## Week 22 And Postseason Handling

Week 22 packet rows:

| Season | Week 22 packet rows |
| --- | ---: |
| 2022 | 1 |
| 2023 | 20 |
| 2024 | 19 |
| 2025 | 17 |

Week 22 text check:

- total Week 22 packets: 57
- packet text with season/week label: 57
- current-like wording count: 0

Recommended rule:

- default regular-season fantasy analysis should exclude Week 22 unless the user asks for playoff/postseason/full historical context
- full historical analysis can include Week 22, but must label it as postseason/historical

## Blocked Metric Presentation

Blocked metrics present in packet JSON:

- route share
- yards per route run
- targets per route run
- first-read share
- red-zone usage
- high-value touches
- touchdown rates
- reception-flag-dependent metrics
- true pressure
- contact yards
- alignment

Also treat as unavailable when present:

- QB sack/scramble details
- pass rate over expected

Presentation rule:

- "Unavailable in this packet/source version" is correct.
- "Zero" is wrong unless the metric is explicitly present and numeric zero.
- Pigskin should not roast or praise a player for a blocked metric.

## Readiness Matrix

| Use case | Status | Notes |
| --- | --- | --- |
| Historical player context for completed seasons | Ready with guardrails | Warehouse and packet integrity pass. Needs retrieval layer for season and identity filters. |
| Historical player comparison | Ready with guardrails | Compare by explicit season/window and player IDs. |
| Historical team/role usage context | Ready with guardrails | Team is historical as-of context only. |
| Trade analyzer enrichment | Needs code | Can enrich with historical packets after deterministic merge rules are defined. |
| Viewer-team roster-aware context | Needs Sleeper merge rules | Current roster source must lead. Historical packets can add evidence only. |
| 2026 current roster/team/free-agent questions | Needs Sleeper merge rules | nflverse packets must not answer current status. |
| Dynasty/keeper forward-looking recommendations | Needs code | Must merge current roster, market, and historical context with clear provenance. |
| Public UI exposure | Needs owner decision | Should require player ID or explicit disambiguation UX. |
| LLM prompt injection into Pigskin | Needs code | Do not inject raw view rows directly. Build a tool with guardrails. |
| Data Ops refresh controls | Needs owner decision | Existing Data Ops controls remain disabled by default. No new controls in this phase. |

## Needed Next Code Or Schema Changes

Recommended next-phase work:

1. Build a Pigskin-safe packet retrieval service/function that reads `compat_pigskin_player_context_current`.
2. Add explicit inputs: `season`, optional `week`, `player_id_internal`, scoring profile, league type, roster format, and inclusion mode for postseason.
3. Add candidate-return behavior for ambiguous compact names.
4. Add full-name or alias support, or join through an identity bridge, so `Tyreek Hill` can resolve without relying on `T.Hill`.
5. Add Sleeper/current roster merge rules for 2026-facing questions.
6. Add prompt guardrails that distinguish `historical_team` from `current_team`.
7. Add Week 22 inclusion/exclusion controls.
8. Add tests that the retrieval layer does not query raw/staging tables.
9. Add tests that current roster questions do not use nflverse packet team as current team.
10. Add blocked-metric display rules to Pigskin schema/tool docs.
11. Consider a narrower view that renames `team` to `historical_team` and `player_name` to `display_name` before LLM exposure.

## No-State-Change Confirmation

Final read-only count confirmation after checks:

- `pigskin_player_context_packet_current`: 4,084 rows
- `compat_pigskin_player_context_current`: 4,084 rows
- 2026+ packet rows: 0
- packet counts by season unchanged from the beginning of the phase

No BigQuery rows were written. No materialization, packet refresh, raw backfill, staging materialization, advanced metrics materialization, packet-display repair, LLM call, Pigskin prompt, Sleeper API call, scrape, deployment, feature flag change, Cloud Run Job, Scheduler job, or commit was run.

## Validation Results

Read-only validation patterns:

- `raw_nflverse`: pass, 3 passed, 0 failed, informational coverage warning
- `stg_`: pass, 7 passed, 0 failed
- `advanced_metrics`: pass, 4 passed, 0 failed
- `compat_pigskin`: pass, 2 passed, 0 failed
- `trade_player_scores`: pass, 12 passed, 0 failed
- `trade_pick_scores`: pass, 17 passed, 0 failed, informational model-version warning

## Final Local Checks

Final checks passed:

- safety checker: pass
- `py_compile` for nflverse packet, advanced metrics, staging, backfill, backfill plan, and `app.py`: pass
- `compileall -q src scripts`: pass
- targeted nflverse tests: pass
- full `unittest discover tests`: pass, 487 tests
- migrations: no pending migrations
- validation dry-run: discovered through validation 200

## Staging And Production Untouched

Production:

- service: `nfl-studio-dashboard`
- revision: `nfl-studio-dashboard-00077-2jp`
- image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f`
- traffic: `nfl-studio-dashboard-00077-2jp=100`
- Data Ops job trigger flags: false
- Data Ops local subprocess flags: false

Staging:

- service: `nfl-studio-dashboard-staging`
- revision: `nfl-studio-dashboard-staging-00029-jtb`
- image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8`
- traffic: `nfl-studio-dashboard-staging-00029-jtb=100`
- Data Ops job trigger flags: false
- Data Ops local subprocess flags: false

## Remaining Warnings

- Integration is not ready for LLM-facing use until a retrieval layer enforces historical context, disambiguation, and current roster separation.
- `compat_pigskin_player_context_current.player_name` is compact display text, not reliable full-name identity.
- 693 ambiguous compact display names exist across 2014-2025.
- Week 22 rows are historical/postseason context and should not be included in regular-season analysis by default.
- Some packet/source freshness JSON values are nested string JSON and should be parsed by a helper before LLM use.
- `raw_nflverse` validation retains its informational coverage-review warning.
- `trade_pick_scores` validation retains its informational model-version warning.

## Recommended Next Phase

Recommended next phase: **Phase 30.2 — Build Pigskin-safe packet retrieval layer**.

That phase should include Sleeper/current roster merge rules and Pigskin prompt/UI guardrails for historical packet exposure.
