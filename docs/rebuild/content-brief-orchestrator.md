# Content Brief Orchestrator

The Content Brief Orchestrator assembles deterministic, evidence-backed show prep briefs for AI vs. Meatbags.

## Scope

This phase adds:

- `content_brief_runs`
- `content_briefs`
- `content_brief_items`
- [src/content_briefs.py](../../src/content_briefs.py)
- Validation SQL for grains, required JSON keys, size bounds, freshness, and missing flags.

This phase does not:

- Call LLMs.
- Create Firebase artifacts.
- Change Pigskin chat.
- Add direct UI behavior.
- Apply migrations automatically.

## Allowed Inputs

The orchestrator uses curated outputs and packets:

- `trade_review_packets`
- `fraud_watch_packets`
- `sleeper_breakout_packets`
- `llm_player_context_packet`
- `projections_player_weekly`
- `projections_player_ros`
- `projections_player_dynasty`
- `projection_rankings_current`
- `claim_grades`
- `claim_source_scorecards`
- `model_runs`
- `scoring_profiles`
- `league_types`
- `roster_formats`

The current helper queries these curated tables where implemented:

- `fraud_watch_packets`
- `sleeper_breakout_packets`
- `trade_review_packets`
- `projection_rankings_current`
- `claim_source_scorecards`

## Supported Brief Types

- `fraud_watch_show`
- `sleeper_breakout_show`
- `trade_review_show`
- `rankings_debate_show`
- `meatbag_accountability_show`
- `weekly_streamers_show`
- `dynasty_value_show`
- `full_weekly_show_prep`

## Brief Contents

Each generated brief includes:

- title
- segment objective
- ordered top items
- evidence summaries
- counterarguments
- confidence
- source freshness
- missing-data flags
- suggested segment order
- snark hooks
- do-not-overclaim caveats
- `llm_prompt_payload_json`

The LLM payload is deterministic and safe for a future writing agent. It contains compact ordered items and explicit caveats. It does not trigger an LLM call.

## Bounds

Default item caps:

- Fraud Watch: 5
- Sleeper Breakout: 5
- Trade Review: 3
- Rankings Debate: 8
- Meatbag Accountability: 6
- Weekly Streamers: 8
- Dynasty Value: 8
- Full Weekly Show Prep: 14

`brief_text` is capped at 12000 characters and `token_estimate` is capped at 3500.

## CLI

Dry-run Fraud Watch:

```powershell
python -m src.content_briefs --brief-type fraud_watch_show --season 2025 --week 7 --scoring-profile ppr --dry-run
```

Dry-run full weekly prep:

```powershell
python -m src.content_briefs --brief-type full_weekly_show_prep --season 2025 --week 7 --dry-run
```

On Windows, prefer the repo venv:

```powershell
.\venv\Scripts\python.exe -m src.content_briefs --brief-type fraud_watch_show --season 2025 --week 7 --scoring-profile ppr --dry-run
```

## Future Work

1. Add Cloud Run Job wrappers for scheduled weekly brief generation.
2. Add Streamlit review screens after the tables are applied.
3. Add brief approval and archive workflow.
4. Add writing-AI integration that consumes only `llm_prompt_payload_json`.
5. Add more source adapters as curated packet tables mature.