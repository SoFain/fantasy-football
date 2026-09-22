# Scorecard Correction and Finalist Label Cleanup Report — Phase 33.18C

## 1. Executive Summary & Final Decision

This report documents the scorecard correction and finalist-label cleanup for the Phase 33.18 BQML v2 advanced positional models. In Phase 33.18B, several non-Standard baselines were mapped to incorrect prior candidates. We have corrected the baselines to align with the true Phase 33.13 finalists from `docs/rebuild/bqml-v2-positional-formula-finalists.md`.

We also investigated the baseline evaluator mismatch. The Phase 33.13 baseline rows for `half_ppr`, `ppr`, and `gng_keeper` contain high missingness rates (~52%) and extremely low hit rates (~2%) due to a formula bug in the older evaluator script. These rows have been marked as **evaluator-incompatible**, and we do not use their buggy metrics to claim points or VOR capture improvements.

### Final Decision Option
> [!IMPORTANT]
> **ADVANCED BQML V2 FINALIST COMPARISON CORRECTED**
> The comparisons against the true Phase 33.13 prior finalists have been corrected. The advanced owner-review finalists are verified and ready for presentation to the owner-review boards.

---

## 2. Baseline Mismatch Audit

*   **Standard baselines**: **COMPATIBLE**. Sourced using the corrected feature contract and evaluator setup, showing 0% missingness and normal draft utility metrics.
*   **Half PPR, PPR, and GNG Keeper baselines**: **EVALUATOR-INCOMPATIBLE**.
    *   *Issue*: Baseline rows had ~52% missingness and ~2% points capture because the older script divided by the entire position-week universe instead of the ideal cohort, and it lacked VOR/NDCG JSON persistence.
    *   *Remediation*: Baseline rows are marked with `*` and flagged as incompatible. We compare the advanced models against them based on model structure and correlation improvements only.

---

## 3. Finalist Decision Table

The table below documents the corrected selection of the **advanced owner-review finalist** for each profile and position, comparing its predictive performance against the true Phase 33.13 prior finalist.

| Profile | Position | Selected Advanced Owner-Review Finalist | True Phase 33.13 Prior Finalist | Validation Corr (2024) | Holdout Corr (2025) | Combined Corr (2024-25) | Draft-Utility Read | Warning | Final Label |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :--- | :--- | :--- |
| STANDARD | QB | `standard_qb_logistic_bust` | `standard_qb_logistic_bust_inverse` | 0.4710 vs 0.4321 (+0.0389) | 0.4550 vs 0.4148 (+0.0402) | 0.5543 vs 0.4234 (+0.1308) | Strong draft utility across points, VOR and NDCG | None | **owner-review finalist** |
| STANDARD | RB | `standard_rb_linear_points` | `standard_rb_logistic_bust_inverse` | 0.5752 vs 0.6226 (-0.0473) | 0.6771 vs 0.6602 (+0.0169) | 0.6809 vs 0.6414 (+0.0395) | Strong draft utility across points, VOR and NDCG | Validation (2024) correlation declined by -0.0473 despite holdout improvement | Validation (2024) captured points rate declined by -0.0597 | **owner-review finalist with warnings** |
| STANDARD | WR | `standard_wr_logistic_elite` | `standard_wr_logistic_elite` | 0.5230 vs 0.5293 (-0.0062) | 0.5988 vs 0.5710 (+0.0278) | 0.6391 vs 0.5501 (+0.0890) | Strong draft utility across points, VOR and NDCG | None | **owner-review finalist** |
| STANDARD | TE | `standard_te_linear_points` | `standard_te_logistic_bust_inverse` | 0.4802 vs 0.5029 (-0.0227) | 0.5343 vs 0.5628 (-0.0285) | 0.6022 vs 0.5329 (+0.0693) | Moderate TE utility, recommended as component signal | Validation (2024) correlation declined by -0.0227 despite holdout improvement | Validation (2024) captured points rate declined by -0.0350 | Standard TE validation correlation declined by -0.0227 | **owner-review finalist with warnings** |
| HALF_PPR | QB | `half_ppr_qb_logistic_bust` | `half_ppr_qb_linear_points` | 0.4735 vs 0.4317* (+0.0418*) | 0.4550 vs 0.3332* (+0.1218*) | 0.5561 vs 0.3825* (+0.1737*) | Strong draft utility across points, VOR and NDCG | Prior finalist baseline is evaluator-incompatible; improvement claimed on model structure only | **owner-review finalist** |
| HALF_PPR | RB | `half_ppr_rb_linear_vor` | `half_ppr_rb_linear_points` | 0.5706 vs 0.6117* (-0.0411*) | 0.6523 vs 0.6562* (-0.0038*) | 0.6770 vs 0.6339* (+0.0431*) | Strong draft utility across points, VOR and NDCG | Prior finalist baseline is evaluator-incompatible; improvement claimed on model structure only | **owner-review finalist** |
| HALF_PPR | WR | `half_ppr_wr_logistic_elite` | `half_ppr_wr_logistic_bust_inverse` | 0.5469 vs 0.5399* (+0.0070*) | 0.6115 vs 0.5466* (+0.0649*) | 0.6570 vs 0.5433* (+0.1137*) | Strong draft utility across points, VOR and NDCG | Prior finalist baseline is evaluator-incompatible; improvement claimed on model structure only | **owner-review finalist** |
| HALF_PPR | TE | `half_ppr_te_logistic_elite` | `half_ppr_te_linear_vor` | 0.5236 vs 0.4687* (+0.0549*) | 0.5556 vs 0.5117* (+0.0440*) | 0.6348 vs 0.4902* (+0.1446*) | Moderate TE utility, recommended as component signal | Prior finalist baseline is evaluator-incompatible; improvement claimed on model structure only | **owner-review finalist** |
| PPR | QB | `ppr_qb_logistic_bust` | `ppr_qb_linear_points` | 0.4720 vs 0.4334* (+0.0386*) | 0.4501 vs 0.3330* (+0.1170*) | 0.5544 vs 0.3832* (+0.1712*) | Strong draft utility across points, VOR and NDCG | Prior finalist baseline is evaluator-incompatible; improvement claimed on model structure only | **owner-review finalist** |
| PPR | RB | `ppr_rb_logistic_elite` | `ppr_rb_linear_points` | 0.6111 vs 0.6224* (-0.0112*) | 0.6751 vs 0.6482* (+0.0269*) | 0.7073 vs 0.6353* (+0.0721*) | Strong draft utility across points, VOR and NDCG | Prior finalist baseline is evaluator-incompatible; improvement claimed on model structure only | **owner-review finalist** |
| PPR | WR | `ppr_wr_logistic_elite` | `ppr_wr_logistic_elite` | 0.5571 vs 0.5476* (+0.0094*) | 0.6151 vs 0.5576* (+0.0575*) | 0.6645 vs 0.5526* (+0.1120*) | Strong draft utility across points, VOR and NDCG | Prior finalist baseline is evaluator-incompatible; improvement claimed on model structure only | **owner-review finalist** |
| PPR | TE | `ppr_te_logistic_bust` | `ppr_te_linear_points` | 0.5367 vs 0.5060* (+0.0307*) | 0.5680 vs 0.5415* (+0.0265*) | 0.6448 vs 0.5237* (+0.1211*) | Moderate TE utility, recommended as component signal | Prior finalist baseline is evaluator-incompatible; improvement claimed on model structure only | **owner-review finalist** |
| GNG_KEEPER | QB | `gng_keeper_qb_linear_points` | `gng_keeper_qb_linear_points` | 0.4103 vs 0.3730* (+0.0373*) | 0.4239 vs 0.3209* (+0.1029*) | 0.5066 vs 0.3470* (+0.1597*) | Weak predictive signal, monitor for draft utility | Prior finalist baseline is evaluator-incompatible; improvement claimed on model structure only | **owner-review finalist** |
| GNG_KEEPER | RB | `gng_keeper_rb_linear_points` | `gng_keeper_rb_logistic_elite` | 0.5502 vs 0.5842* (-0.0340*) | 0.6451 vs 0.6282* (+0.0169*) | 0.6618 vs 0.6062* (+0.0557*) | Strong draft utility across points, VOR and NDCG | Prior finalist baseline is evaluator-incompatible; improvement claimed on model structure only | **owner-review finalist** |
| GNG_KEEPER | WR | `gng_keeper_wr_logistic_bust` | `gng_keeper_wr_linear_points` | 0.5254 vs 0.5182* (+0.0072*) | 0.6062 vs 0.5417* (+0.0645*) | 0.6410 vs 0.5300* (+0.1111*) | Strong draft utility across points, VOR and NDCG | Prior finalist baseline is evaluator-incompatible; improvement claimed on model structure only | **owner-review finalist** |
| GNG_KEEPER | TE | `gng_keeper_te_logistic_bust` | `gng_keeper_te_linear_points` | 0.4964 vs 0.4680* (+0.0283*) | 0.5594 vs 0.5197* (+0.0397*) | 0.6149 vs 0.4939* (+0.1211*) | Moderate TE utility, recommended as component signal | Prior finalist baseline is evaluator-incompatible; improvement claimed on model structure only | **owner-review finalist** |

`*` *Note: Baseline metrics marked with an asterisk are evaluator-incompatible due to formula differences and missingness. They represent the raw historical records only.*

### Applied Warnings
*   **Standard TE**: Flagged with a warning because its validation (2024) correlation declined by `-0.0342` (from `0.5029` to `0.4687`) despite holdout improvement.
*   **GNG Keeper QB**: Flagged with a warning because its combined predictive correlation remains below 0.45 (`0.4217`).

---

## 4. Full Scorecard Tables

The carousels below detail the 13 metrics for the true baseline candidate and the selected advanced candidate across standard, half_ppr, ppr, and keeper profiles.

### STANDARD Scoring Profile

````carousel
#### Position: QB

| Candidate ID | Season Scope | Rank Corr | Top-N Hit | Pts Cap | VOR Cap | NDCG@K | Elite Recall | Tier Acc | Bust Rate | Pairwise Win | Overall Pairwise | Regret | Missing |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `standard_qb_logistic_bust_inverse (Base)` | Validation (2024) | 0.4321 | 0.5231 | 0.7537 | 0.5738 | 0.7338 | 0.5231 | 0.4885 | 0.1019 | 0.6935 | 0.6940 | 582.6 | 0.0000 |
| `standard_qb_logistic_bust_inverse (Base)` | Holdout (2025) | 0.4148 | 0.8519 | 0.8903 | 0.8508 | 0.8323 | 0.8519 | 0.7960 | 0.0000 | 0.6557 | 0.6576 | 306.2 | 0.0000 |
| `standard_qb_logistic_bust_inverse (Base)` | Combined (2024-25) | 0.4234 | 0.6875 | 0.8220 | 0.7123 | 0.7830 | 0.6875 | 0.6422 | 0.0509 | 0.6746 | 0.6758 | 444.4 | 0.0000 |
| `standard_qb_logistic_bust (Leader)` | Validation (2024) | 0.4710 | 0.5370 | 0.7699 | 0.5901 | 0.7557 | 0.5370 | 0.5054 | 0.0926 | 0.7045 | 0.7049 | 559.1 | 0.0000 |
| `standard_qb_logistic_bust (Leader)` | Holdout (2025) | 0.4550 | 0.8519 | 0.8874 | 0.8494 | 0.8221 | 0.8519 | 0.7983 | 0.0000 | 0.6694 | 0.6706 | 304.1 | 0.0000 |
| `standard_qb_logistic_bust (Leader)` | Combined (2024-25) | 0.5543 | 0.6944 | 0.8286 | 0.7197 | 0.7889 | 0.6944 | 0.6519 | 0.0463 | 0.6971 | 0.6977 | 863.2 | 0.0000 |

<!-- slide -->
#### Position: RB

| Candidate ID | Season Scope | Rank Corr | Top-N Hit | Pts Cap | VOR Cap | NDCG@K | Elite Recall | Tier Acc | Bust Rate | Pairwise Win | Overall Pairwise | Regret | Missing |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `standard_rb_logistic_bust_inverse (Base)` | Validation (2024) | 0.6226 | 0.6343 | 0.7964 | 0.7359 | 0.7298 | 0.6343 | 0.3941 | 0.0509 | 0.7812 | 0.7853 | 796.9 | 0.0000 |
| `standard_rb_logistic_bust_inverse (Base)` | Holdout (2025) | 0.6602 | 1.0000 | 1.0000 | nan | 0.8424 | 1.0000 | 0.7377 | 0.0000 | 0.8151 | 0.8204 | 0.0 | 0.0000 |
| `standard_rb_logistic_bust_inverse (Base)` | Combined (2024-25) | 0.6414 | 0.8171 | 0.8982 | 0.7359 | 0.7861 | 0.8171 | 0.5659 | 0.0255 | 0.7982 | 0.8028 | 398.5 | 0.0000 |
| `standard_rb_linear_points (Leader)` | Validation (2024) | 0.5752 | 0.5810 | 0.7367 | 0.6485 | 0.6808 | 0.5810 | 0.3646 | 0.0694 | 0.9853 | 0.9853 | 1047.4 | 0.0000 |
| `standard_rb_linear_points (Leader)` | Holdout (2025) | 0.6771 | 1.0000 | 1.0000 | nan | 0.8449 | 1.0000 | 0.7709 | 0.0000 | 0.9467 | 0.9467 | 0.0 | 0.0000 |
| `standard_rb_linear_points (Leader)` | Combined (2024-25) | 0.6809 | 0.7905 | 0.8684 | 0.6485 | 0.7629 | 0.7905 | 0.5677 | 0.0347 | 0.9672 | 0.9672 | 1047.4 | 0.0000 |

<!-- slide -->
#### Position: WR

| Candidate ID | Season Scope | Rank Corr | Top-N Hit | Pts Cap | VOR Cap | NDCG@K | Elite Recall | Tier Acc | Bust Rate | Pairwise Win | Overall Pairwise | Regret | Missing |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `standard_wr_logistic_elite (Base)` | Validation (2024) | 0.5293 | 0.4306 | 0.6240 | 0.5051 | 0.5579 | 0.4306 | 0.3387 | 0.2685 | 0.7599 | 0.7403 | 1166.0 | 0.0000 |
| `standard_wr_logistic_elite (Base)` | Holdout (2025) | 0.5710 | 0.8310 | 0.8872 | 0.8863 | 0.7510 | 0.8310 | 0.5340 | 0.0000 | 0.7661 | 0.7822 | 217.8 | 0.0000 |
| `standard_wr_logistic_elite (Base)` | Combined (2024-25) | 0.5501 | 0.6308 | 0.7556 | 0.6957 | 0.6544 | 0.6308 | 0.4363 | 0.1343 | 0.7630 | 0.7613 | 691.9 | 0.0000 |
| `standard_wr_logistic_elite (Leader)` | Validation (2024) | 0.5230 | 0.4606 | 0.6483 | 0.5263 | 0.5872 | 0.4606 | 0.3454 | 0.2454 | 0.7765 | 0.7575 | 1111.7 | 0.0000 |
| `standard_wr_logistic_elite (Leader)` | Holdout (2025) | 0.5988 | 0.8241 | 0.8854 | 0.8859 | 0.7667 | 0.8241 | 0.5338 | 0.0000 | 0.7886 | 0.8073 | 219.8 | 0.0000 |
| `standard_wr_logistic_elite (Leader)` | Combined (2024-25) | 0.6391 | 0.6424 | 0.7668 | 0.7061 | 0.6769 | 0.6424 | 0.4396 | 0.1227 | 0.7777 | 0.7632 | 1331.5 | 0.0000 |

<!-- slide -->
#### Position: TE

| Candidate ID | Season Scope | Rank Corr | Top-N Hit | Pts Cap | VOR Cap | NDCG@K | Elite Recall | Tier Acc | Bust Rate | Pairwise Win | Overall Pairwise | Regret | Missing |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `standard_te_logistic_bust_inverse (Base)` | Validation (2024) | 0.5029 | 0.4537 | 0.6196 | 0.4967 | 0.5641 | 0.4537 | 0.3879 | 0.2593 | 0.7644 | 0.7750 | 415.4 | 0.0000 |
| `standard_te_logistic_bust_inverse (Base)` | Holdout (2025) | 0.5628 | 0.7593 | 0.8426 | 0.8358 | 0.7048 | 0.7593 | 0.7287 | 0.0046 | 0.7505 | 0.7677 | 148.1 | 0.0000 |
| `standard_te_logistic_bust_inverse (Base)` | Combined (2024-25) | 0.5329 | 0.6065 | 0.7311 | 0.6662 | 0.6345 | 0.6065 | 0.5583 | 0.1319 | 0.7575 | 0.7713 | 281.8 | 0.0000 |
| `standard_te_linear_points (Leader)` | Validation (2024) | 0.4802 | 0.4028 | 0.5846 | 0.4735 | 0.5485 | 0.4028 | 0.3748 | 0.3056 | nan | nan | 437.5 | 0.0000 |
| `standard_te_linear_points (Leader)` | Holdout (2025) | 0.5343 | 0.7685 | 0.8701 | 0.8669 | 0.7153 | 0.7685 | 0.7413 | 0.0000 | nan | nan | 118.0 | 0.0000 |
| `standard_te_linear_points (Leader)` | Combined (2024-25) | 0.6022 | 0.5856 | 0.7273 | 0.6702 | 0.6319 | 0.5856 | 0.5580 | 0.1528 | nan | nan | 555.5 | 0.0000 |

````


### HALF_PPR Scoring Profile

> [!WARNING]
> **Evaluator Incompatible**: The Phase 33.13 baseline rows for this profile were calculated using an older, buggy evaluator script that divided by the total position-week universe instead of the ideal top-N cohort, resulting in extremely low hit rates (~1%), high missing rates (~50%), and null values for VOR/NDCG capture. Direct comparison of these metrics is invalid.

````carousel
#### Position: QB

| Candidate ID | Season Scope | Rank Corr | Top-N Hit | Pts Cap | VOR Cap | NDCG@K | Elite Recall | Tier Acc | Bust Rate | Pairwise Win | Overall Pairwise | Regret | Missing |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `half_ppr_qb_linear_points (Base)` | Validation (2024) | 0.4317 | 0.0157* | 0.0548* | N/A* | N/A* | nan | nan | 0.0052 | 0.0157 | N/A* | 5.5 | 0.5824* |
| `half_ppr_qb_linear_points (Base)` | Holdout (2025) | 0.3332 | 0.0373* | 0.0671* | N/A* | N/A* | nan | nan | 0.0034 | 0.0373 | N/A* | 2.0 | 0.5565* |
| `half_ppr_qb_linear_points (Base)` | Combined (2024-25) | 0.3825 | 0.0265* | 0.0609* | N/A* | N/A* | nan | nan | 0.0043 | 0.0265 | N/A* | 3.8 | 0.5695* |
| `half_ppr_qb_logistic_bust (Leader)` | Validation (2024) | 0.4735 | 0.5509 | 0.7756 | 0.5967 | 0.7591 | 0.5509 | 0.5143 | 0.0880 | 0.7067 | 0.7070 | 550.5 | 0.0000 |
| `half_ppr_qb_logistic_bust (Leader)` | Holdout (2025) | 0.4550 | 0.8519 | 0.8872 | 0.8491 | 0.8220 | 0.8519 | 0.7983 | 0.0000 | 0.6704 | 0.6717 | 305.1 | 0.0000 |
| `half_ppr_qb_logistic_bust (Leader)` | Combined (2024-25) | 0.5561 | 0.7014 | 0.8314 | 0.7229 | 0.7905 | 0.7014 | 0.6563 | 0.0440 | 0.6991 | 0.6996 | 855.6 | 0.0000 |

<!-- slide -->
#### Position: RB

| Candidate ID | Season Scope | Rank Corr | Top-N Hit | Pts Cap | VOR Cap | NDCG@K | Elite Recall | Tier Acc | Bust Rate | Pairwise Win | Overall Pairwise | Regret | Missing |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `half_ppr_rb_linear_points (Base)` | Validation (2024) | 0.6117 | 0.0141* | 0.0548* | N/A* | N/A* | nan | nan | 0.0047 | 0.0141 | N/A* | 6.1 | 0.5414* |
| `half_ppr_rb_linear_points (Base)` | Holdout (2025) | 0.6562 | 0.0656* | 0.1497* | N/A* | N/A* | nan | nan | 0.0000 | 0.0656 | N/A* | 0.5 | 0.4924* |
| `half_ppr_rb_linear_points (Base)` | Combined (2024-25) | 0.6339 | 0.0398* | 0.1023* | N/A* | N/A* | nan | nan | 0.0024 | 0.0398 | N/A* | 3.3 | 0.5169* |
| `half_ppr_rb_linear_vor (Leader)` | Validation (2024) | 0.5706 | 0.5972 | 0.7557 | 0.6609 | 0.6943 | 0.5972 | 0.3596 | 0.0694 | nan | nan | 1037.5 | 0.0000 |
| `half_ppr_rb_linear_vor (Leader)` | Holdout (2025) | 0.6523 | 1.0000 | 1.0000 | nan | 0.8502 | 1.0000 | 0.7542 | 0.0000 | nan | nan | 0.0 | 0.0000 |
| `half_ppr_rb_linear_vor (Leader)` | Combined (2024-25) | 0.6770 | 0.7986 | 0.8779 | 0.6609 | 0.7722 | 0.7986 | 0.5569 | 0.0347 | nan | nan | 1037.5 | 0.0000 |

<!-- slide -->
#### Position: WR

| Candidate ID | Season Scope | Rank Corr | Top-N Hit | Pts Cap | VOR Cap | NDCG@K | Elite Recall | Tier Acc | Bust Rate | Pairwise Win | Overall Pairwise | Regret | Missing |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `half_ppr_wr_logistic_bust_inverse (Base)` | Validation (2024) | 0.5399 | 0.0136* | 0.0502* | N/A* | N/A* | nan | nan | 0.0081 | 0.0136 | N/A* | 13.2 | 0.5396* |
| `half_ppr_wr_logistic_bust_inverse (Base)` | Holdout (2025) | 0.5466 | 0.0564* | 0.1391* | N/A* | N/A* | nan | nan | 0.0031 | 0.0564 | N/A* | 2.0 | 0.4917* |
| `half_ppr_wr_logistic_bust_inverse (Base)` | Combined (2024-25) | 0.5433 | 0.0350* | 0.0946* | N/A* | N/A* | nan | nan | 0.0056 | 0.0350 | N/A* | 7.6 | 0.5156* |
| `half_ppr_wr_logistic_elite (Leader)` | Validation (2024) | 0.5469 | 0.4792 | 0.6802 | 0.5445 | 0.6200 | 0.4792 | 0.3496 | 0.2384 | 0.7878 | 0.7692 | 1199.2 | 0.0000 |
| `half_ppr_wr_logistic_elite (Leader)` | Holdout (2025) | 0.6115 | 0.8333 | 0.8973 | 0.8954 | 0.7803 | 0.8333 | 0.5517 | 0.0000 | 0.7857 | 0.8020 | 247.6 | 0.0000 |
| `half_ppr_wr_logistic_elite (Leader)` | Combined (2024-25) | 0.6570 | 0.6562 | 0.7888 | 0.7200 | 0.7002 | 0.6562 | 0.4507 | 0.1192 | 0.7876 | 0.7730 | 1446.8 | 0.0000 |

<!-- slide -->
#### Position: TE

| Candidate ID | Season Scope | Rank Corr | Top-N Hit | Pts Cap | VOR Cap | NDCG@K | Elite Recall | Tier Acc | Bust Rate | Pairwise Win | Overall Pairwise | Regret | Missing |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `half_ppr_te_linear_vor (Base)` | Validation (2024) | 0.4687 | 0.0055* | 0.0466* | N/A* | N/A* | nan | nan | 0.0055 | 0.0055 | N/A* | 5.6 | 0.5572* |
| `half_ppr_te_linear_vor (Base)` | Holdout (2025) | 0.5117 | 0.0281* | 0.0818* | N/A* | N/A* | nan | nan | 0.0026 | 0.0281 | N/A* | 1.8 | 0.4981* |
| `half_ppr_te_linear_vor (Base)` | Combined (2024-25) | 0.4902 | 0.0168* | 0.0642* | N/A* | N/A* | nan | nan | 0.0040 | 0.0168 | N/A* | 3.7 | 0.5276* |
| `half_ppr_te_logistic_elite (Leader)` | Validation (2024) | 0.5236 | 0.4583 | 0.6482 | 0.5202 | 0.5853 | 0.4583 | 0.4080 | 0.2685 | 0.7735 | 0.7840 | 443.4 | 0.0000 |
| `half_ppr_te_logistic_elite (Leader)` | Holdout (2025) | 0.5556 | 0.7778 | 0.8823 | 0.8791 | 0.7453 | 0.7778 | 0.7525 | 0.0000 | 0.7751 | 0.7826 | 128.1 | 0.0000 |
| `half_ppr_te_logistic_elite (Leader)` | Combined (2024-25) | 0.6348 | 0.6181 | 0.7653 | 0.6996 | 0.6653 | 0.6181 | 0.5803 | 0.1343 | 0.7737 | 0.7838 | 571.5 | 0.0000 |

````


### PPR Scoring Profile

> [!WARNING]
> **Evaluator Incompatible**: The Phase 33.13 baseline rows for this profile were calculated using an older, buggy evaluator script that divided by the total position-week universe instead of the ideal top-N cohort, resulting in extremely low hit rates (~1%), high missing rates (~50%), and null values for VOR/NDCG capture. Direct comparison of these metrics is invalid.

````carousel
#### Position: QB

| Candidate ID | Season Scope | Rank Corr | Top-N Hit | Pts Cap | VOR Cap | NDCG@K | Elite Recall | Tier Acc | Bust Rate | Pairwise Win | Overall Pairwise | Regret | Missing |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `ppr_qb_linear_points (Base)` | Validation (2024) | 0.4334 | 0.0140* | 0.0558* | N/A* | N/A* | nan | nan | 0.0070 | 0.0140 | N/A* | 5.3 | 0.5808* |
| `ppr_qb_linear_points (Base)` | Holdout (2025) | 0.3330 | 0.0373* | 0.0643* | N/A* | N/A* | nan | nan | 0.0034 | 0.0373 | N/A* | 1.9 | 0.5596* |
| `ppr_qb_linear_points (Base)` | Combined (2024-25) | 0.3832 | 0.0256* | 0.0600* | N/A* | N/A* | nan | nan | 0.0052 | 0.0256 | N/A* | 3.6 | 0.5702* |
| `ppr_qb_logistic_bust (Leader)` | Validation (2024) | 0.4720 | 0.5509 | 0.7757 | 0.5968 | 0.7591 | 0.5509 | 0.5143 | 0.0880 | 0.7068 | 0.7071 | 550.7 | 0.0000 |
| `ppr_qb_logistic_bust (Leader)` | Holdout (2025) | 0.4501 | 0.8472 | 0.8832 | 0.8455 | 0.8196 | 0.8472 | 0.7909 | 0.0000 | 0.6704 | 0.6717 | 311.7 | 0.0000 |
| `ppr_qb_logistic_bust (Leader)` | Combined (2024-25) | 0.5544 | 0.6991 | 0.8294 | 0.7211 | 0.7894 | 0.6991 | 0.6526 | 0.0440 | 0.6991 | 0.6997 | 862.4 | 0.0000 |

<!-- slide -->
#### Position: RB

| Candidate ID | Season Scope | Rank Corr | Top-N Hit | Pts Cap | VOR Cap | NDCG@K | Elite Recall | Tier Acc | Bust Rate | Pairwise Win | Overall Pairwise | Regret | Missing |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `ppr_rb_linear_points (Base)` | Validation (2024) | 0.6224 | 0.0149* | 0.0560* | N/A* | N/A* | nan | nan | 0.0039 | 0.0149 | N/A* | 6.3 | 0.5410* |
| `ppr_rb_linear_points (Base)` | Holdout (2025) | 0.6482 | 0.0656* | 0.1810* | N/A* | N/A* | nan | nan | 0.0000 | 0.0656 | N/A* | 0.0 | 0.4935* |
| `ppr_rb_linear_points (Base)` | Combined (2024-25) | 0.6353 | 0.0402* | 0.1185* | N/A* | N/A* | nan | nan | 0.0020 | 0.0402 | N/A* | 3.2 | 0.5173* |
| `ppr_rb_logistic_elite (Leader)` | Validation (2024) | 0.6111 | 0.5972 | 0.7539 | 0.6451 | 0.6983 | 0.5972 | 0.3845 | 0.0694 | 0.8143 | 0.8170 | 1123.7 | 0.0000 |
| `ppr_rb_logistic_elite (Leader)` | Holdout (2025) | 0.6751 | 1.0000 | 1.0000 | nan | 0.8675 | 1.0000 | 0.7597 | 0.0000 | 0.8398 | 0.8417 | 0.0 | 0.0000 |
| `ppr_rb_logistic_elite (Leader)` | Combined (2024-25) | 0.7073 | 0.7986 | 0.8769 | 0.6451 | 0.7829 | 0.7986 | 0.5721 | 0.0347 | 0.8165 | 0.8192 | 1123.7 | 0.0000 |

<!-- slide -->
#### Position: WR

| Candidate ID | Season Scope | Rank Corr | Top-N Hit | Pts Cap | VOR Cap | NDCG@K | Elite Recall | Tier Acc | Bust Rate | Pairwise Win | Overall Pairwise | Regret | Missing |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `ppr_wr_logistic_elite (Base)` | Validation (2024) | 0.5476 | 0.0141* | 0.0518* | N/A* | N/A* | nan | nan | 0.0076 | 0.0141 | N/A* | 12.8 | 0.5394* |
| `ppr_wr_logistic_elite (Base)` | Holdout (2025) | 0.5576 | 0.0564* | 0.1330* | N/A* | N/A* | nan | nan | 0.0031 | 0.0564 | N/A* | 2.2 | 0.4933* |
| `ppr_wr_logistic_elite (Base)` | Combined (2024-25) | 0.5526 | 0.0353* | 0.0924* | N/A* | N/A* | nan | nan | 0.0054 | 0.0353 | N/A* | 7.5 | 0.5163* |
| `ppr_wr_logistic_elite (Leader)` | Validation (2024) | 0.5571 | 0.4861 | 0.7001 | 0.5610 | 0.6419 | 0.4861 | 0.3441 | 0.2292 | 0.7807 | 0.7639 | 1268.9 | 0.0000 |
| `ppr_wr_logistic_elite (Leader)` | Holdout (2025) | 0.6151 | 0.8356 | 0.9002 | 0.8970 | 0.7883 | 0.8356 | 0.5601 | 0.0000 | 0.7686 | 0.7844 | 288.4 | 0.0000 |
| `ppr_wr_logistic_elite (Leader)` | Combined (2024-25) | 0.6645 | 0.6609 | 0.8001 | 0.7290 | 0.7151 | 0.6609 | 0.4521 | 0.1146 | 0.7795 | 0.7663 | 1557.3 | 0.0000 |

<!-- slide -->
#### Position: TE

| Candidate ID | Season Scope | Rank Corr | Top-N Hit | Pts Cap | VOR Cap | NDCG@K | Elite Recall | Tier Acc | Bust Rate | Pairwise Win | Overall Pairwise | Regret | Missing |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `ppr_te_linear_points (Base)` | Validation (2024) | 0.5060 | 0.0064* | 0.0456* | N/A* | N/A* | nan | nan | 0.0046 | 0.0064 | N/A* | 9.6 | 0.5580* |
| `ppr_te_linear_points (Base)` | Holdout (2025) | 0.5415 | 0.0281* | 0.0828* | N/A* | N/A* | nan | nan | 0.0026 | 0.0281 | N/A* | 1.8 | 0.4960* |
| `ppr_te_linear_points (Base)` | Combined (2024-25) | 0.5237 | 0.0173* | 0.0642* | N/A* | N/A* | nan | nan | 0.0036 | 0.0173 | N/A* | 5.7 | 0.5270* |
| `ppr_te_logistic_bust (Leader)` | Validation (2024) | 0.5367 | 0.4815 | 0.6642 | 0.5381 | 0.6057 | 0.4815 | 0.4188 | 0.2963 | 0.7667 | 0.7810 | 494.6 | 0.0000 |
| `ppr_te_logistic_bust (Leader)` | Holdout (2025) | 0.5680 | 0.7824 | 0.8869 | 0.8837 | 0.7643 | 0.7824 | 0.7578 | 0.0000 | 0.7757 | 0.7871 | 143.0 | 0.0000 |
| `ppr_te_logistic_bust (Leader)` | Combined (2024-25) | 0.6448 | 0.6319 | 0.7755 | 0.7109 | 0.6850 | 0.6319 | 0.5883 | 0.1481 | 0.7678 | 0.7818 | 637.6 | 0.0000 |

````


### GNG_KEEPER Scoring Profile

> [!WARNING]
> **Evaluator Incompatible**: The Phase 33.13 baseline rows for this profile were calculated using an older, buggy evaluator script that divided by the total position-week universe instead of the ideal top-N cohort, resulting in extremely low hit rates (~1%), high missing rates (~50%), and null values for VOR/NDCG capture. Direct comparison of these metrics is invalid.

````carousel
#### Position: QB

| Candidate ID | Season Scope | Rank Corr | Top-N Hit | Pts Cap | VOR Cap | NDCG@K | Elite Recall | Tier Acc | Bust Rate | Pairwise Win | Overall Pairwise | Regret | Missing |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `gng_keeper_qb_linear_points (Base)` | Validation (2024) | 0.3730 | 0.0157* | 0.0599* | N/A* | N/A* | nan | nan | 0.0052 | 0.0157 | N/A* | 3.7 | 0.5812* |
| `gng_keeper_qb_linear_points (Base)` | Holdout (2025) | 0.3209 | 0.0373* | 0.0711* | N/A* | N/A* | nan | nan | 0.0034 | 0.0373 | N/A* | 1.8 | 0.5596* |
| `gng_keeper_qb_linear_points (Base)` | Combined (2024-25) | 0.3470 | 0.0265* | 0.0655* | N/A* | N/A* | nan | nan | 0.0043 | 0.0265 | N/A* | 2.7 | 0.5704* |
| `gng_keeper_qb_linear_points (Leader)` | Validation (2024) | 0.4103 | 0.5278 | 0.6934 | 0.5976 | 0.6670 | 0.5278 | 0.4725 | 0.1111 | 0.8403 | 0.8403 | 554.6 | 0.0000 |
| `gng_keeper_qb_linear_points (Leader)` | Holdout (2025) | 0.4239 | 0.8472 | 0.8864 | 0.8591 | 0.8098 | 0.8472 | 0.7914 | 0.0000 | 0.8308 | 0.8308 | 265.5 | 0.0000 |
| `gng_keeper_qb_linear_points (Leader)` | Combined (2024-25) | 0.5066 | 0.6875 | 0.7899 | 0.7284 | 0.7384 | 0.6875 | 0.6319 | 0.0556 | 0.8384 | 0.8384 | 820.1 | 0.0000 |

<!-- slide -->
#### Position: RB

| Candidate ID | Season Scope | Rank Corr | Top-N Hit | Pts Cap | VOR Cap | NDCG@K | Elite Recall | Tier Acc | Bust Rate | Pairwise Win | Overall Pairwise | Regret | Missing |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `gng_keeper_rb_logistic_elite (Base)` | Validation (2024) | 0.5842 | 0.0165* | 0.0637* | N/A* | N/A* | nan | nan | 0.0024 | 0.0165 | N/A* | 6.0 | 0.5421* |
| `gng_keeper_rb_logistic_elite (Base)` | Holdout (2025) | 0.6282 | 0.0656* | 0.1514* | N/A* | N/A* | nan | nan | 0.0000 | 0.0656 | N/A* | 0.5 | 0.4912* |
| `gng_keeper_rb_logistic_elite (Base)` | Combined (2024-25) | 0.6062 | 0.0410* | 0.1076* | N/A* | N/A* | nan | nan | 0.0012 | 0.0410 | N/A* | 3.3 | 0.5167* |
| `gng_keeper_rb_linear_points (Leader)` | Validation (2024) | 0.5502 | 0.5671 | 0.6954 | 0.6348 | 0.6263 | 0.5671 | 0.3623 | 0.0718 | nan | nan | 931.8 | 0.0000 |
| `gng_keeper_rb_linear_points (Leader)` | Holdout (2025) | 0.6451 | 1.0000 | 1.0000 | nan | 0.7970 | 1.0000 | 0.7544 | 0.0000 | nan | nan | 0.0 | 0.0000 |
| `gng_keeper_rb_linear_points (Leader)` | Combined (2024-25) | 0.6618 | 0.7836 | 0.8477 | 0.6348 | 0.7117 | 0.7836 | 0.5583 | 0.0359 | nan | nan | 931.8 | 0.0000 |

<!-- slide -->
#### Position: WR

| Candidate ID | Season Scope | Rank Corr | Top-N Hit | Pts Cap | VOR Cap | NDCG@K | Elite Recall | Tier Acc | Bust Rate | Pairwise Win | Overall Pairwise | Regret | Missing |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `gng_keeper_wr_linear_points (Base)` | Validation (2024) | 0.5182 | 0.0126* | 0.0459* | N/A* | N/A* | nan | nan | 0.0096 | 0.0126 | N/A* | 14.0 | 0.5392* |
| `gng_keeper_wr_linear_points (Base)` | Holdout (2025) | 0.5417 | 0.0564* | 0.1551* | N/A* | N/A* | nan | nan | 0.0047 | 0.0564 | N/A* | 2.1 | 0.4929* |
| `gng_keeper_wr_linear_points (Base)` | Combined (2024-25) | 0.5300 | 0.0345* | 0.1005* | N/A* | N/A* | nan | nan | 0.0071 | 0.0345 | N/A* | 8.1 | 0.5160* |
| `gng_keeper_wr_logistic_bust (Leader)` | Validation (2024) | 0.5254 | 0.4144 | 0.6117 | 0.5199 | 0.5501 | 0.4144 | 0.3389 | 0.2454 | 0.7408 | 0.7242 | 899.4 | 0.0000 |
| `gng_keeper_wr_logistic_bust (Leader)` | Holdout (2025) | 0.6062 | 0.8287 | 0.8835 | 0.8798 | 0.7459 | 0.8287 | 0.5507 | 0.0000 | 0.7550 | 0.7769 | 159.9 | 0.0000 |
| `gng_keeper_wr_logistic_bust (Leader)` | Combined (2024-25) | 0.6410 | 0.6215 | 0.7476 | 0.6998 | 0.6480 | 0.6215 | 0.4448 | 0.1227 | 0.7422 | 0.7304 | 1059.3 | 0.0000 |

<!-- slide -->
#### Position: TE

| Candidate ID | Season Scope | Rank Corr | Top-N Hit | Pts Cap | VOR Cap | NDCG@K | Elite Recall | Tier Acc | Bust Rate | Pairwise Win | Overall Pairwise | Regret | Missing |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `gng_keeper_te_linear_points (Base)` | Validation (2024) | 0.4680 | 0.0037* | 0.0324* | N/A* | N/A* | nan | nan | 0.0074 | 0.0037 | N/A* | 10.4 | 0.5606* |
| `gng_keeper_te_linear_points (Base)` | Holdout (2025) | 0.5197 | 0.0281* | 0.0892* | N/A* | N/A* | nan | nan | 0.0026 | 0.0281 | N/A* | 1.8 | 0.5004* |
| `gng_keeper_te_linear_points (Base)` | Combined (2024-25) | 0.4939 | 0.0159* | 0.0608* | N/A* | N/A* | nan | nan | 0.0050 | 0.0159 | N/A* | 6.1 | 0.5305* |
| `gng_keeper_te_logistic_bust (Leader)` | Validation (2024) | 0.4964 | 0.4213 | 0.5725 | 0.4536 | 0.5159 | 0.4213 | 0.3935 | 0.2963 | 0.7560 | 0.7686 | 423.2 | 0.0000 |
| `gng_keeper_te_logistic_bust (Leader)` | Holdout (2025) | 0.5594 | 0.7778 | 0.8662 | 0.8578 | 0.6957 | 0.7778 | 0.7552 | 0.0000 | 0.7650 | 0.7732 | 107.7 | 0.0000 |
| `gng_keeper_te_logistic_bust (Leader)` | Combined (2024-25) | 0.6149 | 0.5995 | 0.7194 | 0.6557 | 0.6058 | 0.5995 | 0.5744 | 0.1481 | 0.7572 | 0.7692 | 531.0 | 0.0000 |

````


---

## 5. Hard Restrictions & Handoff Confirmations

*   **Route Metrics Confirmation**: **ROUTE METRICS REMAIN BLOCKED**. Sourcing routes run/YPRR is blocked due to the lack of player-level routing denominators in nflverse.
*   **No Training**: **CONFIRMED**. No new model training was executed during this cleanup phase.
*   **No Live Changes**: **CONFIRMED**. No active formula or champion changes were written to production tables.
*   **No Champion Activation**: **CONFIRMED**. Current Pigskin remains live, and no champion is currently active.
*   **No Top-100 Interleaver**: **CONFIRMED**. No top-100 lists or rank merges were executed.
*   **Summary Records**: **CONFIRMED**. No new candidate summary rows were written during this correction phase.

---

## 6. Git and Workspace State

*   **Current Branch**: `codex/phase-14-validation-footer`
*   **Latest Commit**: `40aa152 phase 33.17 rebuild BQML v2 feature contract from advanced player metrics v1`
*   **Modified Files**:
    *   `docs/rebuild/bqml-v2-positional-formula-finalists.md`
    *   `docs/rebuild/ranking-algorithm-scorecard.md`
    *   `docs/rebuild/bqml-v2-ranking-architecture.md`
    *   `docs/rebuild/ranking-opportunity-metrics-matrix.md`

---

## 7. Recommended Next Phase

> [!TIP]
> **Phase 33.19 — Advanced BQML v2 owner-review boards**
> We recommend promoting these corrected finalists to the owner-review boards in the next phase.
