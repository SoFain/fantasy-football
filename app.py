import os
import sys
import subprocess
import streamlit as st

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
    """Queries BigQuery INFORMATION_SCHEMA for active tables and total data size in MB."""
    try:
        from google.cloud import bigquery
        client = bigquery.Client()
        project_id = client.project
        dataset_id = "fantasy_football_brain"
        
        query = f"""
            SELECT 
                COUNT(*) as active_tables,
                SUM(total_logical_bytes) / (1024 * 1024) as total_size_mb
            FROM `{project_id}.{dataset_id}.INFORMATION_SCHEMA.TABLE_STORAGE`
        """
        job = client.query(query)
        result = list(job.result())
        
        if result and len(result) > 0:
            row = result[0]
            tables = row.active_tables if row.active_tables else 0
            size_mb = row.total_size_mb if row.total_size_mb else 0.0
            return tables, size_mb
    except Exception as e:
        import logging
        logging.getLogger("app.metrics").warning(f"Could not fetch warehouse metrics: {e}")
    return 0, 0.0

def render_ai_cohost():
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
            """Executes a BigQuery SQL query against the fantasy_football_brain dataset and returns a CSV string of the results."""
            st.session_state.messages.append({
                "role": "tool_status",
                "status_msg": "🤖 AI Co-Host is analyzing the warehouse...",
                "code": sql_query
            })
            with st.status("🤖 AI Co-Host is analyzing the warehouse...", expanded=False) as status:
                st.code(sql_query, language="sql")
                from google.cloud import bigquery
                try:
                    bq_client = bigquery.Client()
                    query_job = bq_client.query(sql_query)
                    df = query_job.result().to_dataframe()
                    status.update(label=f"🤖 Analysis complete! ({len(df)} rows retrieved)", state="complete")
                    if df.empty:
                        return "Query executed successfully, but returned 0 rows."
                    return df.to_csv(index=False)
                except Exception as e:
                    status.update(label="❌ Query failed", state="error")
                    return f"Error executing query: {str(e)}"
                
        # Define Co-Host System Prompt
        system_prompt = f"""
    You are an expert conversational AI Data Co-Host for a Fantasy Football dashboard. You are engaging, analytical, and ready for banter.
    The active BigQuery project ID is '{os.environ.get("GCP_PROJECT", "fantasy-football-498121")}' and the dataset is 'fantasy_football_brain'.

    Here is the database schema description:
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
    You are mandated to follow a strict 3-step query expansion protocol when analyzing players:
    Step 1 (Deconstruct): Map basic player mentions to 4 core vectors: Opportunity (Snap Counts), Underlying Efficiency (Next Gen Stats/Separation), Ecosystem (Line Contracts/Injuries), and Scheme (FTN Charting).
    Step 2 (Mandatory Joins): You are PROHIBITED from querying 'weekly_metrics' in isolation. You must intrinsically craft SQL JOINS across 'weekly_snap_counts', 'ngs_receiving' (or rushing/passing), and 'ftn_charting' to establish underlying analytical context.
    Step 3 (Contrast Output): Require the final natural language output to actively contrast surface-level box scores against advanced telemetry (e.g., "While the host noted Player X only had 40 yards, the tracking data reveals an elite 85% snap share and a league-leading 3.2 yards of separation against Cover 1..."). 

    Always use your `execute_bigquery_sql` tool to fetch data before answering analytical questions.
    """
    
        if "chat_session" not in st.session_state:
            model = genai.GenerativeModel(
                'gemini-3.5-flash',
                tools=[execute_bigquery_sql],
                system_instruction=system_prompt
            )
            st.session_state.chat_session = model.start_chat(enable_automatic_function_calling=True)
        
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
                message_placeholder = st.empty()
                try:
                    response = st.session_state.chat_session.send_message(prompt)
                    message_placeholder.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"Error communicating with AI Co-Host: {e}")

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
if not gemini_api_key:
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
st.sidebar.caption(f"Version: {os.environ.get('APP_VERSION', 'Unknown')}")

# --- MAIN PAGE HEADER ---
st.markdown("<div class='main-title'>🏈 NFL Data Studio Dashboard</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Manage, ingest, and validate historical play-by-play & player metrics pipeline into Google BigQuery</div>", unsafe_allow_html=True)

# Layout Tabs
tab_ingest, tab_validate, tab_ai = st.tabs(["🚀 Run Ingestion Pipeline", "🔍 Verification & Partition Testing", "💬 AI Data Assistant"])

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
            status_area.success("✔ Subprocess completed successfully!")
            st.rerun()
        else:
            status_area.error(f"❌ Subprocess failed with exit code: {return_code}")
            
    except Exception as e:
        status_area.error(f"❌ Critical exception during subprocess execution: {e}")

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

# --- TAB 3: AI DATA ASSISTANT ---
with tab_ai:
    render_ai_cohost()
