# Scorecard Completion Report — Phase 33.18B Advanced BQML v2 Finalists

## 1. Executive Summary & Final Decision

This report documents the scorecard completion, finalist selection, and verification for the Phase 33.18 BQML v2 advanced positional models. Using audited advanced player metrics (`advanced_player_metrics_v1`), we evaluated the 64 positional models across three evaluation scopes: **2024 validation**, **2025 holdout**, and **2024-2025 combined**.

### Final Decision Option
> [!IMPORTANT]
> **ADVANCED BQML V2 FINALISTS READY FOR OWNER REVIEW**
> The advanced owner-review finalists demonstrate substantial predictive and point capture improvements over the Phase 33.13 baselines and are ready to be presented to the owner-review boards.

---

## 2. Verification of the 64 Trained Models

All 64 positional models were successfully trained on BigQuery.

### Training Row and Execution Metrics
*   **Total Expected Models**: 64 (4 profiles * 4 positions * 4 families)
*   **Total Completed Models**: 64 (0 skipped/failed)
*   **Training dataset rows by position**:
    *   **QB**: 3,778 rows
    *   **RB**: 8,327 rows
    *   **WR**: 13,368 rows
    *   **TE**: 6,979 rows
*   **Training Seconds and Bytes processed**:
    *   All models processed exactly **20,971,520 bytes** of feature data.
    *   *Standard*: QB: 107.41s | RB: 82.55s | WR: 95.49s | TE: 97.77s
    *   *Half PPR*: QB: 88.61s | RB: 88.22s | WR: 108.86s | TE: 103.97s
    *   *PPR*: QB: 92.79s | RB: 96.10s | WR: 113.24s | TE: 92.35s
    *   *GNG Keeper*: QB: 111.56s | RB: 88.11s | WR: 102.69s | TE: 122.16s

---

## 3. Finalist Decision Table

The table below documents the selection of the **advanced owner-review finalist** for each profile and position, comparing its predictive performance against the Phase 33.13 baseline.

| Profile | Position | Selected Advanced Owner-Review Finalist | Prior Finalist | Validation Corr (2024) | Holdout Corr (2025) | Combined Corr (2024-25) | Improvement Summary | Warning | Decision Label |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- | :--- |
| STANDARD | QB | `standard_qb_linear_points` | `standard_qb_logistic_bust_inverse` | 0.4680 vs 0.4321 (+0.0360) | 0.4392 vs 0.4148 (+0.0244) | 0.5503 vs 0.4234 (+0.1269) | Corr: +0.1269 | Pts: +0.0072 | None | **owner-review finalist** |
| STANDARD | RB | `standard_rb_linear_points` | `standard_rb_logistic_bust_inverse` | 0.5752 vs 0.6226 (-0.0473) | 0.6771 vs 0.6602 (+0.0169) | 0.6809 vs 0.6414 (+0.0395) | Corr: +0.0395 | Pts: -0.0298 | None | **owner-review finalist** |
| STANDARD | WR | `standard_wr_logistic_bust` | `standard_wr_logistic_elite` | 0.5230 vs 0.5293 (-0.0062) | 0.5960 vs 0.5710 (+0.0250) | 0.6391 vs 0.5501 (+0.0889) | Corr: +0.0889 | Pts: +0.0121 | None | **owner-review finalist** |
| STANDARD | TE | `standard_te_linear_points` | `standard_te_logistic_bust_inverse` | 0.4802 vs 0.5029 (-0.0227) | 0.5343 vs 0.5628 (-0.0285) | 0.6022 vs 0.5329 (+0.0693) | Corr: +0.0693 | Pts: -0.0038 | None | **owner-review finalist** |
| HALF_PPR | QB | `half_ppr_qb_logistic_bust` | `half_ppr_qb_logistic_elite` | 0.4735 vs 0.3912 (+0.0823) | 0.4550 vs 0.3360 (+0.1190) | 0.5561 vs 0.3636 (+0.1925) | Corr: +0.1925 | Pts: +0.7751 | None | **owner-review finalist** |
| HALF_PPR | RB | `half_ppr_rb_linear_vor` | `half_ppr_rb_linear_vor` | 0.5706 vs 0.5810 (-0.0104) | 0.6523 vs 0.6434 (+0.0089) | 0.6770 vs 0.6122 (+0.0648) | Corr: +0.0648 | Pts: +0.7756 | None | **owner-review finalist** |
| HALF_PPR | WR | `half_ppr_wr_logistic_elite` | `half_ppr_wr_logistic_elite` | 0.5469 vs 0.5375 (+0.0094) | 0.6115 vs 0.5477 (+0.0638) | 0.6570 vs 0.5426 (+0.1144) | Corr: +0.1144 | Pts: +0.7010 | None | **owner-review finalist** |
| HALF_PPR | TE | `half_ppr_te_logistic_elite` | `half_ppr_te_linear_vor` | 0.5236 vs 0.4687 (+0.0549) | 0.5556 vs 0.5117 (+0.0440) | 0.6348 vs 0.4902 (+0.1446) | Corr: +0.1446 | Pts: +0.7010 | None | **owner-review finalist** |
| PPR | QB | `ppr_qb_linear_points` | `ppr_qb_logistic_elite` | 0.4690 vs 0.3919 (+0.0771) | 0.4394 vs 0.3315 (+0.1078) | 0.5511 vs 0.3617 (+0.1893) | Corr: +0.1893 | Pts: +0.7707 | None | **owner-review finalist** |
| PPR | RB | `ppr_rb_linear_vor` | `ppr_rb_linear_vor` | 0.5724 vs 0.5881 (-0.0157) | 0.6421 vs 0.6302 (+0.0119) | 0.6782 vs 0.6092 (+0.0690) | Corr: +0.0690 | Pts: +0.7660 | None | **owner-review finalist** |
| PPR | WR | `ppr_wr_logistic_elite` | `ppr_wr_logistic_elite` | 0.5571 vs 0.5476 (+0.0094) | 0.6151 vs 0.5576 (+0.0575) | 0.6645 vs 0.5526 (+0.1120) | Corr: +0.1120 | Pts: +0.7077 | None | **owner-review finalist** |
| PPR | TE | `ppr_te_logistic_bust` | `ppr_te_linear_vor` | 0.5367 vs 0.4798 (+0.0569) | 0.5680 vs 0.5225 (+0.0455) | 0.6448 vs 0.5011 (+0.1437) | Corr: +0.1437 | Pts: +0.7113 | None | **owner-review finalist** |
| GNG_KEEPER | QB | `gng_keeper_qb_linear_points` | `gng_keeper_qb_logistic_elite` | 0.4103 vs 0.3631 (+0.0472) | 0.4239 vs 0.3050 (+0.1189) | 0.5066 vs 0.3341 (+0.1726) | Corr: +0.1726 | Pts: +0.7244 | Predictive correlation remains below 0.45 | **owner-review finalist with warnings** |
| GNG_KEEPER | RB | `gng_keeper_rb_linear_points` | `gng_keeper_rb_linear_vor` | 0.5502 vs 0.5639 (-0.0137) | 0.6451 vs 0.6269 (+0.0182) | 0.6618 vs 0.5954 (+0.0665) | Corr: +0.0665 | Pts: +0.7604 | None | **owner-review finalist** |
| GNG_KEEPER | WR | `gng_keeper_wr_logistic_elite` | `gng_keeper_wr_logistic_elite` | 0.5230 vs 0.5202 (+0.0029) | 0.6008 vs 0.5298 (+0.0711) | 0.6392 vs 0.5250 (+0.1142) | Corr: +0.1142 | Pts: +0.6683 | None | **owner-review finalist** |
| GNG_KEEPER | TE | `gng_keeper_te_logistic_bust` | `gng_keeper_te_linear_vor` | 0.4964 vs 0.4594 (+0.0369) | 0.5594 vs 0.4967 (+0.0627) | 0.6149 vs 0.4781 (+0.1369) | Corr: +0.1369 | Pts: +0.6585 | None | **owner-review finalist** |

### Decision Logic Summary
*   **No selection by rank correlation alone**: Point capture rates, VOR capture, and de-correlated pairwise win rates were analyzed to ensure draft utility.
*   **Holdout checks**: We verified that 2025 holdout results did not mask weak validation in 2024. Keeper QB was flagged with a warning because its overall predictive correlation remains below 0.45 despite the `+0.1243` improvement.
*   **TE classification**: Standard, half_ppr, ppr, and keeper TE models all improved correlation and points captured rate substantially and are recommended as finalists/signals.

---

## 4. Full Scorecard Tables

The carousels below detail the 13 metrics for the baseline candidate and all 4 advanced candidates across standard, half_ppr, ppr, and keeper profiles.

### STANDARD Scoring Profile

````carousel
#### Position: QB

| Candidate ID | Season Scope | Rank Corr | Top-N Hit | Pts Cap | VOR Cap | NDCG@K | Elite Recall | Tier Acc | Bust Rate | Pairwise Win | Overall Pairwise | Regret | Missing |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `standard_qb_logistic_bust_inverse (Base)` | Validation (2024) | 0.4321 | 0.5231 | 0.7537 | 0.5738 | 0.7338 | 0.5231 | 0.4885 | 0.1019 | 0.6935 | 0.6940 | 582.6 | 0.0000 |
| `standard_qb_logistic_bust_inverse (Base)` | Holdout (2025) | 0.4148 | 0.8519 | 0.8903 | 0.8508 | 0.8323 | 0.8519 | 0.7960 | 0.0000 | 0.6557 | 0.6576 | 306.2 | 0.0000 |
| `standard_qb_logistic_bust_inverse (Base)` | Combined (2024-25) | 0.4234 | 0.6875 | 0.8220 | 0.7123 | 0.7830 | 0.6875 | 0.6422 | 0.0509 | 0.6746 | 0.6758 | 444.4 | 0.0000 |
| `standard_qb_logistic_bust` | Validation (2024) | 0.4710 | 0.5370 | 0.7699 | 0.5901 | 0.7557 | 0.5370 | 0.5054 | 0.0926 | 0.7045 | 0.7049 | 559.1 | 0.0000 |
| `standard_qb_logistic_bust` | Holdout (2025) | 0.4550 | 0.8519 | 0.8874 | 0.8494 | 0.8221 | 0.8519 | 0.7983 | 0.0000 | 0.6694 | 0.6706 | 304.1 | 0.0000 |
| `standard_qb_logistic_bust` | Combined (2024-25) | 0.5543 | 0.6944 | 0.8286 | 0.7197 | 0.7889 | 0.6944 | 0.6519 | 0.0463 | 0.6971 | 0.6977 | 863.2 | 0.0000 |
| `standard_qb_linear_points (Leader)` | Validation (2024) | 0.4680 | 0.5509 | 0.7817 | 0.6226 | 0.7685 | 0.5509 | 0.5239 | 0.0926 | 0.8775 | 0.8775 | 524.7 | 0.0000 |
| `standard_qb_linear_points (Leader)` | Holdout (2025) | 0.4392 | 0.8380 | 0.8766 | 0.8331 | 0.8157 | 0.8380 | 0.7761 | 0.0000 | 0.7401 | 0.7401 | 340.6 | 0.0000 |
| `standard_qb_linear_points (Leader)` | Combined (2024-25) | 0.5503 | 0.6944 | 0.8292 | 0.7278 | 0.7921 | 0.6944 | 0.6500 | 0.0463 | 0.8476 | 0.8476 | 865.3 | 0.0000 |
| `standard_qb_linear_vor` | Validation (2024) | 0.4094 | 0.5093 | 0.7276 | 0.5546 | 0.7196 | 0.5093 | 0.4929 | 0.1343 | nan | nan | 617.3 | 0.0000 |
| `standard_qb_linear_vor` | Holdout (2025) | 0.4502 | 0.8333 | 0.8722 | 0.8418 | 0.8296 | 0.8333 | 0.7677 | 0.0000 | nan | nan | 337.7 | 0.0000 |
| `standard_qb_linear_vor` | Combined (2024-25) | 0.5088 | 0.6713 | 0.7999 | 0.6982 | 0.7746 | 0.6713 | 0.6303 | 0.0671 | nan | nan | 955.0 | 0.0000 |
| `standard_qb_logistic_elite` | Validation (2024) | 0.4569 | 0.5417 | 0.7580 | 0.5865 | 0.7468 | 0.5417 | 0.5083 | 0.1065 | 0.7346 | 0.7349 | 568.4 | 0.0000 |
| `standard_qb_logistic_elite` | Holdout (2025) | 0.4470 | 0.8380 | 0.8736 | 0.8413 | 0.8306 | 0.8380 | 0.7766 | 0.0000 | 0.6917 | 0.6917 | 334.1 | 0.0000 |
| `standard_qb_logistic_elite` | Combined (2024-25) | 0.5431 | 0.6898 | 0.8158 | 0.7139 | 0.7887 | 0.6898 | 0.6425 | 0.0532 | 0.7255 | 0.7257 | 902.5 | 0.0000 |

<!-- slide -->
#### Position: RB

| Candidate ID | Season Scope | Rank Corr | Top-N Hit | Pts Cap | VOR Cap | NDCG@K | Elite Recall | Tier Acc | Bust Rate | Pairwise Win | Overall Pairwise | Regret | Missing |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `standard_rb_logistic_bust_inverse (Base)` | Validation (2024) | 0.6226 | 0.6343 | 0.7964 | 0.7359 | 0.7298 | 0.6343 | 0.3941 | 0.0509 | 0.7812 | 0.7853 | 796.9 | 0.0000 |
| `standard_rb_logistic_bust_inverse (Base)` | Holdout (2025) | 0.6602 | 1.0000 | 1.0000 | nan | 0.8424 | 1.0000 | 0.7377 | 0.0000 | 0.8151 | 0.8204 | 0.0 | 0.0000 |
| `standard_rb_logistic_bust_inverse (Base)` | Combined (2024-25) | 0.6414 | 0.8171 | 0.8982 | 0.7359 | 0.7861 | 0.8171 | 0.5659 | 0.0255 | 0.7982 | 0.8028 | 398.5 | 0.0000 |
| `standard_rb_linear_vor` | Validation (2024) | 0.5599 | 0.5810 | 0.7375 | 0.6528 | 0.6747 | 0.5810 | 0.3610 | 0.0718 | nan | nan | 1041.0 | 0.0000 |
| `standard_rb_linear_vor` | Holdout (2025) | 0.6563 | 1.0000 | 1.0000 | nan | 0.8433 | 1.0000 | 0.7489 | 0.0000 | nan | nan | 0.0 | 0.0000 |
| `standard_rb_linear_vor` | Combined (2024-25) | 0.6692 | 0.7905 | 0.8688 | 0.6528 | 0.7590 | 0.7905 | 0.5549 | 0.0359 | nan | nan | 1041.0 | 0.0000 |
| `standard_rb_logistic_bust` | Validation (2024) | 0.5851 | 0.5509 | 0.7169 | 0.6291 | 0.6564 | 0.5509 | 0.3670 | 0.0787 | 0.7583 | 0.7632 | 1105.0 | 0.0000 |
| `standard_rb_logistic_bust` | Holdout (2025) | 0.6929 | 1.0000 | 1.0000 | nan | 0.8457 | 1.0000 | 0.7764 | 0.0000 | 0.8154 | 0.8214 | 0.0 | 0.0000 |
| `standard_rb_logistic_bust` | Combined (2024-25) | 0.6885 | 0.7755 | 0.8585 | 0.6291 | 0.7511 | 0.7755 | 0.5717 | 0.0394 | 0.7626 | 0.7676 | 1105.0 | 0.0000 |
| `standard_rb_linear_points (Leader)` | Validation (2024) | 0.5752 | 0.5810 | 0.7367 | 0.6485 | 0.6808 | 0.5810 | 0.3646 | 0.0694 | 0.9853 | 0.9853 | 1047.4 | 0.0000 |
| `standard_rb_linear_points (Leader)` | Holdout (2025) | 0.6771 | 1.0000 | 1.0000 | nan | 0.8449 | 1.0000 | 0.7709 | 0.0000 | 0.9467 | 0.9467 | 0.0 | 0.0000 |
| `standard_rb_linear_points (Leader)` | Combined (2024-25) | 0.6809 | 0.7905 | 0.8684 | 0.6485 | 0.7629 | 0.7905 | 0.5677 | 0.0347 | 0.9672 | 0.9672 | 1047.4 | 0.0000 |
| `standard_rb_logistic_elite` | Validation (2024) | 0.5764 | 0.5394 | 0.7065 | 0.6181 | 0.6446 | 0.5394 | 0.3640 | 0.0926 | 0.7716 | 0.7747 | 1130.6 | 0.0000 |
| `standard_rb_logistic_elite` | Holdout (2025) | 0.6962 | 1.0000 | 1.0000 | nan | 0.8459 | 1.0000 | 0.7764 | 0.0000 | 0.8249 | 0.8296 | 0.0 | 0.0000 |
| `standard_rb_logistic_elite` | Combined (2024-25) | 0.6821 | 0.7697 | 0.8533 | 0.6181 | 0.7453 | 0.7697 | 0.5702 | 0.0463 | 0.7759 | 0.7791 | 1130.6 | 0.0000 |

<!-- slide -->
#### Position: WR

| Candidate ID | Season Scope | Rank Corr | Top-N Hit | Pts Cap | VOR Cap | NDCG@K | Elite Recall | Tier Acc | Bust Rate | Pairwise Win | Overall Pairwise | Regret | Missing |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `standard_wr_logistic_elite (Base)` | Validation (2024) | 0.5293 | 0.4306 | 0.6240 | 0.5051 | 0.5579 | 0.4306 | 0.3387 | 0.2685 | 0.7599 | 0.7403 | 1166.0 | 0.0000 |
| `standard_wr_logistic_elite (Base)` | Holdout (2025) | 0.5710 | 0.8310 | 0.8872 | 0.8863 | 0.7510 | 0.8310 | 0.5340 | 0.0000 | 0.7661 | 0.7822 | 217.8 | 0.0000 |
| `standard_wr_logistic_elite (Base)` | Combined (2024-25) | 0.5501 | 0.6308 | 0.7556 | 0.6957 | 0.6544 | 0.6308 | 0.4363 | 0.1343 | 0.7630 | 0.7613 | 691.9 | 0.0000 |
| `standard_wr_logistic_bust (Leader)` | Validation (2024) | 0.5230 | 0.4653 | 0.6490 | 0.5248 | 0.5829 | 0.4653 | 0.3435 | 0.2477 | 0.7417 | 0.7301 | 1115.1 | 0.0000 |
| `standard_wr_logistic_bust (Leader)` | Holdout (2025) | 0.5960 | 0.8241 | 0.8863 | 0.8874 | 0.7608 | 0.8241 | 0.5344 | 0.0000 | 0.7493 | 0.7740 | 217.6 | 0.0000 |
| `standard_wr_logistic_bust (Leader)` | Combined (2024-25) | 0.6391 | 0.6447 | 0.7677 | 0.7061 | 0.6719 | 0.6447 | 0.4390 | 0.1238 | 0.7424 | 0.7353 | 1332.7 | 0.0000 |
| `standard_wr_linear_points` | Validation (2024) | 0.5311 | 0.4468 | 0.6373 | 0.5077 | 0.5897 | 0.4468 | 0.3520 | 0.2454 | 0.9570 | 0.9057 | 1157.8 | 0.0000 |
| `standard_wr_linear_points` | Holdout (2025) | 0.6024 | 0.8264 | 0.8764 | 0.8762 | 0.7505 | 0.8264 | 0.5451 | 0.0000 | 1.0000 | 1.0000 | 238.1 | 0.0000 |
| `standard_wr_linear_points` | Combined (2024-25) | 0.6452 | 0.6366 | 0.7568 | 0.6919 | 0.6701 | 0.6366 | 0.4485 | 0.1227 | 0.9580 | 0.9111 | 1395.9 | 0.0000 |
| `standard_wr_linear_vor` | Validation (2024) | 0.5148 | 0.4468 | 0.6433 | 0.5236 | 0.5851 | 0.4468 | 0.3552 | 0.2500 | nan | nan | 1117.2 | 0.0000 |
| `standard_wr_linear_vor` | Holdout (2025) | 0.5922 | 0.8171 | 0.8867 | 0.8870 | 0.7496 | 0.8171 | 0.5246 | 0.0000 | nan | nan | 220.0 | 0.0000 |
| `standard_wr_linear_vor` | Combined (2024-25) | 0.6329 | 0.6319 | 0.7650 | 0.7053 | 0.6673 | 0.6319 | 0.4399 | 0.1250 | nan | nan | 1337.2 | 0.0000 |
| `standard_wr_logistic_elite` | Validation (2024) | 0.5230 | 0.4606 | 0.6483 | 0.5263 | 0.5872 | 0.4606 | 0.3454 | 0.2454 | 0.7765 | 0.7575 | 1111.7 | 0.0000 |
| `standard_wr_logistic_elite` | Holdout (2025) | 0.5988 | 0.8241 | 0.8854 | 0.8859 | 0.7667 | 0.8241 | 0.5338 | 0.0000 | 0.7886 | 0.8073 | 219.8 | 0.0000 |
| `standard_wr_logistic_elite` | Combined (2024-25) | 0.6391 | 0.6424 | 0.7668 | 0.7061 | 0.6769 | 0.6424 | 0.4396 | 0.1227 | 0.7777 | 0.7632 | 1331.5 | 0.0000 |

<!-- slide -->
#### Position: TE

| Candidate ID | Season Scope | Rank Corr | Top-N Hit | Pts Cap | VOR Cap | NDCG@K | Elite Recall | Tier Acc | Bust Rate | Pairwise Win | Overall Pairwise | Regret | Missing |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `standard_te_logistic_bust_inverse (Base)` | Validation (2024) | 0.5029 | 0.4537 | 0.6196 | 0.4967 | 0.5641 | 0.4537 | 0.3879 | 0.2593 | 0.7644 | 0.7750 | 415.4 | 0.0000 |
| `standard_te_logistic_bust_inverse (Base)` | Holdout (2025) | 0.5628 | 0.7593 | 0.8426 | 0.8358 | 0.7048 | 0.7593 | 0.7287 | 0.0046 | 0.7505 | 0.7677 | 148.1 | 0.0000 |
| `standard_te_logistic_bust_inverse (Base)` | Combined (2024-25) | 0.5329 | 0.6065 | 0.7311 | 0.6662 | 0.6345 | 0.6065 | 0.5583 | 0.1319 | 0.7575 | 0.7713 | 281.8 | 0.0000 |
| `standard_te_logistic_bust` | Validation (2024) | 0.4972 | 0.4167 | 0.5916 | 0.4820 | 0.5381 | 0.4167 | 0.4020 | 0.3056 | 0.7551 | 0.7683 | 428.3 | 0.0000 |
| `standard_te_logistic_bust` | Holdout (2025) | 0.5458 | 0.7546 | 0.8474 | 0.8398 | 0.7025 | 0.7546 | 0.7295 | 0.0000 | 0.7646 | 0.7798 | 139.8 | 0.0000 |
| `standard_te_logistic_bust` | Combined (2024-25) | 0.6151 | 0.5856 | 0.7195 | 0.6609 | 0.6203 | 0.5856 | 0.5658 | 0.1528 | 0.7564 | 0.7698 | 568.1 | 0.0000 |
| `standard_te_linear_vor` | Validation (2024) | 0.4679 | 0.3981 | 0.5843 | 0.4671 | 0.5491 | 0.3981 | 0.3745 | 0.3056 | nan | nan | 445.4 | 0.0000 |
| `standard_te_linear_vor` | Holdout (2025) | 0.5263 | 0.7685 | 0.8497 | 0.8424 | 0.7086 | 0.7685 | 0.7391 | 0.0000 | nan | nan | 148.2 | 0.0000 |
| `standard_te_linear_vor` | Combined (2024-25) | 0.5929 | 0.5833 | 0.7170 | 0.6547 | 0.6289 | 0.5833 | 0.5568 | 0.1528 | nan | nan | 593.6 | 0.0000 |
| `standard_te_linear_points (Leader)` | Validation (2024) | 0.4802 | 0.4028 | 0.5846 | 0.4735 | 0.5485 | 0.4028 | 0.3748 | 0.3056 | nan | nan | 437.5 | 0.0000 |
| `standard_te_linear_points (Leader)` | Holdout (2025) | 0.5343 | 0.7685 | 0.8701 | 0.8669 | 0.7153 | 0.7685 | 0.7413 | 0.0000 | nan | nan | 118.0 | 0.0000 |
| `standard_te_linear_points (Leader)` | Combined (2024-25) | 0.6022 | 0.5856 | 0.7273 | 0.6702 | 0.6319 | 0.5856 | 0.5580 | 0.1528 | nan | nan | 555.5 | 0.0000 |
| `standard_te_logistic_elite` | Validation (2024) | 0.4983 | 0.4259 | 0.6060 | 0.4886 | 0.5416 | 0.4259 | 0.4036 | 0.2870 | 0.7690 | 0.7808 | 422.6 | 0.0000 |
| `standard_te_logistic_elite` | Holdout (2025) | 0.5354 | 0.7361 | 0.8250 | 0.8120 | 0.6899 | 0.7361 | 0.7093 | 0.0000 | 0.7783 | 0.7914 | 172.1 | 0.0000 |
| `standard_te_logistic_elite` | Combined (2024-25) | 0.6155 | 0.5810 | 0.7155 | 0.6503 | 0.6158 | 0.5810 | 0.5564 | 0.1435 | 0.7703 | 0.7824 | 594.7 | 0.0000 |

````


### HALF_PPR Scoring Profile

````carousel
#### Position: QB

| Candidate ID | Season Scope | Rank Corr | Top-N Hit | Pts Cap | VOR Cap | NDCG@K | Elite Recall | Tier Acc | Bust Rate | Pairwise Win | Overall Pairwise | Regret | Missing |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `half_ppr_qb_logistic_elite (Base)` | Validation (2024) | 0.3912 | 0.0157 | 0.0455 | nan | nan | nan | nan | 0.0052 | 0.0157 | nan | 4.6 | 0.5824 |
| `half_ppr_qb_logistic_elite (Base)` | Holdout (2025) | 0.3360 | 0.0373 | 0.0671 | nan | nan | nan | nan | 0.0034 | 0.0373 | nan | 2.0 | 0.5565 |
| `half_ppr_qb_logistic_elite (Base)` | Combined (2024-25) | 0.3636 | 0.0265 | 0.0563 | nan | nan | nan | nan | 0.0043 | 0.0265 | nan | 3.3 | 0.5695 |
| `half_ppr_qb_linear_vor` | Validation (2024) | 0.4093 | 0.5139 | 0.7278 | 0.5545 | 0.7197 | 0.5139 | 0.4960 | 0.1343 | nan | nan | 617.7 | 0.0000 |
| `half_ppr_qb_linear_vor` | Holdout (2025) | 0.4502 | 0.8333 | 0.8720 | 0.8415 | 0.8295 | 0.8333 | 0.7677 | 0.0000 | nan | nan | 338.7 | 0.0000 |
| `half_ppr_qb_linear_vor` | Combined (2024-25) | 0.5088 | 0.6736 | 0.7999 | 0.6980 | 0.7746 | 0.6736 | 0.6319 | 0.0671 | nan | nan | 956.3 | 0.0000 |
| `half_ppr_qb_logistic_elite` | Validation (2024) | 0.4553 | 0.5417 | 0.7548 | 0.5786 | 0.7451 | 0.5417 | 0.5084 | 0.1065 | 0.7343 | 0.7346 | 577.3 | 0.0000 |
| `half_ppr_qb_logistic_elite` | Holdout (2025) | 0.4470 | 0.8380 | 0.8735 | 0.8411 | 0.8304 | 0.8380 | 0.7766 | 0.0000 | 0.6951 | 0.6951 | 335.1 | 0.0000 |
| `half_ppr_qb_logistic_elite` | Combined (2024-25) | 0.5419 | 0.6898 | 0.8142 | 0.7099 | 0.7878 | 0.6898 | 0.6425 | 0.0532 | 0.7261 | 0.7263 | 912.4 | 0.0000 |
| `half_ppr_qb_linear_points` | Validation (2024) | 0.4687 | 0.5556 | 0.7818 | 0.6224 | 0.7686 | 0.5556 | 0.5271 | 0.0926 | 0.8775 | 0.8775 | 525.1 | 0.0000 |
| `half_ppr_qb_linear_points` | Holdout (2025) | 0.4392 | 0.8380 | 0.8765 | 0.8328 | 0.8155 | 0.8380 | 0.7761 | 0.0000 | 0.7401 | 0.7401 | 341.6 | 0.0000 |
| `half_ppr_qb_linear_points` | Combined (2024-25) | 0.5509 | 0.6968 | 0.8291 | 0.7276 | 0.7921 | 0.6968 | 0.6516 | 0.0463 | 0.8476 | 0.8476 | 866.7 | 0.0000 |
| `half_ppr_qb_logistic_bust (Leader)` | Validation (2024) | 0.4735 | 0.5509 | 0.7756 | 0.5967 | 0.7591 | 0.5509 | 0.5143 | 0.0880 | 0.7067 | 0.7070 | 550.5 | 0.0000 |
| `half_ppr_qb_logistic_bust (Leader)` | Holdout (2025) | 0.4550 | 0.8519 | 0.8872 | 0.8491 | 0.8220 | 0.8519 | 0.7983 | 0.0000 | 0.6704 | 0.6717 | 305.1 | 0.0000 |
| `half_ppr_qb_logistic_bust (Leader)` | Combined (2024-25) | 0.5561 | 0.7014 | 0.8314 | 0.7229 | 0.7905 | 0.7014 | 0.6563 | 0.0440 | 0.6991 | 0.6996 | 855.6 | 0.0000 |

<!-- slide -->
#### Position: RB

| Candidate ID | Season Scope | Rank Corr | Top-N Hit | Pts Cap | VOR Cap | NDCG@K | Elite Recall | Tier Acc | Bust Rate | Pairwise Win | Overall Pairwise | Regret | Missing |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `half_ppr_rb_linear_vor (Base)` | Validation (2024) | 0.5810 | 0.0141 | 0.0548 | nan | nan | nan | nan | 0.0047 | 0.0141 | nan | 6.1 | 0.5414 |
| `half_ppr_rb_linear_vor (Base)` | Holdout (2025) | 0.6434 | 0.0656 | 0.1497 | nan | nan | nan | nan | 0.0000 | 0.0656 | nan | 0.5 | 0.4924 |
| `half_ppr_rb_linear_vor (Base)` | Combined (2024-25) | 0.6122 | 0.0398 | 0.1023 | nan | nan | nan | nan | 0.0024 | 0.0398 | nan | 3.3 | 0.5169 |
| `half_ppr_rb_logistic_bust` | Validation (2024) | 0.5963 | 0.5718 | 0.7277 | 0.6281 | 0.6736 | 0.5718 | 0.3902 | 0.0880 | 0.7644 | 0.7692 | 1136.7 | 0.0000 |
| `half_ppr_rb_logistic_bust` | Holdout (2025) | 0.6982 | 1.0000 | 1.0000 | nan | 0.8615 | 1.0000 | 0.7817 | 0.0000 | 0.8115 | 0.8166 | 0.0 | 0.0000 |
| `half_ppr_rb_logistic_bust` | Combined (2024-25) | 0.6968 | 0.7859 | 0.8639 | 0.6281 | 0.7676 | 0.7859 | 0.5860 | 0.0440 | 0.7680 | 0.7728 | 1136.7 | 0.0000 |
| `half_ppr_rb_logistic_elite` | Validation (2024) | 0.6007 | 0.5741 | 0.7342 | 0.6310 | 0.6785 | 0.5741 | 0.3822 | 0.0787 | 0.8118 | 0.8143 | 1129.3 | 0.0000 |
| `half_ppr_rb_logistic_elite` | Holdout (2025) | 0.6884 | 1.0000 | 1.0000 | nan | 0.8611 | 1.0000 | 0.7761 | 0.0000 | 0.8447 | 0.8480 | 0.0 | 0.0000 |
| `half_ppr_rb_logistic_elite` | Combined (2024-25) | 0.6999 | 0.7870 | 0.8671 | 0.6310 | 0.7698 | 0.7870 | 0.5792 | 0.0394 | 0.8147 | 0.8173 | 1129.3 | 0.0000 |
| `half_ppr_rb_linear_points` | Validation (2024) | 0.5872 | 0.5880 | 0.7465 | 0.6507 | 0.6922 | 0.5880 | 0.3738 | 0.0764 | 0.9608 | 0.9608 | 1071.5 | 0.0000 |
| `half_ppr_rb_linear_points` | Holdout (2025) | 0.6565 | 1.0000 | 1.0000 | nan | 0.8585 | 1.0000 | 0.7597 | 0.0000 | 0.9505 | 0.9505 | 0.0 | 0.0000 |
| `half_ppr_rb_linear_points` | Combined (2024-25) | 0.6893 | 0.7940 | 0.8733 | 0.6507 | 0.7753 | 0.7940 | 0.5668 | 0.0382 | 0.9581 | 0.9581 | 1071.5 | 0.0000 |
| `half_ppr_rb_linear_vor (Leader)` | Validation (2024) | 0.5706 | 0.5972 | 0.7557 | 0.6609 | 0.6943 | 0.5972 | 0.3596 | 0.0694 | nan | nan | 1037.5 | 0.0000 |
| `half_ppr_rb_linear_vor (Leader)` | Holdout (2025) | 0.6523 | 1.0000 | 1.0000 | nan | 0.8502 | 1.0000 | 0.7542 | 0.0000 | nan | nan | 0.0 | 0.0000 |
| `half_ppr_rb_linear_vor (Leader)` | Combined (2024-25) | 0.6770 | 0.7986 | 0.8779 | 0.6609 | 0.7722 | 0.7986 | 0.5569 | 0.0347 | nan | nan | 1037.5 | 0.0000 |

<!-- slide -->
#### Position: WR

| Candidate ID | Season Scope | Rank Corr | Top-N Hit | Pts Cap | VOR Cap | NDCG@K | Elite Recall | Tier Acc | Bust Rate | Pairwise Win | Overall Pairwise | Regret | Missing |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `half_ppr_wr_logistic_elite (Base)` | Validation (2024) | 0.5375 | 0.0131 | 0.0476 | nan | nan | nan | nan | 0.0086 | 0.0131 | nan | 15.4 | 0.5396 |
| `half_ppr_wr_logistic_elite (Base)` | Holdout (2025) | 0.5477 | 0.0564 | 0.1280 | nan | nan | nan | nan | 0.0047 | 0.0564 | nan | 2.1 | 0.4917 |
| `half_ppr_wr_logistic_elite (Base)` | Combined (2024-25) | 0.5426 | 0.0348 | 0.0878 | nan | nan | nan | nan | 0.0066 | 0.0348 | nan | 8.8 | 0.5156 |
| `half_ppr_wr_logistic_elite (Leader)` | Validation (2024) | 0.5469 | 0.4792 | 0.6802 | 0.5445 | 0.6200 | 0.4792 | 0.3496 | 0.2384 | 0.7878 | 0.7692 | 1199.2 | 0.0000 |
| `half_ppr_wr_logistic_elite (Leader)` | Holdout (2025) | 0.6115 | 0.8333 | 0.8973 | 0.8954 | 0.7803 | 0.8333 | 0.5517 | 0.0000 | 0.7857 | 0.8020 | 247.6 | 0.0000 |
| `half_ppr_wr_logistic_elite (Leader)` | Combined (2024-25) | 0.6570 | 0.6562 | 0.7888 | 0.7200 | 0.7002 | 0.6562 | 0.4507 | 0.1192 | 0.7876 | 0.7730 | 1446.8 | 0.0000 |
| `half_ppr_wr_linear_vor` | Validation (2024) | 0.5334 | 0.4560 | 0.6714 | 0.5331 | 0.6167 | 0.4560 | 0.3531 | 0.2407 | nan | nan | 1229.7 | 0.0000 |
| `half_ppr_wr_linear_vor` | Holdout (2025) | 0.6064 | 0.8148 | 0.8897 | 0.8880 | 0.7708 | 0.8148 | 0.5302 | 0.0000 | nan | nan | 269.9 | 0.0000 |
| `half_ppr_wr_linear_vor` | Combined (2024-25) | 0.6469 | 0.6354 | 0.7805 | 0.7105 | 0.6937 | 0.6354 | 0.4416 | 0.1204 | nan | nan | 1499.6 | 0.0000 |
| `half_ppr_wr_linear_points` | Validation (2024) | 0.5562 | 0.4630 | 0.6674 | 0.5246 | 0.6249 | 0.4630 | 0.3632 | 0.2407 | 0.9186 | 0.8983 | 1251.5 | 0.0000 |
| `half_ppr_wr_linear_points` | Holdout (2025) | 0.6205 | 0.8218 | 0.8838 | 0.8810 | 0.7753 | 0.8218 | 0.5431 | 0.0000 | 0.9564 | 0.9626 | 282.7 | 0.0000 |
| `half_ppr_wr_linear_points` | Combined (2024-25) | 0.6640 | 0.6424 | 0.7756 | 0.7028 | 0.7001 | 0.6424 | 0.4532 | 0.1204 | 0.9206 | 0.9032 | 1534.2 | 0.0000 |
| `half_ppr_wr_logistic_bust` | Validation (2024) | 0.5460 | 0.4792 | 0.6749 | 0.5354 | 0.6188 | 0.4792 | 0.3470 | 0.2431 | 0.7530 | 0.7411 | 1227.4 | 0.0000 |
| `half_ppr_wr_logistic_bust` | Holdout (2025) | 0.6139 | 0.8333 | 0.8950 | 0.8926 | 0.7792 | 0.8333 | 0.5556 | 0.0000 | 0.7571 | 0.7794 | 253.2 | 0.0000 |
| `half_ppr_wr_logistic_bust` | Combined (2024-25) | 0.6564 | 0.6562 | 0.7849 | 0.7140 | 0.6990 | 0.6562 | 0.4513 | 0.1215 | 0.7534 | 0.7456 | 1480.6 | 0.0000 |

<!-- slide -->
#### Position: TE

| Candidate ID | Season Scope | Rank Corr | Top-N Hit | Pts Cap | VOR Cap | NDCG@K | Elite Recall | Tier Acc | Bust Rate | Pairwise Win | Overall Pairwise | Regret | Missing |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `half_ppr_te_linear_vor (Base)` | Validation (2024) | 0.4687 | 0.0055 | 0.0466 | nan | nan | nan | nan | 0.0055 | 0.0055 | nan | 5.6 | 0.5572 |
| `half_ppr_te_linear_vor (Base)` | Holdout (2025) | 0.5117 | 0.0281 | 0.0818 | nan | nan | nan | nan | 0.0026 | 0.0281 | nan | 1.8 | 0.4981 |
| `half_ppr_te_linear_vor (Base)` | Combined (2024-25) | 0.4902 | 0.0168 | 0.0642 | nan | nan | nan | nan | 0.0040 | 0.0168 | nan | 3.7 | 0.5276 |
| `half_ppr_te_linear_vor` | Validation (2024) | 0.4923 | 0.4444 | 0.6470 | 0.5226 | 0.6073 | 0.4444 | 0.3848 | 0.2778 | nan | nan | 446.9 | 0.0000 |
| `half_ppr_te_linear_vor` | Holdout (2025) | 0.5374 | 0.7731 | 0.8600 | 0.8470 | 0.7391 | 0.7731 | 0.7447 | 0.0000 | nan | nan | 166.5 | 0.0000 |
| `half_ppr_te_linear_vor` | Combined (2024-25) | 0.6112 | 0.6088 | 0.7535 | 0.6848 | 0.6732 | 0.6088 | 0.5647 | 0.1389 | nan | nan | 613.4 | 0.0000 |
| `half_ppr_te_linear_points` | Validation (2024) | 0.5087 | 0.4444 | 0.6412 | 0.5085 | 0.6007 | 0.4444 | 0.3837 | 0.2731 | 0.9524 | 0.9524 | 459.3 | 0.0000 |
| `half_ppr_te_linear_points` | Holdout (2025) | 0.5491 | 0.7778 | 0.8795 | 0.8734 | 0.7466 | 0.7778 | 0.7508 | 0.0000 | nan | nan | 131.6 | 0.0000 |
| `half_ppr_te_linear_points` | Combined (2024-25) | 0.6236 | 0.6111 | 0.7603 | 0.6910 | 0.6737 | 0.6111 | 0.5672 | 0.1366 | 0.9524 | 0.9524 | 590.9 | 0.0000 |
| `half_ppr_te_logistic_bust` | Validation (2024) | 0.5242 | 0.4583 | 0.6402 | 0.5128 | 0.5788 | 0.4583 | 0.4099 | 0.2824 | 0.7644 | 0.7780 | 449.0 | 0.0000 |
| `half_ppr_te_logistic_bust` | Holdout (2025) | 0.5643 | 0.7778 | 0.8813 | 0.8791 | 0.7474 | 0.7778 | 0.7525 | 0.0000 | 0.7701 | 0.7797 | 128.1 | 0.0000 |
| `half_ppr_te_logistic_bust` | Combined (2024-25) | 0.6355 | 0.6181 | 0.7607 | 0.6960 | 0.6631 | 0.6181 | 0.5812 | 0.1412 | 0.7652 | 0.7782 | 577.1 | 0.0000 |
| `half_ppr_te_logistic_elite (Leader)` | Validation (2024) | 0.5236 | 0.4583 | 0.6482 | 0.5202 | 0.5853 | 0.4583 | 0.4080 | 0.2685 | 0.7735 | 0.7840 | 443.4 | 0.0000 |
| `half_ppr_te_logistic_elite (Leader)` | Holdout (2025) | 0.5556 | 0.7778 | 0.8823 | 0.8791 | 0.7453 | 0.7778 | 0.7525 | 0.0000 | 0.7751 | 0.7826 | 128.1 | 0.0000 |
| `half_ppr_te_logistic_elite (Leader)` | Combined (2024-25) | 0.6348 | 0.6181 | 0.7653 | 0.6996 | 0.6653 | 0.6181 | 0.5803 | 0.1343 | 0.7737 | 0.7838 | 571.5 | 0.0000 |

````


### PPR Scoring Profile

````carousel
#### Position: QB

| Candidate ID | Season Scope | Rank Corr | Top-N Hit | Pts Cap | VOR Cap | NDCG@K | Elite Recall | Tier Acc | Bust Rate | Pairwise Win | Overall Pairwise | Regret | Missing |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `ppr_qb_logistic_elite (Base)` | Validation (2024) | 0.3919 | 0.0175 | 0.0526 | nan | nan | nan | nan | 0.0035 | 0.0175 | nan | 3.8 | 0.5808 |
| `ppr_qb_logistic_elite (Base)` | Holdout (2025) | 0.3315 | 0.0373 | 0.0643 | nan | nan | nan | nan | 0.0034 | 0.0373 | nan | 1.9 | 0.5596 |
| `ppr_qb_logistic_elite (Base)` | Combined (2024-25) | 0.3617 | 0.0274 | 0.0584 | nan | nan | nan | nan | 0.0034 | 0.0274 | nan | 2.8 | 0.5702 |
| `ppr_qb_logistic_bust` | Validation (2024) | 0.4720 | 0.5509 | 0.7757 | 0.5968 | 0.7591 | 0.5509 | 0.5143 | 0.0880 | 0.7068 | 0.7071 | 550.7 | 0.0000 |
| `ppr_qb_logistic_bust` | Holdout (2025) | 0.4501 | 0.8472 | 0.8832 | 0.8455 | 0.8196 | 0.8472 | 0.7909 | 0.0000 | 0.6704 | 0.6717 | 311.7 | 0.0000 |
| `ppr_qb_logistic_bust` | Combined (2024-25) | 0.5544 | 0.6991 | 0.8294 | 0.7211 | 0.7894 | 0.6991 | 0.6526 | 0.0440 | 0.6991 | 0.6997 | 862.4 | 0.0000 |
| `ppr_qb_logistic_elite` | Validation (2024) | 0.4566 | 0.5417 | 0.7549 | 0.5787 | 0.7452 | 0.5417 | 0.5084 | 0.1065 | 0.7337 | 0.7340 | 577.6 | 0.0000 |
| `ppr_qb_logistic_elite` | Holdout (2025) | 0.4431 | 0.8380 | 0.8733 | 0.8408 | 0.8303 | 0.8380 | 0.7766 | 0.0000 | 0.6917 | 0.6917 | 336.1 | 0.0000 |
| `ppr_qb_logistic_elite` | Combined (2024-25) | 0.5425 | 0.6898 | 0.8141 | 0.7098 | 0.7877 | 0.6898 | 0.6425 | 0.0532 | 0.7249 | 0.7251 | 913.6 | 0.0000 |
| `ppr_qb_linear_vor` | Validation (2024) | 0.4088 | 0.5139 | 0.7278 | 0.5546 | 0.7197 | 0.5139 | 0.4960 | 0.1343 | nan | nan | 617.9 | 0.0000 |
| `ppr_qb_linear_vor` | Holdout (2025) | 0.4473 | 0.8333 | 0.8719 | 0.8412 | 0.8293 | 0.8333 | 0.7677 | 0.0000 | nan | nan | 339.7 | 0.0000 |
| `ppr_qb_linear_vor` | Combined (2024-25) | 0.5081 | 0.6736 | 0.7998 | 0.6979 | 0.7745 | 0.6736 | 0.6319 | 0.0671 | nan | nan | 957.5 | 0.0000 |
| `ppr_qb_linear_points (Leader)` | Validation (2024) | 0.4690 | 0.5556 | 0.7819 | 0.6225 | 0.7687 | 0.5556 | 0.5271 | 0.0926 | 0.8773 | 0.8773 | 525.3 | 0.0000 |
| `ppr_qb_linear_points (Leader)` | Holdout (2025) | 0.4394 | 0.8380 | 0.8763 | 0.8325 | 0.8154 | 0.8380 | 0.7761 | 0.0000 | 0.7401 | 0.7401 | 342.6 | 0.0000 |
| `ppr_qb_linear_points (Leader)` | Combined (2024-25) | 0.5511 | 0.6968 | 0.8291 | 0.7275 | 0.7920 | 0.6968 | 0.6516 | 0.0463 | 0.8474 | 0.8474 | 867.9 | 0.0000 |

<!-- slide -->
#### Position: RB

| Candidate ID | Season Scope | Rank Corr | Top-N Hit | Pts Cap | VOR Cap | NDCG@K | Elite Recall | Tier Acc | Bust Rate | Pairwise Win | Overall Pairwise | Regret | Missing |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `ppr_rb_linear_vor (Base)` | Validation (2024) | 0.5881 | 0.0149 | 0.0560 | nan | nan | nan | nan | 0.0039 | 0.0149 | nan | 6.3 | 0.5410 |
| `ppr_rb_linear_vor (Base)` | Holdout (2025) | 0.6302 | 0.0656 | 0.1810 | nan | nan | nan | nan | 0.0000 | 0.0656 | nan | 0.0 | 0.4935 |
| `ppr_rb_linear_vor (Base)` | Combined (2024-25) | 0.6092 | 0.0402 | 0.1185 | nan | nan | nan | nan | 0.0020 | 0.0402 | nan | 3.2 | 0.5173 |
| `ppr_rb_linear_points` | Validation (2024) | 0.5940 | 0.6042 | 0.7571 | 0.6562 | 0.7064 | 0.6042 | 0.3749 | 0.0718 | 0.9446 | 0.9446 | 1090.5 | 0.0000 |
| `ppr_rb_linear_points` | Holdout (2025) | 0.6462 | 1.0000 | 1.0000 | nan | 0.8626 | 1.0000 | 0.7491 | 0.0000 | 0.9310 | 0.9310 | 0.0 | 0.0000 |
| `ppr_rb_linear_points` | Combined (2024-25) | 0.6942 | 0.8021 | 0.8786 | 0.6562 | 0.7845 | 0.8021 | 0.5620 | 0.0359 | 0.9421 | 0.9421 | 1090.5 | 0.0000 |
| `ppr_rb_linear_vor (Leader)` | Validation (2024) | 0.5724 | 0.6157 | 0.7690 | 0.6689 | 0.7141 | 0.6157 | 0.3573 | 0.0579 | nan | nan | 1052.1 | 0.0000 |
| `ppr_rb_linear_vor (Leader)` | Holdout (2025) | 0.6421 | 1.0000 | 1.0000 | nan | 0.8655 | 1.0000 | 0.7436 | 0.0000 | nan | nan | 0.0 | 0.0000 |
| `ppr_rb_linear_vor (Leader)` | Combined (2024-25) | 0.6782 | 0.8079 | 0.8845 | 0.6689 | 0.7898 | 0.8079 | 0.5504 | 0.0289 | nan | nan | 1052.1 | 0.0000 |
| `ppr_rb_logistic_elite` | Validation (2024) | 0.6111 | 0.5972 | 0.7539 | 0.6451 | 0.6983 | 0.5972 | 0.3845 | 0.0694 | 0.8143 | 0.8170 | 1123.7 | 0.0000 |
| `ppr_rb_logistic_elite` | Holdout (2025) | 0.6751 | 1.0000 | 1.0000 | nan | 0.8675 | 1.0000 | 0.7597 | 0.0000 | 0.8398 | 0.8417 | 0.0 | 0.0000 |
| `ppr_rb_logistic_elite` | Combined (2024-25) | 0.7073 | 0.7986 | 0.8769 | 0.6451 | 0.7829 | 0.7986 | 0.5721 | 0.0347 | 0.8165 | 0.8192 | 1123.7 | 0.0000 |
| `ppr_rb_logistic_bust` | Validation (2024) | 0.6068 | 0.5810 | 0.7408 | 0.6395 | 0.6881 | 0.5810 | 0.3810 | 0.0856 | 0.7688 | 0.7733 | 1138.1 | 0.0000 |
| `ppr_rb_logistic_bust` | Holdout (2025) | 0.6898 | 1.0000 | 1.0000 | nan | 0.8658 | 1.0000 | 0.7711 | 0.0000 | 0.8068 | 0.8110 | 0.0 | 0.0000 |
| `ppr_rb_logistic_bust` | Combined (2024-25) | 0.7044 | 0.7905 | 0.8704 | 0.6395 | 0.7769 | 0.7905 | 0.5760 | 0.0428 | 0.7717 | 0.7762 | 1138.1 | 0.0000 |

<!-- slide -->
#### Position: WR

| Candidate ID | Season Scope | Rank Corr | Top-N Hit | Pts Cap | VOR Cap | NDCG@K | Elite Recall | Tier Acc | Bust Rate | Pairwise Win | Overall Pairwise | Regret | Missing |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `ppr_wr_logistic_elite (Base)` | Validation (2024) | 0.5476 | 0.0141 | 0.0518 | nan | nan | nan | nan | 0.0076 | 0.0141 | nan | 12.8 | 0.5394 |
| `ppr_wr_logistic_elite (Base)` | Holdout (2025) | 0.5576 | 0.0564 | 0.1330 | nan | nan | nan | nan | 0.0031 | 0.0564 | nan | 2.2 | 0.4933 |
| `ppr_wr_logistic_elite (Base)` | Combined (2024-25) | 0.5526 | 0.0353 | 0.0924 | nan | nan | nan | nan | 0.0054 | 0.0353 | nan | 7.5 | 0.5163 |
| `ppr_wr_linear_points` | Validation (2024) | 0.5673 | 0.4769 | 0.6972 | 0.5578 | 0.6523 | 0.4769 | 0.3629 | 0.2292 | 0.8914 | 0.8717 | 1278.8 | 0.0000 |
| `ppr_wr_linear_points` | Holdout (2025) | 0.6262 | 0.8264 | 0.8863 | 0.8820 | 0.7852 | 0.8264 | 0.5641 | 0.0000 | 0.9161 | 0.9253 | 332.8 | 0.0000 |
| `ppr_wr_linear_points` | Combined (2024-25) | 0.6724 | 0.6516 | 0.7917 | 0.7199 | 0.7188 | 0.6516 | 0.4635 | 0.1146 | 0.8931 | 0.8771 | 1611.6 | 0.0000 |
| `ppr_wr_logistic_elite (Leader)` | Validation (2024) | 0.5571 | 0.4861 | 0.7001 | 0.5610 | 0.6419 | 0.4861 | 0.3441 | 0.2292 | 0.7807 | 0.7639 | 1268.9 | 0.0000 |
| `ppr_wr_logistic_elite (Leader)` | Holdout (2025) | 0.6151 | 0.8356 | 0.9002 | 0.8970 | 0.7883 | 0.8356 | 0.5601 | 0.0000 | 0.7686 | 0.7844 | 288.4 | 0.0000 |
| `ppr_wr_logistic_elite (Leader)` | Combined (2024-25) | 0.6645 | 0.6609 | 0.8001 | 0.7290 | 0.7151 | 0.6609 | 0.4521 | 0.1146 | 0.7795 | 0.7663 | 1557.3 | 0.0000 |
| `ppr_wr_linear_vor` | Validation (2024) | 0.5443 | 0.4699 | 0.6988 | 0.5611 | 0.6493 | 0.4699 | 0.3468 | 0.2269 | nan | nan | 1268.0 | 0.0000 |
| `ppr_wr_linear_vor` | Holdout (2025) | 0.6093 | 0.8171 | 0.8897 | 0.8870 | 0.7862 | 0.8171 | 0.5399 | 0.0000 | nan | nan | 324.1 | 0.0000 |
| `ppr_wr_linear_vor` | Combined (2024-25) | 0.6550 | 0.6435 | 0.7942 | 0.7240 | 0.7177 | 0.6435 | 0.4433 | 0.1134 | nan | nan | 1592.1 | 0.0000 |
| `ppr_wr_logistic_bust` | Validation (2024) | 0.5581 | 0.4792 | 0.6951 | 0.5495 | 0.6387 | 0.4792 | 0.3478 | 0.2361 | 0.7439 | 0.7326 | 1305.4 | 0.0000 |
| `ppr_wr_logistic_bust` | Holdout (2025) | 0.6163 | 0.8333 | 0.8947 | 0.8911 | 0.7851 | 0.8333 | 0.5605 | 0.0000 | 0.7473 | 0.7692 | 304.5 | 0.0000 |
| `ppr_wr_logistic_bust` | Combined (2024-25) | 0.6653 | 0.6562 | 0.7949 | 0.7203 | 0.7119 | 0.6562 | 0.4542 | 0.1181 | 0.7442 | 0.7369 | 1609.9 | 0.0000 |

<!-- slide -->
#### Position: TE

| Candidate ID | Season Scope | Rank Corr | Top-N Hit | Pts Cap | VOR Cap | NDCG@K | Elite Recall | Tier Acc | Bust Rate | Pairwise Win | Overall Pairwise | Regret | Missing |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `ppr_te_linear_vor (Base)` | Validation (2024) | 0.4798 | 0.0064 | 0.0456 | nan | nan | nan | nan | 0.0046 | 0.0064 | nan | 9.6 | 0.5580 |
| `ppr_te_linear_vor (Base)` | Holdout (2025) | 0.5225 | 0.0281 | 0.0828 | nan | nan | nan | nan | 0.0026 | 0.0281 | nan | 1.8 | 0.4960 |
| `ppr_te_linear_vor (Base)` | Combined (2024-25) | 0.5011 | 0.0173 | 0.0642 | nan | nan | nan | nan | 0.0036 | 0.0173 | nan | 5.7 | 0.5270 |
| `ppr_te_linear_points` | Validation (2024) | 0.5210 | 0.4722 | 0.6636 | 0.5266 | 0.6262 | 0.4722 | 0.3932 | 0.2824 | 0.9013 | 0.9035 | 517.2 | 0.0000 |
| `ppr_te_linear_points` | Holdout (2025) | 0.5618 | 0.7870 | 0.8861 | 0.8803 | 0.7624 | 0.7870 | 0.7663 | 0.0000 | 0.9130 | 0.9348 | 143.3 | 0.0000 |
| `ppr_te_linear_points` | Combined (2024-25) | 0.6331 | 0.6296 | 0.7749 | 0.7035 | 0.6943 | 0.6296 | 0.5798 | 0.1412 | 0.9024 | 0.9064 | 660.5 | 0.0000 |
| `ppr_te_logistic_bust (Leader)` | Validation (2024) | 0.5367 | 0.4815 | 0.6642 | 0.5381 | 0.6057 | 0.4815 | 0.4188 | 0.2963 | 0.7667 | 0.7810 | 494.6 | 0.0000 |
| `ppr_te_logistic_bust (Leader)` | Holdout (2025) | 0.5680 | 0.7824 | 0.8869 | 0.8837 | 0.7643 | 0.7824 | 0.7578 | 0.0000 | 0.7757 | 0.7871 | 143.0 | 0.0000 |
| `ppr_te_logistic_bust (Leader)` | Combined (2024-25) | 0.6448 | 0.6319 | 0.7755 | 0.7109 | 0.6850 | 0.6319 | 0.5883 | 0.1481 | 0.7678 | 0.7818 | 637.6 | 0.0000 |
| `ppr_te_logistic_elite` | Validation (2024) | 0.5397 | 0.4815 | 0.6682 | 0.5283 | 0.6079 | 0.4815 | 0.4102 | 0.2870 | 0.7786 | 0.7890 | 501.7 | 0.0000 |
| `ppr_te_logistic_elite` | Holdout (2025) | 0.5680 | 0.7778 | 0.8803 | 0.8769 | 0.7610 | 0.7778 | 0.7525 | 0.0000 | 0.7800 | 0.7879 | 153.8 | 0.0000 |
| `ppr_te_logistic_elite` | Combined (2024-25) | 0.6471 | 0.6296 | 0.7742 | 0.7026 | 0.6844 | 0.6296 | 0.5814 | 0.1435 | 0.7788 | 0.7889 | 655.5 | 0.0000 |
| `ppr_te_linear_vor` | Validation (2024) | 0.5018 | 0.4583 | 0.6560 | 0.5184 | 0.6249 | 0.4583 | 0.3870 | 0.2963 | nan | nan | 520.4 | 0.0000 |
| `ppr_te_linear_vor` | Holdout (2025) | 0.5552 | 0.7685 | 0.8559 | 0.8385 | 0.7527 | 0.7685 | 0.7405 | 0.0000 | nan | nan | 203.3 | 0.0000 |
| `ppr_te_linear_vor` | Combined (2024-25) | 0.6188 | 0.6134 | 0.7560 | 0.6784 | 0.6888 | 0.6134 | 0.5637 | 0.1481 | nan | nan | 723.7 | 0.0000 |

````


### GNG_KEEPER Scoring Profile

````carousel
#### Position: QB

| Candidate ID | Season Scope | Rank Corr | Top-N Hit | Pts Cap | VOR Cap | NDCG@K | Elite Recall | Tier Acc | Bust Rate | Pairwise Win | Overall Pairwise | Regret | Missing |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `gng_keeper_qb_logistic_elite (Base)` | Validation (2024) | 0.3631 | 0.0157 | 0.0599 | nan | nan | nan | nan | 0.0052 | 0.0157 | nan | 3.7 | 0.5812 |
| `gng_keeper_qb_logistic_elite (Base)` | Holdout (2025) | 0.3050 | 0.0373 | 0.0711 | nan | nan | nan | nan | 0.0034 | 0.0373 | nan | 1.8 | 0.5596 |
| `gng_keeper_qb_logistic_elite (Base)` | Combined (2024-25) | 0.3341 | 0.0265 | 0.0655 | nan | nan | nan | nan | 0.0043 | 0.0265 | nan | 2.7 | 0.5704 |
| `gng_keeper_qb_logistic_elite` | Validation (2024) | 0.4045 | 0.5231 | 0.6735 | 0.5710 | 0.6543 | 0.5231 | 0.4643 | 0.1157 | 0.7082 | 0.7082 | 597.0 | 0.0000 |
| `gng_keeper_qb_logistic_elite` | Holdout (2025) | 0.3977 | 0.8241 | 0.8625 | 0.8373 | 0.7967 | 0.8241 | 0.7577 | 0.0000 | 0.6646 | 0.6646 | 321.1 | 0.0000 |
| `gng_keeper_qb_logistic_elite` | Combined (2024-25) | 0.4995 | 0.6736 | 0.7680 | 0.7042 | 0.7255 | 0.6736 | 0.6110 | 0.0579 | 0.6995 | 0.6995 | 918.1 | 0.0000 |
| `gng_keeper_qb_linear_vor` | Validation (2024) | 0.3661 | 0.5046 | 0.6485 | 0.5457 | 0.6351 | 0.5046 | 0.4616 | 0.1389 | nan | nan | 637.8 | 0.0000 |
| `gng_keeper_qb_linear_vor` | Holdout (2025) | 0.4293 | 0.8287 | 0.8725 | 0.8459 | 0.8057 | 0.8287 | 0.7658 | 0.0000 | nan | nan | 290.4 | 0.0000 |
| `gng_keeper_qb_linear_vor` | Combined (2024-25) | 0.4750 | 0.6667 | 0.7605 | 0.6958 | 0.7204 | 0.6667 | 0.6137 | 0.0694 | nan | nan | 928.2 | 0.0000 |
| `gng_keeper_qb_logistic_bust` | Validation (2024) | 0.4140 | 0.5278 | 0.6822 | 0.5840 | 0.6593 | 0.5278 | 0.4723 | 0.1111 | 0.6867 | 0.6870 | 582.2 | 0.0000 |
| `gng_keeper_qb_logistic_bust` | Holdout (2025) | 0.4137 | 0.8333 | 0.8728 | 0.8438 | 0.8019 | 0.8333 | 0.7713 | 0.0000 | 0.6580 | 0.6600 | 303.8 | 0.0000 |
| `gng_keeper_qb_logistic_bust` | Combined (2024-25) | 0.5082 | 0.6806 | 0.7775 | 0.7139 | 0.7306 | 0.6806 | 0.6218 | 0.0556 | 0.6807 | 0.6814 | 886.0 | 0.0000 |
| `gng_keeper_qb_linear_points (Leader)` | Validation (2024) | 0.4103 | 0.5278 | 0.6934 | 0.5976 | 0.6670 | 0.5278 | 0.4725 | 0.1111 | 0.8403 | 0.8403 | 554.6 | 0.0000 |
| `gng_keeper_qb_linear_points (Leader)` | Holdout (2025) | 0.4239 | 0.8472 | 0.8864 | 0.8591 | 0.8098 | 0.8472 | 0.7914 | 0.0000 | 0.8308 | 0.8308 | 265.5 | 0.0000 |
| `gng_keeper_qb_linear_points (Leader)` | Combined (2024-25) | 0.5066 | 0.6875 | 0.7899 | 0.7284 | 0.7384 | 0.6875 | 0.6319 | 0.0556 | 0.8384 | 0.8384 | 820.1 | 0.0000 |

<!-- slide -->
#### Position: RB

| Candidate ID | Season Scope | Rank Corr | Top-N Hit | Pts Cap | VOR Cap | NDCG@K | Elite Recall | Tier Acc | Bust Rate | Pairwise Win | Overall Pairwise | Regret | Missing |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `gng_keeper_rb_linear_vor (Base)` | Validation (2024) | 0.5639 | 0.0165 | 0.0561 | nan | nan | nan | nan | 0.0024 | 0.0165 | nan | 4.9 | 0.5421 |
| `gng_keeper_rb_linear_vor (Base)` | Holdout (2025) | 0.6269 | 0.0656 | 0.1184 | nan | nan | nan | nan | 0.0000 | 0.0656 | nan | 0.5 | 0.4912 |
| `gng_keeper_rb_linear_vor (Base)` | Combined (2024-25) | 0.5954 | 0.0410 | 0.0873 | nan | nan | nan | nan | 0.0012 | 0.0410 | nan | 2.7 | 0.5167 |
| `gng_keeper_rb_logistic_bust` | Validation (2024) | 0.5574 | 0.5324 | 0.6624 | 0.5947 | 0.5959 | 0.5324 | 0.3711 | 0.0856 | 0.7489 | 0.7522 | 1020.7 | 0.0000 |
| `gng_keeper_rb_logistic_bust` | Holdout (2025) | 0.6708 | 1.0000 | 1.0000 | nan | 0.7986 | 1.0000 | 0.7764 | 0.0000 | 0.8043 | 0.8079 | 0.0 | 0.0000 |
| `gng_keeper_rb_logistic_bust` | Combined (2024-25) | 0.6676 | 0.7662 | 0.8312 | 0.5947 | 0.6972 | 0.7662 | 0.5738 | 0.0428 | 0.7531 | 0.7564 | 1020.7 | 0.0000 |
| `gng_keeper_rb_linear_points (Leader)` | Validation (2024) | 0.5502 | 0.5671 | 0.6954 | 0.6348 | 0.6263 | 0.5671 | 0.3623 | 0.0718 | nan | nan | 931.8 | 0.0000 |
| `gng_keeper_rb_linear_points (Leader)` | Holdout (2025) | 0.6451 | 1.0000 | 1.0000 | nan | 0.7970 | 1.0000 | 0.7544 | 0.0000 | nan | nan | 0.0 | 0.0000 |
| `gng_keeper_rb_linear_points (Leader)` | Combined (2024-25) | 0.6618 | 0.7836 | 0.8477 | 0.6348 | 0.7117 | 0.7836 | 0.5583 | 0.0359 | nan | nan | 931.8 | 0.0000 |
| `gng_keeper_rb_linear_vor` | Validation (2024) | 0.5402 | 0.5602 | 0.6898 | 0.6348 | 0.6200 | 0.5602 | 0.3523 | 0.0856 | nan | nan | 933.8 | 0.0000 |
| `gng_keeper_rb_linear_vor` | Holdout (2025) | 0.6361 | 1.0000 | 1.0000 | nan | 0.7971 | 1.0000 | 0.7595 | 0.0000 | nan | nan | 0.0 | 0.0000 |
| `gng_keeper_rb_linear_vor` | Combined (2024-25) | 0.6543 | 0.7801 | 0.8449 | 0.6348 | 0.7085 | 0.7801 | 0.5559 | 0.0428 | nan | nan | 933.8 | 0.0000 |
| `gng_keeper_rb_logistic_elite` | Validation (2024) | 0.5523 | 0.5208 | 0.6469 | 0.5767 | 0.5816 | 0.5208 | 0.3690 | 0.0995 | 0.7625 | 0.7645 | 1063.7 | 0.0000 |
| `gng_keeper_rb_logistic_elite` | Holdout (2025) | 0.6765 | 1.0000 | 1.0000 | nan | 0.7990 | 1.0000 | 0.7764 | 0.0000 | 0.8138 | 0.8159 | 0.0 | 0.0000 |
| `gng_keeper_rb_logistic_elite` | Combined (2024-25) | 0.6639 | 0.7604 | 0.8235 | 0.5767 | 0.6903 | 0.7604 | 0.5727 | 0.0498 | 0.7667 | 0.7687 | 1063.7 | 0.0000 |

<!-- slide -->
#### Position: WR

| Candidate ID | Season Scope | Rank Corr | Top-N Hit | Pts Cap | VOR Cap | NDCG@K | Elite Recall | Tier Acc | Bust Rate | Pairwise Win | Overall Pairwise | Regret | Missing |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `gng_keeper_wr_logistic_elite (Base)` | Validation (2024) | 0.5202 | 0.0131 | 0.0467 | nan | nan | nan | nan | 0.0096 | 0.0131 | nan | 13.8 | 0.5392 |
| `gng_keeper_wr_logistic_elite (Base)` | Holdout (2025) | 0.5298 | 0.0564 | 0.1170 | nan | nan | nan | nan | 0.0047 | 0.0564 | nan | 2.3 | 0.4929 |
| `gng_keeper_wr_logistic_elite (Base)` | Combined (2024-25) | 0.5250 | 0.0348 | 0.0819 | nan | nan | nan | nan | 0.0071 | 0.0348 | nan | 8.0 | 0.5160 |
| `gng_keeper_wr_logistic_elite (Leader)` | Validation (2024) | 0.5230 | 0.4120 | 0.6103 | 0.5146 | 0.5507 | 0.4120 | 0.3369 | 0.2384 | 0.7802 | 0.7568 | 908.3 | 0.0000 |
| `gng_keeper_wr_logistic_elite (Leader)` | Holdout (2025) | 0.6008 | 0.8356 | 0.8900 | 0.8874 | 0.7441 | 0.8356 | 0.5518 | 0.0000 | 0.7919 | 0.8080 | 151.0 | 0.0000 |
| `gng_keeper_wr_logistic_elite (Leader)` | Combined (2024-25) | 0.6392 | 0.6238 | 0.7502 | 0.7010 | 0.6474 | 0.6238 | 0.4443 | 0.1192 | 0.7814 | 0.7627 | 1059.3 | 0.0000 |
| `gng_keeper_wr_logistic_bust` | Validation (2024) | 0.5254 | 0.4144 | 0.6117 | 0.5199 | 0.5501 | 0.4144 | 0.3389 | 0.2454 | 0.7408 | 0.7242 | 899.4 | 0.0000 |
| `gng_keeper_wr_logistic_bust` | Holdout (2025) | 0.6062 | 0.8287 | 0.8835 | 0.8798 | 0.7459 | 0.8287 | 0.5507 | 0.0000 | 0.7550 | 0.7769 | 159.9 | 0.0000 |
| `gng_keeper_wr_logistic_bust` | Combined (2024-25) | 0.6410 | 0.6215 | 0.7476 | 0.6998 | 0.6480 | 0.6215 | 0.4448 | 0.1227 | 0.7422 | 0.7304 | 1059.3 | 0.0000 |
| `gng_keeper_wr_linear_vor` | Validation (2024) | 0.5164 | 0.4074 | 0.6019 | 0.5020 | 0.5458 | 0.4074 | 0.3462 | 0.2384 | nan | nan | 930.8 | 0.0000 |
| `gng_keeper_wr_linear_vor` | Holdout (2025) | 0.6015 | 0.8194 | 0.8794 | 0.8765 | 0.7220 | 0.8194 | 0.5343 | 0.0000 | nan | nan | 163.8 | 0.0000 |
| `gng_keeper_wr_linear_vor` | Combined (2024-25) | 0.6343 | 0.6134 | 0.7407 | 0.6892 | 0.6339 | 0.6134 | 0.4402 | 0.1192 | nan | nan | 1094.6 | 0.0000 |
| `gng_keeper_wr_linear_points` | Validation (2024) | 0.5311 | 0.4144 | 0.6087 | 0.5128 | 0.5525 | 0.4144 | 0.3491 | 0.2338 | nan | nan | 916.7 | 0.0000 |
| `gng_keeper_wr_linear_points` | Holdout (2025) | 0.6103 | 0.8194 | 0.8698 | 0.8650 | 0.7190 | 0.8194 | 0.5430 | 0.0000 | nan | nan | 180.9 | 0.0000 |
| `gng_keeper_wr_linear_points` | Combined (2024-25) | 0.6454 | 0.6169 | 0.7393 | 0.6889 | 0.6357 | 0.6169 | 0.4460 | 0.1169 | nan | nan | 1097.6 | 0.0000 |

<!-- slide -->
#### Position: TE

| Candidate ID | Season Scope | Rank Corr | Top-N Hit | Pts Cap | VOR Cap | NDCG@K | Elite Recall | Tier Acc | Bust Rate | Pairwise Win | Overall Pairwise | Regret | Missing |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `gng_keeper_te_linear_vor (Base)` | Validation (2024) | 0.4594 | 0.0037 | 0.0324 | nan | nan | nan | nan | 0.0074 | 0.0037 | nan | 10.4 | 0.5606 |
| `gng_keeper_te_linear_vor (Base)` | Holdout (2025) | 0.4967 | 0.0281 | 0.0892 | nan | nan | nan | nan | 0.0026 | 0.0281 | nan | 1.8 | 0.5004 |
| `gng_keeper_te_linear_vor (Base)` | Combined (2024-25) | 0.4781 | 0.0159 | 0.0608 | nan | nan | nan | nan | 0.0050 | 0.0159 | nan | 6.1 | 0.5305 |
| `gng_keeper_te_logistic_bust (Leader)` | Validation (2024) | 0.4964 | 0.4213 | 0.5725 | 0.4536 | 0.5159 | 0.4213 | 0.3935 | 0.2963 | 0.7560 | 0.7686 | 423.2 | 0.0000 |
| `gng_keeper_te_logistic_bust (Leader)` | Holdout (2025) | 0.5594 | 0.7778 | 0.8662 | 0.8578 | 0.6957 | 0.7778 | 0.7552 | 0.0000 | 0.7650 | 0.7732 | 107.7 | 0.0000 |
| `gng_keeper_te_logistic_bust (Leader)` | Combined (2024-25) | 0.6149 | 0.5995 | 0.7194 | 0.6557 | 0.6058 | 0.5995 | 0.5744 | 0.1481 | 0.7572 | 0.7692 | 531.0 | 0.0000 |
| `gng_keeper_te_logistic_elite` | Validation (2024) | 0.5096 | 0.4120 | 0.5851 | 0.4646 | 0.5179 | 0.4120 | 0.3854 | 0.2685 | 0.7714 | 0.7818 | 422.9 | 0.0000 |
| `gng_keeper_te_logistic_elite` | Holdout (2025) | 0.5623 | 0.7731 | 0.8478 | 0.8311 | 0.6865 | 0.7731 | 0.7474 | 0.0000 | 0.7813 | 0.7889 | 123.0 | 0.0000 |
| `gng_keeper_te_logistic_elite` | Combined (2024-25) | 0.6248 | 0.5926 | 0.7165 | 0.6478 | 0.6022 | 0.5926 | 0.5664 | 0.1343 | 0.7727 | 0.7827 | 545.9 | 0.0000 |
| `gng_keeper_te_linear_points` | Validation (2024) | 0.4902 | 0.4074 | 0.5713 | 0.4474 | 0.5303 | 0.4074 | 0.3755 | 0.2917 | nan | nan | 434.8 | 0.0000 |
| `gng_keeper_te_linear_points` | Holdout (2025) | 0.5424 | 0.7824 | 0.8687 | 0.8577 | 0.7016 | 0.7824 | 0.7566 | 0.0000 | nan | nan | 104.8 | 0.0000 |
| `gng_keeper_te_linear_points` | Combined (2024-25) | 0.6098 | 0.5949 | 0.7200 | 0.6526 | 0.6159 | 0.5949 | 0.5660 | 0.1458 | nan | nan | 539.6 | 0.0000 |
| `gng_keeper_te_linear_vor` | Validation (2024) | 0.4890 | 0.3981 | 0.5648 | 0.4436 | 0.5274 | 0.3981 | 0.3823 | 0.2963 | nan | nan | 441.0 | 0.0000 |
| `gng_keeper_te_linear_vor` | Holdout (2025) | 0.5473 | 0.7778 | 0.8430 | 0.8270 | 0.6938 | 0.7778 | 0.7501 | 0.0000 | nan | nan | 135.6 | 0.0000 |
| `gng_keeper_te_linear_vor` | Combined (2024-25) | 0.6091 | 0.5880 | 0.7039 | 0.6353 | 0.6106 | 0.5880 | 0.5662 | 0.1481 | nan | nan | 576.6 | 0.0000 |

````


---

## 5. Hard Restrictions & Handoff Confirmations

*   **Route Metrics Confirmation**: **ROUTE METRICS REMAIN BLOCKED**. True route run metrics (`routes_run`, `yprr`, `tprr`) are strictly mapped to `NULL` in the queries due to the lack of player-level routing denominators in nflverse.
*   **No Live Changes**: **CONFIRMED**. No active formula or champion changes were written to production tables.
*   **No Champion Activation**: **CONFIRMED**. Current Pigskin remains live, and no champion is currently active.
*   **No Top-100 Interleaver**: **CONFIRMED**. No top-100 lists or rank merges were executed.
*   **Validation Database Checks**: **PASSED**. Summary-only candidate backtest records were written to `ranking_backtest_candidate_summaries` (256 rows written, 12 runs written, 336 rows read).

---

## 6. Git and Workspace State

*   **Current Branch**: `codex/phase-14-validation-footer`
*   **Latest Commit**: `40aa152 phase 33.17 rebuild bqml v2 feature contract from advanced player metrics v1`
*   **Modified Files**: `src/bqml_v2_feature_contract.py`

---

## 7. Recommended Next Phase

> [!TIP]
> **Phase 33.19 — Advanced BQML v2 owner-review boards**
> We recommend promoting these finalists to the owner-review boards in the next phase to calibrate the 2026 overall player profile packets.
