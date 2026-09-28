# Advanced BQML v2 Owner Approval Packet

This approval packet presents the **Phase 33.21B Guarded Advanced Positional Boards** for owner review and decision-making. 

Our core BQML v2 models evaluate active 2026 player contexts using pre-2026 rolling 3-year advanced metrics averages. To protect against rookie/prospect artifacts, sparse data, and alternate model overreactions, we have implemented robust, career-history-based guardrails.

---

## 1. Top-Level Recommendation Table

| Scoring Profile | Position | Board Status | Finalist Model | Guardrail Status | Manual Review Burden | Recommendation | Reason |
|---|---|---|---|---|---|---|---|
| **Standard** | QB | Accepted with guardrails | `logistic_bust` | Alt model hidden (rushing bias); rushing warnings applied | Low (1 player: Purdy) | **PROCEED** | Evaluates true passing volume; protected against rushing bias distortion. |
| **Standard** | RB | Accepted | `linear_points` | Sufficient history verified | Low (4 players) | **PROCEED** | Stable career volume; captures true rushing/opportunity profiles. |
| **Standard** | WR | Accepted | `logistic_elite` | Sufficient history verified | Low (12 players) | **PROCEED** | Solid correlation; captures true high-volume targets and shares. |
| **Standard** | TE | Accepted with guardrails | `linear_points` | Current Pigskin floor applied | Low (2 players) | **PROCEED** | Floor protects standard tight ends from aggressive demotion. |
| **Half PPR** | QB | Accepted with guardrails | `logistic_bust` | Rushing warnings applied | Low (2 players) | **PROCEED** | Standardized passing efficiency; safe from rushing bias. |
| **Half PPR** | RB | Accepted with guardrails | `linear_vor` | Points sanity check applied | Low (4 players) | **PROCEED** | VOR captures true positional value; points sanity check verified. |
| **Half PPR** | WR | Accepted | `logistic_elite` | Sufficient history verified | Low (13 players) | **PROCEED** | Stable; highlights premium target share and snap metrics. |
| **Half PPR** | TE | **Held behind Current Pigskin** | `logistic_elite` | Locked to Current Pigskin | Zero | **HOLD** | Weak correlation; locked to Current Pigskin for safety. |
| **PPR** | QB | Accepted with guardrails | `logistic_bust` | Rushing warnings applied | Low (2 players) | **PROCEED** | High stability; anchors low-history passers. |
| **PPR** | RB | Accepted | `logistic_elite` | Sufficient history verified | Low (4 players) | **PROCEED** | Premium targets and carries combined; stable history. |
| **PPR** | WR | Accepted | `logistic_elite` | Sufficient history verified | Low (13 players) | **PROCEED** | Highly predictive; captures elite target profiles cleanly. |
| **PPR** | TE | **Held behind Current Pigskin** | `logistic_bust` | Locked to Current Pigskin | Zero | **HOLD** | Weak predictive signal; held behind Current Pigskin. |
| **GNG Keeper** | QB | **Held behind Current Pigskin** | `linear_points` | Locked to Current Pigskin | Zero | **HOLD** | Low combined correlation (<0.45); held behind Current Pigskin. |
| **GNG Keeper** | RB | Accepted | `linear_points` | Sufficient history verified | Low (4 players) | **PROCEED** | Strong keeper-value correlation; stable historical games. |
| **GNG Keeper** | WR | Accepted | `logistic_bust` | Sufficient history verified | Low (12 players) | **PROCEED** | Stable; protected against high-variance keeper drops. |
| **GNG Keeper** | TE | **Held behind Current Pigskin** | `logistic_bust` | Locked to Current Pigskin | Zero | **HOLD** | Weak predictive correlation; locked to Current Pigskin. |

---

## 2. Guardrails Now Applied

To enforce safety, the following guardrail rules are embedded in the review board output:
1. **Rookie/No-History Guardrail (`ROOKIE_NO_HISTORY`)**: True rookies/prospects with 0 career NFL regular season games are anchored exactly to Current Pigskin rank (0 movement allowed).
2. **Low-History Guardrail (`LOW_HISTORY`)**: Active players with > 0 but < 10 historical NFL regular season games are anchored exactly to Current Pigskin.
3. **Sparse-Feature Guardrail (`SPARSE_FEATURES`)**: Players missing > 50% advanced features are capped at a maximum of `+10` ranks upward movement relative to Current Pigskin.
4. **Model-Disagreement Lock (`MODEL_DISAGREEMENT_LOCK`)**: Anchors a player to Current Pigskin if their finalist and alternate ranks diverge by > 20 ranks (disabled for QB boards).
5. **QB Rushing-Bias Warning (`QB_RUSHING_BIAS_WARNING`)**: Flags rushing-heavy QBs elevated on weak passing EPA/CPOE context.
6. **Standard TE Current Pigskin Floor (`STANDARD_TE_FLOOR`)**: Restricts standard TE demotion below Current Pigskin.
7. **Held-Board Policy**: Positional boards with low predictive signal (Half PPR TE, PPR TE, GNG Keeper QB, GNG Keeper TE) are locked entirely to Current Pigskin ranks.
8. **Route Metrics Blocked Policy**: In strict compliance, all true route run metrics (`routes_run`, `yprr`, `tprr`, etc.) remain **BLOCKED** and mapped to `NULL`. No route calculations or estimations are used or fabricated.
9. **No Sleeper History**: Sleeper active 2026 context is preserved as context only and is never used as historical input.

---

## 3. Cleaned Career-History Labels

We have resolved the false-positive rookie bug by evaluating total career games played in 2023-2025 (`hist_games_3yr`) instead of latest-season weekly rows. Established veterans are no longer flagged under `ROOKIE_NO_HISTORY`.

### Target Player Classifications:
*   **Omarion Hampton** (RB, LAC): **PROSPECT_HISTORY** (1 season, 10 career games). Allowed model-based movement but flagged with `MANUAL_REVIEW_REQUIRED`.
*   **Cam Skattebo** (RB, NYG): **LOW_HISTORY** (1 season, 8 career games). Anchored to Current Pigskin.
*   **Travis Hunter** (WR, JAX): **LOW_HISTORY** (1 season, 7 career games). Anchored to Current Pigskin.
*   **Cam Ward** (QB, MIA): **PROSPECT_HISTORY** (1 season, 17 career games). Allowed model-based movement but flagged with `MANUAL_REVIEW_REQUIRED`.
*   **Tetairoa McMillan** (WR, ARI): **PROSPECT_HISTORY** (1 season, 18 career games). Allowed model-based movement but flagged with `MANUAL_REVIEW_REQUIRED`.
*   **Jakobie Keeney-James** (WR, GB): **LOW_HISTORY** (1 season, 1 career game). Anchored to Current Pigskin.
*   **Theo Wease Jr.** (WR, MIA): **LOW_HISTORY** (1 season, 3 career games). Anchored to Current Pigskin.

---

## 4. Remaining Join Failed QB Item

We identified exactly one `HISTORY_JOIN_FAILED` item from the QB boards:
*   **Player**: Fernando Mendoza (Cal, QB)
*   **Profiles**: Standard, Half PPR, PPR, GNG Keeper (QB Rank 38)
*   **Current ID**: `MEN516487`
*   **Identity Fields**: `sleeper_player_id: MEN516487`, Name: `Fernando Mendoza`
*   **Why Join Failed**: He is a college quarterback playing for the California Golden Bears who has never played in the NFL, resulting in zero NFL regular season stats history in our advanced metrics warehouse.
*   **Impact on Board Approval**: **None**. He is safely anchored to Current Pigskin rank 38 due to the `HISTORY_JOIN_FAILED` guardrail.
*   **Identity Fix Needed**: **No**. His lack of NFL stats is expected and correct. No bridge fix is required.

---

## 5. Compact Manual-Review Summaries

Manual review items are grouped into distinct buckets:
*   **True Rookies / Prospects**: Travis Hunter (LOW_HISTORY), Omarion Hampton (PROSPECT_HISTORY), Marvin Harrison Jr. (PROSPECT_HISTORY).
*   **Low-History Players**: Cam Skattebo (LOW_HISTORY), Theo Wease Jr. (LOW_HISTORY), Jakobie Keeney-James (LOW_HISTORY), Casey Washington (LOW_HISTORY).
*   **Major Veteran Risers**: Ray Davis (+25 PPR RB), Chuba Hubbard (+33 GNG Keeper RB), Justin Fields (+16 Standard QB), Derrick Henry (+18 Standard RB), Michael Pittman (+37 PPR WR).
*   **Major Veteran Fallers**: DJ Moore (-5 Standard WR), Bryce Young (-16 Standard QB), Rashee Rice (-21 PPR WR).
*   **Likely Current Pigskin Floor Candidates**: Tight ends in standard profile (e.g., standard TE floor applied to George Kittle to prevent demotion).
*   **Likely Advanced-Model Useful Calls**: Ray Davis, Chuba Hubbard, Derrick Henry, and Michael Pittman (elevated due to premium snap shares, target shares, and WOPR averages).
*   **Identity/Join Concerns**: Fernando Mendoza (college QB, anchored).

---

## 6. Specific Player Movement Examples

### DJ Moore (WR, CHI)
*   **Current Pigskin Rank**: 15 (Standard)
*   **Guarded Review Rank**: 20
*   **Movement**: -5 positional ranks
*   **Explanation**: Model demotes him slightly due to standard-scoring efficiency averages (WOPR `0.54`, target share `0.23` in 2023-2025).
*   **Recommendation**: **Accept**. Small demotion aligns with standard-scoring volume expectations.

### Ray Davis (RB, BUF)
*   **Current Pigskin Rank**: 45 (PPR)
*   **Guarded Review Rank**: 20
*   **Movement**: +25 positional ranks
*   **Explanation**: Model elevates him aggressively due to high-efficiency metrics (Weighted Opportunity `69.86` and solid snap stability `34.33` in limited history).
*   **Recommendation**: **Review**. A +25 movement is aggressive; verify if he is expected to seize a larger share of the Buffalo backfield.

### Chuba Hubbard (RB, CAR)
*   **Current Pigskin Rank**: 42 (GNG Keeper)
*   **Guarded Review Rank**: 9
*   **Movement**: +33 positional ranks
*   **Explanation**: Model strongly rewards him for substantial weighted opportunity (`125.65`) and snap stability (`50.54`) over the last three seasons.
*   **Recommendation**: **Review**. A rise to RB9 is very aggressive; requires validation of Carolina backfield split.

### David Njoku (TE, CLE)
*   **Current Pigskin Rank**: 29 (Standard)
*   **Guarded Review Rank**: 10
*   **Movement**: +19 positional ranks
*   **Explanation**: Model elevates him due to strong standard-scoring metrics (WOPR `0.44`, target share `0.20` in 2023-2025).
*   **Recommendation**: **Accept**. Highlights his premium target-share profile.

### Derrick Henry (RB, BAL)
*   **Current Pigskin Rank**: 20 (Standard)
*   **Guarded Review Rank**: 2
*   **Movement**: +18 positional ranks
*   **Explanation**: Model heavily weights standard-scoring workload averages (Weighted Opportunity `160.26` and snap stability `48.18`).
*   **Recommendation**: **Accept**. True reflection of standard-scoring workload value.

### Michael Pittman (WR, IND)
*   **Current Pigskin Rank**: 50 (PPR)
*   **Guarded Review Rank**: 13
*   **Movement**: +37 positional ranks
*   **Explanation**: Model highly values his elite PPR metrics (WOPR `0.55`, target share `0.25`).
*   **Recommendation**: **Accept**. High-volume receiver is chronically undervalued in current baseline.

### Rashee Rice (WR, KC)
*   **Current Pigskin Rank**: 7 (PPR)
*   **Guarded Review Rank**: 28
*   **Movement**: -21 positional ranks
*   **Explanation**: Model demotes him due to lower rolling 3-year averages (WOPR `0.47`, target share `0.24` in 2023-2025).
*   **Recommendation**: **Accept**. Model correctly discounts him based on rolling historical volume.

### Omarion Hampton (RB, LAC)
*   **Current Pigskin Rank**: 10 (Standard)
*   **Guarded Review Rank**: 56
*   **Movement**: -46 positional ranks
*   **Explanation**: Labeled `PROSPECT_HISTORY`. Since he has only one season of history in 2025, his rolling averages are based on partial stats.
*   **Recommendation**: **Anchor to Current Pigskin (Rank 10) or Review**. His raw model rank is too low for his draft expectation.

### Travis Hunter (WR, JAX)
*   **Current Pigskin Rank**: 51 (Standard)
*   **Guarded Review Rank**: 51
*   **Movement**: 0 (Anchored)
*   **Explanation**: Labeled `LOW_HISTORY` (7 career games). Anchored exactly to Current Pigskin rank 51.
*   **Recommendation**: **Accept Anchor**.

### Cam Skattebo (RB, NYG)
*   **Current Pigskin Rank**: 15 (Standard)
*   **Guarded Review Rank**: 15
*   **Movement**: 0 (Anchored)
*   **Explanation**: Labeled `LOW_HISTORY` (8 career games). Anchored exactly to Current Pigskin rank 15.
*   **Recommendation**: **Accept Anchor**.

### Bryce Young (QB, CAR)
*   **Current Pigskin Rank**: 21 (Standard)
*   **Guarded Review Rank**: 37
*   **Movement**: -16 positional ranks
*   **Explanation**: Model demotes him due to weak standard-scoring passing averages (Passing EPA `-53.79` in 2023-2025).
*   **Recommendation**: **Accept**. Correctly reflects severe historical passing inefficiency.

### Justin Fields (QB, PIT)
*   **Current Pigskin Rank**: 32 (Standard)
*   **Guarded Review Rank**: 16
*   **Movement**: +16 positional ranks
*   **Explanation**: Model values standard-scoring rushing output (Rushing EPA `12.34` and Passing EPA `-13.38` in 2023-2025).
*   **Recommendation**: **Accept**. Captures his high rushing-floor value.

### Patrick Mahomes (QB, KC) / Josh Allen (QB, BUF)
*   **Mahomes Rank**: 3 (Standard) -> Guarded 6 (Delta -3). Strong passing EPA (`45.54`) and rushing EPA (`15.25`).
*   **Josh Allen Rank**: 1 (Standard) -> Guarded 1 (Delta 0). Elite passing EPA (`56.48`) and rushing EPA (`30.50`).
*   **Mahomes/Allen Context**: By hiding the rejected linear points alternate model, Mahomes and Allen are no longer buried by rushing-heavy quarterbacks (like Richardson/Bagent), preserving their elite status.
*   **Recommendation**: **Accept**.

---

## 7. Approval Decision Section

The owner may choose one of the following decisions for Phase 33.22:

*   **[ ] DECISION A**: **Accept guarded boards for continued formula review**.
    *   *Effect*: All accepted/guarded positional boards proceed to deeper formula review. Held boards remain locked to Current Pigskin. True rookies and low-history players remain anchored.
*   **[ ] DECISION B**: **Accept only veteran movement, keep rookies anchored**.
    *   *Effect*: All rookies/prospects (including `PROSPECT_HISTORY` like Omarion Hampton) are anchored to Current Pigskin. Only established veterans (`NONE` label) are allowed model-based movement.
*   **[ ] DECISION C**: **Hold all advanced boards behind Current Pigskin**.
    *   *Effect*: Rejects all BQML v2 board changes; all positions remain locked to Current Pigskin.
*   **[ ] DECISION D**: **Send specific positions back for refinement**.
    *   *Effect*: Specify positions (e.g., standard TE, PPR WR) to return to model tuning/training.
*   **[ ] DECISION E**: **Approve next phase for position-locked top-100 planning later**.
    *   *Effect*: Approves proceeding to Phase 33.23 top-100 interleaving planning once positional boards are finalized.

> [!IMPORTANT]
> **IMPORTANT DISCLAIMER**: This approval is for review boards only. This is not live activation, is not champion selection, does not change active rankings in the draft queue, and does not build a top-100 interleaver.
