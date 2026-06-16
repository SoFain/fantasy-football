# fantasy_claim_players Contract

Migration: [bigquery/migrations/0022__create_meatbag_claim_ledger.sql](../migrations/0022__create_meatbag_claim_ledger.sql)

Helper: [src/claim_ledger.py](../../src/claim_ledger.py)

## Purpose

Player-level claim participants resolved through `player_identity_bridge` when possible.

## Grain

One row per claim and player role.

Recommended logical uniqueness:

- `claim_id`
- `COALESCE(player_id_internal, source_player_key, display_name)`
- `player_role_in_claim`
- `side`

## Player Roles

Initial helper default is `subject`. Future values may include:

- `subject`
- `comparison`
- `trade_send`
- `trade_receive`
- `beneficiary`
- `hurt_by_claim`

## Identity Rules

- Exact `player_id_internal` wins.
- External IDs from the identity bridge are allowed as `source_player_key`.
- Name, team, and position fallback is allowed only in the backend helper.
- Ambiguous matches return disambiguation instead of silently choosing.
- Unmatched rows are retained with missing identity flags for manual repair.

## UI and LLM Safety

Safe only as claim-ledger metadata. It should feed future curated claim evidence packets, not arbitrary Pigskin SQL access.
