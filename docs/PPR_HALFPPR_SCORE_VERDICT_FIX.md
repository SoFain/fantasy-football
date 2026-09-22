# PPR / Half-PPR Rankings: Score and Verdict Repair

Written 2026-07-13 while debugging why thegng.us/ranks showed broken PPR data. Resolved and published the same day. The GNG site displayed the published feed faithfully; the defect was in how the PPR/Half-PPR positional boards were written into BigQuery.

The permanent release procedure and prevention checks live in `docs/rankings-production-runbook.md`.

## Production status

- PPR board: `unified-ppr-fable-v1-20260713235323`
- Half-PPR board: `unified-half-ppr-fable-v1-20260713235352`
- Public manifest: `v1/manifests/sha256-080157371a26016c10ce35d4a9fa1d293efddac62c27395f140e2d2b649955df.json`
- All four profiles are present with zero warnings.
- PPR and Half-PPR RB/WR/TE scores span `50-99`; missing and rank-only verdict counts are zero.

## Symptom (what a viewer sees)

On the **PPR** and **Half-PPR** Overall boards:
- Skill-position scores are tiny and nonsensical next to QBs: Christian McCaffrey (RB) shows **1.9**, Amon-Ra St. Brown (WR) **2.0**, but Josh Allen (QB) shows **100.0**.
- Verdicts are the flat template: *"RB Fable v1 ranks Christian McCaffrey at RB1 after the shared current-roster safety layer."*

On the **Standard** board everything is correct: scores are 0-100 across all positions (McCaffrey 99, Amon-Ra 99, Josh Allen 100) and verdicts are rich (*"Christian McCaffrey earns RB1 on 24.1 non-garbage-time touches per game plus 23.5% target share..."*).

Measured score ranges by profile/position on the Overall board (from the live feed):

| profile   | QB       | RB          | WR          | TE          |
|-----------|----------|-------------|-------------|-------------|
| standard  | 86-100   | 69.6-99     | 67.8-99     | 70.9-99     |
| ppr       | 85-100   | **0.28-1.89** | **0.25-1.95** | **0.90-2.13** |
| half_ppr  | 86-100   | **0.20-1.89** | **0.40-1.95** | **0.90-2.13** |
| gng_keeper| 94-99.5  | 84-99.5     | 76-99.5     | 95.5-99.5   |

The QB row is normalized on every profile; only the RB/WR/TE rows on ppr/half_ppr are on the raw scale.

## Where the data comes from

The public feed (`scripts/publish_public_rankings.py`) builds each profile from two BigQuery sources:

- Overall board: `fantasy-football-498121.fantasy_football_brain.unified_draft_rankings_current`
- Positional board (carries `ranking_score` + `pigskin_verdict`): `fantasy-football-498121.fantasy_football_brain.analytics_pigskin_rankings`

The score and verdict shown on the site come from `analytics_pigskin_rankings` (`ranking_score`, `pigskin_verdict`). Those rows are written by per-profile "promote" scripts.

## Root cause: two divergent promote lineages

RB/WR/TE rows are written by different scripts for standard vs the reception profiles, and they disagree on exactly two columns.

### `promote_standard_fable_v1_positional.py` (correct)

```sql
-- ranking_score: per-position min-max normalization to ~50-99
ROUND(50 + 49*SAFE_DIVIDE(adjusted_score - min_score, max_score - min_score), 1) AS ranking_score,
...
-- pigskin_verdict: rich, metric-driven
CONCAT(
  FORMAT('%s earns RB%d on %.1f non-garbage-time touches per game plus %.1f%% target share. ',
    player_name, final_rank, non_garbage_time_touches_per_game, target_share),
  FORMAT('His %.1f red-zone touches and %.2f blended TDs per game support the scoring case',
    red_zone_touches_per_game, blended_td_per_game),
  CASE WHEN epa_per_touch < 0
    THEN FORMAT(', while %.2f EPA per touch limits the efficiency boost.', epa_per_touch)
    ELSE FORMAT('; %+.2f EPA per touch adds efficiency support.', epa_per_touch) END
) AS pigskin_verdict,
```

### `promote_ppr_fable_v1_positional.py` (the bug)

```sql
c.adjusted_score AS ranking_score,          -- RAW score, no normalization (~0.2-2.1)
...
-- no rich pigskin_verdict; only a flat rationale template:
CONCAT('PPR Fable v1; ', context.post_formula_adjustment_detail, ' ', c.decision_note) AS rank_rationale,
```

So for ppr/half_ppr, `ranking_score` is the raw `adjusted_score` (a VORP-scale number ~0-2) instead of the 50-99 min-max scaling standard uses, and the rich `pigskin_verdict` is never populated (the site falls back to the flat "Fable v1 ranks ... after the shared current-roster safety layer" text).

### Why QBs look fine on every profile

QB rows are not written by these Fable scripts. They come from the shared guarded-QB promote (`promote_guarded_qb_to_reception_profiles.py` / `promote_standard_qb_guarded_75_25.py`), which already emits a 0-100 `ranking_score`. That is why Josh Allen is 100 on PPR while the RB/WR/TE around him are 1-2. On the PPR board, Josh Allen's verdict even reads "guarded Standard formula," confirming the QB rows are borrowed from the standard/guarded lineage.

## Implemented fix

Bring `promote_ppr_fable_v1_positional.py` (and the half_ppr path it shares via `--scoring-profile`) in line with `promote_standard_fable_v1_positional.py` for the RB/WR/TE INSERT blocks:

1. **Normalize `ranking_score`.** Replace `c.adjusted_score AS ranking_score` with the same per-position min-max scaling:
   ```sql
   ROUND(50 + 49*SAFE_DIVIDE(adjusted_score - min_score, max_score - min_score), 1) AS ranking_score
   ```
   Compute `min_score`/`max_score` as `MIN(adjusted_score)`/`MAX(adjusted_score)` windowed per position within the profile board (standard does this in its `ranked` CTE). Keep the raw value in `raw_ranking_score` as standard does.

2. **Populate `pigskin_verdict`.** The promotion now joins the RB, WR, and TE scored metric views and emits profile-specific summaries. RB uses target share, touches, red-zone work, touchdown rate, and EPA per touch. WR uses target share, WOPR, meaningful targets, YPRR, and scoring or availability context. TE uses routes, target share, red-zone targets, YPRR, targets per route, and scoring or availability context.

3. **Fail closed.** Promotion rejects null or rank-only verdicts and any RB/WR/TE position that does not normalize to an exact `50-99` range.

4. **Avoid unified-board streaming locks.** Unified promotion now uses committed BigQuery load jobs rather than streaming inserts.

5. **Publish all profiles together.** `scripts/publish_public_rankings.py --publish --gcloud-auth` defaults to all four scoring profiles and updates the manifest only after immutable board objects succeed.

### Publish contract

`publish_public_rankings.py` rewrites `v1/manifest.json` with only the profiles passed in that run. Publish all four profiles in the same invocation, or omit `--profile` and use the default `SCORING_PROFILES` set.

## Verification (before publishing)

Confirm the reception boards are normalized and verdict-filled, matching standard:

```sql
SELECT scoring_profile_id, position,
       ROUND(MIN(ranking_score),1) AS mn,
       ROUND(MAX(ranking_score),1) AS mx,
       COUNTIF(pigskin_verdict IS NULL OR pigskin_verdict = '') AS missing_verdicts
FROM `fantasy-football-498121.fantasy_football_brain.analytics_pigskin_rankings`
WHERE is_active AND scoring_profile_id IN ('standard','ppr','half_ppr')
  AND position IN ('QB','RB','WR','TE')
GROUP BY scoring_profile_id, position
ORDER BY scoring_profile_id, position;
```

Expect every PPR and Half-PPR RB/WR/TE position to have `mn = 50`, `mx = 99`, and `missing_verdicts = 0`. Also count rank-only templates because they are populated strings:

```sql
COUNTIF(REGEXP_CONTAINS(
  COALESCE(pigskin_verdict,''),
  r'Fable v1.*ranks .* after the shared current-roster safety layer'
)) AS flat_verdicts
```

The production result is `flat_verdicts = 0` for both reception profiles.

## GNG side

No GNG change is needed. The daily cron (`tasks/import_pigskin_rankings.php` -> `pigskin_rankings_import()`) imports whatever profiles the manifest lists and skips unchanged boards by sha256. Once all four profiles are republished, the morning cron picks them up automatically, or the GNG maintainer can run the import on demand to see it immediately.
