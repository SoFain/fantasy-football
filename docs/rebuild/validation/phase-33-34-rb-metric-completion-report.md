# Phase 33.34 - RB Metric Completion Sprint

## Final Decision

`RB STD GPT 5.5 v1.0A REVISION REQUIRED`

The exact `RB STD GPT 5.5 v1.0` formula remains blocked. No true RB receiving YAC-above-expectation records exist in the loaded warehouse for the historical windows required by Standard RB targets 2023, 2024, and 2025.

No formula was tested. No rankings, champions, models, or deployments changed.

## Files Changed

- `docs/rebuild/validation/phase-33-34-rb-metric-completion-report.md`

No source, SQL, migration, validation, model, or application file changed.

## Git State

The worktree was already dirty with prior Phase 33 changes. This phase preserved those changes and did not stage or commit files.

## True RB Receiving YAC-AOE Source Audit

The audit searched schema columns, populated values, source payload text, downstream materializations, and representative RB names.

| Source | Candidate field | RB rows | RB non-null values | Finding |
|---|---|---:|---:|---|
| `raw_nflverse_ngs_receiving` | `avg_yac_above_expectation` | 0 for 2020-2025 | 0 | Raw source contains WR and TE records only. |
| `ngs_receiving` | `avg_yac_above_expectation` | 0 in loaded 2025 table | 0 | Current loaded table contains WR and TE only. |
| `player_week_ngs_metrics` | `ngs_yac_over_expected` | 3,392 RB/HB rows for 2020-2025 | 0 | RB rows exist because the table also carries rushing NGS fields; receiving YAC-OE is null. |
| `player_week_advanced_metrics` | `ngs_yac_above_expectation` | 9,508 RB rows for 2020-2025 | 0 | Downstream field remains null for every RB row. |
| `player_season_advanced_metrics` | `ngs_yac_above_expectation` | 1,175 RB rows for 2020-2025 | 0 | Seasonal aggregation cannot create a missing source metric. |
| `ranking_backtest_feature_mart` | `ngs_yac_over_expected_score_3yr` | 1,254 / 1,276 / 366 Standard RB rows for targets 2023 / 2024 / 2025 | 0 / 0 / 0 | No usable backtest predictor. |
| `analytics_player_weekly_truth` | `avg_yac_above_expectation` | 1,578 RB rows in current 2025 truth | 0 | No RB source value. |
| `stg_player_week_stats` | none | N/A | N/A | Carries, targets, receptions, and yards exist; expected YAC does not. |
| `raw_nflverse_weekly` payload | searched for YAC expectation keys | 0 matching payloads | 0 | No hidden source field. |
| `raw_nflverse_pbp` payload | searched for YAC expectation keys | 0 matching payloads | 0 | No hidden source field. |
| `raw_ffopportunity_pbp_pass` payload | searched for YAC expectation keys | 0 matching payloads | 0 | Expected fantasy opportunity fields are not NGS receiving YAC-OE. |
| `raw_nflverse_participation` payload | searched for YAC expectation keys | 0 matching payloads | 0 | Participation cannot supply receiving YAC-OE. |

The only loaded raw payload family containing `expected_yac` or `yac_above_expectation` keys is `raw_nflverse_ngs_receiving`, with 8,856 matching records for 2020-2025. Those records are WR/TE-only. Searches for Christian McCaffrey, Alvin Kamara, Austin Ekeler, De'Von Achane, Jahmyr Gibbs, Bijan Robinson, Saquon Barkley, and Derrick Henry returned no RB receiving NGS rows.

### Conclusion

`RB RECEIVING YAC AOE METRIC UNAVAILABLE`

The field exists in schema but not for the RB population. Backfilling the current downstream columns would only copy nulls. No warehouse write or backfill was performed.

## Leakage-Safe Coverage Windows

| Target season | Allowed source seasons | RB YAC-AOE non-null |
|---|---|---:|
| 2023 | 2020-2022 | 0/603 player-seasons |
| 2024 | 2021-2023 | 0/596 player-seasons |
| 2025 | 2022-2024 | 0/575 player-seasons |

No 2026 outcomes were queried or used.

## Owner-Approved v1.0a Revision Proposal

The exact v1.0 efficiency score is not testable:

```text
Efficiency_Score =
  0.35 * RYOE_Per_Attempt_Modifier
  + 0.25 * NGS_Rushing_Efficiency_Modifier
  + 0.20 * Box_Resilience_Modifier
  + 0.20 * Receiving_YAC_Above_Expectation_Modifier
```

### Recommended v1.0a: rushing-only redistribution

Remove the unavailable receiving component and redistribute its weight proportionally:

```text
Efficiency_Score_v1_0a =
  0.4375 * RYOE_Per_Attempt_Modifier
  + 0.3125 * NGS_Rushing_Efficiency_Modifier
  + 0.2500 * Box_Resilience_Modifier
```

This is the narrowest revision. It uses only the three approved source-backed metrics and preserves their original relative weighting. It still needs an explicit missing-data policy because each NGS rushing field covers only 319/603, 305/596, and 295/575 RB player-seasons across the three target windows.

### Optional v1.0a-EPA: separate owner decision

Receiving EPA is source-backed for RBs through `player_season_advanced_metrics.receiving_epa`:

| Target | Receiving EPA coverage | Missingness |
|---|---:|---:|
| 2023 | 512/603 | 15.1% |
| 2024 | 507/596 | 14.9% |
| 2025 | 487/575 | 15.3% |

If the owner wants to preserve a receiving-efficiency component, test this as a separately named variant:

```text
Efficiency_Score_v1_0a_EPA =
  0.35 * RYOE_Per_Attempt_Modifier
  + 0.25 * NGS_Rushing_Efficiency_Modifier
  + 0.20 * Box_Resilience_Modifier
  + 0.20 * Receiving_EPA_Per_Target_Modifier
```

Use `receiving_epa_per_target`, not total receiving EPA, so receiving volume does not masquerade as efficiency. This is a concept change, not a drop-in replacement for YAC above expectation. It requires explicit owner approval and separate testing.

Raw YAC remains prohibited as a substitute.

## Fumble Metric Implementation Plan

### Source

- Fumbles lost: `analytics_player_fantasy_points_by_profile.source_stat_json.fumbles_lost`.
- Source-season coverage for Standard RB player-week rows is complete for 2020-2024: 1,459/1,459, 1,511/1,511, 1,587/1,587, 1,487/1,487, and 1,524/1,524.
- Touch denominator: `player_week_advanced_metrics.carries + receptions`.
- Opportunity context for the risk flag remains `carries + targets`, matching the existing opportunity convention. Do not use targets as fumble exposures.

### Leakage-Safe Projection

For target season `T`:

```text
Season_Fumble_Lost_Rate_y =
  Fumbles_Lost_y / (Carries_y + Receptions_y)

Projected_Fumble_Lost_Rate =
  0.60 * Rate_(T-1)
  + 0.30 * Rate_(T-2)
  + 0.10 * Rate_(T-3)

Projected_Touches =
  0.60 * Touches_(T-1)
  + 0.30 * Touches_(T-2)
  + 0.10 * Touches_(T-3)

Projected_Fumbles_Lost =
  Projected_Fumble_Lost_Rate * Projected_Touches

Fumble_Lost_Penalty =
  2 * Projected_Fumbles_Lost
```

Rules:

- use only seasons before `T`;
- retain true zero fumbles lost as zero, not missing;
- mark a season rate missing when touches are zero or unavailable;
- renormalize weights across available prior seasons rather than zero-filling missing rates;
- require at least one prior season with touches;
- expose source-season counts and a `fumble_rate_limited_history` flag;
- do not use 2026 outcomes or current Sleeper context.

Owner clarification is still needed on small-sample shrinkage. A future implementation should compare the direct weighted rate with an RB-league-average shrinkage variant, but should not silently add a prior in v1.0a.

## Availability Metric Implementation Plan

### Source Definitions

For target season `T`:

```text
Games_With_Offensive_Snaps_Last_Season =
  COUNT(DISTINCT week WHERE season = T-1 AND offensive_snaps > 0)

Games_With_Offensive_Snaps_Two_Years_Ago =
  COUNT(DISTINCT week WHERE season = T-2 AND offensive_snaps > 0)
```

Source: `player_week_advanced_metrics.offensive_snaps`, `metric_version='advanced_player_metrics_v1'`.

Coverage is effectively complete in the Phase 33.33 audit: 4,757/4,761, 4,793/4,793, and 4,808/4,808 RB player-week rows have a non-null offensive snap value across the three target windows.

### Age Factor

Derive age as of September 1 in target season `T` from `dim_players_current.birth_date`. Do not use the current stored age. Birth-date coverage is 231/234, 229/232, and 224/226 RB identities for the target windows.

| Target-season age | Factor |
|---:|---:|
| 21-24 | 1.00 |
| 25 | 0.99 |
| 26 | 0.98 |
| 27 | 0.96 |
| 28 | 0.93 |
| 29 | 0.89 |
| 30+ | 0.84 |

Missing birth date must produce an explicit flag. It must not default to a favorable age factor without owner approval.

### Historical Availability

```text
Historical_Availability_Factor =
  (
    0.70 * Games_With_Offensive_Snaps_Last_Season
    + 0.30 * Games_With_Offensive_Snaps_Two_Years_Ago
  ) / 17

Historical_Availability_Factor =
  CLAMP(Historical_Availability_Factor, 0.65, 1.00)

Projected_Games_Played =
  17 * Age_Availability_Factor * Historical_Availability_Factor

Availability_Multiplier =
  Projected_Games_Played / 17
```

### Availability Risk Flag

Set `availability_risk_flag=true` when at least two conditions are true:

- last-season games with offensive snaps are 12 or fewer;
- combined games with offensive snaps over the last two seasons are 26 or fewer;
- target-season age is at least 28;
- historical availability factor is below 0.80;
- prior-season opportunities, defined as carries plus targets, are at least 300 and target-season age is at least 27.

Do not call this `injury_prone`. Store the individual condition flags so the result is explainable.

## Leakage Validation Contract

Any future implementation must assert:

- every source season is less than the target season;
- target 2023 uses no data after 2022;
- target 2024 uses no data after 2023;
- target 2025 uses no data after 2024;
- age is calculated as of the target season, not current date;
- no current Sleeper roster, market, ranking, or 2026 outcome enters a historical feature;
- fumble and availability missingness remains visible;
- raw/source tables stay outside Pigskin-facing views.

## Validation Performed

- Warehouse schema search for all YAC expectation columns.
- Position and non-null counts across raw NGS, derived NGS, advanced metrics, truth, and ranking feature mart tables.
- Raw payload search across weekly, PBP, ffopportunity PBP, participation, and NGS receiving sources.
- Representative RB-name search in the direct NGS receiving source.
- Focused receiving EPA, fumble, touch, snap, and birth-date coverage checks.
- `check_deployment_safety.py`: PASS, all checks true.
- `run_bigquery_validations.py --run --pattern ngs_direct_metrics`: PASS, 1 validation.
- `run_bigquery_validations.py --run --pattern route_metrics`: PASS, 2 validations.
- `git diff --check`: PASS with preexisting LF-to-CRLF warnings on four tracked research docs.

## No-Live-Change Confirmation

- No formula tests.
- No ranking writes.
- No champion activation.
- No model training.
- No deployment.
- No BigQuery writes or backfills.
- No Gemini, Pigskin chat, or Sleeper API calls.
- No 2026 outcomes used.
- No raw YAC substitution.

## Warnings

- The exact formula remains blocked even though its fumble and availability lanes are implementable.
- NGS rushing efficiency coverage is only about half of the broad RB player-season universe. The next formula phase must define eligibility or missingness behavior before scoring.
- Receiving EPA is a valid optional source-backed metric, but it measures play value rather than YAC above expectation.

## Recommended Next Phase

Owner decision between:

- `Phase 33.35 - implement RB STD GPT 5.5 v1.0a rushing-only dry-run`; or
- `Phase 33.35 - implement and compare v1.0a rushing-only versus v1.0a-EPA`.

Do not resume formula testing until the owner explicitly selects the revision and missing-data policy.
