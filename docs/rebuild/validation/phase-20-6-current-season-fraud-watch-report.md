# Phase 20.6 Current-Season Fraud Watch Report

## Purpose

Generate current-season Fraud Watch packets and a deterministic draft `fraud_watch_show` content brief only from real 2025 rows.

This phase did not use historical 2016 Fraud Watch rows and did not fabricate current-season content.

## Source Slice

Selected latest eligible slice:

| Field | Value |
| --- | --- |
| Season | `2025` |
| Week | `18` |
| Scoring profile | `ppr` |
| League type | `redraft` |
| Roster format | `one_qb` |

Eligibility query required nonzero rows in all three current-season marts.

| Mart | 2025 week 18 rows |
| --- | ---: |
| `analytics_fraud_watch` | 57 |
| `analytics_player_weekly_truth` | 1,067 |
| `analytics_player_fantasy_points_by_profile` | 1,067 |

Proof of current-season scope:

- all selected source rows were filtered to `season = 2025`;
- all packet rows written below have `season = 2025` and `week = 18`;
- no historical rows were used as current content.

## Packet Dry Run

Command:

```powershell
.\venv\Scripts\python.exe -m src.segment_packets --packet-type fraud-watch --season 2025 --week 18 --scoring-profile ppr --limit 10 --dry-run
```

Result:

- dry-run completed successfully;
- previewed deterministic Fraud Watch packets from `analytics_fraud_watch`, `compat_trade_assets_current`, and `compat_player_profiles_current`;
- previewed source freshness included `analytics_fraud_watch` season `2025`, week `18`.

## Packet Materialization

Command:

```powershell
.\venv\Scripts\python.exe -m src.segment_packets --packet-type fraud-watch --season 2025 --week 18 --scoring-profile ppr --limit 10
```

Result:

- materialized 10 bounded `fraud_watch_packets` rows;
- packet rows are deterministic and scoped to `2025` week `18`;
- no LLM calls were made.

Packet IDs:

| Packet ID | Player | Fraud score |
| --- | --- | ---: |
| `cd84151396eabb377ac157ed2b4b347d` | Riley Leonard | 83.287 |
| `ab644f8058d4f107acedf9f9e57786cd` | Matthew Stafford | 81.469 |
| `761b6a695b79073ce56ec4a12131ff78` | Mitchell Trubisky | 80.211 |
| `59ee037c09ffc29cba8fc534c0b2d744` | Joe Burrow | 76.739 |
| `1fe2fe5d17fd4c4cbfeef24590449e70` | Trevor Lawrence | 76.456 |
| `e9abb3624816c4dd98d36d470b217373` | Lamar Jackson | 76.285 |
| `e6ee8d1108a0b94942d894018b8f68b7` | C.J. Stroud | 69.543 |
| `1ca00a800933ab334412d403f2c4e4bd` | Bryce Young | 68.970 |
| `dd841f8744b3b253d2aec1fef31b2205` | Caleb Williams | 68.779 |
| `aaa86c34d5369291a47ddc3823c7d5e9` | Jacoby Brissett | 68.281 |

## Content Brief Dry Run

A source-backed dry run was run through the content brief helper with `save_content_brief(..., dry_run=True)` so it could read the newly materialized packet rows without writing.

Result:

| Field | Value |
| --- | --- |
| Brief type | `fraud_watch_show` |
| Review status | `draft` |
| Item count | 5 |
| Dry-run write behavior | no rows inserted |

Preview items:

- Fraud Watch: Riley Leonard
- Fraud Watch: Matthew Stafford
- Fraud Watch: Mitchell Trubisky
- Fraud Watch: Joe Burrow
- Fraud Watch: Trevor Lawrence

## Draft Content Brief

Command:

```powershell
.\venv\Scripts\python.exe -m src.content_briefs --brief-type fraud_watch_show --season 2025 --week 18 --scoring-profile ppr
```

Result:

| Field | Value |
| --- | --- |
| Content brief ID | `brief-fraud_watch_show-2025-w18-20260617T031022Z-bf78cfef` |
| Content brief run ID | `fraud_watch_show-2025-w18-20260617T031022Z-bed3f8ae` |
| Review status | `draft` |
| Item count | 5 |
| Token estimate | 1,310 |

The brief remains draft content for human review. It was not published, approved, or sent to any LLM.

## Validation

Command:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern content_brief
```

Result:

| Pattern | Result |
| --- | --- |
| `content_brief` | 11 passed, 0 failed |

Notable validation coverage:

- content brief run grain passed;
- content brief grain passed;
- content brief item grain passed;
- required JSON keys passed;
- source freshness exists passed;
- missing flags exist passed;
- review status values passed;
- item joins passed;
- no raw source dependency passed.

## Missing Data Notes

The generated packets and brief include expected missing-data flags, including:

- `expected_points_proxy_used`
- `missing_bye_week`
- `missing_fraud_context`
- `missing_model_run_id`
- `missing_rookie_scouting_summary`
- `missing_snaps_last_3`

These flags are carried into the draft brief and should remain visible during human review.

## Safety Status

| Rule | Status |
| --- | --- |
| Used only real 2025 source/mart rows | pass |
| Historical Fraud Watch rows avoided | pass |
| No fabricated current-season rows | pass |
| No LLM calls | pass |
| No scraping | pass |
| No Firebase artifacts | pass |
| Draft-only content output | pass |
| Content brief validation | pass |

## Production Suitability

`draft-ready`

The 2025 week 18 Fraud Watch packets and deterministic draft brief are suitable for human review in the content brief workflow. They are not approved public content and should not be presented as final production content until reviewed.

## Final Decision

`CURRENT-SEASON FRAUD WATCH DRAFT READY`

Current-season Fraud Watch is no longer blocked for the selected 2025 week 18 slice. The generated packet and content brief outputs are bounded, deterministic, draft-only, and sourced from real 2025 marts.
