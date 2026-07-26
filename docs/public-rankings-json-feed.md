# Public Rankings JSON Feed

Production ranking changes must follow `docs/rankings-production-runbook.md`. That runbook owns the formula-preservation, promotion, unified-board, all-profile publication, and anonymous-verification sequence.

The rankings project publishes validated public snapshots from these canonical BigQuery tables:

- Overall Top 150: `fantasy_football_brain.unified_draft_rankings_current`
- Positional boards and verdicts: `fantasy_football_brain.analytics_pigskin_rankings`
- GNG scoring context: `fantasy_football_advanced_metrics.gng_2026_rank_context`

## Public contract

Current manifest:

`https://storage.googleapis.com/fantasy-football-498121-public-rankings/v1/manifest.json`

The manifest lists Standard, PPR, Half PPR, and GNG Keeper. Each entry points to a content-addressed JSON object under `v1/boards/<profile>/sha256-<digest>.json`.

Board objects and versioned manifests are immutable. Uploads use the Cloud Storage `ifGenerationMatch=0` precondition. `v1/manifest.json` is the only mutable object. It is updated after every board object and the versioned manifest have uploaded successfully.

Consumers should fetch `v1/manifest.json`, compare each profile's `sha256` or `board_version`, and download only changed profiles. They should verify the downloaded bytes against the manifest SHA-256 before importing.

Each profile contains:

- The canonical overall Top 150.
- Full active QB, RB, WR, and TE positional boards.
- Pigskin scores, verdicts, public adjustment details, risk flags, and formula source metadata.
- Source table names, board version, and source generation time.

Schema `1.2` expands every overall board from 100 to 150 players. GNG Keeper retains its `context` field on both overall and positional players. Veteran text starts from the player's strongest percentile signal, adds support from a different metric family when available, then identifies the weakest modeled input. The scoring language changes with the resulting workload, receiving, efficiency, or role archetype. Rookie context is marked provisional because no NFL metric history exists.

The other scoring profiles do not include `context`. Their existing `pigskin_verdict` and `rank_rationale` fields are unchanged.

`rank_rationale` is the shared scientific provenance summary for every scoring profile. It must remain free of Pigskin voice. Formula changes and confirmed post-formula injury or suspension movement must state what changed, the source-backed missed-time estimate when applicable, and the candidate-to-final rank effect. The GNG site may apply Pigskin's personality only after importing this neutral record.

## Publication

Install dependencies, generate local artifacts, then publish:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe scripts\publish_public_rankings.py
.\venv\Scripts\python.exe scripts\publish_public_rankings.py --publish --gcloud-auth
```

The first command without `--publish` validates the live source boards and writes local artifacts under `output/public-rankings`. It does not change Cloud Storage. The `--publish` flag is the explicit external-write gate. `--gcloud-auth` uses the active `gcloud` user only for Cloud Storage and avoids changing local Application Default Credentials. Omit it in Cloud Run or another environment whose attached service account owns the bucket write permission.

The publisher fails closed unless every profile has exactly 150 unique overall players with contiguous ranks. Every active positional board must exist with contiguous ranks. Teamless players are rejected from both overall and positional feeds. A Top 150 player without a matching active positional row remains in the canonical overall board with `positional_context_status: "missing"`; positional fields stay null and the feed reports a named warning instead of fabricating context.

GNG publication also fails if an active positional row lacks `context` or the text exceeds 320 characters. Generate and inspect the context table before running the public publisher:

```powershell
.\venv\Scripts\python.exe scripts\build_gng_rank_context.py
$env:ALLOW_GNG_RANK_CONTEXT_PUBLISH='true'
.\venv\Scripts\python.exe scripts\build_gng_rank_context.py --apply
```

This step reads the active GNG boards and the same advanced-input query used by their approved formulas. It does not update `analytics_pigskin_rankings` or the unified board.

`ranking_score` is a normalized public Pigskin score. It is not the raw formula output. RB, WR, and TE public scores must span `50-99` within each active positional board. Raw formula values remain in their provenance fields.

Normal production publication must include all four profiles. Supplying one or more `--profile` arguments replaces the manifest with only that subset. Omit `--profile` for a complete release.

## Initial bucket setup

The dedicated bucket is created once in `us-central1` with uniform bucket-level access. Public access grants only `roles/storage.objectViewer` to `allUsers`. No service-account credentials or BigQuery access are exposed through the feed.

Browser CORS permits read-only `GET` and `HEAD` requests from `https://www.thegng.us` and `https://thegng.us`. The configuration lives at `config/public_rankings_cors.json`.
