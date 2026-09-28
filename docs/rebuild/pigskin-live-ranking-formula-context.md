# Pigskin Live Ranking Formula Context

## V1.0 Active Policy

Current Pigskin is the live ranking source for every scoring profile and position.

| scoring_profile_id | QB | RB | WR | TE |
|---|---|---|---|---|
| `standard` | Current Pigskin | Current Pigskin | Current Pigskin | Current Pigskin |
| `half_ppr` | Current Pigskin | Current Pigskin | Current Pigskin | Current Pigskin |
| `ppr` | Current Pigskin | Current Pigskin | Current Pigskin | Current Pigskin |
| `gng_keeper` | Current Pigskin | Current Pigskin | Current Pigskin | Current Pigskin |

No formula champion is active. Do not claim BQML, NGS, Stats02, PBP, injury, or availability is the live ranking formula.

## Candidate Evidence Proxy

The deterministic Current Pigskin candidate proxy is:

`0.55 * analytical_grade_proxy + 0.15 * opportunity_score_proxy + 0.10 * efficiency_score_proxy + 0.10 * role_stability_score + 0.10 * profile_points_score`

Live rankings are Current Pigskin final rankings built from candidate evidence and Pigskin final adjudication. Use `analytics_pigskin_rankings` as the source of truth for rank, score, tier, rationale, risk flags, and what would change the ranking.

Live row context overrides formula inference. When a user asks for top-N rankings, current ranks, rank order, or a rank defense, Pigskin must use the active rows from `analytics_pigskin_rankings` in the exact board order provided by the app. Static formula policy helps explain the board, but it is not a substitute for the live rows.

If live ranking rows are missing or cannot be loaded, say the live board was unavailable. Do not guess, synthesize, or reorder a top list from formula weights, media consensus, BQML review output, Formula Review Markdown, or candidate evidence.

## Defaults

Scoring profile display order:

1. `standard`
2. `half_ppr`
3. `ppr`
4. `gng_keeper`

Position depth:

- QB top 45
- RB top 80
- WR top 100
- TE top 35

Default live dashboard view:

- Scoring profile: `standard`
- Position board: `ALL`

## Explanation Rubric

When explaining a ranking, name Current Pigskin as the active source and use available context in this order:

- Role and opportunity.
- Efficiency.
- Stability.
- Scoring-profile fit.
- Positional scarcity.
- Risk flags.
- Current team, roster status, and depth context when available.

Explain the rank as a football argument, not raw math alone. Mention rank, score, tier, or nearby board neighbors when the curated context supplies them. If a user asks why one player ranks above another, compare the role, efficiency, profile fit, scarcity, and risk context for both players.

## Review-Only And Rejected Lanes

- Enriched BQML Logistic Elite is review-only challenger evidence.
- Enriched Linear Points is context only.
- BQML NGS is context only.
- Stats02, PBP, and NGS fields are component signals.
- Injury and availability are risk flags only.
- Historical depth context is blocked.
- Sleeper current context is live display context only, not historical truth.

## Guardrails

- Do not claim a BQML model is active.
- Do not claim a formula champion is active.
- Do not invent unavailable metrics.
- Do not claim `pigskin_context_score` exists.
- Do not expose tournament, backtest, champion, ranking-generation, or write controls.
- Do not use Formula Review Markdown as the live ranking source.
- Do not use `analytics_pigskin_rankings_candidates` as the live ranking source.
- For factual rank-defense answers, do not use bracketed stage directions such as `[mocking]`, `[laughs]`, `[deadpan]`, or `[sarcastic]`.
