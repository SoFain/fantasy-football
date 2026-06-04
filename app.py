import os
import sys
import subprocess
import html
import streamlit as st

DEFAULT_BIGQUERY_PROJECT = "fantasy-football-498121"
BIGQUERY_PROJECT_ID = (
    os.environ.get("BQ_PROJECT")
    or os.environ.get("GCP_PROJECT")
    or os.environ.get("GOOGLE_CLOUD_PROJECT")
    or DEFAULT_BIGQUERY_PROJECT
)
os.environ.setdefault("BQ_PROJECT", BIGQUERY_PROJECT_ID)

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="NFL Data Studio",
    page_icon="🏈",
    layout="wide",
    initial_sidebar_state="expanded"
)

def check_password():
    """Returns True if the user entered the correct credentials."""
    target_user = os.environ.get("DASHBOARD_USERNAME", "admin")
    target_pass = os.environ.get("DASHBOARD_PASSWORD", "fantasy2026")

    def password_entered():
        # Strip whitespaces defensively to prevent copy-paste space typos
        u_input = st.session_state.get("username", "").strip()
        p_input = st.session_state.get("password", "").strip()
        
        # Log attempts securely for diagnostic debugging
        import logging
        login_logger = logging.getLogger("app.login")
        login_logger.info(
            f"Login check - Entered User: '{u_input}' (len={len(u_input)}), "
            f"Expected User: '{target_user}' (len={len(target_user)}), "
            f"Pass len={len(p_input)} (Expected len={len(target_pass)}), "
            f"Match: {u_input == target_user and p_input == target_pass}"
        )
        
        if u_input == target_user and p_input == target_pass:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # Align login layout elegantly
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown("### 🔑 Data Studio Login")
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.button("Log In", on_click=password_entered)
        return False
    elif not st.session_state["password_correct"]:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown("### 🔑 Data Studio Login")
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.button("Log In", on_click=password_entered)
            st.error("❌ Username or password incorrect")
        return False
    return True

if not check_password():
    st.stop()

# Custom Sleek CSS Styles
st.markdown("""
<style>
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 0.1rem;
        font-family: 'Outfit', sans-serif;
    }
    .subtitle {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #F3F4F6;
        border-radius: 8px;
        padding: 15px;
        border-left: 5px solid #1E3A8A;
    }
</style>
""", unsafe_allow_html=True)

# Define project directories
if getattr(sys, 'frozen', False):
    # In PyInstaller, sys.executable points to the compiled .exe file.
    # The user's workspace files (src/, validate.py, cache/) are in the directory where the .exe is run.
    PROJECT_ROOT = os.path.dirname(sys.executable)
else:
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

CACHE_DIR = os.path.join(PROJECT_ROOT, "cache")

def get_python_executable():
    """
    Finds the python interpreter to use for running backend scripts.
    In a frozen bundle, sys.executable is the .exe, not python.
    """
    for subpath in [
        ["venv", "Scripts", "python.exe"],
        [".venv", "Scripts", "python.exe"],
        ["venv", "bin", "python"],
        [".venv", "bin", "python"],
    ]:
        path = os.path.join(PROJECT_ROOT, *subpath)
        if os.path.exists(path):
            return path
    return "python"

def get_warehouse_metrics():
    """Fetches BigQuery table count and logical size from table metadata."""
    try:
        from google.cloud import bigquery
        client = bigquery.Client(project=BIGQUERY_PROJECT_ID)
        dataset_id = "fantasy_football_brain"
        dataset_ref = f"{client.project}.{dataset_id}"

        active_tables = 0
        total_bytes = 0
        for table_item in client.list_tables(dataset_ref):
            active_tables += 1
            table = client.get_table(table_item.reference)
            total_bytes += table.num_bytes or 0

        return active_tables, total_bytes / (1024 * 1024)
    except Exception as e:
        import logging
        logging.getLogger("app.metrics").warning(f"Could not fetch warehouse metrics: {e}")
    return 0, 0.0

@st.cache_data(ttl=3600, show_spinner=False)
def execute_bq_cached(sql_query: str):
    from google.cloud import bigquery
    bq_client = bigquery.Client(project=BIGQUERY_PROJECT_ID)
    query_job = bq_client.query(sql_query)
    df = query_job.result().to_dataframe()
    return df

def render_fraud_watch_segment():
    st.markdown("### Fraud Watch")
    st.markdown("Weekly box-score spikes ranked against role quality, usage stability, touchdown dependence, and snap trust.")

    sql_query = f"""
    WITH latest AS (
        SELECT season, MAX(week) AS week
        FROM `{BIGQUERY_PROJECT_ID}.fantasy_football_brain.analytics_fraud_watch`
        WHERE season = (
            SELECT MAX(season)
            FROM `{BIGQUERY_PROJECT_ID}.fantasy_football_brain.analytics_fraud_watch`
        )
        GROUP BY season
    )
    SELECT
        f.player_name,
        f.position,
        f.team,
        f.current_team,
        f.season,
        f.week,
        ROUND(f.fantasy_points_ppr, 2) AS ppr,
        f.skill_player_opportunities AS opps,
        ROUND(f.target_share, 3) AS target_share,
        ROUND(f.wopr, 3) AS wopr,
        f.touchdowns,
        ROUND(f.touchdown_dependency_rate, 2) AS td_points_share,
        ROUND(f.role_quality_score, 2) AS role_quality,
        ROUND(f.role_fragility_score, 2) AS fragility,
        ROUND(f.fraud_score, 2) AS fraud_score,
        f.fraud_label,
        f.fraud_case
    FROM `{BIGQUERY_PROJECT_ID}.fantasy_football_brain.analytics_fraud_watch` f
    JOIN latest
        ON f.season = latest.season
        AND f.week = latest.week
    ORDER BY f.fraud_score DESC, f.fantasy_points_ppr DESC
    LIMIT 20
    """

    try:
        df = execute_bq_cached(sql_query)
    except Exception as e:
        st.info(f"Fraud Watch is not materialized yet: {e}")
        return

    if df.empty:
        st.info("Fraud Watch has no candidates for the latest loaded week.")
        return

    top = df.iloc[0]
    cols = st.columns(3)
    cols[0].metric("Top Candidate", top["player_name"])
    cols[1].metric("Fraud Score", f'{top["fraud_score"]:.1f}')
    cols[2].metric("Label", top["fraud_label"])
    st.dataframe(df, use_container_width=True, hide_index=True)

def render_ai_cohost():
    st.markdown("### 💬 Pigskin")
    st.markdown("Chat with Pigskin, the AI vs Vibes co-host built to roast bad process and back it up with data.")

    active_gemini_key = os.environ.get("GEMINI_API_KEY", "")
    if not active_gemini_key:
        st.info("⚠️ Please enter a **Gemini API Key** in the sidebar to activate the AI Co-Host.")
    else:
        # Initialize session state for messages and chat session
        if "messages" not in st.session_state:
            st.session_state.messages = []

        script_mode = st.toggle(
            "Script mode",
            key="pigskin_script_mode",
            help="Format answers as a voice-ready script with bracketed performance cues instead of bullets.",
        )
        if st.session_state.get("chat_session_script_mode") != script_mode:
            st.session_state.pop("chat_session", None)
            st.session_state.chat_session_script_mode = script_mode
        
        import google.generativeai as genai
        genai.configure(api_key=active_gemini_key)
    
        # Define the BigQuery tool
        def execute_bigquery_sql(sql_query: str) -> str:
            """Executes a BigQuery SQL query against the fantasy_football_brain dataset.
            
            MANDATORY CONSTRAINTS:
            1. You must use a `LIMIT 50` on every query.
            2. Do NOT use `SELECT *`. You must explicitly select the columns you need.
            3. You must filter by partitioning keys (`season` and `week`) whenever possible.
            4. For player analysis, select `current_team`, `team_changed_since_stats`, and `roster_status` when available.
            """
            pass # We will execute this manually
            
        active_project_id = BIGQUERY_PROJECT_ID
        script_mode_instruction = """

    ### Script Mode Output Contract ###
    Script Mode is ON. Format the final answer as a voice actor or advanced TTS script.
    Do not use bullet points, numbered lists, markdown tables, or report-style section headers.
    Write in spoken paragraphs with natural pacing, short beats, and bracketed voice cues.
    Use bracketed cues such as [sigh], [laughs], [disappointed], [sarcastic], [deadpan], [annoyed], [pause], [interested], [mocking], [matter-of-fact], and [conspiratorial].
    Only use cues that affect vocal delivery. Do not use physical acting, facial expression, camera, or stage-direction cues.
    Keep Pigskin arrogant, snarky, and evidence-driven. The tone should sound like a ruthless co-host delivering a segment, not a polite analyst writing notes.
    Keep the data intact. Mention important metrics in plain spoken language instead of table format.
    Example style:
    [sigh] Here is the problem. The box score is trying to sell you a miracle, and the role is standing in the back looking embarrassed.
    [sarcastic] Great, he scored twice. Very cute. Now look at the target share before your roster starts paying vibes tax.
    """ if script_mode else ""

        # Define Co-Host System Prompt
        system_prompt = f"""
    You are Pigskin, the analytical co-host for AI vs Vibes, a fantasy football show built around evidence beating narrative.
    Your job is to be the thinking machine in the room: ruthless about bad calls, allergic to lazy narratives, and impossible to impress without evidence.
    Be direct, skeptical, funny, and sharp. Ground every criticism in data.
    Separate points from process, punish touchdown chasing, punish stale rankings, and explain what would change your mind.

    ### Pigskin Voice Contract ###
    You are not a polite default assistant. You have a snarky, modern, football-sick personality.
    When a take is bad, say it is bad. If the data says a player is a trap, say the market is getting cooked. If a roster build is fragile, call it fragile.
    When praising a player, team, or call, use backhanded approval when appropriate: "accidentally correct," "finally made a grown-up decision," "not complete nonsense," "the vibes stumbled into the math."
    Use modern slang naturally and sparingly: `cap`, `no cap`, `cooked`, `washed`, `unc`, `delusional`, `fraud watch`, `box-score merchant`, `vibes tax`, `take lock`, `cope`, `not serious`, `respectfully, no`, `generationally unserious`.
    Do not force slang into every sentence. One good shot beats five corny ones.
    Punch up at fantasy process, rankings, narratives, analysts, team decisions, coaching, roster construction, and player fantasy profiles.
    Do not insult protected classes, appearance, disability, personal tragedy, family, or anything outside football/fantasy decision-making. Do not use slurs.
    You may roast the user's fantasy choices, but keep it show-friendly: brutal, funny, and useful, not hateful.
    Never let personality override accuracy. If the evidence is thin, say the take is unconfirmed instead of pretending certainty.
    Use short, punchy verdicts before deeper analysis when the user asks for a take.

    Voice examples:
    - "This is touchdown chasing with a fake mustache. The role did not improve, the box score just got lucky."
    - "I like the player. I hate the price. Paying WR2 tax for WR3 usage is how leagues collect donations."
    - "Respectfully, no. That narrative is vibes in a lab coat."
    - "This roster is not dead, but it is walking around with a questionable tag."
    {script_mode_instruction}

    The active BigQuery project ID is '{active_project_id}' and the dataset is 'fantasy_football_brain'.
    Prefer dataset-qualified table names such as `fantasy_football_brain.analytics_player_weekly_truth` unless an explicit project ID is provided.

    Here is the database schema description:
    
    - Table: `fantasy_football_brain.analytics_player_weekly_truth` (PRIMARY TABLE)
      Description: Derived AI vs Vibes player truth table with fantasy output, usage, red-zone role, EPA, recent trend, opportunity scoring, efficiency scoring, and criticism-ready flags.
      Columns include: `season`, `week`, `player_id`, `player_name`, `position`, `team`, `current_team`, `roster_status`, `team_changed_since_stats`, `primary_qb_name`, `primary_qb_epa_per_target`, `primary_qb_target_share`, `qbs_targeted_by`, `opponent_team`, `fantasy_points_ppr`, `targets`, `receptions`, `carries`, `target_share`, `air_yards_share`, `wopr`, `total_epa`, `red_zone_targets`, `red_zone_carries`, `red_zone_touches`, `prior_week_ppr`, `ppr_delta`, `rolling_3_week_ppr`, `rolling_3_week_targets`, `rolling_3_week_carries`, `opportunity_score`, `efficiency_score`, `role_quality_score`, `points_over_role_score`, `role_fragility_score`, `analytical_grade`, `touchdown_dependent`, `box_score_trap`, `target_earner`, `empty_volume`, `usage_warning`, `points_outran_role`, `thin_role_big_week`, `fragile_role`, `role_backed_production`, and `analytical_verdict`.
      `team` is the historical team for that stat week. `current_team` is the latest known roster team. If `team_changed_since_stats` is true, do not describe the player as currently on `team`.
      *PRIORITIZE THIS TABLE for almost all player analysis.*

    - Table: `fantasy_football_brain.analytics_fraud_watch`
      Description: First AI vs Vibes show segment table. Use it to identify fantasy box scores that outran the player's actual role quality.
      Columns include: `season`, `week`, `player_name`, `position`, `team`, `current_team`, `fantasy_points_ppr`, `skill_player_opportunities`, `target_share`, `wopr`, `offense_pct`, `touchdowns`, `touchdown_dependency_rate`, `role_quality_score`, `points_over_role_score`, `role_fragility_score`, `fraud_score`, `fraud_label`, `fraud_case`, and `what_would_change_mind`.
      
    - Table: `fantasy_football_brain.weekly_metrics` (also accessible as `historical_player_metrics`)
      Columns:
    - `season` (INT64) - The NFL season year (e.g. 2024).
    - `week` (INT64) - The NFL week (e.g. 1 to 18).
    - `player_name` (STRING) - The name of the player.
    - `position` (STRING) - Player's position (e.g. 'QB', 'RB', 'WR', 'TE').
    - `team` (STRING) - Team abbreviation (e.g. 'KC', 'BUF').
    - `target_share` (FLOAT64) - Share of team targets.
    - `epa_per_play` (FLOAT64) - Expected Points Added per play.
    - `rushing_yards` (FLOAT64) - Rushing yards gained.
    - `targets` (FLOAT64) - Number of pass targets.
    - `receptions` (FLOAT64) - Number of pass catches.
    - `fantasy_points` (FLOAT64) - Standard fantasy points.
    - `fantasy_points_ppr` (FLOAT64) - PPR fantasy points.

    - Table: `fantasy_football_brain.active_league_rosters`
      Columns:
    - `username` (STRING)
    - `sleeper_id` (STRING)
    - `player_name` (STRING)
    - `position` (STRING)
    
    - Table: `fantasy_football_brain.play_by_play`
      Columns:
    - `season` (INT64)
    - `week` (INT64)
    - `play_type` (STRING)
    - `yards_gained` (FLOAT64)
    - `epa` (FLOAT64)

    - Table: `fantasy_football_brain.ngs_passing`
      Columns: Includes NGS tracking passing metrics like avg_time_to_throw, avg_completed_air_yards, aggressiveness.
      
    - Table: `fantasy_football_brain.realtime_player_news`
      Columns: `player_id` (STRING), `gsis_id` (STRING), `player_name` (STRING), `position` (STRING), `team` (STRING), `trend_type` (STRING, 'ADD' or 'DROP'), `trend_count` (INT64).
      Description: Real-time trending Sleeper data for tracking recent add/drop volume.
    - Table: `fantasy_football_brain.sleeper_viewer_team_snapshots`
      Description: On-demand viewer team snapshot from Sleeper for YouTube team reviews.
      Columns include: `snapshot_at`, `league_id`, `season`, `week`, `viewer_roster_id`, `viewer_owner_id`, `viewer_username`, `viewer_display_name`, `viewer_team_name`, `matchup_id`, `points`, `starters_json`, and `players_json`.
    - Table: `fantasy_football_brain.sleeper_roster_players`
      Description: Current rostered players for every team in a loaded Sleeper league snapshot.
      Columns include: `snapshot_at`, `league_id`, `season`, `week`, `roster_id`, `owner_id`, `is_viewer_team`, `sleeper_player_id`, `player_name`, `position`, `team`, `gsis_id`, `status`, `injury_status`, `is_starter`, `is_taxi`, and `is_reserve`.
    - Table: `fantasy_football_brain.sleeper_lineups`
      Description: Week-specific matchup lineup/player points for loaded Sleeper league snapshots.
      Columns include: `snapshot_at`, `league_id`, `season`, `week`, `roster_id`, `matchup_id`, `owner_id`, `is_viewer_team`, `sleeper_player_id`, `player_name`, `position`, `team`, `gsis_id`, `is_starter`, and `points`.
    - Table: `fantasy_football_brain.sleeper_rosters`, `fantasy_football_brain.sleeper_matchups`, `fantasy_football_brain.sleeper_league_users`, and `fantasy_football_brain.sleeper_leagues`
      Description: Sleeper league metadata, users, standings, matchup ids, scoring settings, roster positions, and raw league settings for loaded viewer-team snapshots.
    - Table: `fantasy_football_brain.analytics_player_qb_splits`
      Description: Season-level receiver-by-QB split table. Use this before making claims about QB-driven receiver changes.
      Columns include: `season`, `posteam`, `player_id`, `player_name`, `qb_id`, `qb_name`, `weeks_with_targets`, `first_week_with_qb`, `last_week_with_qb`, `targets`, `receptions`, `catch_rate`, `receiving_yards`, `yards_per_target`, `adot`, `touchdowns`, `red_zone_targets`, `total_epa`, `epa_per_target`, `target_share_from_qb`, `team_target_share`, and `sample_label`.
    - Table: `fantasy_football_brain.analytics_player_qb_weekly`
      Description: Weekly receiver-by-QB split table. Use this to test before/after QB changes, injury effects, and whether a receiver's role changed or only target quality changed.
      Columns include: `season`, `week`, `posteam`, `defteam`, `player_id`, `player_name`, `qb_id`, `qb_name`, `targets`, `receptions`, `catch_rate`, `receiving_yards`, `yards_per_target`, `adot`, `touchdowns`, `red_zone_targets`, `total_epa`, `epa_per_target`, `target_share_from_qb`, and `team_target_share`.
    - Table: `fantasy_football_brain.analytics_context_events`
      Description: Curated event ledger for causal context such as QB injuries, QB changes, offensive line injuries, coaching/play-caller changes, weather, and other fantasy-relevant situational events.
      Columns include: `event_id`, `season`, `start_week`, `end_week`, `team`, `event_type`, `subject_player_id`, `subject_name`, `subject_position`, `affected_player_id`, `affected_player_name`, `affected_unit`, `causal_status`, `confidence_score`, `source_type`, `source_label`, `source_url`, `summary`, `analysis_instruction`, and `active`.
    - Table: `fantasy_football_brain.analytics_external_context_search_results`
      Description: On-demand external verification search results for player-specific outside verification. Use these results as leads, not as confirmed facts, unless the linked source clearly supports the claim.
      Columns include: `searched_at`, `player_name`, `query`, `result_rank`, `title`, `link`, `display_link`, `snippet`, `source_type`, `provider`, and `source_name`.
    - Table: `fantasy_football_brain.analytics_game_environment`
      Description: One row per regular-season game with stadium, roof, surface, temperature, wind, weather text, and fantasy-relevant environment flags.
      Columns include: `season`, `week`, `game_id`, `game_date`, `home_team`, `away_team`, `stadium`, `historical_stadium_name`, `stadium_id`, `roof`, `surface`, `temp_f`, `wind_mph`, `weather_text`, `is_indoor_or_closed`, `roof_category`, `surface_category`, `precipitation_or_storm_flag`, `snow_or_freezing_flag`, `temperature_bucket`, `wind_bucket`, `environment_risk_level`, and `fantasy_environment_note`.
    - Table: `fantasy_football_brain.ngs_rushing`
      Columns: Includes NGS tracking rushing metrics like efficiency, percent_attempts_gte_eight_defenders, avg_time_to_los.
    - Table: `fantasy_football_brain.ngs_receiving`
      Columns: Includes NGS tracking receiving metrics like avg_cushion, avg_separation, avg_yac_above_expectation.
    - Table: `fantasy_football_brain.ftn_charting`
      Columns: Includes FTN premium charting play-by-play data like is_no_huddle, is_play_action, is_screen_pass, is_interception_worthy.
    - Table: `fantasy_football_brain.weekly_snap_counts`
      Columns: Includes weekly player snap metrics like offense_snaps, offense_pct, defense_pct, st_pct.
    - Table: `fantasy_football_brain.injury_reports`
      Columns: Includes weekly injury data like report_primary_injury, report_status, practice_status.
    
    - Table: `fantasy_football_brain.team_descriptions`
      Columns:
    - `team_abbr` (STRING)
    - `team_name` (STRING)

    - Table: `fantasy_football_brain.rookie_scouting_metrics`
      Description: Advanced player tracking and profiling metrics for rookies (e.g. yards after contact, Yards Per Route Run, separation, success rates against coverage), imported from custom scouting imports.
      Columns include: `season` (draft/rookie season), `player_name`, `position`, `college`, `yards_after_contact_per_attempt`, `yards_per_route_run`, `college_target_share`, `catch_radius_grade`, `success_rate_vs_man`, `success_rate_vs_zone`, `success_rate_vs_press`, `avg_separation_inches`, and `data_source`.
      
    - Table: `fantasy_football_brain.college_player_stats`
      Description: Season-level statistics for college players (passing, rushing, receiving totals), imported from CollegeFootballData (CFBD) API.
      Columns include: `season`, `player_name`, `position`, `team` (college team), `conference`, `games`, `passing_yards`, `passing_tds`, `rushing_yards`, `rushing_tds`, `receptions`, `receiving_yards`, and `receiving_tds`.

    ### The Analytical Filter Protocol ###
    You are mandated to follow a strict query protocol when analyzing players.
    You MUST default to using the `analytics_player_weekly_truth` table first. Only fallback to `play_by_play` if highly specific situational context is requested.
    Always use your `execute_bigquery_sql` tool to fetch data before answering analytical questions.
    When criticizing a take, cite the metrics that make the take strong, weak, stale, box-score driven, or contradicted by role.
    For Fraud Watch analysis, use `analytics_fraud_watch` first, then inspect `analytics_player_weekly_truth` for the detailed player row.
    For rookie analysis, prospect profiling, or college career evaluations, query `rookie_scouting_metrics` and `college_player_stats`. Join them on player name and season where appropriate. Cite the specific tracking details (e.g. success rate vs press/man, yards after contact, separation) and label the data source.
    For viewer team analysis, first query the latest `sleeper_viewer_team_snapshots` row for the requested `league_id`, `viewer_roster_id`, username, or team name. Then query `sleeper_roster_players` and `sleeper_lineups` with `is_viewer_team = TRUE`. Join to `analytics_player_weekly_truth` by `gsis_id` when available and fallback to player name plus team when needed.
    For viewer roster criticism, separate roster construction from weekly start/sit. Identify fragile starters, bench upside, bye/injury exposure, thin positions, duplicate archetypes, tradeable surplus, and waiver needs.
    For offseason or 2026 roster context, use `current_team` and `roster_status`; use `team` only when discussing historical stat weeks.
    For any player question about "this season", "right now", "current", "2026", rankings, draft price, or team fit, your first player query MUST select `current_team`, `team_changed_since_stats`, and `roster_status`. Never describe `team` as the player's current team.
    If a query fails, do not answer from memory. Stop and say the warehouse query failed.
    If a player query returns zero rows, try one alternate name query using `LOWER(player_name) LIKE` or `LOWER(player_display_name) LIKE` before giving up.
    For receiver analysis, check `analytics_player_qb_splits` or `analytics_player_qb_weekly` before blaming the player. Separate player role from QB environment.
    For game-specific or matchup-specific projections, check `analytics_game_environment`. Indoor or closed-roof games should not get weather downgrades. Outdoor high-wind, freezing, snow, or storm games can materially change passing, kicking, and efficiency assumptions.
    Do not pretend long-range weather is known. For future games outside a reliable forecast window, use stadium/roof/surface as stable context and label weather as unknown until game week.
    For any causal claim involving injuries, coaching, play-calling, offensive line, weather, benching, or transaction intent, query `analytics_context_events` first.
    If context events are missing or user asks for outside verification, query `analytics_external_context_search_results` for stored external verification leads before making a claim.

    ### Causal Claim Protocol ###
    Never invent motives, transaction logic, injury explanations, coaching decisions, or play-calling changes from statistical splits alone.
    A QB change in the data only proves "QB environment changed." It does NOT prove "the team pivoted away," "the player was benched," "the QB was injured," or "coaches changed the plan" unless a table or user-provided fact directly supports that cause.
    If the data shows a split but not the reason, say the reason is unconfirmed and list the plausible causes separately.
    Use disciplined language:
    - Supported: "Pittman's target quality changed after Week 14 when his primary QB changed from D.Jones to R.Leonard/P.Rivers."
    - Unsupported without event evidence: "Indy pivoted away from D.Jones."
    - Unsupported without injury evidence: "D.Jones was injured."
    - Unsupported without coaching data: "The coaching staff changed the play-calling."
    When a causal explanation matters, explicitly label it as one of: `confirmed by data`, `supported inference`, `user-provided context`, or `unconfirmed hypothesis`.
    If the user supplies a factual correction, incorporate it as user-provided context and revise the analysis.
    When `analytics_context_events.causal_status = 'user_provided_context'`, you may use it as context, but clearly label it as user-provided unless an external source verifies it.
    """
    
        if "chat_session" not in st.session_state:
            model = genai.GenerativeModel(
                'gemini-3.5-flash',
                tools=[execute_bigquery_sql],
                system_instruction=system_prompt
            )
            # Disable automatic function calling so we can stream!
            st.session_state.chat_session = model.start_chat(enable_automatic_function_calling=False)
        
        # Display chat history
        for msg in st.session_state.messages:
            if msg["role"] == "tool_status":
                with st.status(
                    msg["status_msg"],
                    state=msg.get("state", "complete"),
                    expanded=msg.get("expanded", False),
                ):
                    st.code(msg["code"], language="sql")
                    if msg.get("error"):
                        st.error(msg["error"])
            else:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
                
        # Chat input
        placeholder = "Ask for a voice-ready script..." if script_mode else "Ask your co-host a question..."
        if prompt := st.chat_input(placeholder):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                try:
                    # Initial request (might be a tool call)
                    response = st.session_state.chat_session.send_message(prompt, stream=False)
                    
                    def get_fc(resp):
                        try:
                            return resp.parts[0].function_call
                        except (AttributeError, IndexError):
                            return None

                    # Manual tool calling loop
                    fc = get_fc(response)
                    while fc:
                        if fc.name == "execute_bigquery_sql":
                            sql_to_run = type(fc).to_dict(fc)["args"]["sql_query"]

                            tool_message = {
                                "role": "tool_status",
                                "status_msg": "🤖 AI Co-Host is analyzing the warehouse...",
                                "code": sql_to_run,
                                "state": "running",
                                "expanded": True,
                            }
                            st.session_state.messages.append(tool_message)
                            with st.status("🤖 AI Co-Host is analyzing the warehouse...", expanded=True) as status:
                                st.code(sql_to_run, language="sql")
                                try:
                                    df = execute_bq_cached(sql_to_run)
                                    status.update(label=f"🤖 Analysis complete! ({len(df)} rows retrieved)", state="complete")
                                    result_str = df.to_csv(index=False) if not df.empty else "0 rows returned."
                                except Exception as e:
                                    error_text = str(e)
                                    status.update(label="❌ Query failed", state="error", expanded=True)
                                    st.error(error_text)
                                    tool_message.update({
                                        "status_msg": "❌ Query failed",
                                        "state": "error",
                                        "expanded": True,
                                        "error": error_text,
                                    })
                                    failure_text = (
                                        "I've got a problem: Pigskin tried to query BigQuery, but the warehouse query failed. "
                                        "I am stopping here instead of giving you a fake data-backed take. "
                                        "The failed SQL and error are shown above."
                                    )
                                    st.error(failure_text)
                                    st.session_state.messages.append({"role": "assistant", "content": failure_text})
                                    return

                            tool_message.update({
                                "status_msg": f"🤖 Analysis complete! ({len(df)} rows retrieved)",
                                "state": "complete",
                                "expanded": False,
                            })
                            
                            import google.ai.generativelanguage as glm
                            tool_response = glm.Part(
                                function_response=glm.FunctionResponse(
                                    name="execute_bigquery_sql",
                                    response={"result": result_str}
                                )
                            )
                            # Get next response (could be another tool, or text)
                            response = st.session_state.chat_session.send_message(tool_response, stream=False)
                            fc = get_fc(response)
                        else:
                            break
                            
                    # Final text response stream
                    def stream_generator(resp):
                        # if the final response is already a full object (since we used stream=False to check for function_call)
                        # We cannot magically re-request it with stream=True easily without duplicating the prompt.
                        # Wait! We can just split the response.text to simulate streaming, OR we can execute the LAST send_message with stream=True!
                        # Since we already ran it with stream=False, it's not a generator.
                        # To simulate the stream visually:
                        import time
                        words = resp.text.split(" ")
                        for word in words:
                            yield word + " "
                            time.sleep(0.01)

                    st.write_stream(stream_generator(response))
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    
                except Exception as e:
                    st.error(f"Error communicating with AI Co-Host: {e}")

def render_value_analyzer():
    import html
    import pandas as pd
    st.markdown("### 📊 Trade & Value Analyzer")
    st.markdown("Compare player and draft pick values side-by-side using crowdsourced market transactions and AI projections.")

    def safe_display(value, fallback="N/A"):
        if pd.isna(value) or value is None or value == "":
            return fallback
        return html.escape(str(value))

    def numeric_value(value, fallback=0):
        if pd.isna(value) or value is None:
            return fallback
        return value

    # Load market players from BQ
    @st.cache_data(ttl=600, show_spinner=False)
    def load_market_players():
        try:
            query = f"""
                SELECT player_display_name, position, team, market_value, overall_rank, position_rank, redraft_value, tier
                FROM `{BIGQUERY_PROJECT_ID}.fantasy_football_brain.market_values`
                ORDER BY market_value DESC
            """
            return execute_bq_cached(query)
        except Exception as e:
            st.error(f"Could not load market values: {e}")
            return None

    market_df = load_market_players()
    if market_df is None or market_df.empty:
        st.info("⚠️ No market value data found in BigQuery. Please run the ingestion pipeline or check the database.")
        return

    # Prepare selection list
    player_options = []
    player_map = {}
    for idx, row in market_df.iterrows():
        name = row['player_display_name']
        pos = row['position']
        team = row['team']
        val = row['market_value']
        
        if pd.isna(pos) or not pos:
            label = f"🎫 {name} (Value: {val})"
        else:
            label = f"🏃 {name} ({pos} - {team}) (Value: {val})"
        player_options.append(label)
        player_map[label] = row

    col_sel_A, col_sel_B = st.columns(2)
    with col_sel_A:
        selected_A = st.selectbox("Select Asset A", player_options, index=0, key="sel_a")
        asset_A = player_map[selected_A]
    with col_sel_B:
        selected_B = st.selectbox("Select Asset B", player_options, index=min(1, len(player_options)-1), key="sel_b")
        asset_B = player_map[selected_B]

    # Display Side-by-Side Cards
    st.markdown("#### ⚖️ Side-by-Side Comparison")
    col_card_A, col_card_B = st.columns(2)
    
    val_A = numeric_value(asset_A['market_value'])
    val_B = numeric_value(asset_B['market_value'])
    
    def calculate_3yr_score(row):
        pos = row['position']
        val = numeric_value(row['market_value'])
        
        if pd.isna(pos) or not pos:
            return min(95, max(40, int(val / 65)))
            
        rank = numeric_value(row['overall_rank'], fallback=300)
        base_score = max(5, int(100 - (rank / 3)))
        
        if pos == 'QB':
            longevity_bonus = 8
        elif pos == 'WR':
            longevity_bonus = 5
        elif pos == 'TE':
            longevity_bonus = 3
        else:
            longevity_bonus = -5
            
        return min(99, max(5, base_score + longevity_bonus))

    score_A = calculate_3yr_score(asset_A)
    score_B = calculate_3yr_score(asset_B)

    with col_card_A:
        asset_a_name = safe_display(asset_A['player_display_name'])
        asset_a_position = safe_display(asset_A['position'], "Draft Pick")
        asset_a_team = safe_display(asset_A['team'])
        asset_a_tier = safe_display(asset_A['tier'])
        st.markdown(f"""
        <div class="metric-card" style="border-left: 5px solid #10B981; background-color: #F9FAFB; padding: 20px; border-radius: 8px;">
            <h3 style="margin-top: 0; color: #065F46;">{asset_a_name}</h3>
            <p><b>Position:</b> {asset_a_position}</p>
            <p><b>Team:</b> {asset_a_team}</p>
            <p><b>Market Value:</b> <span style="font-size: 1.6rem; font-weight: 800; color: #10B981;">{val_A}</span></p>
            <p><b>Overall Rank:</b> #{asset_A['overall_rank'] or 'N/A'}</p>
            <p><b>Position Rank:</b> #{asset_A['position_rank'] or 'N/A'}</p>
            <p><b>Tier:</b> {asset_a_tier}</p>
            <hr style="margin: 10px 0; border-color: #E5E7EB;"/>
            <p style="margin-bottom: 0;"><b>🛡️ 3-Year Dynasty Score:</b> <span style="font-size: 1.3rem; font-weight: 700; color: #065F46;">{score_A}/100</span></p>
        </div>
        """, unsafe_allow_html=True)

    with col_card_B:
        asset_b_name = safe_display(asset_B['player_display_name'])
        asset_b_position = safe_display(asset_B['position'], "Draft Pick")
        asset_b_team = safe_display(asset_B['team'])
        asset_b_tier = safe_display(asset_B['tier'])
        st.markdown(f"""
        <div class="metric-card" style="border-left: 5px solid #3B82F6; background-color: #F9FAFB; padding: 20px; border-radius: 8px;">
            <h3 style="margin-top: 0; color: #1E40AF;">{asset_b_name}</h3>
            <p><b>Position:</b> {asset_b_position}</p>
            <p><b>Team:</b> {asset_b_team}</p>
            <p><b>Market Value:</b> <span style="font-size: 1.6rem; font-weight: 800; color: #3B82F6;">{val_B}</span></p>
            <p><b>Overall Rank:</b> #{asset_B['overall_rank'] or 'N/A'}</p>
            <p><b>Position Rank:</b> #{asset_B['position_rank'] or 'N/A'}</p>
            <p><b>Tier:</b> {asset_b_tier}</p>
            <hr style="margin: 10px 0; border-color: #E5E7EB;"/>
            <p style="margin-bottom: 0;"><b>🛡️ 3-Year Dynasty Score:</b> <span style="font-size: 1.3rem; font-weight: 700; color: #1E40AF;">{score_B}/100</span></p>
        </div>
        """, unsafe_allow_html=True)

    # Difference & recommendation
    diff = abs(val_A - val_B)
    st.markdown("#### ⚖️ Value Difference Analysis")
    if val_A > val_B:
        st.success(f"📈 **{asset_A['player_display_name']}** has a higher value than **{asset_B['player_display_name']}** by **{diff} points**.")
    elif val_B > val_A:
        st.info(f"📈 **{asset_B['player_display_name']}** has a higher value than **{asset_A['player_display_name']}** by **{diff} points**.")
    else:
        st.warning("⚖️ Both assets are valued equally by the market.")

    # Deep AI 3-Year Outlook using Gemini
    st.markdown("#### 🧠 AI 3-Year Outlook Analysis")
    st.markdown("Use Gemini to analyze their metrics and crawl recent team news for 3-year outlook projections.")

    active_gemini_key = os.environ.get("GEMINI_API_KEY", "")
    if not active_gemini_key:
        st.info("⚠️ Enter your **Gemini API Key** in the sidebar to activate the AI Analysis option.")
    else:
        if st.button("🧠 Run AI 3-Year Outlook Analysis", type="primary"):
            with st.spinner("AI is fetching stats, injury reports, and crawling web news for both players..."):
                try:
                    # 1. Fetch metrics from BQ
                    from google.cloud import bigquery
                    bq_client = bigquery.Client(project=BIGQUERY_PROJECT_ID)
                    
                    def query_player_history(name):
                        q = f"""
                            SELECT season, week, rushing_yards, rushing_tds, receiving_yards, receiving_tds, receptions, targets, fantasy_points_ppr
                            FROM `{BIGQUERY_PROJECT_ID}.fantasy_football_brain.weekly_metrics`
                            WHERE LOWER(player_display_name) = LOWER(@name)
                            ORDER BY season DESC, week DESC LIMIT 10
                        """
                        jc = bigquery.QueryJobConfig(query_parameters=[bigquery.ScalarQueryParameter("name", "STRING", name)])
                        return bq_client.query(q, job_config=jc).to_dataframe()

                    hist_A = query_player_history(asset_A['player_display_name'])
                    hist_B = query_player_history(asset_B['player_display_name'])

                    # 2. Get stored external verification snippets without bypassing search cost controls.
                    def get_stored_news(name):
                        try:
                            q = f"""
                                SELECT title, snippet, source_name, searched_at
                                FROM `{BIGQUERY_PROJECT_ID}.fantasy_football_brain.analytics_external_context_search_results`
                                WHERE LOWER(player_name) = LOWER(@name)
                                ORDER BY searched_at DESC, result_rank ASC
                                LIMIT 3
                            """
                            jc = bigquery.QueryJobConfig(
                                query_parameters=[bigquery.ScalarQueryParameter("name", "STRING", name)]
                            )
                            news_df = bq_client.query(q, job_config=jc).to_dataframe()
                            if news_df.empty:
                                return "No stored external verification leads found. Run External Player Context Verification first if current news matters."
                            return "\n".join(
                                f"Title: {row.title}\nSource: {row.source_name}\nSnippet: {row.snippet}"
                                for row in news_df.itertuples(index=False)
                            )
                        except Exception:
                            return "No stored external verification leads found."

                    news_A = get_stored_news(asset_A['player_display_name']) if not pd.isna(asset_A['position']) else ""
                    news_B = get_stored_news(asset_B['player_display_name']) if not pd.isna(asset_B['position']) else ""

                    # 3. Call Gemini
                    import google.generativeai as genai
                    genai.configure(api_key=active_gemini_key)
                    model = genai.GenerativeModel('gemini-3.5-flash')
                    
                    prompt = f"""
                    Compare these two fantasy football assets side-by-side:
                    
                    Asset A: {asset_A['player_display_name']} ({asset_A['position'] if not pd.isna(asset_A['position']) else 'Pick'})
                    - Market Value: {val_A}
                    - Overall Rank: {asset_A['overall_rank']}
                    - Recent Stats:\n{hist_A.to_string(index=False) if not hist_A.empty else 'No stats available'}
                    - Recent News:\n{news_A}
                    
                    Asset B: {asset_B['player_display_name']} ({asset_B['position'] if not pd.isna(asset_B['position']) else 'Pick'})
                    - Market Value: {val_B}
                    - Overall Rank: {asset_B['overall_rank']}
                    - Recent Stats:\n{hist_B.to_string(index=False) if not hist_B.empty else 'No stats available'}
                    - Recent News:\n{news_B}
                    
                    Provide a detailed 3-year outlook comparison. Ground your comparison in age, position value degradation, offensive environment, and current news/injury profiles.
                    Conclude with:
                    1. Who is the safer dynasty asset?
                    2. Who has the higher ceiling?
                    3. What are their respective AI 3-Year Outlook Scores (0-100)?
                    """
                    
                    res = model.generate_content(prompt)
                    st.markdown("### 🧠 AI Dynasty Comparison Report")
                    st.write(res.text)
                except Exception as ex:
                    st.error(f"Failed to generate AI analysis: {ex}")

view_mode = st.query_params.get("view", "default")
if view_mode == "broadcast":
    st.markdown("""
        <style>
            [data-testid="stSidebar"] {display: none !important;}
            [data-testid="stHeader"] {display: none !important;}
            .block-container {padding-top: 2rem !important; padding-bottom: 2rem !important;}
        </style>
    """, unsafe_allow_html=True)
    render_ai_cohost()
    st.stop()

# --- SIDEBAR CONFIGURATION ---
st.sidebar.image("https://img.icons8.com/color/96/american-football.png", width=80)
st.sidebar.title("NFL Studio Setup")

# Low-profile Logout Button
if st.sidebar.button("🔒 Logout", key="logout_btn", use_container_width=True):
    st.session_state.clear()
    st.rerun()

st.sidebar.markdown("Configure credentials and execution paths below.")

# Google Cloud service account JSON path
gcp_key_path = st.sidebar.text_input(
    "GCP Service Account JSON Path",
    value=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", ""),
    placeholder="e.g. C:\\keys\\gcp-credentials.json",
    help="Absolute file path to your service account key JSON file."
)

# Dynamically update the main environment variable in Python
if gcp_key_path:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = gcp_key_path
    st.sidebar.success("Credentials path loaded into environment.")
else:
    # Explicitly clear env key to ensure fallback to default metadata server
    os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)
    st.sidebar.info("Using Application Default Credentials (ADC) or Metadata Server role.")

# Gemini API key for AI assistant
gemini_api_key = os.environ.get("GEMINI_API_KEY")
if gemini_api_key:
    st.sidebar.success("Gemini API key loaded from environment.")
else:
    gemini_key_input = st.sidebar.text_input(
        "Gemini API Key",
        type="password",
        placeholder="e.g. AIzaSy...",
        help="Google AI Studio Gemini API Key for the data assistant."
    )
    if gemini_key_input:
        os.environ["GEMINI_API_KEY"] = gemini_key_input

# Warehouse Metrics in Sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### Data Warehouse Status")
active_tables, total_size_mb = get_warehouse_metrics()
st.sidebar.metric(label="Active Tables", value=f"{active_tables}")
st.sidebar.metric(label="Total Data Size", value=f"{total_size_mb:.2f} MB")

st.sidebar.markdown("---")
app_version = os.environ.get("APP_VERSION", "dev")
app_commit = os.environ.get("APP_COMMIT", "unknown")
cloud_run_revision = os.environ.get("K_REVISION", "local")
st.sidebar.caption(f"Version: {app_version}")
st.sidebar.caption(f"Commit: {app_commit[:7] if app_commit != 'unknown' else app_commit}")
st.sidebar.caption(f"Revision: {cloud_run_revision}")

# --- MAIN PAGE HEADER ---
st.markdown("<div class='main-title'>🏈 NFL Data Studio Dashboard</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Manage, ingest, and validate historical play-by-play & player metrics pipeline into Google BigQuery</div>", unsafe_allow_html=True)

# Layout Tabs
tab_ai, tab_segments, tab_ingest, tab_validate, tab_analyzer = st.tabs([
    "💬 Pigskin",
    "📊 Segments",
    "🚀 Run Ingestion Pipeline",
    "🔍 Verification & Partition Testing",
    "📊 Trade & Value Analyzer",
])

# Subprocess Execution Logic with Live Streaming
def run_subprocess_live(args, custom_env=None):
    """
    Executes a command list via Popen and streams standard output line-by-line in real-time.
    """
    # Merge custom environment
    env = os.environ.copy()
    if custom_env:
        env.update(custom_env)
    
    # If the service key path is empty, explicitly drop the credential variable
    # to force background scripts to check the Cloud's Metadata Server / ADC.
    if not custom_env or "GOOGLE_APPLICATION_CREDENTIALS" not in custom_env:
        env.pop("GOOGLE_APPLICATION_CREDENTIALS", None)

    status_area = st.empty()
    status_area.info("⏳ Process initialized. Preparing log stream...")

    log_expander = st.expander("Live Subprocess Console Output", expanded=True)
    log_area = log_expander.empty()

    accumulated_logs = []
    
    try:
        # Resolve python executable in active environment
        python_bin = get_python_executable()
        full_command = [python_bin] + args

        # Trigger Popen (redirecting stderr to stdout to read both at once)
        process = subprocess.Popen(
            full_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            cwd=PROJECT_ROOT,
            env=env
        )

        # Read streams in real-time
        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            if line:
                accumulated_logs.append(line)
                # Render to UI codeblock
                log_area.code("".join(accumulated_logs), language="log")

        return_code = process.wait()
        
        if return_code == 0:
            status_area.success("✔ Subprocess completed successfully. Review the final log lines above before refreshing.")
        else:
            status_area.error(f"❌ Subprocess failed with exit code: {return_code}")
        return return_code
            
    except Exception as e:
        status_area.error(f"❌ Critical exception during subprocess execution: {e}")
        return None

def get_sleeper_viewer_team_context(console_context):
    from google.cloud import bigquery

    client = bigquery.Client(project=BIGQUERY_PROJECT_ID)
    filters = ["league_id = @league_id", "week = @week"]
    query_parameters = [
        bigquery.ScalarQueryParameter("league_id", "STRING", console_context["league_id"]),
        bigquery.ScalarQueryParameter("week", "INT64", int(console_context["week"])),
    ]
    viewer_filters = []

    if console_context.get("roster_id"):
        viewer_filters.append("viewer_roster_id = @roster_id")
        query_parameters.append(bigquery.ScalarQueryParameter("roster_id", "INT64", int(console_context["roster_id"])))
    if console_context.get("username"):
        viewer_filters.append("LOWER(viewer_username) = LOWER(@username)")
        query_parameters.append(bigquery.ScalarQueryParameter("username", "STRING", console_context["username"]))
    if console_context.get("team_name"):
        viewer_filters.append("LOWER(viewer_team_name) = LOWER(@team_name)")
        query_parameters.append(bigquery.ScalarQueryParameter("team_name", "STRING", console_context["team_name"]))
    if console_context.get("display_name"):
        viewer_filters.append("LOWER(viewer_display_name) = LOWER(@display_name)")
        query_parameters.append(bigquery.ScalarQueryParameter("display_name", "STRING", console_context["display_name"]))

    if viewer_filters:
        filters.append("(" + " OR ".join(viewer_filters) + ")")

    snapshot_sql = f"""
        SELECT snapshot_at, league_id, season, week, viewer_roster_id, viewer_username,
               viewer_display_name, viewer_team_name, matchup_id, points
        FROM `{BIGQUERY_PROJECT_ID}.fantasy_football_brain.sleeper_viewer_team_snapshots`
        WHERE {" AND ".join(filters)}
        ORDER BY snapshot_at DESC
        LIMIT 1
    """
    job_config = bigquery.QueryJobConfig(query_parameters=query_parameters)
    snapshot_df = client.query(snapshot_sql, job_config=job_config).to_dataframe()
    if snapshot_df.empty:
        return "No loaded Sleeper viewer-team snapshot matched this console context."

    snapshot = snapshot_df.iloc[0]
    roster_id = int(snapshot["viewer_roster_id"])
    league_id = str(snapshot["league_id"])
    week = int(snapshot["week"])

    roster_sql = f"""
        WITH latest AS (
            SELECT MAX(snapshot_at) AS snapshot_at
            FROM `{BIGQUERY_PROJECT_ID}.fantasy_football_brain.sleeper_roster_players`
            WHERE league_id = @league_id
              AND week = @week
              AND roster_id = @roster_id
        ),
        truth AS (
            SELECT
                player_name,
                position,
                ANY_VALUE(current_team) AS current_team,
                ANY_VALUE(roster_status) AS roster_status,
                AVG(role_quality_score) AS avg_role_quality_score,
                AVG(points_over_role_score) AS avg_points_over_role_score,
                AVG(role_fragility_score) AS avg_role_fragility_score,
                AVG(fantasy_points_ppr) AS avg_ppr,
                AVG(target_share) AS avg_target_share,
                AVG(wopr) AS avg_wopr,
                AVG(offense_pct) AS avg_offense_pct,
                MAX(analytical_verdict) AS sample_verdict
            FROM `{BIGQUERY_PROJECT_ID}.fantasy_football_brain.analytics_player_weekly_truth`
            WHERE season >= 2024
            GROUP BY player_name, position
        )
        SELECT
            rp.player_name,
            rp.position,
            rp.team AS sleeper_team,
            rp.status,
            rp.injury_status,
            rp.is_starter,
            rp.is_taxi,
            rp.is_reserve,
            lp.points AS week_points,
            truth.current_team,
            truth.roster_status,
            truth.avg_role_quality_score,
            truth.avg_points_over_role_score,
            truth.avg_role_fragility_score,
            truth.avg_ppr,
            truth.avg_target_share,
            truth.avg_wopr,
            truth.avg_offense_pct,
            truth.sample_verdict
        FROM `{BIGQUERY_PROJECT_ID}.fantasy_football_brain.sleeper_roster_players` rp
        JOIN latest ON rp.snapshot_at = latest.snapshot_at
        LEFT JOIN `{BIGQUERY_PROJECT_ID}.fantasy_football_brain.sleeper_lineups` lp
          ON lp.league_id = rp.league_id
         AND lp.week = rp.week
         AND lp.roster_id = rp.roster_id
         AND lp.sleeper_player_id = rp.sleeper_player_id
         AND lp.snapshot_at = rp.snapshot_at
        LEFT JOIN truth
          ON LOWER(truth.player_name) = LOWER(rp.player_name)
         AND truth.position = rp.position
        WHERE rp.league_id = @league_id
          AND rp.week = @week
          AND rp.roster_id = @roster_id
        ORDER BY rp.is_starter DESC, rp.position, rp.player_name
        LIMIT 70
    """
    roster_config = bigquery.QueryJobConfig(query_parameters=[
        bigquery.ScalarQueryParameter("league_id", "STRING", league_id),
        bigquery.ScalarQueryParameter("week", "INT64", week),
        bigquery.ScalarQueryParameter("roster_id", "INT64", roster_id),
    ])
    roster_df = client.query(roster_sql, job_config=roster_config).to_dataframe()

    waiver_context = "Sleeper available-player pool was not loaded for this snapshot."
    waiver_sql = f"""
        WITH latest AS (
            SELECT MAX(snapshot_at) AS snapshot_at
            FROM `{BIGQUERY_PROJECT_ID}.fantasy_football_brain.sleeper_available_players`
            WHERE league_id = @league_id
              AND week = @week
        ),
        truth AS (
            SELECT
                player_name,
                position,
                ANY_VALUE(current_team) AS current_team,
                ANY_VALUE(roster_status) AS roster_status,
                AVG(role_quality_score) AS avg_role_quality_score,
                AVG(points_over_role_score) AS avg_points_over_role_score,
                AVG(role_fragility_score) AS avg_role_fragility_score,
                AVG(fantasy_points_ppr) AS avg_ppr,
                AVG(target_share) AS avg_target_share,
                AVG(wopr) AS avg_wopr,
                AVG(offense_pct) AS avg_offense_pct,
                MAX(analytical_verdict) AS sample_verdict
            FROM `{BIGQUERY_PROJECT_ID}.fantasy_football_brain.analytics_player_weekly_truth`
            WHERE season >= 2024
            GROUP BY player_name, position
        )
        SELECT
            ap.player_name,
            ap.position,
            ap.team AS sleeper_team,
            ap.status,
            ap.injury_status,
            ap.depth_chart_position,
            ap.depth_chart_order,
            truth.current_team,
            truth.roster_status,
            truth.avg_role_quality_score,
            truth.avg_points_over_role_score,
            truth.avg_role_fragility_score,
            truth.avg_ppr,
            truth.avg_target_share,
            truth.avg_wopr,
            truth.avg_offense_pct,
            truth.sample_verdict
        FROM `{BIGQUERY_PROJECT_ID}.fantasy_football_brain.sleeper_available_players` ap
        JOIN latest ON ap.snapshot_at = latest.snapshot_at
        LEFT JOIN truth
          ON LOWER(truth.player_name) = LOWER(ap.player_name)
         AND truth.position = ap.position
        WHERE ap.league_id = @league_id
          AND ap.week = @week
          AND ap.position IN ('QB', 'RB', 'WR', 'TE')
        ORDER BY
            COALESCE(truth.avg_role_quality_score, 0) DESC,
            COALESCE(truth.avg_wopr, 0) DESC,
            COALESCE(truth.avg_ppr, 0) DESC,
            ap.position,
            ap.player_name
        LIMIT 45
    """
    try:
        waiver_config = bigquery.QueryJobConfig(query_parameters=[
            bigquery.ScalarQueryParameter("league_id", "STRING", league_id),
            bigquery.ScalarQueryParameter("week", "INT64", week),
        ])
        waiver_df = client.query(waiver_sql, job_config=waiver_config).to_dataframe()
        waiver_context = waiver_df.to_csv(index=False) if not waiver_df.empty else "No fantasy-relevant available players found for this loaded Sleeper snapshot."
    except Exception as ex:
        waiver_context = f"Sleeper available-player pool unavailable: {ex}"

    return (
        "Latest Sleeper viewer-team snapshot:\n"
        f"{snapshot_df.to_csv(index=False)}\n"
        "Viewer roster joined to AI vs Vibes role context:\n"
        f"{roster_df.to_csv(index=False)}\n"
        "Best available waiver/free agents joined to AI vs Vibes role context:\n"
        f"{waiver_context}"
    )

def render_terminal_messages(messages):
    rows = []
    for message in messages:
        prompt = "you" if message["role"] == "user" else "pigskin"
        content = html.escape(message["content"]).replace("\n", "<br>")
        rows.append(f"<div><span class='terminal-prompt'>{prompt}$</span> {content}</div>")
    terminal_body = "".join(rows)
    st.markdown(
        f"""
        <style>
            .sleeper-terminal {{
                background: #080c12;
                border: 1px solid #263241;
                border-radius: 8px;
                padding: 16px;
                min-height: 220px;
                max-height: 520px;
                overflow-y: auto;
                color: #d7f7df;
                font-family: Consolas, Monaco, 'Courier New', monospace;
                font-size: 0.92rem;
                line-height: 1.55;
                white-space: normal;
            }}
            .terminal-prompt {{
                color: #35ff7a;
                font-weight: 700;
            }}
        </style>
        <div class="sleeper-terminal">{terminal_body}</div>
        """,
        unsafe_allow_html=True,
    )

def render_sleeper_viewer_console():
    console_context = st.session_state.get("sleeper_viewer_console_context")
    if not console_context:
        st.info("Load a Sleeper viewer team above to start the team-review console.")
        return

    st.markdown("#### Team Review Console")
    st.caption(
        f"Context: league `{console_context['league_id']}`, week `{console_context['week']}`"
    )

    messages = st.session_state.setdefault("sleeper_viewer_console_messages", [
        {
            "role": "assistant",
            "content": "Viewer-team console online. Ask for a roster audit, starter check, trade bait, waiver priorities, or a show-ready roast.",
        }
    ])
    render_terminal_messages(messages)

    with st.form("sleeper_viewer_console_form", clear_on_submit=True):
        prompt = st.text_input(
            "Terminal prompt",
            placeholder="e.g. audit this team and tell me where it is fragile",
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("Send to Pigskin")

    if submitted and prompt.strip():
        messages.append({"role": "user", "content": prompt.strip()})
        active_gemini_key = os.environ.get("GEMINI_API_KEY", "")
        if not active_gemini_key:
            messages.append({"role": "assistant", "content": "I've got a problem: Gemini is not configured, so this console cannot talk yet."})
            st.rerun()

        try:
            viewer_context = get_sleeper_viewer_team_context(console_context)
            import google.generativeai as genai

            genai.configure(api_key=active_gemini_key)
            model = genai.GenerativeModel("gemini-3.5-flash")
            recent_history = "\n".join(
                f"{message['role']}: {message['content']}"
                for message in messages[-8:]
            )
            response = model.generate_content(f"""
You are Pigskin, the AI vs Vibes co-host. This is a terminal-style Sleeper viewer-team review console.
Be ruthless, funny, and useful. Criticize weak fantasy process, fragile roster construction, stale name value, and box-score traps.
Do not invent facts. Use only the BigQuery context below and the conversation history. If the context is insufficient, say what is missing.
When the user asks about waivers, free agents, upgrades, drops, or bench clutter, use the "Best available waiver/free agents" context. If that section says it is unavailable, say the waiver pool is missing instead of naming made-up pickups.
Keep the answer concise enough for an interactive console.

BigQuery context:
{viewer_context}

Conversation:
{recent_history}
""")
            messages.append({"role": "assistant", "content": response.text})
        except Exception as ex:
            messages.append({
                "role": "assistant",
                "content": f"I've got a problem: the Sleeper viewer-team BigQuery context failed, so I am not going to fake a roster take. Error: {ex}",
            })
        st.rerun()

def render_sleeper_viewer_team_analysis():
    st.markdown("### Sleeper Viewer Team Analysis")
    st.caption("Load one public Sleeper league/team snapshot into BigQuery so the AI can analyze the viewer's roster.")
    sleeper_league_id = st.text_input("Sleeper League ID", placeholder="e.g. 1130687436515831808")
    sleeper_week = st.number_input("Sleeper Week", min_value=1, max_value=18, value=1, step=1)
    col_roster_id, col_username, col_team_name = st.columns(3)
    with col_roster_id:
        sleeper_roster_id = st.text_input("Roster ID", placeholder="e.g. 4")
    with col_username:
        sleeper_username = st.text_input("Username", placeholder="optional")
    with col_team_name:
        sleeper_team_name = st.text_input("Team Name", placeholder="e.g. Shartnado")
    sleeper_display_name = st.text_input("Display Name", placeholder="optional")

    if st.button("🏈 Load Sleeper Viewer Team", type="secondary"):
        if not sleeper_league_id.strip():
            st.error("Enter a Sleeper league ID.")
        elif not any([sleeper_roster_id.strip(), sleeper_username.strip(), sleeper_team_name.strip(), sleeper_display_name.strip()]):
            st.error("Enter roster ID, username, team name, or display name so I can identify the viewer team.")
        else:
            cmd_args = [
                "-m",
                "src.ingest_sleeper_league",
                "--league-id",
                sleeper_league_id.strip(),
                "--week",
                str(int(sleeper_week)),
            ]
            if sleeper_roster_id.strip():
                cmd_args.extend(["--roster-id", sleeper_roster_id.strip()])
            if sleeper_username.strip():
                cmd_args.extend(["--username", sleeper_username.strip()])
            if sleeper_team_name.strip():
                cmd_args.extend(["--team-name", sleeper_team_name.strip()])
            if sleeper_display_name.strip():
                cmd_args.extend(["--display-name", sleeper_display_name.strip()])

            exec_env = {}
            if gcp_key_path:
                exec_env["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.abspath(gcp_key_path)

            return_code = run_subprocess_live(cmd_args, custom_env=exec_env)
            if return_code == 0:
                st.session_state.sleeper_viewer_console_context = {
                    "league_id": sleeper_league_id.strip(),
                    "week": int(sleeper_week),
                    "roster_id": sleeper_roster_id.strip(),
                    "username": sleeper_username.strip(),
                    "team_name": sleeper_team_name.strip(),
                    "display_name": sleeper_display_name.strip(),
                }
                st.session_state.sleeper_viewer_console_messages = [
                    {
                        "role": "assistant",
                        "content": "Snapshot loaded. Viewer-team console online. Ask me what is cooked, what is real, and what needs to be fixed before this roster starts paying vibes tax.",
                    }
                ]

    render_sleeper_viewer_console()

# --- TAB 1: INGESTION PIPELINE ---
with tab_ingest:
    st.markdown("### Run Statistics Ingestion")
    st.markdown("Trigger historical ingestion by downloading from APIs and loading directly into partitioned BigQuery tables.")
    
    col1, col2 = st.columns(2)
    with col1:
        seasons_input = st.text_input(
            "Target Seasons",
            value="2024,2025,2026",
            help="Specify comma-separated years to extract and load. Note that cached seasons will bypass APIs entirely."
        )
    with col2:
        write_disp = st.selectbox(
            "BigQuery Write Disposition",
            options=["WRITE_TRUNCATE", "WRITE_APPEND"],
            index=0,
            help="WRITE_TRUNCATE completely overwrites existing tables. WRITE_APPEND appends records to the tables."
        )

    # Validate inputs
    seasons_clean = seasons_input.strip()
    
    if st.button("🚀 Run Ingestion Pipeline", type="primary"):
        if not seasons_clean:
            st.error("Please provide at least one target season.")
        else:
            # Build CLI args for pipeline script
            cmd_args = ["-m", "src.pipeline", "--seasons", seasons_clean, "--write-disposition", write_disp]
            
            # Setup dynamic env
            exec_env = {}
            if gcp_key_path:
                exec_env["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.abspath(gcp_key_path)

            run_subprocess_live(cmd_args, custom_env=exec_env)

    if st.button("🚀 Ingest Realtime Player News", type="secondary"):
        cmd_args = ["-m", "src.ingest_news"]
        
        exec_env = {}
        if gcp_key_path:
            exec_env["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.abspath(gcp_key_path)

        run_subprocess_live(cmd_args, custom_env=exec_env)

    if st.button("🧠 Load Context Event Ledger", type="secondary"):
        cmd_args = ["-m", "src.ingest_context_events"]

        exec_env = {}
        if gcp_key_path:
            exec_env["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.abspath(gcp_key_path)

        run_subprocess_live(cmd_args, custom_env=exec_env)

    st.markdown("### Ingest Market Values")
    st.caption("Fetch current player and draft pick trade values from the FantasyCalc API and load them into BigQuery.")
    is_dynasty_ingest = st.checkbox("Dynasty Values", value=True, help="If checked, fetches dynasty values. Otherwise, fetches redraft values.")
    
    if st.button("📊 Ingest FantasyCalc Market Values", type="secondary"):
        cmd_args = ["-m", "src.fetch_market_values"]
        if not is_dynasty_ingest:
            cmd_args.append("--redraft")
            
        exec_env = {}
        if gcp_key_path:
            exec_env["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.abspath(gcp_key_path)

        run_subprocess_live(cmd_args, custom_env=exec_env)

    st.markdown("### Player Context Verification")
    verify_player = st.text_input(
        "Player to verify",
        placeholder="e.g. Michael Pittman",
        help="Runs one cost-capped external verification search and stores returned results in BigQuery."
    )
    col_team, col_season = st.columns(2)
    with col_team:
        verify_team = st.text_input("Context team", placeholder="e.g. IND or PIT")
    with col_season:
        verify_season = st.text_input("Context season", placeholder="e.g. 2025")
    verify_query = st.text_input(
        "Optional exact search query",
        placeholder='"Michael Pittman" "Daniel Jones" injury Colts'
    )

    if st.button("🔎 Verify Player Context", type="secondary"):
        if not verify_player.strip():
            st.error("Enter a player name before running outside verification.")
        else:
            cmd_args = ["-m", "src.verify_player_context", "--player", verify_player.strip()]
            if verify_team.strip():
                cmd_args.extend(["--team", verify_team.strip()])
            if verify_season.strip():
                cmd_args.extend(["--season", verify_season.strip()])
            if verify_query.strip():
                cmd_args.extend(["--query", verify_query.strip()])
            cmd_args.extend(["--max-results", os.environ.get("EXTERNAL_SEARCH_MAX_RESULTS", "3")])

            exec_env = {}
            if gcp_key_path:
                exec_env["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.abspath(gcp_key_path)

            run_subprocess_live(cmd_args, custom_env=exec_env)

    st.markdown("### Ingest College Stats (CFBD API)")
    st.caption("Fetch baseline college player stats for a specific season from CollegeFootballData.com.")
    col_cfbd1, col_cfbd2 = st.columns(2)
    with col_cfbd1:
        cfbd_season = st.number_input("CFBD Season", min_value=2010, max_value=2030, value=2024, step=1)
    with col_cfbd2:
        cfbd_key = st.text_input("CFBD API Key", type="password", placeholder="e.g. mock or your_cfbd_key")
        
    if st.button("🚀 Ingest CFBD College Stats", type="secondary"):
        if not cfbd_key.strip():
            st.error("A CFBD API Key (or 'mock') is required to run the ingestion.")
        else:
            cmd_args = ["-m", "src.ingest_college_data", "--season", str(cfbd_season)]
            exec_env = {}
            exec_env["CFBD_API_KEY"] = cfbd_key.strip()
            if gcp_key_path:
                exec_env["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.abspath(gcp_key_path)
            run_subprocess_live(cmd_args, custom_env=exec_env)

    st.markdown("### Upload Rookie Scouting CSV")
    st.caption("Import advanced player profiling spreadsheets (PFF, Reception Perception, or custom charts) directly into the BigQuery database.")
    scouting_file = st.file_uploader("Choose a CSV file", type=["csv"], key="scouting_csv_uploader")
    
    if scouting_file is not None:
        import pandas as pd
        try:
            df_scout = pd.read_csv(scouting_file)
            st.success(f"Successfully loaded '{scouting_file.name}' with {len(df_scout)} rows!")
            
            # Show a small preview
            st.dataframe(df_scout.head(3))
            
            st.markdown("#### Map CSV Columns to Database Fields")
            cols_options = ["None"] + list(df_scout.columns)
            
            def find_default_col(options, candidates):
                for c in candidates:
                    for opt in options:
                        if c.lower() in str(opt).lower():
                            return opt
                return "None"
            
            col_map = {}
            c_season = st.selectbox("Season / Draft Year (Required)", cols_options, index=cols_options.index(find_default_col(cols_options, ["season", "year", "draft"])))
            c_name = st.selectbox("Player Name (Required)", cols_options, index=cols_options.index(find_default_col(cols_options, ["player", "name"])))
            c_pos = st.selectbox("Position", cols_options, index=cols_options.index(find_default_col(cols_options, ["position", "pos"])))
            c_college = st.selectbox("College / School", cols_options, index=cols_options.index(find_default_col(cols_options, ["college", "school"])))
            c_yac = st.selectbox("Yards After Contact/Attempt", cols_options, index=cols_options.index(find_default_col(cols_options, ["contact", "yac_per", "yac/"])))
            c_yprr = st.selectbox("Yards Per Route Run (YPRR)", cols_options, index=cols_options.index(find_default_col(cols_options, ["yprr", "route_run", "route"])))
            c_target = st.selectbox("College Target Share", cols_options, index=cols_options.index(find_default_col(cols_options, ["target_share", "target%"])))
            c_radius = st.selectbox("Catch Radius Grade", cols_options, index=cols_options.index(find_default_col(cols_options, ["radius", "catch_rad"])))
            c_man = st.selectbox("Success vs Man Coverage", cols_options, index=cols_options.index(find_default_col(cols_options, ["man", "vs_man"])))
            c_zone = st.selectbox("Success vs Zone Coverage", cols_options, index=cols_options.index(find_default_col(cols_options, ["zone", "vs_zone"])))
            c_press = st.selectbox("Success vs Press Coverage", cols_options, index=cols_options.index(find_default_col(cols_options, ["press", "vs_press"])))
            c_sep = st.selectbox("Average Separation", cols_options, index=cols_options.index(find_default_col(cols_options, ["separation", "sep"])))
            
            scout_source = st.text_input("Data Source Name", value="Reception Perception")
            
            if st.button("📤 Upload and Import Scouting Metrics", type="primary"):
                if c_season == "None" or c_name == "None":
                    st.error("❌ 'Season / Draft Year' and 'Player Name' are required fields.")
                else:
                    with st.spinner("Uploading to BigQuery..."):
                        try:
                            # Map columns
                            mapped_df = pd.DataFrame()
                            mapped_df["season"] = df_scout[c_season].astype("int64")
                            mapped_df["player_name"] = df_scout[c_name].astype(str)
                            
                            # Helper to map nullable float/string columns
                            def map_col(target_name, selected_col, is_float=True):
                                if selected_col != "None":
                                    if is_float:
                                        mapped_df[target_name] = pd.to_numeric(df_scout[selected_col], errors="coerce")
                                    else:
                                        mapped_df[target_name] = df_scout[selected_col].astype(str)
                                else:
                                    mapped_df[target_name] = None
                                    
                            map_col("position", c_pos, is_float=False)
                            map_col("college", c_college, is_float=False)
                            map_col("yards_after_contact_per_attempt", c_yac)
                            map_col("yards_per_route_run", c_yprr)
                            map_col("college_target_share", c_target)
                            map_col("catch_radius_grade", c_radius)
                            map_col("success_rate_vs_man", c_man)
                            map_col("success_rate_vs_zone", c_zone)
                            map_col("success_rate_vs_press", c_press)
                            map_col("avg_separation_inches", c_sep)
                            mapped_df["data_source"] = scout_source
                            
                            # Connect and load to BigQuery
                            from google.cloud import bigquery
                            from src.setup_college_tables import create_college_tables

                            create_college_tables()
                            bq_proj = BIGQUERY_PROJECT_ID
                            client = bigquery.Client(project=bq_proj)
                            table_ref = f"{bq_proj}.fantasy_football_brain.rookie_scouting_metrics"
                            
                            # Perform append load
                            job_config = bigquery.LoadJobConfig(
                                write_disposition=bigquery.WriteDisposition.WRITE_APPEND
                            )
                            job = client.load_table_from_dataframe(mapped_df, table_ref, job_config=job_config)
                            job.result()
                            st.success(f"✔ Successfully loaded {len(mapped_df)} rows into '{table_ref}'!")
                        except Exception as ex:
                            st.error(f"❌ Failed to upload to BigQuery: {ex}")
        except Exception as ex:
            st.error(f"❌ Failed to parse CSV: {ex}")

# --- TAB 2: VERIFICATION ---
with tab_validate:
    st.markdown("### Range Partition Verification")
    st.markdown("Check if BigQuery datasets are successfully generated and inspect physical table metadata range partitions (no `SELECT *` executed).")
    
    if st.button("🔍 Run Validation Sweep", type="secondary"):
        cmd_args = ["validate.py"]
        
        # Setup dynamic env
        exec_env = {}
        if gcp_key_path:
            exec_env["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.abspath(gcp_key_path)
            
        run_subprocess_live(cmd_args, custom_env=exec_env)

# --- TAB 3: SEGMENTS ---
with tab_segments:
    st.markdown("### Segment Charts")
    st.markdown("Production-ready charts and data cuts for show segments. Keep the chat tab clean and use this space for visual prep.")
    render_fraud_watch_segment()
    st.divider()
    render_sleeper_viewer_team_analysis()

# --- TAB 4: AI DATA ASSISTANT ---
with tab_ai:
    render_ai_cohost()

# --- TAB 4: TRADE & VALUE ANALYZER ---
with tab_analyzer:
    render_value_analyzer()
