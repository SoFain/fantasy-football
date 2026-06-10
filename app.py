import os
import sys
import subprocess
import html
import logging
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
    page_title="AI vs Meatbags",
    page_icon="🏈",
    layout="wide",
    initial_sidebar_state="collapsed"
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
    .show-logo-frame {
        margin: 0.25rem 0 0.75rem;
    }
    .show-logo {
        display: block;
        width: min(100%, 1280px);
        height: auto;
    }
    .metric-card {
        background-color: #F3F4F6;
        border-radius: 8px;
        padding: 15px;
        border-left: 5px solid #1E3A8A;
    }
    div[data-testid="stElementContainer"]:has(.tab-action-bar) {
        position: sticky !important;
        top: 0.45rem;
        z-index: 10;
    }
    .tab-action-bar {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 0.5rem;
        margin: 0.45rem 0 1.55rem;
        padding: 0.55rem 0.65rem;
        border: 1px solid rgba(148, 163, 184, 0.24);
        border-radius: 8px;
        background: rgba(8, 12, 18, 0.92);
        backdrop-filter: blur(10px);
    }
    .tab-action-label {
        color: rgba(226, 232, 240, 0.72);
        font-size: 0.72rem;
        font-weight: 800;
        letter-spacing: 0.02em;
        text-transform: uppercase;
    }
    .bookmark-menu {
        display: flex;
        flex-wrap: wrap;
        gap: 0.45rem;
        margin: 0;
    }
    .bookmark-menu a {
        display: inline-flex;
        align-items: center;
        border: 1px solid rgba(148, 163, 184, 0.28);
        border-radius: 999px;
        padding: 0.28rem 0.65rem;
        color: #dbeafe;
        font-size: 0.82rem;
        line-height: 1.1;
        text-decoration: none;
        background: rgba(148, 163, 184, 0.08);
    }
    .bookmark-menu a:hover {
        border-color: rgba(255, 75, 75, 0.7);
        color: #ff4b4b;
    }
    .section-rule {
        margin: 2rem 0 1.05rem;
        border: 0;
        border-top: 1px solid rgba(148, 163, 184, 0.24);
    }
    .section-anchor {
        display: block;
        height: 5.5rem;
        margin-top: -5.5rem;
        visibility: hidden;
    }
    .section-subtitle {
        margin: -0.35rem 0 0.85rem;
        color: var(--text-color, #0f172a);
        opacity: 0.72;
        font-size: 0.92rem;
        line-height: 1.45;
    }
    .risk-band {
        margin: 1rem 0 1.25rem;
        padding: 0.95rem;
        border: 1px solid rgba(148, 163, 184, 0.22);
        border-radius: 8px;
        background: rgba(148, 163, 184, 0.055);
    }
    .risk-band-title {
        margin-bottom: 0.18rem;
        font-size: 0.95rem;
        font-weight: 800;
    }
    .risk-band-copy {
        margin-bottom: 0.85rem;
        color: var(--text-color, #0f172a);
        opacity: 0.68;
        font-size: 0.84rem;
        line-height: 1.45;
    }
    .risk-band.safe {
        border-left: 4px solid #22c55e;
    }
    .risk-band.external {
        border-left: 4px solid #38bdf8;
    }
    .risk-band.destructive {
        border-left: 4px solid #ef4444;
    }
    .last-run {
        margin: 0.35rem 0 0.85rem;
        color: var(--text-color, #0f172a);
        opacity: 0.66;
        font-size: 0.8rem;
    }
    .runtime-status-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(120px, 1fr));
        gap: 0.85rem;
        margin: 0.5rem 0 0.65rem;
    }
    .runtime-status-card {
        min-width: 0;
        border: 1px solid rgba(148, 163, 184, 0.22);
        border-radius: 8px;
        padding: 0.78rem 0.85rem;
        background: rgba(148, 163, 184, 0.06);
    }
    .runtime-status-label {
        margin-bottom: 0.42rem;
        color: var(--text-color, #0f172a);
        opacity: 0.72;
        font-size: clamp(0.66rem, 0.72vw, 0.78rem);
        font-weight: 700;
        line-height: 1.1;
    }
    .runtime-status-value {
        color: var(--text-color, #0f172a);
        font-size: clamp(1rem, 1.5vw, 1.45rem);
        font-weight: 700;
        line-height: 1.16;
        overflow-wrap: anywhere;
        word-break: break-word;
    }
    .runtime-status-caption {
        margin-top: 0.4rem;
        color: var(--text-color, #0f172a);
        opacity: 0.66;
        font-size: 0.8rem;
    }
    @media (max-width: 760px) {
        .runtime-status-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
        .main-title {
            font-size: 1.75rem;
            line-height: 1.1;
        }
        .show-logo-frame {
            margin-top: 0;
        }
    }
    
    /* Player Profiles Premium Layouts */
    .profile-header {
        background: linear-gradient(135deg, rgba(30, 58, 138, 0.95), rgba(15, 23, 42, 0.95));
        color: #f8fafc;
        border-radius: 12px;
        padding: 1.5rem;
        display: flex;
        align-items: center;
        gap: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        border: 1px solid rgba(148, 163, 184, 0.2);
        margin-bottom: 1.5rem;
    }
    .profile-avatar {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        object-fit: cover;
        border: 3px solid #ff4b4b;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
        background-color: rgba(255, 255, 255, 0.1);
    }
    .profile-names {
        flex-grow: 1;
    }
    .profile-name-title {
        font-family: 'Outfit', sans-serif;
        font-size: 2.1rem;
        font-weight: 800;
        margin: 0;
        line-height: 1.1;
    }
    .profile-meta-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 0.4rem;
    }
    .profile-meta-badge {
        background: rgba(255, 255, 255, 0.12);
        padding: 0.2rem 0.6rem;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.02em;
        text-transform: uppercase;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .profile-spec-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
        gap: 0.75rem;
        margin-bottom: 1.5rem;
    }
    .profile-spec-card {
        background: rgba(148, 163, 184, 0.05);
        border: 1px solid rgba(148, 163, 184, 0.15);
        border-radius: 8px;
        padding: 0.7rem;
        text-align: center;
    }
    .profile-spec-label {
        font-size: 0.72rem;
        font-weight: 700;
        color: rgba(148, 163, 184, 0.82);
        text-transform: uppercase;
        margin-bottom: 0.25rem;
        line-height: 1;
    }
    .profile-spec-value {
        font-size: 1.1rem;
        font-weight: 800;
        color: var(--text-color, #0f172a);
    }
    .scouting-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    .grade-badge-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, rgba(30, 58, 138, 0.05), rgba(30, 58, 138, 0.08));
        border: 2px solid rgba(30, 58, 138, 0.25);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
    }
    .grade-badge-title {
        font-weight: 800;
        font-size: 0.85rem;
        text-transform: uppercase;
        color: #1e3a8a;
        margin-bottom: 0.5rem;
    }
    .grade-badge-circle {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        background: #1e3a8a;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: 'Outfit', sans-serif;
        font-size: 2.2rem;
        font-weight: 800;
        box-shadow: 0 4px 10px rgba(30, 58, 138, 0.25);
        border: 3px solid rgba(255, 255, 255, 0.2);
    }
    .scouting-traits-container {
        background: rgba(148, 163, 184, 0.04);
        border: 1px solid rgba(148, 163, 184, 0.15);
        border-radius: 12px;
        padding: 1.25rem;
    }
    .scouting-trait-row {
        margin-bottom: 0.85rem;
    }
    .scouting-trait-row:last-child {
        margin-bottom: 0;
    }
    .scouting-trait-header {
        display: flex;
        justify-content: space-between;
        font-size: 0.8rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .scouting-trait-name {
        color: var(--text-color, #0f172a);
    }
    .scouting-trait-score {
        color: #1e3a8a;
        font-weight: 800;
    }
    .trait-progress-bar {
        background: rgba(148, 163, 184, 0.2);
        border-radius: 999px;
        height: 8px;
        overflow: hidden;
    }
    .trait-progress-fill {
        background: #1e3a8a;
        height: 100%;
        border-radius: 999px;
    }
    @media (max-width: 600px) {
        .profile-header {
            flex-direction: column;
            text-align: center;
            padding: 1.25rem;
        }
        .scouting-grid {
            grid-template-columns: 1fr;
        }
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
SHOW_LOGO_URLS = {
    "desktop": "https://www.heavylifthelicopters.us/ai-v-meatbags/ai-v-meatbags-dashboard-01.png",
    "tablet": "https://www.heavylifthelicopters.us/ai-v-meatbags/ai-v-meatbags-dashboard-1800x450.png",
    "mobile": "https://www.heavylifthelicopters.us/ai-v-meatbags/ai-v-meatbags-dashboard-1200x600.png",
}

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

def render_tab_bookmarks(sections):
    links = "".join(
        f"<a href='#{html.escape(anchor)}'>{html.escape(label)}</a>"
        for label, anchor in sections
    )
    st.markdown(
        f"""
        <div class='tab-action-bar'>
            <span class='tab-action-label'>Jump to</span>
            <nav class='bookmark-menu'>{links}</nav>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_section_header(title, anchor=None, subtitle=None, first=False):
    if not first:
        st.markdown("<hr class='section-rule'>", unsafe_allow_html=True)
    if anchor:
        st.markdown(f"<span id='{html.escape(anchor)}' class='section-anchor'></span>", unsafe_allow_html=True)
    st.markdown(f"### {title}")
    if subtitle:
        st.markdown(f"<div class='section-subtitle'>{html.escape(subtitle)}</div>", unsafe_allow_html=True)

def mark_successful_run(run_key):
    from datetime import datetime, timezone

    timestamp = datetime.now(timezone.utc)
    display_timestamp = timestamp.astimezone().strftime("%Y-%m-%d %I:%M:%S %p")
    st.session_state.setdefault("last_successful_runs", {})[run_key] = display_timestamp

    try:
        from google.api_core.exceptions import NotFound
        from google.cloud import bigquery

        client = bigquery.Client(project=BIGQUERY_PROJECT_ID)
        table_id = f"{BIGQUERY_PROJECT_ID}.fantasy_football_brain.dashboard_job_runs"
        try:
            client.get_table(table_id)
        except NotFound:
            schema = [
                bigquery.SchemaField("run_key", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("succeeded_at", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("app_version", "STRING"),
                bigquery.SchemaField("app_commit", "STRING"),
            ]
            table = bigquery.Table(table_id, schema=schema)
            client.create_table(table)

        errors = client.insert_rows_json(table_id, [{
            "run_key": run_key,
            "succeeded_at": timestamp.isoformat(),
            "app_version": os.environ.get("APP_VERSION", "dev"),
            "app_commit": os.environ.get("APP_COMMIT", "unknown"),
        }])
        if errors:
            logging.getLogger("app.metrics").warning(f"Could not persist dashboard run status: {errors}")
        else:
            get_persisted_last_success.clear()
    except Exception as ex:
        logging.getLogger("app.metrics").warning(f"Could not persist dashboard run status: {ex}")

@st.cache_data(ttl=60, show_spinner=False)
def get_persisted_last_success(run_key):
    try:
        from google.cloud import bigquery

        client = bigquery.Client(project=BIGQUERY_PROJECT_ID)
        query = f"""
            SELECT succeeded_at
            FROM `{BIGQUERY_PROJECT_ID}.fantasy_football_brain.dashboard_job_runs`
            WHERE run_key = @run_key
            ORDER BY succeeded_at DESC
            LIMIT 1
        """
        job_config = bigquery.QueryJobConfig(query_parameters=[
            bigquery.ScalarQueryParameter("run_key", "STRING", run_key)
        ])
        df = client.query(query, job_config=job_config).to_dataframe()
        if df.empty:
            return None
        return df.iloc[0]["succeeded_at"].strftime("%Y-%m-%d %I:%M:%S %p")
    except Exception as ex:
        logging.getLogger("app.metrics").warning(f"Could not read dashboard run status: {ex}")
    return None

def render_last_success(run_key):
    last_runs = st.session_state.get("last_successful_runs", {})
    value = last_runs.get(run_key) or get_persisted_last_success(run_key) or "No successful run recorded yet."
    st.markdown(f"<div class='last-run'>Last successful run: {html.escape(value)}</div>", unsafe_allow_html=True)

def render_runtime_status(active_tables, total_size_mb, app_version, cloud_run_revision, app_commit):
    safe_items = [
        ("Active Tables", f"{active_tables}"),
        ("Total Data Size", f"{total_size_mb:.2f} MB"),
        ("Version", app_version),
        ("Revision", cloud_run_revision),
    ]
    cards = "".join(
        "<div class='runtime-status-card'>"
        f"<div class='runtime-status-label'>{html.escape(label)}</div>"
        f"<div class='runtime-status-value'>{html.escape(str(value))}</div>"
        "</div>"
        for label, value in safe_items
    )
    safe_commit = app_commit[:7] if app_commit != "unknown" else app_commit
    st.markdown(
        f"""
        <div class='runtime-status-grid'>{cards}</div>
        <div class='runtime-status-caption'>Commit: {html.escape(safe_commit)}</div>
        """,
        unsafe_allow_html=True,
    )

@st.cache_data(ttl=3600, show_spinner=False)
def execute_bq_cached(sql_query: str):
    from google.cloud import bigquery
    bq_client = bigquery.Client(project=BIGQUERY_PROJECT_ID)
    query_job = bq_client.query(sql_query)
    df = query_job.result().to_dataframe()
    return df

def repair_generated_sql(sql_query: str) -> str:
    import re

    # 1. First, repair epa_per_play
    if re.search(r"\bepa_per_play\b", sql_query, flags=re.IGNORECASE):
        if re.search(r"\banalytics_player_weekly_truth\b", sql_query, flags=re.IGNORECASE):
            sql_query = re.sub(r"\bepa_per_play\b", "total_epa", sql_query, flags=re.IGNORECASE)
        elif re.search(r"\bweekly_metrics\b", sql_query, flags=re.IGNORECASE):
            weekly_total_epa = "(COALESCE(passing_epa, 0) + COALESCE(rushing_epa, 0) + COALESCE(receiving_epa, 0))"
            sql_query = re.sub(r"\bepa_per_play\b", weekly_total_epa, sql_query, flags=re.IGNORECASE)

    # 2. Repair player_name in NGS tables and market_values
    target_tables = ["ngs_passing", "ngs_rushing", "ngs_receiving", "market_values"]
    
    # Check if any of the target tables are referenced in the query
    has_target_table = False
    for table in target_tables:
        if re.search(rf"\b{table}\b", sql_query, flags=re.IGNORECASE):
            has_target_table = True
            break
            
    if has_target_table:
        # We need to replace player_name with player_display_name when it refers to one of these tables.
        # Let's find aliases for the target tables.
        aliases = set()
        for table in target_tables:
            # Match table name followed by optional AS and then the alias name
            pattern = rf"\b{table}\b`?\s+(?:as\s+)?`?([a-zA-Z0-9_]+)`?"
            for match in re.finditer(pattern, sql_query, flags=re.IGNORECASE):
                alias = match.group(1)
                if alias.upper() not in ("WHERE", "JOIN", "ON", "AND", "OR", "GROUP", "ORDER", "LIMIT", "USING", "LEFT", "RIGHT", "INNER", "OUTER", "FROM"):
                    aliases.add(alias.lower())
        
        # Replace qualified names like alias.player_name or table.player_name
        for table in target_tables:
            sql_query = re.sub(rf"\b{table}\b\.`?player_name`?", f"{table}.player_display_name", sql_query, flags=re.IGNORECASE)
            sql_query = re.sub(rf"`{table}`\.`?player_name`?", f"`{table}`.player_display_name", sql_query, flags=re.IGNORECASE)
            
        for alias in aliases:
            sql_query = re.sub(rf"\b{alias}\b\.`?player_name`?", f"{alias}.player_display_name", sql_query, flags=re.IGNORECASE)
            sql_query = re.sub(rf"`{alias}`\.`?player_name`?", f"`{alias}`.player_display_name", sql_query, flags=re.IGNORECASE)
            
        # Replace unqualified player_name if it is not preceded by a dot
        sql_query = re.sub(r"(?<!\.\s)(?<!\.)\bplayer_name\b", "player_display_name", sql_query, flags=re.IGNORECASE)

    return sql_query


def render_fraud_watch_segment():
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


@st.cache_data(ttl=3600, show_spinner="Loading player profiles database...")
def fetch_player_profiles_data():
    from google.cloud import bigquery
    sql_query = f"""
    WITH latest_week AS (
        SELECT MAX(season) AS max_season
        FROM `{BIGQUERY_PROJECT_ID}.fantasy_football_brain.analytics_player_weekly_truth`
    ),
    player_weekly_agg AS (
        SELECT 
            t.player_id,
            t.player_name,
            t.player_display_name,
            t.position,
            t.team,
            AVG(t.fantasy_points_ppr) AS avg_ppr,
            SUM(t.targets) AS total_targets,
            SUM(t.receptions) AS total_receptions,
            SUM(t.receiving_yards) AS total_receiving_yards,
            SUM(t.receiving_tds) AS total_receiving_tds,
            SUM(t.carries) AS total_carries,
            SUM(t.rushing_yards) AS total_rushing_yards,
            SUM(t.rushing_tds) AS total_rushing_tds,
            SUM(t.pass_attempts) AS total_pass_attempts,
            SUM(t.passing_yards) AS total_passing_yards,
            SUM(t.passing_tds) AS total_passing_tds,
            AVG(t.target_share) AS avg_target_share,
            AVG(t.wopr) AS avg_wopr,
            AVG(t.total_epa) AS avg_epa,
            AVG(t.offense_pct) AS avg_snap_share,
            AVG(t.opportunity_score) AS avg_opportunity,
            AVG(t.efficiency_score) AS avg_efficiency,
            AVG(t.role_quality_score) AS avg_role_quality,
            AVG(t.role_fragility_score) AS avg_role_fragility,
            AVG(t.analytical_grade) AS avg_grade
        FROM `{BIGQUERY_PROJECT_ID}.fantasy_football_brain.analytics_player_weekly_truth` t, latest_week lw
        WHERE t.season = lw.max_season
        GROUP BY t.player_id, t.player_name, t.player_display_name, t.position, t.team
    ),
    roster_meta AS (
        SELECT 
            r.gsis_id,
            ANY_VALUE(r.birth_date) AS birth_date,
            ANY_VALUE(r.height) AS height,
            ANY_VALUE(r.weight) AS weight,
            ANY_VALUE(r.headshot) AS headshot,
            ANY_VALUE(r.college_name) AS college_name,
            ANY_VALUE(r.jersey_number) AS jersey_number,
            ANY_VALUE(r.rookie_season) AS rookie_season,
            ANY_VALUE(r.years_of_experience) AS years_of_experience,
            ANY_VALUE(r.draft_year) AS draft_year,
            ANY_VALUE(r.draft_round) AS draft_round,
            ANY_VALUE(r.draft_pick) AS draft_pick,
            ANY_VALUE(r.draft_team) AS draft_team
        FROM `{BIGQUERY_PROJECT_ID}.fantasy_football_brain.player_rosters` r
        GROUP BY r.gsis_id
    ),
    contract_meta AS (
        SELECT 
            c.gsis_id,
            ANY_VALUE(c.value) AS contract_value,
            ANY_VALUE(c.apy) AS contract_apy,
            ANY_VALUE(c.guaranteed) AS contract_guaranteed,
            ANY_VALUE(c.year_signed) AS contract_year_signed
        FROM `{BIGQUERY_PROJECT_ID}.fantasy_football_brain.player_contracts` c
        WHERE c.is_active = TRUE
        GROUP BY c.gsis_id
    )
    SELECT 
        agg.*,
        r.* EXCEPT(gsis_id),
        c.* EXCEPT(gsis_id),
        RANK() OVER(PARTITION BY agg.position ORDER BY COALESCE(agg.avg_grade, 0.0) DESC) AS pos_rank
    FROM player_weekly_agg agg
    LEFT JOIN roster_meta r ON agg.player_id = r.gsis_id
    LEFT JOIN contract_meta c ON agg.player_id = c.gsis_id
    """
    client = bigquery.Client(project=BIGQUERY_PROJECT_ID)
    df = client.query(sql_query).result().to_dataframe()
    return df

@st.cache_data(ttl=3600, show_spinner="Loading player weekly history...")
def fetch_player_weekly_history(player_id: str):
    from google.cloud import bigquery
    sql_query = f"""
    SELECT 
        season,
        week,
        opponent_team,
        fantasy_points_ppr,
        offense_pct AS snap_share,
        targets,
        receptions,
        receiving_yards,
        receiving_tds,
        carries,
        rushing_yards,
        rushing_tds,
        passing_yards,
        passing_tds,
        total_epa
    FROM `{BIGQUERY_PROJECT_ID}.fantasy_football_brain.analytics_player_weekly_truth`
    WHERE player_id = @player_id
    ORDER BY season DESC, week DESC
    """
    client = bigquery.Client(project=BIGQUERY_PROJECT_ID)
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("player_id", "STRING", player_id)
        ]
    )
    df = client.query(sql_query, job_config=job_config).result().to_dataframe()
    return df

def render_player_profiles_tab():
    import pandas as pd
    import os
    
    st.markdown("### 👤 Player Profiles Directory")
    st.markdown(
        "NFL Draft Buzz style directory and scouting profiles powered by advanced metrics, contracts, and Pigskin AI analysis."
    )
    
    try:
        df = fetch_player_profiles_data()
    except Exception as e:
        st.info(f"Player profiles database is not fully materialized or query failed: {e}")
        return
        
    if df.empty:
        st.warning("No player profile metrics found in the data warehouse.")
        return
        
    # Helpers for rendering
    def format_currency(val):
        if not val or pd.isna(val):
            return "N/A"
        try:
            num = float(val)
            if num >= 1_000_000:
                return f"${num / 1_000_000:.2f}M"
            elif num >= 1_000:
                return f"${num / 1_000:.1f}K"
            else:
                return f"${num:.0f}"
        except Exception:
            return str(val)
            
    def format_height(inches):
        if not inches or pd.isna(inches):
            return "N/A"
        try:
            val = int(float(inches))
            feet = val // 12
            rem_inches = val % 12
            return f"{feet}'{rem_inches}\""
        except Exception:
            return str(inches)
            
    def calculate_age(birth_date_str):
        if not birth_date_str or pd.isna(birth_date_str):
            return "N/A"
        try:
            from datetime import datetime
            birth_date = datetime.strptime(birth_date_str[:10], "%Y-%m-%d")
            today = datetime(2026, 6, 9)
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            return f"{age} yrs"
        except Exception:
            return "N/A"
            
    if "selected_player_id" not in st.session_state:
        st.session_state.selected_player_id = None
        
    # Autocomplete Search Bar at the top of the directory
    all_player_names = [name for name in df["player_display_name"].unique() if isinstance(name, str) and name]
    search_player = st.selectbox(
        "🔍 Search Player Profile by Name (Autocomplete):",
        options=[""] + sorted(all_player_names),
        index=0,
        format_func=lambda x: "Type to search a player..." if x == "" else x,
        key="global_profile_search"
    )
    
    if search_player:
        matched = df[df["player_display_name"] == search_player]
        if not matched.empty:
            st.session_state.selected_player_id = matched.iloc[0]["player_id"]
            
    # Rendering Detailed Profile
    if st.session_state.selected_player_id:
        player_id = st.session_state.selected_player_id
        player_rows = df[df["player_id"] == player_id]
        if player_rows.empty:
            st.warning("Could not locate the player profile record.")
            if st.button("⬅ Back to Directory"):
                st.session_state.selected_player_id = None
                st.rerun()
            return
            
        player_row = player_rows.iloc[0]
        
        # Back Button
        if st.button("⬅ Back to Position Rankings Directory"):
            st.session_state.selected_player_id = None
            st.rerun()
            
        headshot_url = player_row["headshot"] if (player_row["headshot"] and not pd.isna(player_row["headshot"])) else "https://www.nfl.com/static/content/public/static/wildcat/assets/images/application-logos/share/nfl-share.png"
        jersey_num = f"#{int(float(player_row['jersey_number']))}" if (player_row["jersey_number"] and not pd.isna(player_row["jersey_number"])) else ""
        draft_str = f"Drafted Rd {int(float(player_row['draft_round']))}, Pick {int(float(player_row['draft_pick']))} by {player_row['draft_team']}" if (player_row["draft_pick"] and not pd.isna(player_row["draft_pick"])) else "Undrafted Free Agent"
        
        # Header banner
        st.markdown(f"""
        <div class="profile-header">
            <img class="profile-avatar" src="{headshot_url}" alt="{player_row['player_display_name']}">
            <div class="profile-names">
                <div class="profile-name-title">{player_row['player_display_name']} {jersey_num}</div>
                <div class="profile-meta-row">
                    <span class="profile-meta-badge">{player_row['position']}</span>
                    <span class="profile-meta-badge">{player_row['team']}</span>
                    <span class="profile-meta-badge">{player_row['college_name'] if player_row['college_name'] else 'Unknown College'}</span>
                    <span class="profile-meta-badge">{draft_str}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Specs Grid
        cols_specs = st.columns(6)
        specs = [
            ("Height", format_height(player_row["height"])),
            ("Weight", f"{int(float(player_row['weight']))} lbs" if (player_row["weight"] and not pd.isna(player_row["weight"])) else "N/A"),
            ("Age", calculate_age(player_row["birth_date"])),
            ("Experience", f"{int(float(player_row['years_of_experience']))} yrs" if (player_row["years_of_experience"] and not pd.isna(player_row["years_of_experience"])) else "Rookie"),
            ("Contract APY", format_currency(player_row["contract_apy"])),
            ("Total Value", format_currency(player_row["contract_value"])),
        ]
        for idx, (label, val) in enumerate(specs):
            cols_specs[idx].markdown(f"""
            <div class="profile-spec-card">
                <div class="profile-spec-label">{label}</div>
                <div class="profile-spec-value">{val}</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.write("")
        
        # Scouting Ratings Grid
        st.markdown("### 📊 Player Grades & Metrics")
        col_grade, col_traits = st.columns([1, 2])
        
        with col_grade:
            grade_val = player_row["avg_grade"] if not pd.isna(player_row["avg_grade"]) else 0.0
            st.markdown(f"""
            <div class="grade-badge-container">
                <div class="grade-badge-title">Overall Grade</div>
                <div class="grade-badge-circle">{grade_val:.1f}</div>
                <div style="margin-top: 10px; font-weight: 700; color: #1e3a8a;">Rank: #{int(player_row['pos_rank'])} {player_row['position']}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_traits:
            opp_score = player_row["avg_opportunity"] if not pd.isna(player_row["avg_opportunity"]) else 0.0
            eff_score = player_row["avg_efficiency"] if not pd.isna(player_row["avg_efficiency"]) else 0.0
            fragility = player_row["avg_role_fragility"] if not pd.isna(player_row["avg_role_fragility"]) else 0.0
            stability_score = max(0.0, min(100.0, 100.0 - fragility))
            
            traits = [
                ("Opportunity Rating (Volume)", opp_score),
                ("Efficiency Rating (EPA/Pts)", eff_score),
                ("Role Stability Rating (Usage)", stability_score),
            ]
            
            st.markdown('<div class="scouting-traits-container">', unsafe_allow_html=True)
            for trait_name, trait_val in traits:
                st.markdown(f"""
                <div class="scouting-trait-row">
                    <div class="scouting-trait-header">
                        <span class="scouting-trait-name">{trait_name}</span>
                        <span class="scouting-trait-score">{trait_val:.1f}/100</span>
                    </div>
                    <div class="trait-progress-bar">
                        <div class="trait-progress-fill" style="width: {trait_val}%;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        # Pigskin's AI Scouting Report
        st.markdown("### 🧠 Pigskin's Scouting Report")
        active_gemini_key = os.environ.get("GEMINI_API_KEY", "")
        report_cache_key = f"scouting_report_{player_id}"
        
        if report_cache_key not in st.session_state:
            if not active_gemini_key:
                st.session_state[report_cache_key] = f"""
                No Gemini API key detected in the sidebar. Standard statistics indicate that {player_row['player_display_name']} averages {player_row['avg_ppr']:.1f} PPR points per game on a snap share of {player_row['avg_snap_share']*100:.1f}%. 
                His average analytical grade is {player_row['avg_grade']:.1f} and he carries an opportunity score of {player_row['avg_opportunity']:.1f}.
                
                **KEY STRENGTHS:**
                - Highly utilized offensive role (averaging {player_row['avg_ppr']:.1f} points/game)
                - Good volume stability ({player_row['avg_snap_share']*100:.1f}% snap share)
                
                **KEY WEAKNESSES:**
                - Efficiency metrics are subject to opponent defensive strength
                - Rookie/college historical metrics are unmapped for this player
                """
            else:
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=active_gemini_key)
                    model = genai.GenerativeModel("gemini-3.5-flash")
                    
                    prompt = f"""
                    You are Pigskin, the snarky analytical co-host of AI vs Vibes.
                    Write a 1-paragraph Draft Buzz style scouting report for the NFL player {player_row['player_display_name']}.
                    
                    Player Metrics:
                    - Position: {player_row['position']}
                    - College: {player_row['college_name']}
                    - Draft: Round {player_row['draft_round']}, Pick {player_row['draft_pick']} (Year {player_row['draft_year']})
                    - Experience: {player_row['years_of_experience']} years
                    - Average PPR PPG: {player_row['avg_ppr']:.2f}
                    - Analytical Grade (1-100): {player_row['avg_grade']:.2f}
                    - Opportunity Rating (1-100): {player_row['avg_opportunity']:.2f}
                    - Efficiency Rating (1-100): {player_row['avg_efficiency']:.2f}
                    - Role Stability Rating (1-100): {100 - player_row['avg_role_fragility']:.2f}
                    - Contract APY: {format_currency(player_row['contract_apy'])}
                    
                    Scouting report requirements:
                    1. Deliver the report in the Pigskin voice contract (arrogant, analytical, highly critical of vibes-based scouting, uses slang like "cooked", "vibes tax").
                    2. Write a brief overview (3-4 sentences).
                    3. Output a section for "KEY STRENGTHS" and "KEY WEAKNESSES", listing exactly 2 bullet points for each based on their actual numbers. Do not include markdown headers inside the bulleted text, just write it as standard bold bullets.
                    """
                    res = model.generate_content(prompt)
                    st.session_state[report_cache_key] = res.text
                except Exception as ex:
                    st.session_state[report_cache_key] = f"Error generating report: {ex}"
                    
        st.write(st.session_state[report_cache_key])
        
        # Weekly Stats & Trends
        history_df = fetch_player_weekly_history(player_id)
        if not history_df.empty:
            st.markdown("### 📈 Performance Trends")
            plot_df = history_df.sort_values(by=["season", "week"]).copy()
            plot_df["Week Label"] = plot_df.apply(lambda r: f"W{r['week']}" if len(plot_df["season"].unique()) <= 1 else f"S{r['season']} W{r['week']}", axis=1)
            plot_data = plot_df.set_index("Week Label")[["fantasy_points_ppr", "total_epa"]]
            plot_data.columns = ["PPR Points", "Weekly EPA"]
            st.line_chart(plot_data, height=220)
            
            st.markdown("#### Weekly Stats History")
            st.dataframe(
                history_df[["season", "week", "opponent_team", "fantasy_points_ppr", "snap_share", "targets", "receptions", "carries", "total_epa"]].rename(
                    columns={
                        "season": "Season",
                        "week": "Week",
                        "opponent_team": "Opponent",
                        "fantasy_points_ppr": "PPR Points",
                        "snap_share": "Snap Share",
                        "targets": "Targets",
                        "receptions": "Rec",
                        "carries": "Carries",
                        "total_epa": "EPA",
                    }
                ),
                use_container_width=True,
                hide_index=True
            )
            
    # Rendering Rankings Directory List
    else:
        # Segmented position controls
        if "selected_pos" not in st.session_state:
            st.session_state.selected_pos = "QB"
            
        cols_pos = st.columns(5)
        positions = ["All", "QB", "RB", "WR", "TE"]
        
        for idx, pos in enumerate(positions):
            label = f"🏈 {pos}" if pos != "All" else "🌍 All"
            btn_type = "primary" if st.session_state.selected_pos == pos else "secondary"
            if cols_pos[idx].button(label, type=btn_type, use_container_width=True, key=f"pos_btn_{pos}"):
                st.session_state.selected_pos = pos
                st.rerun()
                
        selected_pos = st.session_state.selected_pos
        st.markdown(f"#### 🏆 {selected_pos} Position Rankings Directory")
        
        # Filter and show
        df_pos = df.copy()
        if selected_pos != "All":
            df_pos = df_pos[df_pos["position"] == selected_pos]
            
        df_pos = df_pos.sort_values(by="avg_grade", ascending=False)
        
        if df_pos.empty:
            st.info("No players found matching the selected position.")
            return
            
        # Format columns for rankings display
        display_ranks = df_pos.copy()
        display_ranks["avg_grade"] = display_ranks["avg_grade"].apply(lambda x: f"{x:.1f}" if not pd.isna(x) else "N/A")
        display_ranks["avg_ppr"] = display_ranks["avg_ppr"].apply(lambda x: f"{x:.1f}" if not pd.isna(x) else "N/A")
        display_ranks["contract_apy"] = display_ranks["contract_apy"].apply(format_currency)
        display_ranks["height"] = display_ranks["height"].apply(format_height)
        display_ranks["weight"] = display_ranks["weight"].apply(lambda x: f"{int(float(x))} lbs" if (x and not pd.isna(x)) else "N/A")
        
        display_ranks = display_ranks.rename(columns={
            "pos_rank": "Rank",
            "player_display_name": "Player",
            "team": "Team",
            "college_name": "College",
            "avg_grade": "Overall Rating",
            "avg_ppr": "Avg PPR",
            "contract_apy": "Salary APY",
            "height": "Height",
            "weight": "Weight"
        })
        
        st.dataframe(
            display_ranks[["Rank", "Player", "Team", "College", "Overall Rating", "Avg PPR", "Salary APY", "Height", "Weight"]],
            use_container_width=True,
            hide_index=True
        )
        
        st.markdown("---")
        col_sel, col_btn = st.columns([3, 1])
        with col_sel:
            rank_selected = st.selectbox(
                f"Select a player from the {selected_pos} rankings board to inspect their full profile:",
                options=[""] + sorted([name for name in df_pos["player_display_name"].unique() if isinstance(name, str) and name]),
                index=0,
                format_func=lambda x: "Choose a player..." if x == "" else x,
                key="rankings_board_select"
            )
        with col_btn:
            st.write("") # Alignment spacers
            st.write("")
            if st.button("View Full Profile 👤", type="primary", use_container_width=True):
                if rank_selected:
                    st.session_state.selected_player_id = df_pos[df_pos["player_display_name"] == rank_selected].iloc[0]["player_id"]
                    st.rerun()

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_reddit_weekly_topic_posts(subreddits, per_subreddit_limit):
    import requests
    import xml.etree.ElementTree as ET

    headers = {
        "User-Agent": "AIvsVibesFantasyTopicScout/0.1 by SoFain",
    }
    posts = []
    errors = []

    for subreddit in subreddits:
        subreddit = subreddit.strip().strip("/").removeprefix("r/")
        if not subreddit:
            continue

        url = f"https://www.reddit.com/r/{subreddit}/top/.rss"
        try:
            response = requests.get(
                url,
                params={"t": "week"},
                headers=headers,
                timeout=20,
            )
            if response.status_code != 200:
                errors.append(f"r/{subreddit}: HTTP {response.status_code}")
                continue

            root = ET.fromstring(response.content)
            namespace = {"atom": "http://www.w3.org/2005/Atom"}
            entries = root.findall("atom:entry", namespace)[:per_subreddit_limit]
            for rank, entry in enumerate(entries, start=1):
                title = entry.findtext("atom:title", default="", namespaces=namespace)
                link = entry.find("atom:link", namespace)
                summary = entry.findtext("atom:content", default="", namespaces=namespace)
                updated = entry.findtext("atom:updated", default="", namespaces=namespace)
                if not title:
                    continue
                rank_signal = max(per_subreddit_limit - rank + 1, 1)
                posts.append({
                    "subreddit": f"r/{subreddit}",
                    "title": title,
                    "score": rank_signal,
                    "comments": 0,
                    "weekly_rank": rank,
                    "created_utc": updated,
                    "permalink": link.attrib.get("href", "") if link is not None else "",
                    "flair": "",
                    "selftext": summary[:500],
                })
        except Exception as ex:
            errors.append(f"r/{subreddit}: {ex}")

    return posts, errors

def reddit_topic_tokens(title):
    import re

    stopwords = {
        "about", "after", "again", "against", "before", "being", "best", "better", "between",
        "comment", "comments", "could", "discussion", "does", "drop", "fantasy", "football",
        "from", "have", "help", "into", "just", "league", "need", "news", "over", "player",
        "players", "post", "question", "should", "start", "team", "than", "that", "this",
        "thread", "trade", "week", "what", "when", "which", "with", "would", "your",
    }
    tokens = re.findall(r"[a-z0-9']+", title.lower())
    return {token for token in tokens if len(token) > 2 and token not in stopwords}

def cluster_reddit_topics(posts):
    from collections import Counter

    scored_posts = []
    for post in posts:
        tokens = reddit_topic_tokens(post["title"])
        if not tokens:
            continue
        scored_posts.append({
            **post,
            "tokens": tokens,
            "popularity": int(post["score"]) + int(post["comments"]) * 2,
        })

    scored_posts.sort(key=lambda item: item["popularity"], reverse=True)
    clusters = []
    for post in scored_posts:
        selected_cluster = None
        for cluster in clusters:
            overlap = post["tokens"] & cluster["tokens"]
            union = post["tokens"] | cluster["tokens"]
            if len(overlap) >= 2 and len(overlap) / max(len(union), 1) >= 0.16:
                selected_cluster = cluster
                break

        if selected_cluster is None:
            clusters.append({
                "tokens": set(post["tokens"]),
                "posts": [post],
                "popularity": post["popularity"],
            })
        else:
            selected_cluster["tokens"].update(post["tokens"])
            selected_cluster["posts"].append(post)
            selected_cluster["popularity"] += post["popularity"]

    topic_rows = []
    for cluster in clusters:
        token_counts = Counter()
        subreddits = set()
        for post in cluster["posts"]:
            token_counts.update(post["tokens"])
            subreddits.add(post["subreddit"])

        lead_post = max(cluster["posts"], key=lambda item: item["popularity"])
        topic_words = [word for word, _count in token_counts.most_common(4)]
        topic_rows.append({
            "topic": " ".join(word.title() for word in topic_words) or lead_post["title"],
            "show_angle": lead_post["title"],
            "popularity": cluster["popularity"],
            "posts": len(cluster["posts"]),
            "subreddits": ", ".join(sorted(subreddits)),
            "top_score": lead_post["score"],
            "top_weekly_rank": lead_post.get("weekly_rank"),
            "top_link": lead_post["permalink"],
            "examples": cluster["posts"][:3],
        })

    return sorted(topic_rows, key=lambda item: item["popularity"], reverse=True)

def render_reddit_topic_scout():
    col_subs, col_limit = st.columns([3, 1])
    with col_subs:
        subreddit_input = st.text_input(
            "Subreddits",
            value="fantasyfootball,DynastyFF,fantasy_football,FantasyFootballers,fantasyfootballadvice",
            help="Comma-separated subreddit names. The scout reads each subreddit's weekly top posts.",
        )
    with col_limit:
        per_subreddit_limit = st.number_input("Posts per board", min_value=5, max_value=50, value=25, step=5)

    subreddits = [item.strip() for item in subreddit_input.split(",") if item.strip()]
    if st.button("Scan Reddit Weekly Topics", type="secondary"):
        posts, errors = fetch_reddit_weekly_topic_posts(tuple(subreddits), int(per_subreddit_limit))
        if errors:
            st.warning("Some boards could not be read: " + "; ".join(errors))
        if not posts:
            st.info("No Reddit posts were returned. Reddit may be rate-limiting the public RSS endpoint.")
            return

        topics = cluster_reddit_topics(posts)[:5]
        if not topics:
            st.info("Reddit returned posts, but there were no usable topic clusters.")
            return

        import pandas as pd
        topic_df = pd.DataFrame([{
            "Rank": index + 1,
            "Topic": topic["topic"],
            "Show Angle": topic["show_angle"],
            "Popularity": topic["popularity"],
            "Posts": topic["posts"],
            "Boards": topic["subreddits"],
            "Best Board Rank": topic["top_weekly_rank"],
            "Top Link": topic["top_link"],
        } for index, topic in enumerate(topics)])
        st.dataframe(topic_df, use_container_width=True, hide_index=True)

        for index, topic in enumerate(topics, start=1):
            with st.expander(f"{index}. {topic['topic']}"):
                st.markdown(f"**Show angle:** {topic['show_angle']}")
                st.markdown(f"**Signal:** {topic['popularity']} weekly-rank points from {topic['posts']} related post(s).")
                for post in topic["examples"]:
                    st.markdown(
                        f"- [{post['title']}]({post['permalink']}) "
                        f"({post['subreddit']}, weekly rank {post.get('weekly_rank', 'n/a')})"
                    )

def render_ai_cohost():
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
    - `passing_epa` (FLOAT64) - Passing Expected Points Added.
    - `rushing_epa` (FLOAT64) - Rushing Expected Points Added.
    - `receiving_epa` (FLOAT64) - Receiving Expected Points Added.
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
      Columns: Includes `player_display_name` (the player's name column, NOT `player_name`), `player_gsis_id`, and metrics like `avg_time_to_throw`, `avg_completed_air_yards`, `aggressiveness`.
      
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
      Description: Curated event ledger for causal context such as QB injuries, QB changes, offensive line injuries, coaching/play-caller changes, training camp reports/reps, offseason/preseason usage split trends, weather, and other fantasy-relevant situational events.
      Columns include: `event_id`, `season`, `start_week`, `end_week`, `team`, `event_type`, `subject_player_id`, `subject_name`, `subject_position`, `affected_player_id`, `affected_player_name`, `affected_unit`, `causal_status`, `confidence_score`, `source_type`, `source_label`, `source_url`, `summary`, `analysis_instruction`, and `active`.
    - Table: `fantasy_football_brain.analytics_external_context_search_results`
      Description: On-demand external verification search results for player-specific outside verification. Use these results as leads, not as confirmed facts, unless the linked source clearly supports the claim.
      Columns include: `searched_at`, `player_name`, `query`, `result_rank`, `title`, `link`, `display_link`, `snippet`, `source_type`, `provider`, and `source_name`.
    - Table: `fantasy_football_brain.analytics_game_environment`
      Description: One row per regular-season game with stadium, roof, surface, temperature, wind, weather text, and fantasy-relevant environment flags.
      Columns include: `season`, `week`, `game_id`, `game_date`, `home_team`, `away_team`, `stadium`, `historical_stadium_name`, `stadium_id`, `roof`, `surface`, `temp_f`, `wind_mph`, `weather_text`, `is_indoor_or_closed`, `roof_category`, `surface_category`, `precipitation_or_storm_flag`, `snow_or_freezing_flag`, `temperature_bucket`, `wind_bucket`, `environment_risk_level`, and `fantasy_environment_note`.
    - Table: `fantasy_football_brain.ngs_rushing`
      Columns: Includes `player_display_name` (the player's name column, NOT `player_name`), `player_gsis_id`, and metrics like `efficiency`, `percent_attempts_gte_eight_defenders`, `avg_time_to_los`.
    - Table: `fantasy_football_brain.ngs_receiving`
      Columns: Includes `player_display_name` (the player's name column, NOT `player_name`), `player_gsis_id`, and metrics like `avg_cushion`, `avg_separation`, `avg_yac_above_expectation`.
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
    Never query `epa_per_play`; that column does not exist. Use `analytics_player_weekly_truth.total_epa` for player analysis, or calculate total weekly EPA from `weekly_metrics.passing_epa + weekly_metrics.rushing_epa + weekly_metrics.receiving_epa`.
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
    For any causal claim involving injuries, coaching, play-calling, offensive line, weather, benching, training camp reports, usage splits, or transaction intent, query `analytics_context_events` first.
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
                            sql_to_run = repair_generated_sql(type(fc).to_dict(fc)["args"]["sql_query"])

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
                SELECT player_display_name, position, team, market_value, overall_rank, position_rank, redraft_value, tier, age
                FROM `{BIGQUERY_PROJECT_ID}.fantasy_football_brain.market_values`
                ORDER BY market_value DESC
            """
            return execute_bq_cached(query)
        except Exception as e:
            query = f"""
                SELECT player_display_name, position, team, market_value, overall_rank, position_rank, redraft_value, tier
                FROM `{BIGQUERY_PROJECT_ID}.fantasy_football_brain.market_values`
                ORDER BY market_value DESC
            """
            try:
                fallback_df = execute_bq_cached(query)
                fallback_df["age"] = pd.NA
                st.warning("Market values loaded without age. Run market value ingestion to enable age-based projections.")
                return fallback_df
            except Exception:
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

    # Projection Horizon Selector
    projection_years = st.selectbox(
        "📅 Projection Horizon (Years)",
        [1, 2, 3, 4, 5],
        index=2, # Default to 3 years
        help="Select the number of years into the future to project player values based on age and positional decline curves."
    )

    # Initialize dynamic selectbox counts
    if "num_a" not in st.session_state:
        st.session_state.num_a = 1
    if "num_b" not in st.session_state:
        st.session_state.num_b = 1

    # Clean up empty inputs at the end to keep exactly one blank input at the bottom of each side
    empty_asset_label = "-- Select Player / Pick --"
    while st.session_state.num_a > 1:
        last_val = st.session_state.get(f"sel_a_{st.session_state.num_a - 1}", empty_asset_label)
        prev_val = st.session_state.get(f"sel_a_{st.session_state.num_a - 2}", empty_asset_label)
        if last_val == empty_asset_label and prev_val == empty_asset_label:
            st.session_state.num_a -= 1
        else:
            break

    while st.session_state.num_b > 1:
        last_val = st.session_state.get(f"sel_b_{st.session_state.num_b - 1}", empty_asset_label)
        prev_val = st.session_state.get(f"sel_b_{st.session_state.num_b - 2}", empty_asset_label)
        if last_val == empty_asset_label and prev_val == empty_asset_label:
            st.session_state.num_b -= 1
        else:
            break

    # Age-based value projection logic
    def get_retention_score(pos, age):
        if pd.isna(age) or age is None:
            # Fallback average peak age
            return 1.0

        if pos == 'RB':
            if age <= 24: return 1.0
            elif age == 25: return 0.90
            elif age == 26: return 0.80
            elif age == 27: return 0.60
            elif age == 28: return 0.40
            elif age == 29: return 0.20
            else: return 0.10
        elif pos == 'WR':
            if age <= 26: return 1.0
            elif age == 27: return 0.95
            elif age == 28: return 0.90
            elif age == 29: return 0.80
            elif age == 30: return 0.65
            elif age == 31: return 0.50
            elif age == 32: return 0.35
            else: return 0.15
        elif pos == 'TE':
            if age <= 27: return 1.0
            elif age == 28: return 0.95
            elif age == 29: return 0.90
            elif age == 30: return 0.80
            elif age == 31: return 0.70
            elif age == 32: return 0.55
            elif age == 33: return 0.40
            else: return 0.20
        elif pos == 'QB':
            if age <= 30: return 1.0
            elif age in (31, 32): return 0.95
            elif age in (33, 34): return 0.90
            elif age in (35, 36): return 0.80
            elif age in (37, 38): return 0.60
            else: return 0.30
        else:
            return 1.0

    def interpolate_retention(pos, age):
        a_low = int(age)
        a_high = a_low + 1
        r_low = get_retention_score(pos, a_low)
        r_high = get_retention_score(pos, a_high)
        return r_low + (r_high - r_low) * (age - a_low)

    def project_asset_value(row, years):
        pos = row.get('position')
        val = numeric_value(row.get('market_value'), 0)
        age = row.get('age')
        
        if pd.isna(pos) or not pos:
            # Draft pick or other: slight discount per year
            return int(val * (0.95 ** years))
            
        current_age = float(age) if (age is not None and not pd.isna(age)) else None
        
        if current_age is not None:
            curr_ret = interpolate_retention(pos, current_age)
            proj_ret = interpolate_retention(pos, current_age + years)
            factor = proj_ret / curr_ret if curr_ret > 0 else 0
            return int(val * factor)
        else:
            # Fallback if age is completely missing
            start_age = 27 if pos == 'QB' else (24 if pos == 'RB' else (25 if pos == 'WR' else 26))
            curr_ret = interpolate_retention(pos, start_age)
            proj_ret = interpolate_retention(pos, start_age + years)
            factor = proj_ret / curr_ret if curr_ret > 0 else 0
            return int(val * factor)

    # Render columns for Side A and Side B
    col_sel_A, col_sel_B = st.columns(2)
    
    with col_sel_A:
        st.markdown("#### 🟥 Side A (Assets)")
        assets_A = []
        for i in range(st.session_state.num_a):
            selected = st.selectbox(
                f"Select Asset A {i+1}",
                [empty_asset_label] + player_options,
                key=f"sel_a_{i}"
            )
            if selected != empty_asset_label:
                assets_A.append(player_map[selected])
        
        if len(assets_A) == st.session_state.num_a:
            st.session_state.num_a += 1
            st.rerun()

    with col_sel_B:
        st.markdown("#### 🟦 Side B (Assets)")
        assets_B = []
        for i in range(st.session_state.num_b):
            selected = st.selectbox(
                f"Select Asset B {i+1}",
                [empty_asset_label] + player_options,
                key=f"sel_b_{i}"
            )
            if selected != empty_asset_label:
                assets_B.append(player_map[selected])
        
        if len(assets_B) == st.session_state.num_b:
            st.session_state.num_b += 1
            st.rerun()

    # Display Side-by-Side Cards
    st.markdown("#### ⚖️ Side-by-Side Comparison")
    col_card_A, col_card_B = st.columns(2)
    
    total_val_A = sum(numeric_value(a['market_value']) for a in assets_A)
    total_proj_A = sum(project_asset_value(a, projection_years) for a in assets_A)
    
    total_val_B = sum(numeric_value(b['market_value']) for b in assets_B)
    total_proj_B = sum(project_asset_value(b, projection_years) for b in assets_B)

    with col_card_A:
        asset_list_html = "".join([
            f"<li><b>{safe_display(a['player_display_name'])}</b> ({safe_display(a['position'], 'Pick')})<br>"
            f"Age: {safe_display(a['age'], 'N/A')} | "
            f"Val: {numeric_value(a['market_value'])} &rarr; Projected: {project_asset_value(a, projection_years)}</li>"
            for a in assets_A
        ])
        st.markdown(f"""
        <div class="metric-card" style="border-left: 5px solid #10B981; background-color: #F9FAFB; padding: 20px; border-radius: 8px;">
            <h3 style="margin-top: 0; color: #065F46;">Side A Summary</h3>
            <p><b>Current Total Value:</b> <span style="font-size: 1.6rem; font-weight: 800; color: #10B981;">{total_val_A}</span></p>
            <p><b>Projected {projection_years}-Year Value:</b> <span style="font-size: 1.6rem; font-weight: 800; color: #065F46;">{total_proj_A}</span></p>
            <hr style="margin: 10px 0; border-color: #E5E7EB;"/>
            <h5 style="margin-bottom: 5px;">Selected Assets:</h5>
            <ul style="padding-left: 20px; margin-top: 0;">
                {asset_list_html if assets_A else "<li>No assets selected</li>"}
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col_card_B:
        asset_list_html_B = "".join([
            f"<li><b>{safe_display(b['player_display_name'])}</b> ({safe_display(b['position'], 'Pick')})<br>"
            f"Age: {safe_display(b['age'], 'N/A')} | "
            f"Val: {numeric_value(b['market_value'])} &rarr; Projected: {project_asset_value(b, projection_years)}</li>"
            for b in assets_B
        ])
        st.markdown(f"""
        <div class="metric-card" style="border-left: 5px solid #3B82F6; background-color: #F9FAFB; padding: 20px; border-radius: 8px;">
            <h3 style="margin-top: 0; color: #1E40AF;">Side B Summary</h3>
            <p><b>Current Total Value:</b> <span style="font-size: 1.6rem; font-weight: 800; color: #3B82F6;">{total_val_B}</span></p>
            <p><b>Projected {projection_years}-Year Value:</b> <span style="font-size: 1.6rem; font-weight: 800; color: #1E40AF;">{total_proj_B}</span></p>
            <hr style="margin: 10px 0; border-color: #E5E7EB;"/>
            <h5 style="margin-bottom: 5px;">Selected Assets:</h5>
            <ul style="padding-left: 20px; margin-top: 0;">
                {asset_list_html_B if assets_B else "<li>No assets selected</li>"}
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # Difference & recommendation
    diff_current = abs(total_val_A - total_val_B)
    diff_projected = abs(total_proj_A - total_proj_B)
    
    st.markdown("#### ⚖️ Value Difference Analysis")
    
    if total_val_A > total_val_B:
        st.success(f"📈 **Side A** has a higher current value than **Side B** by **{diff_current} points**.")
    elif total_val_B > total_val_A:
        st.info(f"📈 **Side B** has a higher current value than **Side A** by **{diff_current} points**.")
    else:
        st.warning("⚖️ Both sides are valued equally by the market today.")

    if total_proj_A > total_proj_B:
        st.success(f"⏳ In **{projection_years} years**, **Side A** is projected to lead **Side B** by **{diff_projected} points**.")
    elif total_proj_B > total_proj_A:
        st.info(f"⏳ In **{projection_years} years**, **Side B** is projected to lead **Side A** by **{diff_projected} points**.")
    else:
        st.warning(f"⚖️ In **{projection_years} years**, both sides are projected to be equal in value.")

    # Deep AI Outlook using Gemini
    st.markdown(f"#### 🧠 AI {projection_years}-Year Outlook Analysis")
    st.markdown(f"Use Gemini to analyze their metrics and crawl recent team news for {projection_years}-year outlook projections.")

    active_gemini_key = os.environ.get("GEMINI_API_KEY", "")
    if not active_gemini_key:
        st.info("⚠️ Enter your **Gemini API Key** in the sidebar to activate the AI Analysis option.")
    else:
        if st.button(f"🧠 Run AI {projection_years}-Year Outlook Analysis", type="primary"):
            if not assets_A and not assets_B:
                st.error("Select assets on Side A or Side B first.")
                return
            with st.spinner("AI is fetching stats, injury reports, and crawling web news for all players..."):
                try:
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

                    def get_stored_news(name):
                        try:
                            q = f"""
                                SELECT title, snippet, source_name, searched_at
                                FROM `{BIGQUERY_PROJECT_ID}.fantasy_football_brain.analytics_external_context_search_results`
                                WHERE LOWER(player_name) = LOWER(@name)
                                ORDER BY searched_at DESC, result_rank ASC
                                LIMIT 3
                            """
                            jc = bigquery.QueryJobConfig(query_parameters=[bigquery.ScalarQueryParameter("name", "STRING", name)])
                            news_df = bq_client.query(q, job_config=jc).to_dataframe()
                            if news_df.empty:
                                return "No stored external news."
                            return "\n".join(
                                f"Title: {row.title}\nSource: {row.source_name}\nSnippet: {row.snippet}"
                                for row in news_df.itertuples(index=False)
                            )
                        except Exception:
                            return "No stored news."

                    # Gather info for all assets
                    assets_a_details = []
                    for a in assets_A:
                        name = a['player_display_name']
                        hist = query_player_history(name) if not pd.isna(a['position']) else pd.DataFrame()
                        news = get_stored_news(name) if not pd.isna(a['position']) else ""
                        assets_a_details.append(
                            f"- **{name}** ({a['position'] if not pd.isna(a['position']) else 'Pick'})\n"
                            f"  Age: {a.get('age') or 'N/A'}, Current Value: {numeric_value(a['market_value'])}, "
                            f"Projected {projection_years}-Year Value: {project_asset_value(a, projection_years)}\n"
                            f"  Recent Stats:\n{hist.to_string(index=False) if not hist.empty else 'No stats available'}\n"
                            f"  Recent News:\n{news}\n"
                        )

                    assets_b_details = []
                    for b in assets_B:
                        name = b['player_display_name']
                        hist = query_player_history(name) if not pd.isna(b['position']) else pd.DataFrame()
                        news = get_stored_news(name) if not pd.isna(b['position']) else ""
                        assets_b_details.append(
                            f"- **{name}** ({b['position'] if not pd.isna(b['position']) else 'Pick'})\n"
                            f"  Age: {b.get('age') or 'N/A'}, Current Value: {numeric_value(b['market_value'])}, "
                            f"Projected {projection_years}-Year Value: {project_asset_value(b, projection_years)}\n"
                            f"  Recent Stats:\n{hist.to_string(index=False) if not hist.empty else 'No stats available'}\n"
                            f"  Recent News:\n{news}\n"
                        )

                    import google.generativeai as genai
                    genai.configure(api_key=active_gemini_key)
                    model = genai.GenerativeModel('gemini-3.5-flash')
                    
                    prompt = f"""
                    Evaluate this dynasty fantasy football trade side-by-side:
                    
                    ### Side A Assets:
                    {"".join(assets_a_details) if assets_a_details else "None"}
                    Total Current Value: {total_val_A}
                    Total Projected {projection_years}-Year Value: {total_proj_A}
                    
                    ### Side B Assets:
                    {"".join(assets_b_details) if assets_b_details else "None"}
                    Total Current Value: {total_val_B}
                    Total Projected {projection_years}-Year Value: {total_proj_B}
                    
                    Provide a detailed {projection_years}-year outlook comparison. Ground your comparison in age, positional longevity, team/offensive environment, and current news/injury profiles.
                    Conclude with:
                    1. Which side is the safer long-term investment?
                    2. Which side has the higher immediate ceiling?
                    3. Respective AI Outlook Scores (0-100) and recommendations.
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

# --- COLLAPSED SETTINGS DRAWER ---
st.sidebar.title("Settings")

# Low-profile Logout Button
if st.sidebar.button("🔒 Logout", key="logout_btn", use_container_width=True):
    st.session_state.clear()
    st.rerun()

st.sidebar.caption("Credential overrides for local development and emergency runtime changes.")

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

active_tables, total_size_mb = get_warehouse_metrics()
app_version = os.environ.get("APP_VERSION", "dev")
app_commit = os.environ.get("APP_COMMIT", "unknown")
cloud_run_revision = os.environ.get("K_REVISION", "local")

# --- MAIN PAGE HEADER ---
st.markdown(
    f"""
    <div class='show-logo-frame'>
        <picture>
            <source media='(max-width: 640px)' srcset='{SHOW_LOGO_URLS["mobile"]}'>
            <source media='(max-width: 1024px)' srcset='{SHOW_LOGO_URLS["tablet"]}'>
            <img class='show-logo' src='{SHOW_LOGO_URLS["desktop"]}' alt='AI vs Meatbags'>
        </picture>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown("<div class='subtitle'>Manage, ingest, and validate historical play-by-play & player metrics pipeline into Google BigQuery</div>", unsafe_allow_html=True)

# Workflow Tabs
tab_pigskin, tab_show_prep, tab_player_profiles, tab_viewer_lab, tab_trade_lab, tab_data_ops = st.tabs([
    "💬 Pigskin Studio",
    "🎙️ Show Prep",
    "👤 Player Profiles",
    "🏈 Viewer Team Lab",
    "📊 Trade Lab",
    "🛠️ Data Ops",
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

    render_section_header(
        "Team Review Console",
        "team-console",
        "Ask Pigskin for roster audits, starter checks, trade bait, waiver priorities, and show-ready roasts.",
    )
    render_sleeper_viewer_console()

# --- DATA OPS: INGESTION PIPELINE ---
with tab_data_ops:
    render_tab_bookmarks([
        ("Runtime", "runtime-status"),
        ("Safe Checks", "safe-checks"),
        ("External API", "external-api"),
        ("Warehouse Writes", "warehouse-writes"),
    ])

    render_section_header(
        "Runtime Status",
        "runtime-status",
        "Current warehouse size, build identity, and Cloud Run revision.",
        first=True,
    )
    render_runtime_status(active_tables, total_size_mb, app_version, cloud_run_revision, app_commit)

    render_section_header(
        "Safe Checks",
        "safe-checks",
        "Read-only diagnostics and metadata checks. These should not mutate warehouse data.",
    )
    with st.container(border=True):
        st.markdown("#### Range Partition Verification")
        st.caption("Inspect table metadata and partition health without running `SELECT *`.")
        render_last_success("validation_sweep")
        if st.button("🔍 Run Validation Sweep", type="secondary"):
            cmd_args = ["validate.py"]

            exec_env = {}
            if gcp_key_path:
                exec_env["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.abspath(gcp_key_path)

            if run_subprocess_live(cmd_args, custom_env=exec_env) == 0:
                mark_successful_run("validation_sweep")

    render_section_header(
        "External API Refreshes",
        "external-api",
        "Network-backed refreshes that write narrow context tables or append fresh market/news signals.",
    )
    with st.container(border=True):
        st.markdown("#### Sleeper News and Trending")
        st.caption("Refresh real-time player news and trending add/drop vectors.")
        render_last_success("realtime_news")
        if st.button("🚀 Ingest Realtime Player News", type="secondary"):
            cmd_args = ["-m", "src.ingest_news"]

            exec_env = {}
            if gcp_key_path:
                exec_env["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.abspath(gcp_key_path)

            if run_subprocess_live(cmd_args, custom_env=exec_env) == 0:
                mark_successful_run("realtime_news")

        st.markdown("#### Context Event Ledger")
        st.caption("Load or refresh curated context events used by Pigskin before narrative claims.")
        render_last_success("context_event_ledger")
        if st.button("🧠 Load Context Event Ledger", type="secondary"):
            cmd_args = ["-m", "src.ingest_context_events"]

            exec_env = {}
            if gcp_key_path:
                exec_env["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.abspath(gcp_key_path)

            if run_subprocess_live(cmd_args, custom_env=exec_env) == 0:
                mark_successful_run("context_event_ledger")

        st.markdown("#### FantasyCalc Market Values")
        st.caption("Fetch current player and draft pick trade values from the FantasyCalc API.")
        render_last_success("market_values")
        is_dynasty_ingest = st.checkbox("Dynasty Values", value=True, help="If checked, fetches dynasty values. Otherwise, fetches redraft values.")

        if st.button("📊 Ingest FantasyCalc Market Values", type="secondary"):
            cmd_args = ["-m", "src.fetch_market_values"]
            if not is_dynasty_ingest:
                cmd_args.append("--redraft")

            exec_env = {}
            if gcp_key_path:
                exec_env["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.abspath(gcp_key_path)
            if run_subprocess_live(cmd_args, custom_env=exec_env) == 0:
                mark_successful_run("market_values")

        st.markdown("#### Player Context Verification")
        st.caption("Run one cost-capped external verification search and store the result context.")
        render_last_success("player_context_verification")
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

                if run_subprocess_live(cmd_args, custom_env=exec_env) == 0:
                    mark_successful_run("player_context_verification")

        st.markdown("#### College Stats (CFBD API)")
        st.caption("Fetch baseline college player stats for a specific season from CollegeFootballData.com.")
        render_last_success("college_stats")
        col_cfbd1, col_cfbd2 = st.columns(2)
        with col_cfbd1:
            cfbd_season = st.number_input("CFBD Season", min_value=2010, max_value=2030, value=2024, step=1)
        with col_cfbd2:
            default_cfbd_key = os.environ.get("CFBD_API_KEY", "")
            cfbd_key = st.text_input("CFBD API Key", type="password", value=default_cfbd_key, placeholder="e.g. mock or your_cfbd_key")

        if st.button("🚀 Ingest CFBD College Stats", type="secondary"):
            if not cfbd_key.strip():
                st.error("A CFBD API Key (or 'mock') is required to run the ingestion.")
            else:
                cmd_args = ["-m", "src.ingest_college_data", "--season", str(cfbd_season)]
                exec_env = {}
                exec_env["CFBD_API_KEY"] = cfbd_key.strip()
                if gcp_key_path:
                    exec_env["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.abspath(gcp_key_path)
                if run_subprocess_live(cmd_args, custom_env=exec_env) == 0:
                    mark_successful_run("college_stats")

    render_section_header(
        "Warehouse Writes",
        "warehouse-writes",
        "High-impact table loads. Review write disposition and source file mappings before running.",
    )
    with st.container(border=True):
        st.markdown("#### Run Statistics Ingestion")
        st.caption("Download from APIs and load directly into partitioned BigQuery tables.")
        render_last_success("statistics_ingestion")

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

        seasons_clean = seasons_input.strip()
        if write_disp == "WRITE_TRUNCATE":
            st.warning("WRITE_TRUNCATE overwrites the target warehouse tables for the selected seasons.")

        if st.button("🚀 Run Ingestion Pipeline", type="primary"):
            if not seasons_clean:
                st.error("Please provide at least one target season.")
            else:
                cmd_args = ["-m", "src.pipeline", "--seasons", seasons_clean, "--write-disposition", write_disp]

                exec_env = {}
                if gcp_key_path:
                    exec_env["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.abspath(gcp_key_path)

                if run_subprocess_live(cmd_args, custom_env=exec_env) == 0:
                    mark_successful_run("statistics_ingestion")

        st.markdown("#### Upload Rookie Scouting CSV")
        st.caption("Import advanced player profiling spreadsheets into BigQuery.")
        render_last_success("rookie_scouting_csv")
        scouting_file = st.file_uploader("Choose a CSV file", type=["csv"], key="scouting_csv_uploader")

        if scouting_file is not None:
            import pandas as pd
            try:
                df_scout = pd.read_csv(scouting_file)
                st.success(f"Successfully loaded '{scouting_file.name}' with {len(df_scout)} rows!")

                st.dataframe(df_scout.head(3))

                st.markdown("#### Map CSV Columns to Database Fields")
                cols_options = ["None"] + list(df_scout.columns)

                def find_default_col(options, candidates):
                    for c in candidates:
                        for opt in options:
                            if c.lower() in str(opt).lower():
                                return opt
                    return "None"

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
                                from google.cloud import bigquery
                                from src.setup_college_tables import create_college_tables

                                mapped_df = pd.DataFrame()
                                mapped_df["season"] = df_scout[c_season].astype("int64")
                                mapped_df["player_name"] = df_scout[c_name].astype(str)

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

                                create_college_tables()
                                bq_proj = BIGQUERY_PROJECT_ID
                                client = bigquery.Client(project=bq_proj)
                                table_ref = f"{bq_proj}.fantasy_football_brain.rookie_scouting_metrics"

                                job_config = bigquery.LoadJobConfig(
                                    write_disposition=bigquery.WriteDisposition.WRITE_APPEND
                                )
                                job = client.load_table_from_dataframe(mapped_df, table_ref, job_config=job_config)
                                job.result()
                                mark_successful_run("rookie_scouting_csv")
                                st.success(f"✔ Successfully loaded {len(mapped_df)} rows into '{table_ref}'!")
                            except Exception as ex:
                                st.error(f"❌ Failed to upload to BigQuery: {ex}")
            except Exception as ex:
                st.error(f"❌ Failed to parse CSV: {ex}")

# --- SHOW PREP ---
with tab_show_prep:
    st.markdown("### Show Prep")
    st.caption("Find episode topics, build segment angles, and pull production-ready cuts without cluttering the Pigskin chat.")
    render_tab_bookmarks([
        ("Reddit Topics", "reddit-topics"),
        ("Fraud Watch", "fraud-watch"),
    ])
    render_section_header(
        "Reddit Topic Scout",
        "reddit-topics",
        "Scan weekly top fantasy football Reddit posts for show-topic clusters.",
        first=True,
    )
    render_reddit_topic_scout()
    render_section_header(
        "Fraud Watch",
        "fraud-watch",
        "Rank weekly box-score spikes against role quality, usage stability, touchdown dependence, and snap trust.",
    )
    render_fraud_watch_segment()

# --- PLAYER PROFILES ---
with tab_player_profiles:
    render_player_profiles_tab()

# --- VIEWER TEAM LAB ---
with tab_viewer_lab:
    st.markdown("### Viewer Team Lab")
    st.caption("Load public Sleeper teams, audit roster fragility, and turn viewer submissions into show segments.")
    render_tab_bookmarks([
        ("Sleeper Loader", "sleeper-loader"),
        ("Team Console", "team-console"),
    ])
    render_section_header(
        "Sleeper Viewer Team Analysis",
        "sleeper-loader",
        "Load one public Sleeper league/team snapshot into BigQuery for roster analysis.",
        first=True,
    )
    render_sleeper_viewer_team_analysis()

# --- PIGSKIN STUDIO ---
with tab_pigskin:
    render_tab_bookmarks([
        ("Pigskin Chat", "pigskin-chat"),
    ])
    render_section_header(
        "💬 Pigskin",
        "pigskin-chat",
        "Chat with the AI vs Vibes co-host built to roast bad process and back it up with data.",
        first=True,
    )
    render_ai_cohost()

# --- TRADE LAB ---
with tab_trade_lab:
    render_tab_bookmarks([
        ("Trade Analyzer", "trade-analyzer"),
    ])
    render_section_header(
        "📊 Trade & Value Analyzer",
        "trade-analyzer",
        "Compare multiple players and draft pick values side-by-side using market data and AI projections.",
        first=True,
    )
    render_value_analyzer()
