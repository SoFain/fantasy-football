# fraud_watch_packets Contract

Migration: [bigquery/migrations/0017__create_fraud_breakout_packets.sql](../migrations/0017__create_fraud_breakout_packets.sql)

Helper: [src/segment_packets.py](../../src/segment_packets.py)

## Purpose

Precomputed deterministic Fraud Watch evidence packets for future Segment, Pigskin chat, and show-writing tools.

The packet exists to keep Fraud Watch from becoming a shallow fantasy-points leaderboard. It stores the claim, evidence, counterargument, confidence, freshness, and show framing needed to explain why a player is a box-score trap or why the fraud case is weak.

## Grain

One row per player, model run, scoring profile, league type, roster format, season, and week.

The helper generates deterministic `packet_id` values from that grain so repeated writes are idempotent.

## Required Fields

- `packet_id`
- `season`
- `week`
- `scoring_profile_id`
- `league_type_id`
- `roster_format_id`
- `fraud_score`
- `confidence_score`
- `recommended_take`
- `packet_json`
- `packet_text`
- `snark_hooks_json`
- `counterargument`
- `source_freshness_json`
- `missing_data_flags`
- `created_at`
- `updated_at`

## Packet JSON Sections

- `identity`
- `ranking_context`
- `fraud_claim`
- `evidence`
- `counterargument`
- `what_would_change_the_take`
- `show_framing`
- `snark_hooks`
- `source_metadata`

## Deterministic Formula

The helper uses an explicit config dictionary in [src/segment_packets.py](../../src/segment_packets.py):

- points over expected component, weight `0.22`
- touchdown dependency component, weight `0.18`
- usage weakness component, weight `0.16`
- efficiency outlier component, weight `0.14`
- declining role component, weight `0.12`
- market hype component, weight `0.10`
- role instability component, weight `0.08`

This is the deterministic packet baseline. It is not final machine learning, but it is reproducible and reviewable.

## Missing Data Flags

The helper must add flags when important inputs are unavailable:

- `missing_model_run_id`
- `missing_expected_points`
- `expected_points_proxy_used`
- `missing_usage_score`
- `missing_td_dependency`
- `missing_rank_vs_value_gap`

Future flags should be added to the packet, not hidden from Pigskin.

## Source Freshness

`source_freshness_json` should identify the curated objects used for the packet:

- `analytics_fraud_watch`
- `compat_trade_assets_current`
- `compat_player_profiles_current`

The packet should not name raw source tables in freshness metadata.

## Consumer Guidance

Pigskin and script-mode tooling should treat `packet_json` as evidence and `packet_text` as a compact, voice-ready summary. Consumers should preserve:

- the claim
- the strongest evidence rows
- the counterargument
- the confidence caveat
- the `what_would_change_the_take` section

If missing flags exist, Pigskin should say the gap out loud instead of inventing certainty.

## Limitations

- This table does not replace future weekly, rest-of-season, dynasty, or best-ball projection tables.
- Fraud scores are deterministic baseline scores, not an LLM ranking.
- Expected-points fields can be proxies until a richer expected-points mart is promoted.
- No Streamlit runtime behavior is wired to this table yet.

## Source Rules

Allowed curated inputs:

- `analytics_fraud_watch`
- `compat_trade_assets_current`
- `compat_player_profiles_current`
- `model_runs`
- config metadata such as scoring profile, league type, roster format, and feature config version

The helper must not read raw `weekly_metrics`, `play_by_play`, NGS, FTN, snap, injury, or raw Sleeper source tables.

## Runtime Status

No Streamlit runtime behavior is wired to this table yet.
