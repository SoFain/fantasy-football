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
    st.markdown("### 💬 Natural Language Data Assistant")
    st.markdown(
        "Ask questions about your league's statistics, rosters, or team data in plain English. "
        "Gemini will generate and execute the BigQuery SQL query to retrieve the results."
    )
    
    # Check for API key
    active_gemini_key = os.environ.get("GEMINI_API_KEY", "")
    
    if not active_gemini_key:
        st.info("⚠️ Please enter a **Gemini API Key** in the sidebar to activate the AI Assistant.")
    else:
        user_query = st.text_input(
            "What would you like to know about the league data?",
            placeholder="e.g. Show me the top 5 players by epa_per_play in 2024 with more than 50 targets."
        )
        
        if st.button("🔍 Ask Assistant", type="primary"):
            if not user_query.strip():
                 st.error("Please enter a question.")
            else:
                 with st.spinner("Gemini is analyzing schemas and generating query..."):
                     import google.generativeai as genai
                     
                     # Configure model
                     genai.configure(api_key=active_gemini_key)
                     
                     # System prompt outlining the database schema
                     system_prompt = f"""
You are an expert Google BigQuery SQL developer analyzing fantasy football data.
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

- Table: `fantasy_football_brain.active_league_rosters` (also accessible as `active_league_rosters`)
  Columns:
    - `username` (STRING) - The Sleeper league manager's username.
    - `sleeper_id` (STRING) - The Sleeper ID of the player.
    - `player_name` (STRING) - The name of the player.
    - `position` (STRING) - Player's position.
    
- Table: `fantasy_football_brain.play_by_play`
  Columns:
    - `season` (INT64)
    - `week` (INT64)
    - `play_type` (STRING) - e.g. 'pass', 'run'
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
    
- Table: `fantasy_football_brain.team_descriptions`
  Columns:
    - `team_abbr` (STRING)
    - `team_name` (STRING)

Strict Constraint: You must output ONLY the raw, executable BigQuery SQL query string. 
- Do NOT wrap your query in markdown syntax (do NOT use ```sql or ```).
- Do NOT include any explanations, introduction, or prose.
- Start the response directly with the SELECT keyword.
- Always reference tables with their fully-qualified name: `fantasy_football_brain.table_name`.

User Question: {user_query}
"""
                     try:
                         # Generate SQL query
                         # We use gemini-3.5-flash as the reasoning model
                         model = genai.GenerativeModel('gemini-3.5-flash')
                         response = model.generate_content(system_prompt)
                         sql_query = response.text.strip()
                         
                         # Defensive cleanup for any markdown wrappers if model disobeyed
                         if sql_query.startswith("```"):
                             lines = sql_query.splitlines()
                             if lines[0].startswith("```"):
                                 lines = lines[1:]
                             if lines[-1].startswith("```"):
                                 lines = lines[:-1]
                             sql_query = "\n".join(lines).strip()
                             
                         # If sql_query begins with "sql", strip it
                         if sql_query.lower().startswith("sql\n") or sql_query.lower().startswith("sql "):
                             sql_query = sql_query[3:].strip()
                             
                         st.info("🤖 SQL Query Generated!")
                         
                         # Execute SQL query on BigQuery
                         from google.cloud import bigquery
                         bq_client = bigquery.Client()
                         
                         query_job = bq_client.query(sql_query)
                         df_result = query_job.result().to_dataframe()
                         
                         st.success(f"✔ Query executed successfully! Returned {len(df_result)} rows.")
                         st.dataframe(df_result, use_container_width=True)
                         
                         # Expandable section to show code
                         with st.expander("📝 Show Generated SQL Code"):
                             st.code(sql_query, language="sql")
                             
                     except Exception as e:
                         st.error(f"❌ Error during AI query generation or execution: {e}")
                         if 'sql_query' in locals():
                             with st.expander("📝 Show Attempted SQL Code"):
                                 st.code(sql_query, language="sql")
