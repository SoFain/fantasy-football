# Claim Grading V1

Claim Grading V1 turns manual Meatbag Claim Ledger entries into deterministic accountability rows.

## Scope

This phase adds:

- `claim_grading_runs`
- `claim_grades`
- `claim_source_scorecards`
- [src/claim_grading.py](../../src/claim_grading.py)
- Validation SQL for grading-run grain, grade grain, required scores, claim joins, scorecard grain, and missing flags.

This phase does not:

- Call LLMs.
- Scrape YouTube, podcasts, articles, or TV content.
- Create Firebase artifacts.
- Change Pigskin chat.
- Wire Streamlit UI.
- Apply migrations automatically.

## Grading Inputs

Allowed curated inputs:

- `fantasy_claims`
- `fantasy_claim_players`
- `claim_evaluation_windows`
- `analytics_player_fantasy_points_by_profile`
- `projection_rankings_current`
- `market_consensus_baseline_current`

The helper must not query raw source tables.

## CLI

Dry-run a season and week:

```powershell
python -m src.claim_grading --season 2025 --week 6 --dry-run
```

Dry-run a single claim:

```powershell
python -m src.claim_grading --claim-id claim_123 --dry-run
```

On Windows, prefer the repo venv:

```powershell
.\venv\Scripts\python.exe -m src.claim_grading --season 2025 --week 6 --dry-run
```

## Deterministic Verdicts

- `good_take`: the claim clearly matches the result.
- `wrong`: the claim clearly misses.
- `lucky`: the claim was right, but confidence is weak.
- `fraud`: the claim was badly wrong while Pigskin or market evidence was substantially better.
- `galaxy_brain`: the claim was strongly right against available Pigskin or market evidence.
- `inconclusive`: the claim cannot be graded honestly.

## V1 Claim Logic

Start and sit:

- Start claims reward strong positional finish or high points.
- Sit claims reward low points or poor positional finish.

Buy, sell, breakout, bust, and fraud:

- Positive claims use the same strong-outcome signal as starts.
- Negative claims invert the strong-outcome signal.

Ranking:

- Claimed rank is compared to actual rank.
- Wider rank misses reduce the score.

Dynasty:

- Multi-year evidence is not complete yet.
- V1 marks dynasty claims as `inconclusive` with `insufficient_dynasty_window`.

## Missing Data

Missing actuals, missing player identity, missing Pigskin snapshots, missing market snapshots, and insufficient dynasty windows are written to `missing_data_flags`.

Missing actuals should not crash grading. The claim becomes `inconclusive`.

## Future Work

1. Add a Cloud Run Job wrapper for scheduled grading runs.
2. Add a Streamlit scoreboard tab after the table contracts are applied.
3. Add correction workflows for audited grade edits.
4. Add claim evidence packets for show prep.
5. Add dynasty grading once multi-year windows mature.
