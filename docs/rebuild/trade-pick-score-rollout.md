# Trade Pick Score Rollout

## Purpose

The draft-pick score lane gives Trade Lab a deterministic way to compare pick assets without pretending generic picks are players.

This lane is separate from `trade_player_scores`.

## V0 Position

`trade_pick_score_v0_2026_001` is market-led:

- current market value drives the largest component;
- parsed pick round, slot, and pick year provide draft-capital structure;
- round-only picks carry explicit uncertainty;
- college context is neutral and flagged unavailable;
- draft outcome priors are not used yet.

## Source Rules

Allowed v0 builder input:

- `compat_trade_assets_current`

Forbidden direct v0 compatibility-view dependencies:

- `draft_picks`
- `college_player_stats`
- `rookie_scouting_metrics`
- raw/source tables

Future college or rookie context requires a curated identity bridge and source contract before it can affect public pick scores.

## Warehouse Objects

Phase 28.3 proposes:

- `trade_pick_scores`
- `trade_pick_scores_current`
- `compat_trade_pick_scores_current`

The migration is additive and does not write pick score rows.

## Runtime And Flags

No production exposure is approved by this contract work.

Future UI wiring should stay default-off and staging-first. If no pick score row exists, Trade Lab should keep the existing market-only behavior and show a clear unavailable state.

## Validation Plan

Pick score validations cover:

- table and view existence;
- score grain uniqueness;
- score and component ranges;
- exact-slot and round-only parse rules;
- missing flags, source freshness, and component JSON;
- no raw/source dependencies in current or compatibility views;
- no `PICK` rows in `trade_player_scores`;
- no player identity columns in `trade_pick_scores`.

## Future Work

1. Apply migration only after explicit authorization.
2. Materialize a bounded staging-only pick score run after explicit authorization.
3. Wire staging UI to read `compat_trade_pick_scores_current`.
4. Add a college or rookie context mart only after durable identity mapping exists.
5. Revisit production exposure as a separate rollout.
