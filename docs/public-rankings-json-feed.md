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

## Datasets

The manifest's `datasets` block lists supporting objects next to the four profiles. Each entry carries at least `object`, `url`, `sha256`, `bytes`, and `source_generated_at`; objects are content-addressed under `v1/datasets/<name>/sha256-<digest>.json` in the same public bucket (`https://storage.googleapis.com/fantasy-football-498121-public-rankings/`) and are immutable. The daily chain uploads each dataset object before the publisher runs. A dataset whose artifacts are missing on a given day is carried forward unchanged from the live manifest, so an entry can be older than the boards. Consumers verify each object against its `sha256` like a board.

| Dataset | Producer | Contents |
|---|---|---|
| `coaching_staff` | `src/coaching_staff_feed.py` | Current NFL coaching staffs |
| `player_situation` | `src/situation_feed.py` | Per-player 2026 situation context |
| `market_context` | `src/market_context_feed.py` | Sleeper ADP and trending market context |
| `inseason_rankings` | `scripts/inseason_rankings.py --release-artifacts` | Experimental weekly and ROS horizons |
| `availability` | `scripts/run_availability_decisions.py --live` (`src/availability_feed.py`) | Injury availability context for every currently injured player |

### `availability` (schema `availability-1.0`)

Context only: it never moves a rank, and nothing in the four profiles depends on it. The manifest entry adds `decision_date`, `week`, `player_count`, and `warnings` (a count of injured players omitted for lacking a Sleeper id). Built by `docs/ai-decision-layer.md` Pilot 1: code computes every date, count, and probability; Jev (TypeSafe) only reads news text.

```json
{
  "schema_version": "availability-1.0",
  "generated_at": "2026-09-28T05:07:18Z",
  "decision_date": "2026-09-28",
  "season": 2026,
  "week": 3,
  "models": {"base_rates": "availability_base_rates_other_v1,availability_base_rates_v1,availability_next_buckets_v1", "jev_question_set": "availability_qs_v1", "jev_model": "jev-1.13.0"},
  "players": [
    {
      "gsis_id": "00-0036285",
      "sleeper_player_id": "6836",
      "player_name": "A.J. Terrell",
      "team": "ATL",
      "position": "CB",
      "designation": "IR",
      "designation_source": "team_roster",
      "practice": "Did Not Participate",
      "body_part": "Groin",
      "next_game": {"opponent": "NO", "kickoff_utc": "2026-10-06T00:15:00Z"},
      "base_rate": {"p_play_next_game": 0.124, "missed_bucket": {"0": 0.14, "1": 0.047, "2_4": 0.169, "5_plus_or_season": 0.644}},
      "text": {
        "availability": "will_miss", "availability_confidence": 0.9,
        "absence": "5_plus_or_season", "absence_confidence": 0.81,
        "trend": "worsening", "trend_confidence": 0.55,
        "relevant_items": 5,
        "sources": [{"source": "Team news feed", "url": "https://...", "published_at": "2026-09-23T02:38:57Z"}]
      },
      "caveats": [
        "Sleeper data is not collected for this position; the designation is from the team's weekly roster.",
        "No official injury report for this game yet; the base rate uses his report for his last game."
      ]
    }
  ]
}
```

Field rules (validated in `src/availability_feed.py` before upload and again by `scripts/verify_live_rankings.py`):

- `decision_date` is the America/New_York date of the run; `week` is the NFL week of the league's next kickoff (1 to 22). `generated_at` and every `kickoff_utc` or `published_at` are ISO 8601 UTC with `Z`.
- Only players with a current injury designation are included, sorted by `team` then `player_name`. `team` and `next_game.opponent` are Sleeper team codes (`LAR`, not `LA`). `sleeper_player_id` is always a string; `gsis_id` is `00-` plus seven digits or null. `next_game` may be null.
- `designation` is the Sleeper `injury_status` as shown when `designation_source` is `sleeper`. For positions the Sleeper snapshot does not store (offensive line, defense, P, LS) it comes from the official injury report (`official_report`: Out, Doubtful, Questionable) or the team's weekly roster reserve list (`team_roster`: IR, PUP, NFI). `designation_source` is the one field added to the owner's fixed schema.
- `practice` is the official practice participation for the report the base rate uses (`Did Not Participate`, `Limited`, `Full`) or null. `body_part` is the listed injury or null.
- `base_rate` is always an object: `p_play_next_game` is the structured base rate (no language model) that he plays the next game, and `missed_bucket` always has the four keys `0`, `1`, `2_4`, `5_plus_or_season` (games missed counted from the next game). Probabilities are rounded to 3 decimals. `missed_bucket["0"]` and `p_play_next_game` are separate estimates of the same event (the bucket lanes drop censored outcomes), so they can differ by a few points; use `p_play_next_game` for "will he play".
- `text` is always an object with all eight keys. `availability`, `absence`, and `trend` (and their confidences) are null when Jev was below its confidence threshold or no news item was judged relevant; they are never guessed. `relevant_items` is the count of items Jev judged relevant; `sources` lists at most three of them, newest first.
- `caveats` are short plain-English notes built by code (which report the base rate used, missing snap counts, blank text and why).

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
