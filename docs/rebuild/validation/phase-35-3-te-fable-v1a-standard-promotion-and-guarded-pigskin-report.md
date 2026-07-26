# Phase 35.3 TE Fable v1.0a Standard Promotion And Guarded Pigskin Report

## Final Decision

`TE FABLE V1.0A NO-MAN PROMOTED; GUARDED PIGSKIN MADE NO RANK CHANGES`

TE Fable v1.0a no-man is the active Standard TE champion and deterministic ranking source. One guarded Gemini 3.5 Flash exception review ran against its TE35 board. Pigskin requested no substantive repairs and changed no ranks.

## Previous Production State

- Ranking version: `pigskin-llm-20260704071412`.
- Rank source: `llm_pigskin_adjudicated`.
- Model run: `pigskin_rankings-2026-na-20260704T071419Z-9c498edc`.
- Scope: Standard/redraft/one-QB TE35.

The prior board was already present in `analytics_pigskin_rankings_history`, so the idempotent archive statement inserted zero duplicate rows.

## Deterministic Promotion

- Candidate: `te_fable_v1a_no_man_standard_te`.
- Formula version: `1.0a-no-man-phase-35.2a`.
- Champion ID: `te-fable-v1a-standard-20260711010758`.
- Promotion model run: `te_fable_v1a_promotion-20260711T010758Z`.
- Formula ranking version: `te-fable-v1a-standard-20260711010758`.
- Rows deactivated: 35 prior Standard TE rows.
- Rows inserted: 35 TE Fable rows.
- Champion metric: same-cohort pairwise win rate `0.761`.

No QB, RB, WR, non-Standard profile, or live application service was intentionally changed by the promotion statements.

## Guardrail Contract

Pigskin is now an exception-repair layer. It cannot return a replacement board order.

- The model returns a bounded `requested_rank_delta` and approved adjustment code per player.
- At most five substantive repairs are allowed on TE35.
- Total requested movement cannot exceed 12 ranks.
- Formula metrics, efficiency, opportunity, age, touchdown regression, and sustainability cannot be reinterpreted by the model.
- Preseason `Questionable` status alone has zero rank effect.
- Injury movement requires a source-backed estimated regular-season games-missed range.
- The application deterministically rebuilds the board from accepted repair requests.
- Collateral movement receives application-generated `ORDER_REBALANCE`, never an invented model reason.
- Every final row stores candidate rank, candidate score, code, signed delta, detail, evidence, and estimated games missed when applicable.

## Guarded Pigskin Result

- Gemini calls: 1.
- Model: `gemini-3.5-flash`.
- Prompt version: `pigskin-rankings-exception-repair-v1`.
- Final ranking version: `te-fable-guarded-pigskin-20260711010953`.
- Model run: `pigskin_rankings_guarded_exception_review-2026-na-20260711T010958Z-77b729a5`.
- Final rows: 35.
- Candidate ranks unchanged: 35.
- Substantive adjustments: 0.
- Total rank movement: 0.
- Codes: 32 `NO_ADJUSTMENT`, 3 `INJURY_UNCERTAIN`.

`INJURY_UNCERTAIN` with zero movement:

| Rank | Player | Sleeper status | Result |
|---:|---|---|---|
| 4 | George Kittle | Questionable | No movement |
| 22 | Zach Ertz | Questionable, current team unknown | No movement |
| 27 | Darren Waller | Questionable, current team unknown | No movement |

The result confirms the formula owns the order. Pigskin added visible uncertainty context and did not overrule the board.

## Live Verification

- Active Standard TE rows: 35.
- Rank range: 1 through 35.
- Rows with adjustment codes: 35.
- Rows with candidate rank equal to final rank: 35.
- Active champion: `te_fable_v1a_no_man_standard_te`.
- Promotion gate after run: unset.
- Gemini key after run: unset.

The dashboard already queries adjustment fields and displays `INJURY_UNCERTAIN`. Local UI copy was updated for the full exception-only vocabulary. No dashboard image was built from the dirty worktree in this phase.

## Checks

- 45 focused tests passed.
- `app.py`, ranking generator, promotion script, and guarded adjudication script compile.
- Deployment safety checker passed all checks.
- Six promotion DML statements passed BigQuery dry-run parsing before apply.
- No Firebase artifacts or tracked secrets appeared.

## Rollback

Rollback baseline: `pigskin-llm-20260704071412` in `analytics_pigskin_rankings_history`.

A rollback must be a separately authorized Standard TE-only transaction that archives the new board, deactivates the TE Fable champion, deletes the active Standard TE scope, and restores the 35 baseline rows from history. No rollback was needed.

## Remaining Work

- Package the guardrail source, tests, promotion scripts, UI key, and Phase 35 reports in a clean reviewed commit.
- Build and deploy a clean dashboard image so future runtime ranking generation uses the same guardrail code.
- Add a separate rookie candidate lane. A returning-player TE formula cannot rank players absent from its source cohort.
