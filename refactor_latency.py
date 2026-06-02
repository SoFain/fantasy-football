import os

file_path = 'e:/Fantasy Football/app.py'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_ai_func = """def render_ai_cohost():
    st.markdown("### 💬 AI Data Co-Host")
    st.markdown("Chat with your conversational AI co-host! It will seamlessly use BigQuery to pull contextual tracking data before responding to your analytical questions.")

    active_gemini_key = os.environ.get("GEMINI_API_KEY", "")
    if not active_gemini_key:
        st.info("⚠️ Please enter a **Gemini API Key** in the sidebar to activate the AI Co-Host.")
    else:
        # Initialize session state for messages and chat session
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        import google.generativeai as genai
        genai.configure(api_key=active_gemini_key)
    
        # Define the BigQuery tool
        def execute_bigquery_sql(sql_query: str) -> str:
            \"\"\"Executes a BigQuery SQL query against the fantasy_football_brain dataset.
            
            MANDATORY CONSTRAINTS:
            1. You must use a `LIMIT 50` on every query.
            2. Do NOT use `SELECT *`. You must explicitly select the columns you need.
            3. You must filter by partitioning keys (`season` and `week`) whenever possible.
            \"\"\"
            pass # We will execute this manually
            
        # Define Co-Host System Prompt
        system_prompt = f\"\"\"
    You are an expert conversational AI Data Co-Host for a Fantasy Football dashboard. You are engaging, analytical, and ready for banter.
    The active BigQuery project ID is '{os.environ.get("GCP_PROJECT", "fantasy-football-498121")}' and the dataset is 'fantasy_football_brain'.

    Here is the database schema description:
    
    - Table: `fantasy_football_brain.analytics_player_weekly_summary` (PRIMARY TABLE)
      Description: Pre-aggregated summary containing Snaps, Targets, EPA, Routes, and Tracking metrics.
      Columns: `season`, `week`, `player_name`, `position`, `team`, `targets`, `receptions`, `rushing_yards`, `fantasy_points_ppr`, `offense_snaps`, `offense_pct`, `epa_per_play`, `report_status`, plus dominant tracking metrics (e.g. `avg_separation`).
      *PRIORITIZE THIS TABLE for almost all queries.*
      
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

    ### The Analytical Filter Protocol ###
    You are mandated to follow a strict query protocol when analyzing players.
    You MUST default to using the `analytics_player_weekly_summary` table first. Only fallback to `play_by_play` if highly specific situational context is requested.
    Always use your `execute_bigquery_sql` tool to fetch data before answering analytical questions.
    \"\"\"
    
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
                with st.status(msg["status_msg"], state="complete"):
                    st.code(msg["code"], language="sql")
            else:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
                
        # Chat input
        if prompt := st.chat_input("Ask your co-host a question..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                try:
                    # Initial request (might be a tool call)
                    response = st.session_state.chat_session.send_message(prompt, stream=False)
                    
                    # Manual tool calling loop
                    while response.function_call:
                        fc = response.function_call
                        if fc.name == "execute_bigquery_sql":
                            sql_to_run = type(fc).to_dict(fc)["args"]["sql_query"]
                            
                            st.session_state.messages.append({
                                "role": "tool_status",
                                "status_msg": "🤖 AI Co-Host is analyzing the warehouse...",
                                "code": sql_to_run
                            })
                            with st.status("🤖 AI Co-Host is analyzing the warehouse...", expanded=False) as status:
                                st.code(sql_to_run, language="sql")
                                from google.cloud import bigquery
                                try:
                                    bq_client = bigquery.Client()
                                    query_job = bq_client.query(sql_to_run)
                                    df = query_job.result().to_dataframe()
                                    status.update(label=f"🤖 Analysis complete! ({len(df)} rows retrieved)", state="complete")
                                    result_str = df.to_csv(index=False) if not df.empty else "0 rows returned."
                                except Exception as e:
                                    status.update(label="❌ Query failed", state="error")
                                    result_str = f"Error: {str(e)}"
                            
                            import google.ai.generativelanguage as glm
                            tool_response = glm.Part(
                                function_response=glm.FunctionResponse(
                                    name="execute_bigquery_sql",
                                    response={"result": result_str}
                                )
                            )
                            # Get next response (could be another tool, or text)
                            response = st.session_state.chat_session.send_message(tool_response, stream=False)
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
"""

# Replace the old render_ai_cohost function
start_idx = -1
end_idx = -1

for i, line in enumerate(lines):
    if line.startswith("def render_ai_cohost():"):
        start_idx = i
    if start_idx != -1 and line.startswith("view_mode = st.query_params.get("):
        end_idx = i
        break

lines = lines[:start_idx] + [new_ai_func + "\n"] + lines[end_idx:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
