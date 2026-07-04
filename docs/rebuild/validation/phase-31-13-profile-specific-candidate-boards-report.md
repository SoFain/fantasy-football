# Phase 31.13 Profile Specific Candidate Boards Report

Date: 2026-07-04

Final decision: **PROFILE SPECIFIC CANDIDATE BOARDS READY WITH WARNINGS**

## Scope

Phase 31.13 generated Pigskin ranking candidate boards one scoring profile at a time:

- `ppr`
- `half_ppr`
- `standard`
- `gng_keeper`

The work used `league_type_id=redraft` and `roster_format_id=one_qb`.

Only the transient table `analytics_pigskin_rankings_candidates` was written. No final LLM ranking generation was run. No deployment was run.

## Git State

Starting git state:

- Latest commit before this phase: `fd2c00c Materialize GNG Keeper fantasy points by profile`
- No staged files at start.
- Historical validation backlog remained untracked.
- No pending migrations.

Files changed in this phase:

- `docs/rebuild/validation/phase-31-13-profile-specific-candidate-boards-report.md`

## Pre Checks

Commands run:

```powershell
git status --short --untracked-files=all
git log -10 --oneline
.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending
```

Migration result:

- No pending migrations.

## Profile Point Availability

Read-only check against `analytics_player_fantasy_points_by_profile` confirmed 2025 QB/RB/WR/TE rows for all four profiles.

| scoring_profile_id | QB row_count | RB row_count | WR row_count | TE row_count |
| --- | ---: | ---: | ---: | ---: |
| `ppr` | 664 | 1,578 | 2,500 | 1,301 |
| `half_ppr` | 664 | 1,578 | 2,500 | 1,301 |
| `standard` | 664 | 1,578 | 2,500 | 1,301 |
| `gng_keeper` | 664 | 1,578 | 2,500 | 1,301 |

Average 2025 fantasy points by profile and position:

| scoring_profile_id | QB avg | RB avg | WR avg | TE avg |
| --- | ---: | ---: | ---: | ---: |
| `ppr` | 14.675 | 7.635 | 6.677 | 5.575 |
| `half_ppr` | 14.668 | 6.911 | 5.477 | 4.472 |
| `standard` | 14.661 | 6.187 | 4.277 | 3.369 |
| `gng_keeper` | 11.315 | 3.726 | 2.889 | 2.673 |

## Active Final Rankings Before Candidate Work

Read-only check against `analytics_pigskin_rankings`:

- Active final ranking row_count: 285
- Active profiles present: `ppr` only

| scoring_profile_id | position | row_count | rank range |
| --- | --- | ---: | --- |
| `ppr` | QB | 45 | 1 to 45 |
| `ppr` | RB | 80 | 1 to 80 |
| `ppr` | WR | 100 | 1 to 100 |
| `ppr` | TE | 60 | 1 to 60 |

Trey McBride final ranking before candidate work:

- `scoring_profile_id=ppr`
- `position=TE`
- `rank=1`
- `tier=elite`
- `ranking_score=98.0`

## Candidate SQL Dry Runs

The candidate SQL dry-run passed for all profiles. Each dry-run used the selected `scoring_profile_id`, used `avg_profile_points`, and included the `missing selected scoring profile sample` risk flag.

| scoring_profile_id | label | estimated bytes | avg_profile_points used | missing-profile flag present |
| --- | --- | ---: | --- | --- |
| `ppr` | PPR | 10,166,129 | yes | yes |
| `half_ppr` | Half PPR | 10,166,129 | yes | yes |
| `standard` | Standard | 10,166,129 | yes | yes |
| `gng_keeper` | GNG Keeper | 10,166,129 | yes | yes |

## Candidate Board Materialization

Each profile was materialized through `src.materialize.materialize_pigskin_rankings(...)` with:

- `dry_run=False`
- selected `scoring_profile_id`
- `league_type_id=redraft`
- `roster_format_id=one_qb`

This path creates or replaces only `analytics_pigskin_rankings_candidates`. It does not call Gemini and does not write `analytics_pigskin_rankings`.

### PPR Candidate Board

Materialization job ID:

- `d80b2455-a07d-4767-b1dc-4063ed726f5f`

Profile purity:

- distinct profile count: 1
- profiles: `ppr`

| position | row_count | rank range |
| --- | ---: | --- |
| QB | 128 | 1 to 128 |
| RB | 202 | 1 to 202 |
| WR | 393 | 1 to 393 |
| TE | 213 | 1 to 213 |

Top 20 by position, shown as `rank. player (avg_profile_points)`:

- QB: Josh Allen (24.289), Drake Maye (21.762), Patrick Mahomes (21.691), Brock Purdy (22.153), Jalen Hurts (19.941), Trevor Lawrence (21.54), Daniel Jones (18.957), Bo Nix (18.991), Caleb Williams (19.54), Matthew Stafford (21.905), Justin Herbert (19.68), Jayden Daniels (17.469), Dak Prescott (19.516), Lamar Jackson (17.912), Jordan Love (16.476), Jaxson Dart (18.113), Jared Goff (19.004), Kyler Murray (17.156), C.J. Stroud (16.039), Tyler Shough (15.633)
- RB: Christian McCaffrey (24.506), Bijan Robinson (22.047), Jahmyr Gibbs (21.7), De'Von Achane (20.175), Jonathan Taylor (21.312), Chase Brown (16.506), Javonte Williams (15.425), Saquon Barkley (14.519), Kyren Williams (15.724), Omarion Hampton (15.078), Ashton Jeanty (14.535), James Cook (18.129), Josh Jacobs (16.073), Travis Etienne (14.935), Cam Skattebo (15.962), Bucky Irving (14.05), D'Andre Swift (14.538), Breece Hall (13.229), Jaylen Warren (13.569), Derrick Henry (16.794)
- WR: Jaxon Smith-Njigba (21.288), Puka Nacua (23.563), Ja'Marr Chase (19.725), Amon-Ra St. Brown (19.059), Drake London (16.825), Garrett Wilson (14.214), Rashee Rice (18.513), Chris Olave (16.875), A.J. Brown (14.687), George Pickens (17.053), Justin Jefferson (11.853), Zay Flowers (14.665), CeeDee Lamb (15.454), Davante Adams (15.921), Nico Collins (15.08), Wan'Dale Robinson (13.619), Tetairoa McMillan (12.553), Malik Nabers (14.275), Rome Odunze (12.175), DeVonta Smith (11.871)
- TE: Trey McBride (18.582), Brock Bowers (14.517), Tucker Kraft (14.65), George Kittle (14.682), Kyle Pitts (12.4), Tyler Warren (11.088), Sam LaPorta (11.878), Dallas Goedert (12.34), Travis Kelce (11.247), Hunter Henry (10.518), Dalton Schultz (10.453), Juwan Johnson (10.818), Colston Loveland (10.319), Jake Ferguson (11.182), Brenton Strange (9.833), Harold Fannin Jr. (11.775), Cade Otton (8.147), Theo Johnson (8.52), Mason Taylor (6.685), Oronde Gadsden II (8.893)

Trey McBride candidate row:

- rank 1
- player_id `00-0037744`
- ranking_score `60.04`
- avg_profile_points `18.582`
- weekly_rows `17`

Weekly-zero-with-historical-metrics diagnostic:

- warning count: 82
- first examples: Odell Beckham Jr., Ben Roethlisberger, Jack Doyle, Jalen Richard, Le'Veon Bell

### Half PPR Candidate Board

Materialization job ID:

- `04d2ebd3-4cb1-4848-bc3b-54b6dd87243c`

Profile purity:

- distinct profile count: 1
- profiles: `half_ppr`

| position | row_count | rank range |
| --- | ---: | --- |
| QB | 128 | 1 to 128 |
| RB | 202 | 1 to 202 |
| WR | 393 | 1 to 393 |
| TE | 213 | 1 to 213 |

Top 20 by position:

- QB: Josh Allen (24.289), Drake Maye (21.733), Patrick Mahomes (21.656), Brock Purdy (22.153), Jalen Hurts (19.941), Trevor Lawrence (21.54), Daniel Jones (18.957), Bo Nix (18.991), Caleb Williams (19.481), Matthew Stafford (21.905), Justin Herbert (19.68), Jayden Daniels (17.469), Dak Prescott (19.516), Lamar Jackson (17.912), Jordan Love (16.476), Jaxson Dart (18.113), Jared Goff (19.004), Kyler Murray (17.156), C.J. Stroud (16.039), Tyler Shough (15.633)
- RB: Christian McCaffrey (21.506), Bijan Robinson (19.724), Jahmyr Gibbs (19.435), De'Von Achane (18.081), Jonathan Taylor (19.959), Chase Brown (14.476), Javonte Williams (14.331), Saquon Barkley (13.362), Kyren Williams (14.665), Omarion Hampton (13.3), Ashton Jeanty (12.918), James Cook (17.159), Josh Jacobs (14.873), Travis Etienne (13.876), Cam Skattebo (14.462), Bucky Irving (12.55), D'Andre Swift (13.475), Breece Hall (12.104), Jaylen Warren (12.319), Derrick Henry (16.353)
- WR: Jaxon Smith-Njigba (17.788), Puka Nacua (19.531), Ja'Marr Chase (15.819), Amon-Ra St. Brown (15.618), Drake London (13.992), Garrett Wilson (11.643), Rashee Rice (15.2), Chris Olave (13.75), A.J. Brown (12.087), Justin Jefferson (9.382), George Pickens (14.318), Zay Flowers (12.135), Davante Adams (13.779), CeeDee Lamb (12.569), Nico Collins (12.713), Wan'Dale Robinson (10.744), Tetairoa McMillan (10.494), Malik Nabers (12.025), Rome Odunze (10.342), DeVonta Smith (9.606)
- TE: Trey McBride (14.876), Brock Bowers (11.85), Tucker Kraft (12.65), George Kittle (12.091), Kyle Pitts (9.812), Tyler Warren (8.853), Sam LaPorta (9.656), Dallas Goedert (10.34), Travis Kelce (9.012), Hunter Henry (8.753), Dalton Schultz (8.041), Juwan Johnson (8.553), Colston Loveland (8.506), Jake Ferguson (8.771), Brenton Strange (7.917), Harold Fannin Jr. (9.525), Cade Otton (6.18), Theo Johnson (7.02), Mason Taylor (4.992), Oronde Gadsden II (7.26)

Trey McBride candidate row:

- rank 1
- player_id `00-0037744`
- ranking_score `58.55`
- avg_profile_points `14.876`
- weekly_rows `17`

Profile-specific point change versus PPR is visible, especially RB, WR, and TE reception-heavy profiles. Trey McBride moved from PPR `18.582` to Half PPR `14.876`.

Weekly-zero-with-historical-metrics diagnostic:

- warning count: 82

### Standard Candidate Board

Materialization job ID:

- `68336d69-d53d-403c-852e-2611febcf3cd`

Profile purity:

- distinct profile count: 1
- profiles: `standard`

| position | row_count | rank range |
| --- | ---: | --- |
| QB | 128 | 1 to 128 |
| RB | 202 | 1 to 202 |
| WR | 393 | 1 to 393 |
| TE | 213 | 1 to 213 |

Top 20 by position:

- QB: Josh Allen (24.289), Drake Maye (21.704), Patrick Mahomes (21.62), Brock Purdy (22.153), Jalen Hurts (19.941), Trevor Lawrence (21.54), Daniel Jones (18.957), Bo Nix (18.991), Caleb Williams (19.422), Matthew Stafford (21.905), Justin Herbert (19.68), Jayden Daniels (17.469), Dak Prescott (19.516), Lamar Jackson (17.912), Jordan Love (16.476), Jaxson Dart (18.113), Jared Goff (19.004), Kyler Murray (17.156), C.J. Stroud (16.039), Tyler Shough (15.633)
- RB: Christian McCaffrey (18.506), Bijan Robinson (17.4), Jahmyr Gibbs (17.171), Jonathan Taylor (18.606), De'Von Achane (15.988), Chase Brown (12.447), Javonte Williams (13.238), Kyren Williams (13.606), Saquon Barkley (12.206), Omarion Hampton (11.522), James Cook (16.188), Ashton Jeanty (11.3), Josh Jacobs (13.673), Travis Etienne (12.818), Cam Skattebo (12.962), Bucky Irving (11.05), D'Andre Swift (12.413), Breece Hall (10.979), Jaylen Warren (11.069), Derrick Henry (15.912)
- WR: Jaxon Smith-Njigba (14.288), Puka Nacua (15.5), Amon-Ra St. Brown (12.176), Ja'Marr Chase (11.913), Drake London (11.158), Garrett Wilson (9.071), Rashee Rice (11.888), Chris Olave (10.625), A.J. Brown (9.487), Justin Jefferson (6.912), George Pickens (11.582), Zay Flowers (9.606), Davante Adams (11.636), CeeDee Lamb (9.685), Nico Collins (10.347), Tetairoa McMillan (8.435), Wan'Dale Robinson (7.869), Malik Nabers (9.775), Rome Odunze (8.508), DeVonta Smith (7.341)
- TE: Trey McBride (11.171), Brock Bowers (9.183), Tucker Kraft (10.65), George Kittle (9.5), Kyle Pitts (7.224), Tyler Warren (6.618), Sam LaPorta (7.433), Dallas Goedert (8.34), Travis Kelce (6.776), Hunter Henry (6.988), Dalton Schultz (5.629), Juwan Johnson (6.288), Colston Loveland (6.694), Brenton Strange (6.0), Jake Ferguson (6.359), Harold Fannin Jr. (7.275), Cade Otton (4.213), Theo Johnson (5.52), Mason Taylor (3.3), Oronde Gadsden II (5.627)

Trey McBride candidate row:

- rank 1
- player_id `00-0037744`
- ranking_score `57.07`
- avg_profile_points `11.171`
- weekly_rows `17`

Profile-specific point change versus PPR and Half PPR is visible. Trey McBride moved from PPR `18.582` to Half PPR `14.876` to Standard `11.171`.

Weekly-zero-with-historical-metrics diagnostic:

- warning count: 82

### GNG Keeper Candidate Board

Materialization job ID:

- `e024b268-35cd-440c-a058-0452f98ad2b3`

Profile purity:

- distinct profile count: 1
- profiles: `gng_keeper`

| position | row_count | rank range |
| --- | ---: | --- |
| QB | 128 | 1 to 128 |
| RB | 202 | 1 to 202 |
| WR | 393 | 1 to 393 |
| TE | 213 | 1 to 213 |

Top 20 by position:

- QB: Josh Allen (19.095), Drake Maye (16.768), Brock Purdy (18.58), Patrick Mahomes (16.309), Jalen Hurts (15.895), Trevor Lawrence (17.265), Daniel Jones (14.891), Bo Nix (14.58), Matthew Stafford (19.069), Caleb Williams (14.955), Jayden Daniels (12.623), Justin Herbert (14.779), Dak Prescott (15.301), Lamar Jackson (13.995), Jordan Love (12.705), Jaxson Dart (13.851), Jared Goff (15.475), Aaron Rodgers (12.164), Kyler Murray (12.432), C.J. Stroud (12.156)
- RB: Christian McCaffrey (11.602), Bijan Robinson (9.754), Jahmyr Gibbs (11.133), Jonathan Taylor (11.948), De'Von Achane (9.514), Chase Brown (7.714), Javonte Williams (8.439), Saquon Barkley (7.139), Kyren Williams (8.407), Omarion Hampton (6.964), Ashton Jeanty (6.961), James Cook (9.634), Josh Jacobs (9.069), Travis Etienne (8.092), Cam Skattebo (8.635), Bucky Irving (6.16), D'Andre Swift (7.427), Breece Hall (5.955), Jaylen Warren (6.477), Derrick Henry (9.841)
- WR: Jaxon Smith-Njigba (9.233), Amon-Ra St. Brown (8.576), Ja'Marr Chase (8.127), Puka Nacua (10.287), Garrett Wilson (6.714), Drake London (7.697), Rashee Rice (8.78), Chris Olave (7.525), A.J. Brown (6.515), Justin Jefferson (4.176), George Pickens (7.633), Davante Adams (9.111), Zay Flowers (6.125), CeeDee Lamb (5.858), Nico Collins (6.765), Tetairoa McMillan (5.68), Wan'Dale Robinson (5.197), Malik Nabers (6.61), Rome Odunze (5.937), DeVonta Smith (4.689)
- TE: Trey McBride (9.021), Brock Bowers (7.373), Tucker Kraft (8.16), George Kittle (7.645), Kyle Pitts (5.501), Tyler Warren (5.047), Sam LaPorta (5.507), Dallas Goedert (7.176), Travis Kelce (5.111), Hunter Henry (5.336), Dalton Schultz (4.334), Juwan Johnson (4.509), Colston Loveland (5.115), Jake Ferguson (5.685), Brenton Strange (4.45), Harold Fannin Jr. (5.835), Cade Otton (3.105), Theo Johnson (4.308), Mason Taylor (2.612), Oronde Gadsden II (3.951)

Trey McBride candidate row:

- rank 1
- player_id `00-0037744`
- ranking_score `56.21`
- avg_profile_points `9.021`
- weekly_rows `17`

GNG profile points were present and lower overall than PPR because GNG Keeper uses different passing, receiving, kicking, DST, and turnover settings. TE premium behavior is reflected in the profile points: Trey McBride stays TE rank 1 with `avg_profile_points=9.021`, while WR reception scoring is lower than PPR.

Weekly-zero-with-historical-metrics diagnostic:

- warning count: 82

## Final Restored Candidate Board State

The transient candidate board was restored to `ppr` at the end of the phase.

Restore job ID:

- `ab67a14d-53f2-41d1-ab6e-9a044937dfee`

Final profile purity:

- distinct profile count: 1
- profiles: `ppr`

| position | row_count | rank range |
| --- | ---: | --- |
| QB | 128 | 1 to 128 |
| RB | 202 | 1 to 202 |
| WR | 393 | 1 to 393 |
| TE | 213 | 1 to 213 |

Final Trey McBride candidate row:

- `scoring_profile_id=ppr`
- `rank=1`
- `player_id=00-0037744`
- `ranking_score=60.04`
- `avg_profile_points=18.582`
- `weekly_rows=17`

## Active Final Ranking No-Change Confirmation

Read-only check after candidate materialization:

- Active final ranking row_count: 285
- Active profiles present: `ppr` only
- No active Half PPR final rows.
- No active Standard final rows.
- No active GNG Keeper final rows.

| scoring_profile_id | position | row_count | rank range |
| --- | --- | ---: | --- |
| `ppr` | QB | 45 | 1 to 45 |
| `ppr` | RB | 80 | 1 to 80 |
| `ppr` | WR | 100 | 1 to 100 |
| `ppr` | TE | 60 | 1 to 60 |

Trey McBride final ranking after candidate work:

- `scoring_profile_id=ppr`
- `position=TE`
- `rank=1`
- `tier=elite`
- `ranking_score=98.0`

## Ranking Formula And Backtest No-Change Confirmation

Read-only table counts after candidate materialization:

| table | row_count |
| --- | ---: |
| `ranking_formula_candidates` | 12 |
| `ranking_formula_sets` | 1 |
| `ranking_backtest_runs` | 0 |
| `ranking_backtest_results` | 0 |
| `ranking_backtest_candidate_summaries` | 0 |
| `ranking_formula_champions` | 0 |

No champion formulas were selected. No ranking formula or backtest rows were written.

## Pigskin Formula Exposure Check

Searched:

- `app.py`
- `src/pigskin_context_tools.py`
- `src/pigskin_packet_guardrails.py`
- `src/pigskin_context_qa.py`

Search terms:

- `ranking_formula`
- `ranking_backtest`
- `ALLOW_RANKING_FORMULA_BACKTEST_WRITE`
- `execute_bigquery_sql`

Result:

- No matches.
- No Pigskin-visible ranking formula read/write tool exposure found.
- No arbitrary SQL path added.
- No Streamlit request-time formula/backtest write path added.

## Tests And Checks

Commands run:

```powershell
.\venv\Scripts\python.exe scripts\check_deployment_safety.py
.\venv\Scripts\python.exe -m compileall -q src scripts
.\venv\Scripts\python.exe -m unittest tests.test_fantasy_scoring tests.test_materialize_fantasy_points tests.test_player_profile_ranking_profiles tests.test_pigskin_rankings_materialize_identity tests.test_pigskin_rankings_model_runs
.\venv\Scripts\python.exe -m unittest discover tests
.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run
```

Results:

- Safety checker passed.
- Compile passed.
- Focused tests passed: 39 tests.
- Full test suite passed: 676 tests.
- No pending migrations.
- BigQuery validation dry-run passed and discovered validation files through `209_ranking_backtest_candidate_summaries_grain_and_ranges.sql`.

## Restrictions Confirmation

Confirmed:

- No production deploy.
- No staging deploy.
- No Pigskin chat call.
- No final LLM ranking generation.
- No final ranking generation.
- No write to `analytics_pigskin_rankings`.
- No live Sleeper API call.
- No Cloud Run Job trigger.
- No Scheduler job creation.
- No champion formula selection.
- No ranking formula/backtest table writes.
- No ranking formula/backtest exposure to Pigskin chat.

## Remaining Warnings

1. `analytics_pigskin_rankings_candidates` remains transient and single-profile. Phase 31.13 handled this by verifying one profile at a time and restoring PPR at the end.
2. The weekly-zero-with-historical-metrics diagnostic returns 82 rows for each profile. The first examples are historical/inactive or roster-edge players such as Odell Beckham Jr., Ben Roethlisberger, Jack Doyle, Jalen Richard, and Le'Veon Bell. This warning predates profile-specific candidate work and should be handled as candidate-universe cleanup, not as a profile scoring blocker.
3. Full tests emit expected local log noise from mocked ranking generation and pipeline tests. No live LLM call was made.

## Recommended Next Phase

Recommended next phase:

- Phase 31.14: Generate final rankings for Half PPR, Standard, and GNG Keeper, only with explicit owner authorization for final ranking generation.

Other valid next phases:

- Deploy Player Profiles scoring dropdown.
- Make candidate boards profile-sliced instead of transient single-profile.
- Build a formula comparison dashboard skeleton.
