# Market Context Layer

## Purpose

Pigskin's articles and show prep compare the local boards against "market consensus." Before this layer, those market numbers came from the LLM's memory — last season's values presented as current (a 2026-07-26 article claimed the market treats Drake Maye as a streamer; the live market signal had him aligned with our QB2). This layer supplies **quotable, dated, source-backed market context**.

## Hard Rule

Market data is never a ranking input. No formula view, candidate builder, promoter, situation adjuster, unified-board builder, or the daily refresh chain may read this layer. `tests/test_market_rankings_context.py` enforces this against every ranking-producing surface and fails the build if a reference appears. The only sanctioned market-flavored ranking surfaces remain the owner-approved rookie lanes, which must declare "not a fantasy ranking" in their headers.

## Current Source: Sleeper search_rank

`fantasy_football_advanced_metrics.v_market_rankings_context` joins the active positional boards to the daily Sleeper snapshot (`sleeper_players_current`, refreshed by the 07:00 `ingest-sleeper-news` job — no new API calls, no new ingestion):

- `market_overall_rank` / `market_position_rank`: rank of Sleeper's `search_rank` across active QB/RB/WR/TE.
- `market_delta` = market position rank − Pigskin position rank (positive = Pigskin higher on the player than the market).
- `market_gap_bucket`: `PIGSKIN_MUCH_HIGHER` (10+), `PIGSKIN_HIGHER` (4-9), `ALIGNED`, `MARKET_HIGHER`, `MARKET_MUCH_HIGHER`, `NO_MARKET_SIGNAL`.
- `market_snapshot_at` so every quoted number is dated.

Coverage on 2026-07-26: ~98% of active board rows per profile carry a market signal. Sleeper's `search_rank` is market *perception* (popularity/default ordering), not format-specific ADP — good enough to ground "the market thinks X" claims, and honest about what it is via `market_source_id`.

## Deliberately Not Built (Yet)

- **External crawlers** (CBS top-200, DraftSharks, FantasyPros consensus): feasible, but scraping is fragile and terms-of-service gray. If a true consensus-ADP source is wanted, FantasyPros ECR alone is the right single target — it already aggregates the other outlets. `market_consensus_player_values` (brain) is the purpose-built landing table: it has `source_id`, `adp`, `rank_overall`, `rank_position`, identity `match_method`, and per-profile keys. It currently holds one stale manual PPR seed (2026-06-16) and should be either refreshed or fed by any future source.
- **Feed/dataset wiring**: the article generator (GNG site) should eventually read this as a published dataset artifact (`market_context`) alongside `coaching_staff` and `player_situation` in the public manifest, so Pigskin quotes real numbers instead of memory. That is a publisher/wrapper change plus a site-side prompt change and should be its own reviewed step.

## Operator Commands

```powershell
.\venv\Scripts\python.exe scripts\build_market_rankings_context.py --dry-run
.\venv\Scripts\python.exe scripts\build_market_rankings_context.py --apply
.\venv\Scripts\python.exe -m unittest tests.test_market_rankings_context
```
