# Claim Import Format

The Claim Ledger CSV import is an admin-provided manual workflow. It does not scrape, fetch URLs, or call an LLM.

## Required Header

The CSV must include these columns:

```csv
source_name,source_type,person_name,show_name,source_url,episode_or_video_title,published_at,claimed_at,claim_text,claim_type,claim_direction,time_horizon,season,week,scoring_profile_id,league_type_id,roster_format_id,player_names,team_names,claimed_rank,claimed_projection,claimed_value,notes
```

Optional extra column:

```csv
review_status
```

If `review_status` is omitted, rows import as `draft`.

## Allowed Values

`source_type`:

- `youtube`
- `tv`
- `podcast`
- `article`
- `internal_pigskin`
- `manual`

`claim_type`:

- `start`
- `sit`
- `buy`
- `sell`
- `trade`
- `breakout`
- `bust`
- `fraud`
- `ranking`
- `dynasty`
- `streamer`
- `waiver`
- `projection`

`claim_direction`:

- `positive`
- `negative`
- `neutral`
- `start`
- `sit`
- `buy`
- `sell`

`time_horizon`:

- `weekly`
- `ros`
- `season`
- `dynasty`
- `multi_year`

`review_status`:

- `draft`
- `reviewed`
- `ready_to_grade`
- `graded`
- `archived`
- `correction`

## Player and Team Subjects

Use semicolons for multiple player or team values:

```csv
player_names
"A.J. Brown; DeVonta Smith"
```

Players are resolved through the canonical identity helper. Ambiguous or unresolved players are flagged in preview. They can be written only as draft rows.

## Validation Rules

Draft rows require:

- source metadata
- claim text
- claim type
- time horizon
- season

Reviewed, ready, and graded rows also require:

- claim direction
- at least one resolved player or a team subject

CSV import previews every row before writing. Invalid rows are skipped and can be exported as an error CSV.

## Example

```csv
source_name,source_type,person_name,show_name,source_url,episode_or_video_title,published_at,claimed_at,claim_text,claim_type,claim_direction,time_horizon,season,week,scoring_profile_id,league_type_id,roster_format_id,player_names,team_names,claimed_rank,claimed_projection,claimed_value,notes
Analyst X,youtube,Analyst X,Week 1 Show,https://example.com/video,Week 1 Takes,2026-08-01T12:00:00Z,2026-08-01T12:05:00Z,A.J. Brown is a league winner,breakout,positive,season,2026,1,ppr,redraft,one_qb,A.J. Brown,,12,18.5,42,manual test row
```

## Local Test Command

```powershell
.\venv\Scripts\python.exe -m unittest tests.test_claim_import
```
