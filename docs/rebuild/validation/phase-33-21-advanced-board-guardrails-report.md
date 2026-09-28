# Validation Report — Phase 33.21 Advanced Review-Board Guardrails

> [!WARNING]
> **SUPERSEDED**: This validation report contains incorrect classification data. Please refer to the corrected report in [phase-33-21b-guardrail-identity-history-fix-report.md](file:///e:/Fantasy%20Football/docs/rebuild/validation/phase-33-21b-guardrail-identity-history-fix-report.md) for the true guardrails validation status.

## 1. Final Decision

`ADVANCED BOARD GUARDRAILS IMPLEMENTED`

## 2. Files Changed

- [advanced-bqml-v2-owner-review-boards.md](file:///e:/Fantasy%20Football/docs/rebuild/advanced-bqml-v2-owner-review-boards.md) [MODIFY]
- [phase-33-21-advanced-board-guardrails-report.md](file:///e:/Fantasy%20Football/docs/rebuild/validation/phase-33-21-advanced-board-guardrails-report.md) [NEW]
- [bqml-v2-positional-formula-finalists.md](file:///e:/Fantasy%20Football/docs/rebuild/bqml-v2-positional-formula-finalists.md) [MODIFY]
- [ranking-algorithm-scorecard.md](file:///e:/Fantasy%20Football/docs/rebuild/ranking-algorithm-scorecard.md) [MODIFY]
- [bqml-v2-ranking-architecture.md](file:///e:/Fantasy%20Football/docs/rebuild/bqml-v2-ranking-architecture.md) [MODIFY]
- [ranking-opportunity-metrics-matrix.md](file:///e:/Fantasy%20Football/docs/rebuild/ranking-opportunity-metrics-matrix.md) [MODIFY]

## 3. Git State & Checks

- All 26 unit tests passed cleanly.
- Safety compiler check and deployment safety scripts passed.
- BigQuery warehouse validations passed with 0 errors.
- Trailing empty lines at EOF removed, and `git diff --check` passed successfully.

## 4. Guardrails Implemented & Row Counts

We implemented the following guardrail logic in the review board pipeline:
1. **Rookie/Low-History Guardrail**: Anchors `ROOKIE_NO_HISTORY` (weekly_rows < 10 or missingness = 100%) to Current Pigskin.
2. **Sparse Feature Capping**: Capped upward movement to +10 ranks for `SPARSE_FEATURES` (missingness > 50%).
3. **Model Disagreement Lock**: Anchored player to Current Pigskin if finalist and alternate ranks diverge by > 20.
4. **QB Rushing Bias Warning**: Added warning for rushing-heavy QBs elevated on weak passing EPA/CPOE context.
5. **Standard TE Floor**: Restricted standard TE demotion below Current Pigskin.

## 5. Board Acceptance Status & Row Counts

| Profile | QB (Limit 45) | RB (Limit 80) | WR (Limit 100) | TE (Limit 35) |
|---|---|---|---|---|
| standard | 45 (Accepted with guardrails) | 80 (Accepted) | 100 (Accepted) | 35 (Accepted with guardrails) |
| half_ppr | 45 (Accepted with guardrails) | 80 (Accepted with guardrails) | 100 (Accepted) | 35 (Held behind Current Pigskin) |
| ppr | 45 (Accepted with guardrails) | 80 (Accepted) | 100 (Accepted) | 35 (Held behind Current Pigskin) |
| gng_keeper | 45 (Held behind Current Pigskin) | 80 (Accepted) | 100 (Accepted) | 35 (Held behind Current Pigskin) |

## 6. Guardrail Summary by Board

### STANDARD Guardrail Statistics

| Position | Unchanged | Capped Up | Capped Down | Anchored | Manual Review | Disagreement Lock | Sparse Features | Rookie/No History |
|---|---|---|---|---|---|---|---|---|
| QB | 0 | 0 | 0 | 45 | 2 | 29 | 0 | 16 |
| RB | 64 | 0 | 0 | 16 | 4 | 0 | 0 | 16 |
| WR | 81 | 0 | 0 | 19 | 13 | 0 | 0 | 19 |
| TE | 14 | 0 | 16 | 5 | 2 | 0 | 0 | 5 |

### HALF_PPR Guardrail Statistics

| Position | Unchanged | Capped Up | Capped Down | Anchored | Manual Review | Disagreement Lock | Sparse Features | Rookie/No History |
|---|---|---|---|---|---|---|---|---|
| QB | 28 | 0 | 0 | 16 | 2 | 0 | 0 | 16 |
| RB | 60 | 0 | 0 | 16 | 4 | 0 | 0 | 16 |
| WR | 81 | 0 | 0 | 19 | 13 | 0 | 0 | 19 |
| TE | 0 | 0 | 0 | 35 | 0 | 0 | 0 | 0 |

### PPR Guardrail Statistics

| Position | Unchanged | Capped Up | Capped Down | Anchored | Manual Review | Disagreement Lock | Sparse Features | Rookie/No History |
|---|---|---|---|---|---|---|---|---|
| QB | 0 | 0 | 0 | 45 | 2 | 29 | 0 | 16 |
| RB | 65 | 0 | 0 | 15 | 4 | 0 | 0 | 15 |
| WR | 81 | 0 | 0 | 19 | 13 | 0 | 0 | 19 |
| TE | 0 | 0 | 0 | 35 | 0 | 0 | 0 | 0 |

### GNG_KEEPER Guardrail Statistics

| Position | Unchanged | Capped Up | Capped Down | Anchored | Manual Review | Disagreement Lock | Sparse Features | Rookie/No History |
|---|---|---|---|---|---|---|---|---|
| QB | 0 | 0 | 0 | 45 | 0 | 0 | 0 | 0 |
| RB | 65 | 0 | 0 | 15 | 4 | 0 | 0 | 15 |
| WR | 76 | 0 | 0 | 24 | 12 | 5 | 0 | 19 |
| TE | 0 | 0 | 0 | 35 | 0 | 0 | 0 | 0 |

## 7. Overall Manual Review List

| Player | Team | Position | Profile | Current Pigskin Rank | Reason |
|---|---|---|---|---|---|
| Brock Purdy | SF | QB | standard | 4 | Rookie/no-history inside overall top-150 range (QB4) |
| Jayden Daniels | WAS | QB | standard | 12 | Rookie/no-history inside overall top-150 range (QB12) |
| Omarion Hampton | LAC | RB | standard | 10 | Rookie/no-history inside overall top-150 range (RB10) |
| Cam Skattebo | NYG | RB | standard | 15 | Rookie/no-history inside overall top-150 range (RB15) |
| James Conner | ARI | RB | standard | 25 | Rookie/no-history inside overall top-150 range (RB25) |
| Trey Benson | ARI | RB | standard | 36 | Rookie/no-history inside overall top-150 range (RB36) |
| Garrett Wilson | NYJ | WR | standard | 6 | Rookie/no-history inside overall top-150 range (WR6) |
| Rashee Rice | KC | WR | standard | 7 | Rookie/no-history inside overall top-150 range (WR7) |
| Malik Nabers | NYG | WR | standard | 18 | Rookie/no-history inside overall top-150 range (WR18) |
| Mike Evans | SF | WR | standard | 29 | Rookie/no-history inside overall top-150 range (WR29) |
| Ricky Pearsall | SF | WR | standard | 40 | Rookie/no-history inside overall top-150 range (WR40) |
| Calvin Ridley | TEN | WR | standard | 45 | Rookie/no-history inside overall top-150 range (WR45) |
| Travis Hunter | JAX | WR | standard | 51 | Rookie/no-history inside overall top-150 range (WR51) |
| Jakobie Keeney-James | GB | WR | standard | 54 | Rookie/no-history inside overall top-150 range (WR54) |
| Jayden Reed | GB | WR | standard | 56 | Rookie/no-history inside overall top-150 range (WR56) |
| Chris Godwin Jr. | TB | WR | standard | 61 | Rookie/no-history inside overall top-150 range (WR61) |
| Jalen McMillan | TB | WR | standard | 62 | Rookie/no-history inside overall top-150 range (WR62) |
| Devaughn Vele | NO | WR | standard | 63 | Rookie/no-history inside overall top-150 range (WR63) |
| Theo Wease Jr. | MIA | WR | standard | 70 | Rookie/no-history inside overall top-150 range (WR70) |
| Tucker Kraft | GB | TE | standard | 3 | Rookie/no-history inside overall top-150 range (TE3) |
| Sam LaPorta | DET | TE | standard | 7 | Rookie/no-history inside overall top-150 range (TE7) |
| Brock Purdy | SF | QB | half_ppr | 4 | Rookie/no-history inside overall top-150 range (QB4) |
| Jayden Daniels | WAS | QB | half_ppr | 12 | Rookie/no-history inside overall top-150 range (QB12) |
| Omarion Hampton | LAC | RB | half_ppr | 10 | Rookie/no-history inside overall top-150 range (RB10) |
| Cam Skattebo | NYG | RB | half_ppr | 15 | Rookie/no-history inside overall top-150 range (RB15) |
| James Conner | ARI | RB | half_ppr | 24 | Rookie/no-history inside overall top-150 range (RB24) |
| Trey Benson | ARI | RB | half_ppr | 36 | Rookie/no-history inside overall top-150 range (RB36) |
| Garrett Wilson | NYJ | WR | half_ppr | 6 | Rookie/no-history inside overall top-150 range (WR6) |
| Rashee Rice | KC | WR | half_ppr | 7 | Rookie/no-history inside overall top-150 range (WR7) |
| Malik Nabers | NYG | WR | half_ppr | 18 | Rookie/no-history inside overall top-150 range (WR18) |
| Mike Evans | SF | WR | half_ppr | 29 | Rookie/no-history inside overall top-150 range (WR29) |
| Ricky Pearsall | SF | WR | half_ppr | 40 | Rookie/no-history inside overall top-150 range (WR40) |
| Calvin Ridley | TEN | WR | half_ppr | 45 | Rookie/no-history inside overall top-150 range (WR45) |
| Travis Hunter | JAX | WR | half_ppr | 50 | Rookie/no-history inside overall top-150 range (WR50) |
| Jakobie Keeney-James | GB | WR | half_ppr | 54 | Rookie/no-history inside overall top-150 range (WR54) |
| Jayden Reed | GB | WR | half_ppr | 56 | Rookie/no-history inside overall top-150 range (WR56) |
| Chris Godwin Jr. | TB | WR | half_ppr | 61 | Rookie/no-history inside overall top-150 range (WR61) |
| Jalen McMillan | TB | WR | half_ppr | 62 | Rookie/no-history inside overall top-150 range (WR62) |
| Devaughn Vele | NO | WR | half_ppr | 63 | Rookie/no-history inside overall top-150 range (WR63) |
| Theo Wease Jr. | MIA | WR | half_ppr | 70 | Rookie/no-history inside overall top-150 range (WR70) |
| Brock Purdy | SF | QB | ppr | 4 | Rookie/no-history inside overall top-150 range (QB4) |
| Jayden Daniels | WAS | QB | ppr | 12 | Rookie/no-history inside overall top-150 range (QB12) |
| Omarion Hampton | LAC | RB | ppr | 10 | Rookie/no-history inside overall top-150 range (RB10) |
| Cam Skattebo | NYG | RB | ppr | 15 | Rookie/no-history inside overall top-150 range (RB15) |
| James Conner | ARI | RB | ppr | 25 | Rookie/no-history inside overall top-150 range (RB25) |
| Trey Benson | ARI | RB | ppr | 36 | Rookie/no-history inside overall top-150 range (RB36) |
| Garrett Wilson | NYJ | WR | ppr | 6 | Rookie/no-history inside overall top-150 range (WR6) |
| Rashee Rice | KC | WR | ppr | 7 | Rookie/no-history inside overall top-150 range (WR7) |
| Malik Nabers | NYG | WR | ppr | 18 | Rookie/no-history inside overall top-150 range (WR18) |
| Mike Evans | SF | WR | ppr | 29 | Rookie/no-history inside overall top-150 range (WR29) |
| Ricky Pearsall | SF | WR | ppr | 40 | Rookie/no-history inside overall top-150 range (WR40) |
| Calvin Ridley | TEN | WR | ppr | 46 | Rookie/no-history inside overall top-150 range (WR46) |
| Travis Hunter | JAX | WR | ppr | 51 | Rookie/no-history inside overall top-150 range (WR51) |
| Jakobie Keeney-James | GB | WR | ppr | 54 | Rookie/no-history inside overall top-150 range (WR54) |
| Jayden Reed | GB | WR | ppr | 55 | Rookie/no-history inside overall top-150 range (WR55) |
| Chris Godwin Jr. | TB | WR | ppr | 61 | Rookie/no-history inside overall top-150 range (WR61) |
| Jalen McMillan | TB | WR | ppr | 62 | Rookie/no-history inside overall top-150 range (WR62) |
| Devaughn Vele | NO | WR | ppr | 63 | Rookie/no-history inside overall top-150 range (WR63) |
| Theo Wease Jr. | MIA | WR | ppr | 70 | Rookie/no-history inside overall top-150 range (WR70) |
| Omarion Hampton | LAC | RB | gng_keeper | 10 | Rookie/no-history inside overall top-150 range (RB10) |
| Cam Skattebo | NYG | RB | gng_keeper | 15 | Rookie/no-history inside overall top-150 range (RB15) |
| James Conner | ARI | RB | gng_keeper | 23 | Rookie/no-history inside overall top-150 range (RB23) |
| Trey Benson | ARI | RB | gng_keeper | 36 | Rookie/no-history inside overall top-150 range (RB36) |
| Garrett Wilson | NYJ | WR | gng_keeper | 5 | Rookie/no-history inside overall top-150 range (WR5) |
| Rashee Rice | KC | WR | gng_keeper | 7 | Rookie/no-history inside overall top-150 range (WR7) |
| Malik Nabers | NYG | WR | gng_keeper | 18 | Rookie/no-history inside overall top-150 range (WR18) |
| Mike Evans | SF | WR | gng_keeper | 28 | Rookie/no-history inside overall top-150 range (WR28) |
| Ricky Pearsall | SF | WR | gng_keeper | 40 | Rookie/no-history inside overall top-150 range (WR40) |
| Calvin Ridley | TEN | WR | gng_keeper | 45 | Rookie/no-history inside overall top-150 range (WR45) |
| Travis Hunter | JAX | WR | gng_keeper | 50 | Rookie/no-history inside overall top-150 range (WR50) |
| Jakobie Keeney-James | GB | WR | gng_keeper | 53 | Rookie/no-history inside overall top-150 range (WR53) |
| Jayden Reed | GB | WR | gng_keeper | 57 | Rookie/no-history inside overall top-150 range (WR57) |
| Chris Godwin Jr. | TB | WR | gng_keeper | 61 | Rookie/no-history inside overall top-150 range (WR61) |
| Devaughn Vele | NO | WR | gng_keeper | 62 | Rookie/no-history inside overall top-150 range (WR62) |
| Jalen McMillan | TB | WR | gng_keeper | 63 | Rookie/no-history inside overall top-150 range (WR63) |

## 8. Confirmations & Next Phase

- **No training occurred**: Confirmed. Checked that no new BQML models were trained during this phase.
- **No live rankings written**: Confirmed. Checked that no active live ranking table rows were changed.
- **No champion selected**: Confirmed. Checked that no champ label or status was promoted.
- **No top-100 Ready**: Confirmed. Positional queues are locked and not interleaved.
- **Route metrics status**: Confirmed strictly mapped to `NULL`. **ROUTE METRICS REMAIN BLOCKED**.
- **Recommended Next Phase**: **Phase 33.22 — Owner approval packet for guarded positional boards**.
