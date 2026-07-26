# Phase 34.1 Advanced Situational Metrics BigQuery Dataset Report

## Final Decision

`ADVANCED SITUATIONAL METRICS DATASET READY WITH IDENTITY WARNINGS`

The isolated dataset `fantasy-football-498121.fantasy_football_advanced_metrics` was created and loaded. Source, parsed, long-form, dictionary, coverage, identity, and validation objects are available. No ranking or production object was changed.

## Imported Sources

| Position | File | SHA256 | Rows | Seasons |
|---|---|---|---:|---|
| QB | `qb_situational.db` | `9620b291f4d0c98923fb5138e8ca0da8736440e1adec0167cfa635fda322a239` | 3,824 | 2022-2025 |
| RB | `rb_situational.db` | `9349259188c307454f2aa13a0b7c722533a7e4fc446ec329a4db30fdbe1d006c` | 6,244 | 2022-2025 |
| WR | `wr_situational.db` | `fd7d949f3295ec077f7891a3e803bf3b370dcee1275593108ba5a01b1f69be1a` | 6,031 | 2022-2025 |
| TE | `te_situational.db` | `a73c2c12acbbf92e0bcfda86e9404120e5d73421fba295d486c636c07f9d9972` | 4,136 | 2022-2025 |

Total source rows: 20,235.

## Warehouse Results

| Object | Row count |
|---|---:|
| `source_manifest` | 4 |
| `raw_situational_rows` | 20,235 |
| `qb_situational_metrics` | 3,824 |
| `rb_situational_metrics` | 6,244 |
| `wr_situational_metrics` | 6,031 |
| `te_situational_metrics` | 4,136 |
| `player_situational_metric_long` | 282,993 |
| `situational_refinements` | 42 |
| `situational_metric_dictionary` | 56 |
| `situational_player_identity_candidates` | 945 |
| `situational_metric_coverage` | 2,472 |
| `situational_import_validation_report` | 27 |

Views created:

- `v_qb_standard_situational`
- `v_rb_standard_situational`
- `v_wr_standard_situational`
- `v_te_standard_situational`
- `v_rb_std_gpt55_metric_inputs`

Dataset labels are `system=pigskin`, `source=situational_sqlite`, `status=research`, and `phase=34_1`.

## Refinements And Metrics

The import contains 13 QB refinements, 13 RB refinements, and 8 each for WR and TE. The dictionary governs 17 QB metrics, 17 RB metrics, and 11 each for WR and TE.

The parser handled 368 comma-formatted source values: 2 QB, 176 RB, 177 WR, and 13 TE. Percent values were not converted to decimals. WR/TE route metrics are source-backed only in the new isolated dataset.

Known missing or blocked metrics:

- RB receiving YAC above expectation is unavailable.
- RB broken tackles are unavailable.
- RB YPRR and route share are unavailable in this source.
- Cross-dataset official identity is not established.

## Validation Results

- Source and parsed counts match at 20,235.
- Raw JSON invalid count: 0.
- Required source-field null count: 0.
- Raw duplicate grain count: 0.
- Parsed wide duplicate grain count: 0.
- Long metric count matches the 282,993 governed expansions.
- Coverage rows were generated for all 2,472 position-season-refinement-metric combinations.
- Blocked RB metric dictionary count: 0.
- Repeat import completed with identical physical row counts, proving idempotency.
- Five requested views are queryable.

Checks run:

- `venv\Scripts\python.exe -m py_compile scripts\import_situational_advanced_metrics.py`: pass.
- `venv\Scripts\python.exe -m compileall -q src scripts`: pass.
- `venv\Scripts\python.exe -m unittest tests.test_import_situational_advanced_metrics`: 4 tests passed.
- `venv\Scripts\python.exe scripts\import_situational_advanced_metrics.py --dry-run`: pass.
- `venv\Scripts\python.exe scripts\import_situational_advanced_metrics.py --import`: pass.
- Second `--import` idempotency run: pass with unchanged counts.
- `venv\Scripts\python.exe scripts\check_deployment_safety.py`: all checks passed.
- `venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run`: validation discovery passed through validation 245.
- Focused BigQuery row-count, duplicate-grain, JSON, blocked-metric, view, label, and identity queries: pass.
- `git diff --check`: pass. Existing line-ending warnings remain informational.

The first import attempt created the empty dataset objects but stopped before loading rows because BigQuery JSON loading required timestamp serialization. The importer was corrected to emit RFC 3339 timestamps. The successful import and repeat import both completed afterward.

## Identity Status

All 945 identity candidates are `UNMAPPED`, with confidence `0` and manual review required. This is the intended safe state. Situational source IDs were not treated as GSIS, Sleeper, or internal IDs.

## Files Changed

- `scripts/import_situational_advanced_metrics.py`
- `tests/test_import_situational_advanced_metrics.py`
- `docs/rebuild/advanced-situational-metrics-dataset-contract.md`
- `docs/rebuild/ranking-algorithm-scorecard.md`
- `docs/rebuild/bqml-v2-ranking-architecture.md`
- `docs/rebuild/ranking-opportunity-metrics-matrix.md`
- this report

## Safety Confirmation

- No live ranking write occurred.
- No candidate or champion table changed.
- No model was trained.
- No 2026 outcome was used.
- No deployment occurred.
- Gemini, Pigskin chat, Cloud Run Jobs, ingestion, and materialization outside this isolated import were not run.
- Existing ranking feature marts were not updated.

## Remaining Warning And Next Phase

Identity mapping blocks safe integration with existing player-based marts. Recommended next phase: `Phase 34.2 - Build identity bridge for situational metrics`. Formula testing should wait until the bridge is reviewed, unless the owner explicitly approves source-local analysis that does not join to existing identities.
