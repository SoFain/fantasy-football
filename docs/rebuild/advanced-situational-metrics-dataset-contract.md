# Advanced Situational Metrics Dataset Contract

## Purpose

`fantasy-football-498121.fantasy_football_advanced_metrics` is the isolated research warehouse for the uploaded QB, RB, WR, and TE situational SQLite sources. It does not feed live rankings, active champions, Pigskin chat, or production feature marts.

Dataset labels:

- `system=pigskin`
- `source=situational_sqlite`
- `status=research`
- `phase=34_1`

## Tables And Grain

| Object | Grain |
|---|---|
| `source_manifest` | One row per imported SQLite file version. |
| `raw_situational_rows` | One row per source file and source row ID. `stats_json` is preserved exactly. |
| `situational_refinements` | One row per position and refinement. |
| `situational_metric_dictionary` | One row per position and governed source metric. |
| `situational_player_identity_candidates` | One row per position, source-local player ID, and player slug. |
| `qb_situational_metrics` | One row per season, refinement, and situational player ID. |
| `rb_situational_metrics` | One row per season, refinement, and situational player ID. |
| `wr_situational_metrics` | One row per season, refinement, and situational player ID. |
| `te_situational_metrics` | One row per season, refinement, and situational player ID. |
| `player_situational_metric_long` | One row per player-season-position-refinement-metric. |
| `situational_metric_coverage` | One row per position-season-refinement-metric. |
| `situational_import_validation_report` | One row per validation and applicable position/context. |

Standard-context views filter `refinement = 'standard'`. `v_rb_std_gpt55_metric_inputs` adds null-safe, source-backed RB derivations and identity status. It does not expose YAC above expectation, broken tackles, RB route metrics, or subjective ranking fields.

## Metric Policy

The dictionary contains 56 source-backed numeric metrics: 17 QB, 17 RB, 11 WR, and 11 TE. Numeric strings containing commas are parsed to `FLOAT64`. Percent values remain on the supplied percent scale. A source value of `44.41` remains `44.41`.

WR and TE `routes_run`, `targets_per_route_run`, and `yprr` are approved only inside this dataset until a later identity and integration phase. RB `yac` is raw yards after catch. RB `yards_after_contact` is contact yardage. Neither may be renamed or interpreted as YAC above expectation or broken tackles.

## Identity Policy

`situational_player_id` is source-local. It is not GSIS, Sleeper, or the internal player ID. Initial candidate records use:

- `identity_status=UNMAPPED`
- `match_method=NONE`
- `identity_confidence=0`
- `manual_review_required=true`

No cross-dataset formula work may join on `situational_player_id` alone. A later identity bridge must establish a verified mapping and preserve ambiguous candidates for manual review.

## Import And Validation

The importer is `scripts/import_situational_advanced_metrics.py`. `--dry-run` performs local source validation without BigQuery mutation. `--import` creates the isolated dataset and uses bounded replacement keys by source file, position, and source season range. Repeated imports must not append duplicates.

Required checks:

- source and parsed row counts match;
- seasons are 2022 through 2025;
- raw JSON is valid and preserved exactly;
- required source fields are present;
- parsed grain is unique;
- long metric count equals governed metric expansion;
- comma-formatted numerics parse without percent rescaling;
- metric coverage exists for every imported position-season-refinement-metric;
- blocked RB metrics remain absent;
- source identities remain explicit about mapping status.

## Relationship To Ranking Marts

This dataset is research-only. It must not be merged into `ranking_backtest_feature_mart`, active ranking tables, candidate tables, or champion tables until identity mapping, leakage review, and a separately approved integration phase pass. Formula testing should read standard-context or formula-specific views, not raw tables, and must retain source season boundaries.

