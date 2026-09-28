# Phase 32.39 Pigskin Chat Ranking Grounding Bugfix Report

Final decision: PIGSKIN CHAT RANKING GROUNDING FIXED

## Summary

Pigskin chat now preloads live Current Pigskin ranking rows before sending rank-order questions to Gemini. For top-N, current ranks, overall board, or rank-defense prompts, the app retrieves the same `analytics_pigskin_rankings` active rows and `ALL` board order used by Player Profiles, then injects that board into the prompt as the source of truth.

No ranking rows were regenerated. No formula champion was activated. No BQML model was trained. No Pigskin chat automated LLM smoke was run.

## Files Changed

- `app.py`
- `src/player_profile_ranking_profiles.py`
- `src/pigskin_context_tools.py`
- `src/pigskin_live_ranking_context.py`
- `tests/test_player_profile_ranking_profiles.py`
- `tests/test_pigskin_context_tools.py`
- `tests/test_pigskin_live_ranking_context.py`
- `tests/test_pigskin_chat_schema.py`
- `docs/rebuild/pigskin-live-ranking-formula-context.md`
- `docs/rebuild/formula-ranking-owner-review-index.md`

Source commit:

- `7ccbb2d phase 32.39 ground pigskin rankings`

## Discrepancy Reproduced

Observed Player Profiles Standard ALL top 10:

1. Jaxon Smith-Njigba
2. Puka Nacua
3. Josh Allen
4. Christian McCaffrey
5. Trey McBride
6. Amon-Ra St. Brown
7. Ja'Marr Chase
8. Drake London
9. Drake Maye
10. Bijan Robinson

Observed Pigskin chat had answered a different Standard top 10 starting with Christian McCaffrey, Bijan Robinson, Jonathan Taylor, Jahmyr Gibbs, and De'Von Achane. That answer was not grounded in the live Standard ALL board.

## Root Cause

The prior chat path had static formula policy context, but it did not guarantee that live board rows were loaded before a current-rank answer. The model could infer or synthesize an order from formula discussion instead of using the same live row order as Player Profiles.

The `get_rankings_slice` tool also did not expose a board-level `board_rank` contract or a shared Player Profiles query helper.

## Ranking Sources Compared

Read-only comparison for:

- `scoring_profile_id=standard`
- `board=ALL`
- `limit=10`

Player Profiles helper:

`Jaxon Smith-Njigba | Puka Nacua | Josh Allen | Christian McCaffrey | Trey McBride | Amon-Ra St. Brown | Ja'Marr Chase | Drake London | Drake Maye | Bijan Robinson`

Pigskin context tool:

`Jaxon Smith-Njigba | Puka Nacua | Josh Allen | Christian McCaffrey | Trey McBride | Amon-Ra St. Brown | Ja'Marr Chase | Drake London | Drake Maye | Bijan Robinson`

Direct BigQuery:

`Jaxon Smith-Njigba | Puka Nacua | Josh Allen | Christian McCaffrey | Trey McBride | Amon-Ra St. Brown | Ja'Marr Chase | Drake London | Drake Maye | Bijan Robinson`

Match results:

- Player Profiles helper equals Pigskin context tool: `True`
- Pigskin context tool equals direct BigQuery: `True`

Active ranking shape after the phase:

- `standard`: QB45, RB80, WR100, TE35
- `half_ppr`: QB45, RB80, WR100, TE35
- `ppr`: QB45, RB80, WR100, TE35
- `gng_keeper`: QB45, RB80, WR100, TE35

## Live Ranking Context Helper Behavior

Added `src/pigskin_live_ranking_context.py`.

The helper:

- detects rank intent such as `top 10`, `top ten`, `overall`, `current ranks`, and `your rankings`;
- defaults scoring profile to `standard`;
- defaults board to `ALL`;
- caps live context requests at 50 rows;
- formats a `Live Ranking Board Context` block with exact `board_rank` order;
- fails closed if rows are unavailable, telling the model not to guess.

`get_rankings_slice` now:

- reads `analytics_pigskin_rankings` only;
- uses the shared Player Profiles live context query;
- returns `board_rank`;
- labels the source as `Current Pigskin live baseline`;
- does not use Formula Review Markdown, `analytics_pigskin_rankings_candidates`, `ranking_formula_champions`, or `pigskin_context_score`.

## Prompt And Style Changes

Pigskin chat system guidance now says:

- live board context is the source of truth for ranking questions;
- exact board order must be preserved;
- missing live rows mean the board is unavailable, not a guessing opportunity;
- BQML, NGS, Stats02, PBP, injury, availability, and formula champions are not active formulas;
- factual rank-defense answers should not use bracketed stage directions such as `[mocking]`, `[laughs]`, `[deadpan]`, or `[sarcastic]`.

## Tests And Checks

Focused tests:

`.\venv\Scripts\python.exe -m unittest tests.test_player_profile_ranking_profiles tests.test_pigskin_context_tools tests.test_pigskin_live_ranking_context tests.test_pigskin_live_formula_context tests.test_pigskin_chat_schema`

Result:

- `Ran 32 tests`
- `OK`

Compile:

`.\venv\Scripts\python.exe -m py_compile app.py src\pigskin_context_tools.py src\pigskin_live_ranking_context.py src\player_profile_ranking_profiles.py src\pigskin_live_formula_context.py src\compat_flags.py`

Result: passed.

Safety:

`.\venv\Scripts\python.exe scripts\check_deployment_safety.py`

Result: passed.

Diff check:

`git diff --check`

Result: exit code 0. Git reported line-ending warnings only.

## Build And Deploy

Cloud Build:

- Build ID: `ebf7c4c0-3d93-4988-a939-2cd8a002f35a`
- Status: `SUCCESS`
- Image tag: `prod-candidate-7ccbb2d79acd-20260706T175923Z`
- Digest-pinned image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:34149c47fb27628b530842156768e4c4f50137891713e522899bf5112ab5a6e3`

Production deploy:

- Previous revision: `nfl-studio-dashboard-00086-wpx`
- New revision: `nfl-studio-dashboard-00087-68g`
- Traffic: `nfl-studio-dashboard-00087-68g:100`
- URL: `https://nfl-studio-dashboard-583607027760.us-central1.run.app`
- Alternate service URL from describe: `https://nfl-studio-dashboard-inypcgbx7a-uc.a.run.app`

Flags verified:

- `USE_FORMULA_COMPARISON_DASHBOARD=true`
- `DATA_OPS_ALLOW_JOB_TRIGGER=false`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER=false`

Rollback command:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services update-traffic nfl-studio-dashboard --project=fantasy-football-498121 --region=us-central1 --to-revisions nfl-studio-dashboard-00086-wpx=100
```

## Production Smoke

Health and shell:

- `https://nfl-studio-dashboard-583607027760.us-central1.run.app/_stcore/health`: `200 ok`
- `https://nfl-studio-dashboard-583607027760.us-central1.run.app/`: `200`, Streamlit shell present, no traceback marker
- `https://nfl-studio-dashboard-inypcgbx7a-uc.a.run.app/_stcore/health`: `200 ok`
- `https://nfl-studio-dashboard-inypcgbx7a-uc.a.run.app/`: `200`, Streamlit shell present, no traceback marker

No rollback was needed.

## Owner Manual Smoke Prompt

Use this in Pigskin chat:

`Can you go thru your top 10 overall players for the 2026 season in Standard Scoring? Based on your ranking system and current ranks. Back up your ranks and claims as some are very different than what we are seeing in mainstream sports media.`

Expected order:

1. Jaxon Smith-Njigba
2. Puka Nacua
3. Josh Allen
4. Christian McCaffrey
5. Trey McBride
6. Amon-Ra St. Brown
7. Ja'Marr Chase
8. Drake London
9. Drake Maye
10. Bijan Robinson

## No-State-Change Confirmation

- No live ranking regeneration occurred.
- No `analytics_pigskin_rankings` write occurred.
- No `analytics_pigskin_rankings_candidates` write occurred.
- No `ranking_formula_champions` write occurred.
- No champion formula was activated.
- No BQML training occurred.
- No Sleeper API call occurred.
- No Data Ops job was triggered.
- No automated Pigskin chat or Gemini smoke was run.

## Remaining Warnings

- The owner manual chat smoke still needs to be run in the app to validate Gemini follows the injected context in the visible answer.
- PowerShell reported native-command wrapper warnings for commands that wrote to stderr, but captured exit codes were 0.

## Recommended Next Phase

Studio use / hold Current Pigskin.

If owner manual smoke still shows a mismatch, the next fix should inspect the visible Gemini response only, not regenerate ranks or change formula policy.
