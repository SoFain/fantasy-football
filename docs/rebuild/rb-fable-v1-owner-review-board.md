# RB Fable v1 Owner Review Board — Top 30 with Current-Team Context

Fable v1 scores come from 2025 source metrics (Phase 34.4 formula). Standard ranks come from the live 2026 preseason board. Sleeper context was fetched 2026-07-10 and is **review evidence only** — it never touches the Fable score. Flags: TRUSTED = current team matches the score's source context; ROLE REVIEW = team changed since the source season; INJURY = active Sleeper injury designation; DEPTH = Sleeper lists the player below RB1; NO ROW = Fable cannot rank him.

| Fable | Std | Player | Sleeper team | Flag | Recommendation |
|---:|---:|---|---|---|---|
| 1 | 1 | Christian McCaffrey | SF | TRUSTED | Consensus RB1 on both boards. |
| 2 | 4 | Jonathan Taylor | IND | TRUSTED | Trust the Fable rise; elite volume and TD blend. |
| 3 | 2 | Bijan Robinson | ATL | TRUSTED | Aligned. |
| 4 | 3 | Jahmyr Gibbs | DET | TRUSTED | Aligned. |
| 5 | 5 | Devon Achane | MIA | INJURY (Questionable) | Same rank on both boards; just confirm health before drafting. |
| 6 | 7 | James Cook | BUF | TRUSTED | Aligned. |
| 7 | 9 | Javonte Williams | DAL | TRUSTED | Aligned; 2025 Dallas role now fully priced in. |
| 8 | 20 | Derrick Henry | BAL | TRUSTED | **The decision player.** Fable's +12 disagreement is context-clean: same team, healthy, RB1, elite volume. This is the age-forgiveness refinement making a real call against the Standard board. |
| 9 | 13 | Josh Jacobs | GB | TRUSTED | Trust the modest Fable rise. |
| 10 | 6 | Kyren Williams | LAR | TRUSTED | Formula opinion (volume ceiling), not a data problem. |
| 11 | 8 | Chase Brown | CIN | TRUSTED | Aligned within 3. |
| 12 | 10 | Saquon Barkley | PHI | TRUSTED | Down-year efficiency priced; aligned within 2. |
| 13 | 14 | Travis Etienne | NO | ROLE REVIEW (JAX→NO) | Score built on Jaguars usage, but Sleeper lists him Saints RB1 and both boards agree within 1. Low-stakes review. |
| 14 | 11 | Omarion Hampton | LAC | TRUSTED | Availability 0.53 from rookie injury drags him; consider mentally crediting a healthy season. |
| 15 | 12 | Ashton Jeanty | LV | TRUSTED | Volume real, efficiency ugly; formula opinion. |
| 16 | 18 | Cam Skattebo | NYG | INJURY (Questionable) | 8-game rookie sample plus injury tag; verify health. |
| 17 | 15 | D'Andre Swift | CHI | TRUSTED | Aligned. |
| 18 | 19 | Jaylen Warren | PIT | TRUSTED | Aligned; note he is listed ahead of Dowdle. |
| 19 | 22 | Rico Dowdle | PIT | ROLE REVIEW (CAR→PIT, depth RB2) | **Discount.** Fable 19 assumes his Carolina lead role; Sleeper lists him RB2 behind Warren. The clearest stale score on the board. |
| 20 | 17 | Bucky Irving | TB | INJURY (Questionable) | Injury-hit 2025 already suppresses his score; if healthy, his strong 2024 argues Standard 17 is fairer. |
| 21 | 30 | Zach Charbonnet | SEA | INJURY (Questionable, depth RB2) | Fable's +9 rise needs review: red-zone role is real, but he is Questionable and not listed SEA RB1. |
| 22 | 16 | Breece Hall | NYJ | TRUSTED | Fable's fade is a genuine formula opinion: bottom-quartile red-zone usage in a TD-driven format. |
| 23 | 21 | Quinshon Judkins | CLE | INJURY (Questionable) | Aligned within 2; confirm health. |
| 24 | 25 | Kenneth Walker | KC | ROLE REVIEW (SEA→KC) | Listed Chiefs RB1 and both boards agree within 1; low-stakes review. |
| 25 | 31 | Kenneth Gainwell | TB | ROLE REVIEW (PIT→TB, depth RB2) | **Discount.** The Pittsburgh receiving role that produced his score does not exist in Tampa. |
| 26 | 28 | TreVeyon Henderson | NE | TRUSTED | Efficiency standout; aligned. |
| 27 | 23 | J.K. Dobbins | DEN | TRUSTED | Availability-driven fade; formula opinion. |
| 28 | 33 | Tyrone Tracy | NYG | DEPTH (RB2) | Marginal top-30 entry now listed behind Skattebo; treat Standard 33 as fairer. |
| 29 | 24 | Rhamondre Stevenson | NE | DEPTH (RB2) | Weak score plus depth warning; nothing to defend. |
| 30 | 34 | Woody Marks | HOU | DEPTH (RB2) | Marginal entry, listed RB2; note David Montgomery is now also in Houston. |
| 34 | 26 | Aaron Jones | MIN | TRUSTED | Fable's fade is the age penalty working on a moderate-volume 31-year-old — the Mostert pattern the backtests validated. |
| 35 | 27 | Tony Pollard | TEN | TRUSTED | Near-bottom red-zone role; the fade is defensible in Standard scoring. |
| — | 29 | James Conner | ARI | NO ROW (Questionable, depth RB3) | Fable cannot rank him (no qualified 2025 season), but Sleeper listing him RB3 behind Benson suggests the gap is less costly than feared. |

## What the context layer proved

1. **The big Fable fades are trustworthy.** Henry, Hall, Jones, and Pollard are all current-team, active-roster formula opinions. Nothing stale is propping them up.
2. **The suspect calls are all Fable risers.** Dowdle (+3), Gainwell (+6), and Charbonnet (+9) each lose their case on current depth-chart or injury evidence. The formula's optimism is where staleness bites.
3. **The Conner gap shrank.** He is Arizona's listed RB3 and Questionable; Fable's inability to rank him is a smaller liability than Phase 34.5 assumed.

## If you want a context modifier later (design note, not implemented)

Keep `rb_fable_01_score` pure and validated. If a context-aware display is wanted, compute a separate `context_adjusted_view_score` in the review layer only: scale the **opportunity component only** by a team-continuity/depth factor (opportunity is role-dependent; efficiency travels with the player), cap any boost at zero (context should only discount, never inflate), and show both numbers side by side. Be explicit that this overlay can never be backtested — no historical Sleeper snapshots exist — so it must stay a labeled display adjustment, not part of the champion-evaluation score. Start archiving dated Sleeper snapshots now so a future season can validate it honestly.

## Recommendation

Approve this board for the owner-review conversation. Keep Current Pigskin live. The single decision worth debating today is Derrick Henry at Fable 8 vs Standard 20 — it is context-clean, backtest-supported, and the largest gap on the board.
