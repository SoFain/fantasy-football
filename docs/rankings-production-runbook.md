# Rankings Production Runbook

## Purpose

This is the canonical release procedure for Standard, PPR, Half-PPR, and GNG Keeper rankings.

The formulas are research assets. Promotion code must preserve their player order and raw scores unless a formula change has completed its own backtest and owner review. Public-score normalization, current-roster checks, Pigskin verdicts, unified-board generation, and JSON publication are separate production stages.

## Production Flow

| Stage | Owns | Must preserve |
|---|---|---|
| Formula and candidate board | Position-specific raw score and formula rank | Approved weights, metrics, backtest result, player order |
| Post-formula safety | Team, eligibility, depth-chart and injury context | Formula score and documented owner decisions |
| Positional promotion | Active positional rows, public score, verdict and provenance | Formula rank unless an approved safety decision changes it |
| Unified Top 150 | Cross-position interleaving | Exact active positional order and source version |
| GNG context | Format-specific scoring explanation and formula-input percentiles | Active GNG ranks, formula IDs and source status |
| Public JSON | Immutable consumer snapshot | Unified ranks plus current positional context |

Never treat `ranking_score` as the formula output. The formula value belongs in `raw_ranking_score` and `candidate_ranking_score`. `ranking_score` is the public Pigskin score normalized within each position to `50-99`.

## Scientific Provenance Contract

Cloud ranking artifacts are scientific records. Pigskin's personality is injected only by the GNG site's runtime prompt. Do not store roasts, slang, or show copy in formula definitions, model runs, adjustment evidence, or `rank_rationale`.

Every active row must connect the final rank to its inputs through `ranking_version`, `model_name`, `rank_source`, `model_run_id`, raw score, candidate rank, final rank, `rank_rationale`, and the adjustment audit fields. A formula revision gets a new version and an archive-backed model run. Record the changed metrics or weights, the approved backtest, and any material player-level effect. Never silently rewrite the meaning of an existing version.

Current injury and suspension information is post-formula context. A designation alone creates a review flag and zero absence movement. A penalty requires source-backed expected regular-season games missed. Store the event type, source and evidence time, `llm_estimated_games_missed`, bounded adjustment code, evidence, candidate-to-final rank delta, and confirmation that the raw formula score was unchanged. The concise version must be appended to `rank_rationale` so the GNG site and future agents can explain the final number.

## Active Formula Sources

| Profile | Position | Formula source |
|---|---|---|
| Standard | QB | Guarded Standard 75/25 queue |
| Standard | RB | RB Fable 0.1 |
| Standard | WR | WR Fable v1 current candidates: exact qualified score plus prior-qualified veteran coverage fallback, followed by post-formula review and the elite-order guardrail |
| Standard | TE | TE Fable v1.0a no-man |
| PPR and Half-PPR | QB | Guarded Standard queue, because QB scoring is unchanged |
| PPR and Half-PPR | RB | RB Fable 0.1 with 2% shifted from non-garbage-time touches to target share |
| PPR and Half-PPR | WR | The same WR Fable v1 current-candidate score transferred unchanged |
| PPR and Half-PPR | TE | TE Fable v1.0a no-man transferred unchanged |
| GNG Keeper | All | Approved GNG position-specific formulas and Sleeper layer |

Reception-profile candidate tables are `ppr_fable_rankings_current` and `half_ppr_fable_rankings_current`. They contain ranks and formula scores, not the advanced fields required for public explanations. `scripts/promote_ppr_fable_v1_positional.py` must join the scored RB, WR, and TE views when generating Pigskin verdicts.

## Release Invariants

A release is invalid if any of these checks fail:

- A teamless player appears on an active positional or unified board.
- Active positional ranks are duplicated, missing, or non-contiguous.
- A unified board contains anything other than 150 unique players ranked 1 through 150.
- A unified board changes the order of players within a position.
- A unified row's positional rank or source version differs from the active positional board.
- An RB, WR, or TE public score falls outside the position's `50-99` normalized range.
- A public verdict is null, empty, or merely repeats the player's rank.
- An identity repair, qualification fallback, guardrail, or manual adjustment lacks granular `rank_rationale` and `llm_adjustment_evidence` that identify the source inputs, formula impact, and post-formula movement.
- A public manifest omits any of `standard`, `ppr`, `half_ppr`, or `gng_keeper`.
- A public board hash differs from the SHA-256 recorded in the manifest.
- A current team or positional context value is borrowed from a stale board.
- A GNG positional row lacks the GNG-only `context` field or exceeds 320 characters.
- An established, active Sleeper depth-order-1 player with a current team disappears before the candidate stage because of identity failure, a one-season qualification threshold, missing situational source data, or a formula transform dropout.

Current positional row contracts:

| Profile | QB | RB | WR | TE |
|---|---:|---:|---:|---:|
| Standard | 45 | 85 | 100 | 35 |
| PPR | 45 | 80 | 100 | 35 |
| Half-PPR | 45 | 80 | 100 | 35 |
| GNG Keeper | 45 | 80 | 100 | 35 |

Standard has 85 RB rows because teamless players are unranked. Do not manufacture fallback players to reach a round number.

## Release Procedure

### 1. Identify the change class

- Formula change: requires backtesting, a candidate comparison, owner approval, and a new formula version.
- Safety-layer change: requires current roster evidence and an explicit adjustment reason.
- Presentation repair: may change `ranking_score` or verdict text, but must prove zero rank changes.
- Unified interleaver change: requires queue-preservation tests and a new Top 150 validation report. A pure cutoff expansion must also prove that the prior Top 100 remains the exact prefix.
- Publication-only change: must not mutate BigQuery ranking rows.

Do not combine a formula experiment with a presentation repair.

### 2. Run focused tests

For the reception profiles:

```powershell
.\venv\Scripts\python.exe -m unittest `
  tests.test_promote_ppr_fable_v1_positional `
  tests.test_build_unified_ppr_fable_v1_top100 `
  tests.test_promote_unified_fable_v1_standard_top100 `
  tests.test_public_rankings_feed
```

Use the narrow tests for the paths being changed. Add a regression assertion for the exact defect.

Run the current-player coverage gate before any positional promotion:

```powershell
.\venv\Scripts\python.exe scripts\audit_current_player_ranking_coverage.py --fail-on-blocking
```

The command is read-only against BigQuery. It writes a local JSON audit and rebuild report, then exits `2` if an established depth-order-1 player has been lost before the candidate or positional board. Rookie-system gaps and players who have valid formula rows below a documented board cutoff remain visible in the report but do not trip this gate.

### 3. Dry-run positional promotion

```powershell
.\venv\Scripts\python.exe scripts\promote_ppr_fable_v1_positional.py --scoring-profile ppr
.\venv\Scripts\python.exe scripts\promote_ppr_fable_v1_positional.py --scoring-profile half_ppr
```

The dry runs must succeed before the write gate is opened.

### 4. Promote positional boards

```powershell
$env:ALLOW_PPR_FABLE_POSITIONAL_PROMOTION='true'
.\venv\Scripts\python.exe scripts\promote_ppr_fable_v1_positional.py --scoring-profile ppr --apply
.\venv\Scripts\python.exe scripts\promote_ppr_fable_v1_positional.py --scoring-profile half_ppr --apply
```

The promoter archives prior active rows before replacement. It must reject teamless players, missing metric context, rank-only verdicts, and a score range other than `50-99`.

### 5. Validate active positional rows

```sql
SELECT
  scoring_profile_id,
  position,
  COUNT(*) AS row_count,
  MIN(rank) AS min_rank,
  MAX(rank) AS max_rank,
  ROUND(MIN(ranking_score),1) AS min_score,
  ROUND(MAX(ranking_score),1) AS max_score,
  COUNTIF(current_team IS NULL) AS teamless_rows,
  COUNTIF(pigskin_verdict IS NULL OR pigskin_verdict='') AS missing_verdicts,
  COUNTIF(REGEXP_CONTAINS(
    COALESCE(pigskin_verdict,''),
    r'Fable v1.*ranks .* after the shared current-roster safety layer'
  )) AS rank_only_verdicts
FROM `fantasy-football-498121.fantasy_football_brain.analytics_pigskin_rankings`
WHERE is_active
  AND scoring_profile_id IN ('ppr','half_ppr')
  AND position IN ('RB','WR','TE')
GROUP BY scoring_profile_id,position
ORDER BY scoring_profile_id,position;
```

Expected result: contiguous ranks, `50-99` scores, zero teamless rows, and zero invalid verdicts.

For a presentation repair, compare the new board with the immediately prior archived version. The required result is zero player-rank mismatches.

### 6. Build separate unified boards

Never reuse one output path for both profiles.
The original builder and Standard/PPR promoter module names retain `top100` for command compatibility, but their production contract and default outputs are Top 150.

```powershell
.\venv\Scripts\python.exe scripts\build_unified_fable_v1_top100.py `
  --json-output output\unified-fable-v1-standard-top150.json `
  --markdown-output docs\rebuild\unified-fable-v1-standard-top150.md

.\venv\Scripts\python.exe scripts\build_unified_ppr_fable_v1_top100.py `
  --scoring-profile ppr `
  --json-output output\unified-ppr-fable-v1-top150.json `
  --markdown-output docs\rebuild\unified-ppr-fable-v1-top150.md

.\venv\Scripts\python.exe scripts\build_unified_ppr_fable_v1_top100.py `
  --scoring-profile half_ppr `
  --json-output output\unified-half-ppr-fable-v1-top150.json `
  --markdown-output docs\rebuild\unified-half-ppr-fable-v1-top150.md

.\venv\Scripts\python.exe scripts\build_unified_gng_2026_top100.py `
  --output output\unified-gng-2026-top150.json
```

### 7. Dry-run and promote unified boards

```powershell
.\venv\Scripts\python.exe scripts\promote_unified_fable_v1_standard_top100.py `
  --board output\unified-fable-v1-standard-top150.json
.\venv\Scripts\python.exe scripts\promote_unified_ppr_fable_v1_top100.py `
  --scoring-profile ppr --board output\unified-ppr-fable-v1-top150.json
.\venv\Scripts\python.exe scripts\promote_unified_ppr_fable_v1_top100.py `
  --scoring-profile half_ppr --board output\unified-half-ppr-fable-v1-top150.json
.\venv\Scripts\python.exe scripts\build_unified_gng_2026_top100.py `
  --output output\unified-gng-2026-top150.json --apply
.\venv\Scripts\python.exe scripts\promote_unified_gng_2026_top150.py `
  --board output\unified-gng-2026-top150.json

$env:ALLOW_UNIFIED_FABLE_V1_TOP100_PROMOTION='true'
$env:ALLOW_UNIFIED_PPR_FABLE_V1_TOP100_PROMOTION='true'
$env:ALLOW_UNIFIED_GNG_2026_TOP150_PROMOTION='true'
.\venv\Scripts\python.exe scripts\promote_unified_fable_v1_standard_top100.py `
  --board output\unified-fable-v1-standard-top150.json --apply
.\venv\Scripts\python.exe scripts\promote_unified_ppr_fable_v1_top100.py `
  --scoring-profile ppr --board output\unified-ppr-fable-v1-top150.json --apply
.\venv\Scripts\python.exe scripts\promote_unified_ppr_fable_v1_top100.py `
  --scoring-profile half_ppr --board output\unified-half-ppr-fable-v1-top150.json --apply
.\venv\Scripts\python.exe scripts\promote_unified_gng_2026_top150.py `
  --board output\unified-gng-2026-top150.json --apply
```

Unified promoters use BigQuery load jobs. Do not replace them with `insert_rows_json`; streaming inserts can block later profile replacement for an extended period.

### 8. Build GNG context

Dry-run the complete active board first:

```powershell
.\venv\Scripts\python.exe scripts\build_gng_rank_context.py
```

Expected counts are QB 45, RB 80, WR 100, and TE 35. The script must preserve every active player, rank, rank source, and formula ID. Veteran text comes from the formula's current advanced inputs and must use at least two driver metrics per position across the full board. The driver picks the player's scoring archetype; a supporting input should come from a different metric family when available. Rookie text must say that it is provisional instead of inventing NFL history.

Materialize the approved rows with a committed load job:

```powershell
$env:ALLOW_GNG_RANK_CONTEXT_PUBLISH='true'
.\venv\Scripts\python.exe scripts\build_gng_rank_context.py --apply
```

This is a presentation stage. It must not write to `analytics_pigskin_rankings` or `unified_draft_rankings_current`.

### 9. Generate all public profiles locally

```powershell
.\venv\Scripts\python.exe scripts\publish_public_rankings.py
```

This must return all four profiles with 150 overall rows and zero warnings. Stop if it does not.

### 10. Publish all profiles

```powershell
.\venv\Scripts\python.exe scripts\publish_public_rankings.py --publish --gcloud-auth
```

Do not pass a single `--profile` during a normal production release. The manifest is replaced, not merged. Omitting `--profile` publishes the complete `SCORING_PROFILES` set.

The publisher uploads content-addressed board objects first, then an immutable versioned manifest, and updates `v1/manifest.json` last.

## Daily automated board refresh, publish, and site import

Since 2026-07-24 the scheduled task `PigskinDailyPublishImport` runs daily at 07:30 America/New_York as the final leg of the 7am chain (07:00 `ingest-sleeper-news` and 07:15 `detect-player-changes` run on Cloud Run). It executes this runbook automatically, fail-closed, via `scripts/run_daily_board_refresh.py` and the wrapper `scripts/daily_pigskin_chain.ps1` (both in this checkout since the 2026-07-26 branch reconciliation merged the platform worktree into the codex line):

1. **Board refresh** — the release procedure above as a chain: safety context rebuilt from today's saved Sleeper snapshot (`build_sleeper_current_player_context.py --from-warehouse`, zero API calls), focused tests, the coverage gate, dry-run of every positional promoter, gated applies, positional invariants, unified builds and promotions, unified invariants, GNG context, and a local all-profile publish validation. Formula changes still require owner review: the chain re-runs approved formulas on fresh data and stops if any guardrail trips.
2. **Publish** — `publish_public_rankings.py --publish --gcloud-auth`, all four profiles, `datasets` carried forward.
3. **Site import** — `run_remote_php.py --file scripts/trigger_site_rankings_import.php`; unchanged profiles skip by sha256.

After GNG context, the chain rebuilds the player situation layer from the freshly promoted boards, emits the `player_situation` public dataset artifacts (the wrapper uploads the immutable object and passes `--dataset-entry`), and writes the owner-review queue of flagged ranked players to `output\daily-publish\situation-review-<date>.md`. Boards publish at schema 1.3 with per-player `situation` and `metrics` blocks; situation facts never move ranks.

Refresh exit policy: `0` publish the new boards; `1` a pre-write gate tripped (for example the QB24 cutline guardrail) — boards are untouched, the last-approved state is republished, and the gate output in `output\daily-publish\` is an owner-review item; `3` failure after writes began — publication is skipped per Recovery below.

Remove with `schtasks /delete /tn "PigskinDailyPublishImport" /f`. The prior publish-only wrapper `scripts/daily_publish_and_import.ps1` remains as a fallback.

### 11. Verify anonymously

Fetch the public manifest without credentials:

`https://storage.googleapis.com/fantasy-football-498121-public-rankings/v1/manifest.json`

Confirm:

- exactly four profile entries;
- each board returns HTTP 200;
- downloaded bytes match the listed SHA-256;
- every board has 150 overall players;
- warnings are empty;
- PPR and Half-PPR skill-position scores span `50-99`;
- rank-only verdict count is zero.
- every GNG positional player has non-empty `context` of at most 320 characters;
- each GNG Top 150 player carries the matching positional `context`.

The release is incomplete until this check passes.

## Recovery

If positional promotion fails before the update statement, no active rows changed. Fix the preflight error and rerun the dry run.

If a failure occurs after active rows are replaced, stop publication. Restore the last approved positional version from `analytics_pigskin_rankings_history` through a reviewed transaction, rebuild the affected unified board, then publish all four profiles together.

If unified promotion fails, do not publish. The positional board may be correct while the Top 150 still references an older positional version.

If public publication fails before `v1/manifest.json` changes, consumers remain on the prior complete release. Immutable objects uploaded before the failure are harmless and may be reused by hash.

If the manifest was published with missing profiles, rerun a full local generation and publish all four profiles. Do not patch the website database by hand.

## 2026-07-13 Incident Record

What broke:

- PPR and Half-PPR promotion wrote raw formula-scale values into public `ranking_score`.
- Reception-profile verdicts inherited a rank-only template instead of using advanced metrics.
- A Standard-only publication replaced the manifest and removed the other three profiles.
- Streaming unified inserts created a BigQuery buffer that blocked immediate replacement.

What did not break:

- The approved positional formulas.
- PPR and Half-PPR player order.
- Backtest results and formula weights.

The repair produced zero rank mismatches across 430 PPR and Half-PPR RB/WR/TE rows. It changed the public score scale, regenerated metric-backed verdicts, replaced streaming writes with committed load jobs, rebuilt the unified boards, and published all four profiles.

The detailed repair evidence is in `docs/rebuild/validation/phase-38-22-ppr-half-ppr-score-verdict-repair.md`.
