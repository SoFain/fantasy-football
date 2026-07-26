# Phase 38.26 WR Coverage Repair And Publication

## Final Decision

Published. The refreshed Sleeper layer, Marvin Harrison identity repair, and veteran-only WR coverage fallback passed the candidate and post-promotion coverage gates. Standard, PPR, and Half-PPR positional boards were rebuilt, their unified Top 100 boards were replaced, and a complete four-profile immutable JSON release is live.

Malik Nabers is WR8 in all three redraft profiles. Marvin Harrison is WR39. The public overall ranks are Standard 22 and 92, PPR 15 and 84, and Half-PPR 19 and 91, respectively.

## Formula And Coverage Decision

The active WR formula weights did not change. `v_wr_fable_v1_current_candidates` keeps every qualified WR Fable v1 score exact. A veteran who misses the current six-game or 40-target threshold may enter only when a prior qualified v1 score exists:

```text
carry_forward_score =
  prior_v1_score
  - prior_v1_age_availability_component
  + current_two_year_age_availability_component
```

The fallback excludes limited-sample rookies. Current Sleeper team, depth, status, and injury remain outside the formula and enter through `v_ranking_post_formula_safety`.

## Backtest Evidence

| Measure | Repaired v1 baseline | Veteran fallback |
|---|---:|---:|
| Complete rows | 364 | 372 |
| Spearman | 0.7578 | 0.7602 |
| Score correlation | 0.7626 | 0.7645 |
| Top-12 precision | 0.6389 | 0.6111 |
| Points captured at 12 | 0.9172 | 0.9216 |
| NDCG at 24 | 0.8500 | 0.8503 |
| Pairwise win rate | 0.7778 | 0.7793 |
| Elite misses | 8 | 8 |
| Top-12 busts | 2 | 2 |

Existing v1 scores changed: `0`. The top-12 precision warning comes from expanding the evaluation cohort to include Rashee Rice's actual WR5 finish while the fallback placed him WR19. It is not movement among existing v1 rows. The coverage lane was accepted because it repairs a real omission, improves the broad rank metrics, and leaves the qualified formula cohort untouched.

## Identity Repair

The WR situational source record `d96487d` with slug `marvin-harrison` now maps explicitly to GSIS `00-0039849`. The override is source-local, reports reason `MARVIN_HARRISON_JR_SOURCE_ID`, and leaves the general same-name bridge fail-closed.

Live verification after deployment:

- identity status `VERIFIED`
- confidence `1.0`
- duplicate collision `false`
- 2025 formula score `0.5690409938477787`
- active redraft positional rank WR39

## Sleeper Refresh

The exact dry-run payload was applied and archived:

- fetched at `2026-07-20T01:59:58.860146+00:00`
- 12,200 current-player rows
- maximum verified context age after load: about 0.02 hours
- Malik Nabers: NYG, active, depth order 1, questionable, two years experience
- Marvin Harrison: ARI, active, depth order 1, two years experience

## Coverage Gates

The candidate-stage and post-promotion runs of:

```powershell
.\venv\Scripts\python.exe scripts\audit_current_player_ranking_coverage.py --fail-on-blocking
```

both exited `0` with:

- blocking established-player omissions: `0`
- PPR versus Half-PPR presence mismatches: `0`
- BigQuery Sleeper context age: `0` whole hours
- current frontline universe: 32 players at each position

The remaining omissions are five unmodeled 2026 rookies and valid TE candidates below TE35. No 2026 rookie entered a redraft positional or public board through the fallback.

## Production Versions

| Layer | Version |
|---|---|
| Standard positional RB, WR, TE | `standard-fable-v1-safety-20260720022301` |
| PPR positional RB, WR, TE | `ppr-fable-v1-safety-20260720022352` |
| Half-PPR positional RB, WR, TE | `half-ppr-fable-v1-safety-20260720022424` |
| Standard unified | `unified-fable-v1-standard-20260720022711` |
| PPR unified | `unified-ppr-fable-v1-20260720022731` |
| Half-PPR unified | `unified-half-ppr-fable-v1-20260720022751` |

All positional rows are contiguous and teamless-free. Standard has RB85, WR100, TE35. PPR and Half-PPR each have RB80, WR100, TE35. The existing QB queues were preserved.

## Public Release

- [Current manifest](https://storage.googleapis.com/fantasy-football-498121-public-rankings/v1/manifest.json)
- [Immutable manifest](https://storage.googleapis.com/fantasy-football-498121-public-rankings/v1/manifests/sha256-42c44719465aa145aa34b9361f2c609d62a087c7cd46fa41d75e61cb5cc96ca1.json)

| Profile | Board SHA-256 |
|---|---|
| Standard | `00ce0001df5499fe4b718b541f60fc999b1396d1e4c10b92903e21bac1c07662` |
| PPR | `983c8ce57c70b95719e3f2e33207ce4b9e100f676e28ad84112a624cc07d5057` |
| Half-PPR | `a683772f9bf51b35559113278f0fae88d606c69bdbc64adcb2b4c193cf7a20b1` |
| GNG Keeper | `ac7616017deae4015a67fb14de0ca3148a6dfcc4fc2ce013d26de0054bafcc9e` |

Anonymous verification returned HTTP 200 and matching byte counts and hashes for all four boards. Each has 100 overall players, zero warnings, zero teamless rows, zero missing or rank-only verdicts, and exact positional counts. GNG has zero missing, over-length, or mismatched context fields.

## Files Changed

- `bigquery/views/v_wr_fable_v1_identity_bridge.sql`
- `bigquery/views/v_wr_fable_v1_current_candidates.sql`
- `scripts/build_wr_fable_v1d_layer.py`
- `scripts/build_standard_wr_fable_v1_safety_review.py`
- `scripts/build_ppr_fable_v1_review_boards.py`
- `scripts/promote_standard_fable_v1_positional.py`
- `scripts/promote_ppr_fable_v1_positional.py`
- `scripts/audit_current_player_ranking_coverage.py`
- focused WR, safety, promotion, and coverage tests
- `AGENTS.md`
- `docs/rankings-production-runbook.md`
- this report

## Checks Run

- 39 focused WR, safety, promotion, and coverage tests passed.
- 14 unified-board and public-feed tests passed.
- WR Fable identity and modified-layer views deployed successfully.
- Standard, PPR, and Half-PPR positional dry-runs passed before writes.
- All three unified dry-runs validated active positional ranks before committed load jobs.
- Local four-profile publication returned zero warnings before the external publish flag was used.
- Anonymous manifest and object verification passed after publication.

## Remaining Work

Build the separate rookie system before admitting Jeremiyah Love, Kenyon Sadiq, Carnell Tate, Jadarian Price, or KC Concepcion to redraft rankings. Isaiah Likely remains a documented TE model-versus-market review, not a pipeline failure.

## Pigskin Provenance Handoff

The active Standard, PPR, and Half-PPR rows for Malik Nabers and Marvin Harrison must retain two levels of explanation:

- `rank_rationale` is the concise, public explanation imported into the website database. Nabers must name the 2024 qualified-score carry-forward, the four-game and 35-target 2025 sample, the availability-component replacement, the raw score, and the Sleeper role adjustment. Harrison must name the verified identity repair, the 12-game and 73-target qualified sample, the raw score, the Sleeper role adjustment, and the fact that formula weights did not change.
- `llm_adjustment_evidence` is the granular warehouse record. It must preserve the exact carry-forward components for Nabers and the source-local identity override details for Harrison.

Pigskin Studio reads `ranking_context` for GNG and falls back to `rank_rationale` for redraft profiles. Future ranking agents must verify the public JSON and the IONOS import after any change to these explanations.

The provenance-only release was verified after publication. It changed no score, positional rank, or unified rank. The IONOS importer refreshed Standard, PPR, and Half-PPR, and the production Studio context returned the complete Nabers and Harrison explanations shown above.
