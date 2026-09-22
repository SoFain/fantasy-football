# Player Identity Preflight Gate for Top-100 Interleaver

## 1. Preflight Purpose

Before any position-locked top-100 interleaver is built or executed, a mandatory **Player Identity Preflight Gate** must run. This gate ensures that all top-100 candidates have verified stable IDs, correct career NFL history mapping, and are free from name-matching or retired-player collisions.

The gate prevents retired-player collisions (e.g., Marvin Harrison Sr. vs. Jr.) and name-only matching from contaminating overall value-over-replacement (VOR) calculations in the interleaver.

---

## 2. Preflight Universe Definition

The preflight gate audits a comprehensive player universe consisting of:
1.  **Top 150 Overall-Equivalent Players**: Players whose Current Pigskin rank falls inside the overall top-150 equivalent range across all 4 profiles.
2.  **Guarded Positional Boards**: All players in the accepted positional boards (QB45, RB80, WR100, TE35).
3.  **Flagged Players**: All players carrying manual review, low-history, prospect, or identity warning flags.
4.  **Held-Board Players**: Any players on held boards (e.g., TE) who fall within the overall top-150 equivalent range.

---

## 3. Audited Identity Fields

For each player in the preflight universe, the gate reports:
*   `display_name` & `normalized_name`
*   `suffix` (Jr., Sr., II, etc.)
*   `team` & `position`
*   `current_pigskin_rank` & `guarded_position_rank`
*   `source_queue` (Guarded BQML v2 or Held Current Pigskin)
*   `player_id_internal` (bridge primary key)
*   `gsis_id` (nflverse ID)
*   `sleeper_player_id` (Sleeper roster ID)
*   `historical_weekly_rows` & `historical_season_rows`
*   `first_season` & `last_season`
*   `college_prospect_only_flag`
*   `retired_player_collision_flag`
*   `name_only_collision_flag`
*   `id_status` (allowed statuses below)

---

## 4. Allowed ID Statuses

*   `ID_VERIFIED`: Active player correctly linked to their own NFL stats history with a verified stable ID.
*   `ID_PROSPECT_ONLY`: Rookie/prospect with 0 historical NFL games (correctly anchored).
*   `ID_LOW_HISTORY`: Veteran player with > 0 but < 10 career NFL games.
*   `ID_JOIN_FAILED`: Roster player whose advanced metrics join failed (anchored).
*   `ID_COLLISION`: Shared name matches multiple active player records.
*   `ID_RETIRED_COLLISION`: Active player shares name with a retired player (e.g. Marvin Harrison Jr. vs. Sr.).
*   `ID_NAME_ONLY_COLLISION`: Joined purely by name without suffix or ID verification.
*   `ID_MANUAL_REVIEW_REQUIRED`: Undergoing manual identity auditing.

---

## 5. Strict Preflight Blocking Rules

The top-100 interleaver build **must be blocked** if any of the following conditions are met:
1.  **Retired-Player Collision**: Any active player resolves to a retired player's ID (e.g., active Marvin Harrison Jr. maps to retired Sr.'s `00-0007024`).
2.  **Unresolved Collision**: Any player in the top-100 candidate pool has a status of `ID_COLLISION` or `ID_RETIRED_COLLISION`.
3.  **Missing Stable ID**: Any top-150 overall-equivalent player lacks a stable `gsis_id` or `sleeper_player_id` unless marked explicitly as `ID_PROSPECT_ONLY`.
4.  **Name-Only Collision Mapping**: Any player is mapped using a name-only join when a suffix or era discrepancy exists.
5.  **Queue Mismatch**: The accepted guarded positional queues contain unresolved identity ambiguity.

---

## 6. Known Collision Tests & Verification Matrix

The preflight gate maintains a regression test matrix for key players:

| Player Name | Expected ID | Expected Status | Suffix Collision? | Action Taken / Verification |
|---|---|---|---|---|
| **Marvin Harrison Jr.** | `00-0039849` | `ID_VERIFIED` | Yes (Sr. `00-0007024`) | **Manual Override Applied**: Mapped Sleeper `11628` to `00-0039849`. Isolated retired Sr. to `00-0007024` on IND. |
| **Brock Purdy** | `00-0038122` | `ID_VERIFIED` | No | Verified career history (39 games, 3 seasons) |
| **Garrett Wilson** | `00-0037617` | `ID_VERIFIED` | No | Verified career history (51 games, 3 seasons) |
| **Rashee Rice** | `00-0038596` | `ID_VERIFIED` | No | Verified career history (32 games, 2 seasons) |
| **Malik Nabers** | `00-0039328` | `ID_VERIFIED` | No | Verified career history (16 games, 1 season) |
| **Mike Evans** | `00-0031235` | `ID_VERIFIED` | No | Verified career history (185 games, 12 seasons) |
| **James Conner** | `00-0033580` | `ID_VERIFIED` | No | Verified career history (118 games, 9 seasons) |
| **Jayden Reed** | `00-0038933` | `ID_VERIFIED` | No | Verified career history (33 games, 2 seasons) |
| **Chris Godwin** | `00-0033857` | `ID_VERIFIED` | No | Verified career history (120 games, 9 seasons) |
| **Sam LaPorta** | `00-0038587` | `ID_VERIFIED` | No | Verified career history (34 games, 2 seasons) |
| **Cam Ward** | `00-0040676` | `ID_PROSPECT_ONLY`| No | Single-season stats (17 games, 1 season). Anchored. |
| **Tetairoa McMillan**| `00-0040124` | `ID_PROSPECT_ONLY`| No | Single-season stats (18 games, 1 season). Anchored. |
| **Fernando Mendoza**| `MEN516487` | `ID_JOIN_FAILED`  | No | College-only player, 0 NFL stats. Anchored. |
| **Travis Hunter** | `HUN568341` | `ID_PROSPECT_ONLY`| No | True rookie, 0 NFL games. Anchored. |
| **Cam Skattebo** | `SKA784319` | `ID_PROSPECT_ONLY`| No | True rookie, 0 NFL games. Anchored. |
| **Jakobie Keeney-James**| `00-0040388`| `ID_PROSPECT_ONLY`| No | Single-season stats (1 game, 1 season). Anchored. |
| **Theo Wease Jr.** | `00-0040311` | `ID_PROSPECT_ONLY`| No | Single-season stats (3 games, 1 season). Anchored. |

---

## 7. Future Interleaver Gate

The interleaver compiler must call the preflight gate as its first compilation step. If the gate returns a fail status, compilation halts, writes are aborted, and the compiler exits with code `1`.
