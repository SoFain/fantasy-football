import os
import sys
import subprocess
import html
import logging
import json
import streamlit as st

from src.compat_flags import (
    USE_COMPAT_PLAYER_PROFILES,
    USE_COMPAT_SLEEPER_WATCH,
    USE_COMPAT_TRADE_ASSETS,
    USE_COMPAT_TRADE_PLAYER_HISTORY,
    USE_COMPAT_VIEWER_TEAM_CONTEXT,
    compat_flag_enabled,
)
from src.cloud_run_jobs import (
    DATA_OPS_ALLOW_JOB_TRIGGER,
    USE_CLOUD_RUN_JOBS_FOR_DATA_OPS,
    build_job_overrides,
    cloud_run_jobs_feature_enabled,
    command_to_string,
    data_ops_job_trigger_allowed,
    get_recent_cloud_run_job_runs,
    list_configured_jobs,
    should_use_cloud_run_jobs_for_data_ops,
    trigger_cloud_run_job,
)
from src.pigskin_chat_schema import render_pigskin_chat_schema
from src.pigskin_context_tools import (
    execute_pigskin_context_tool,
    get_pigskin_context_tool_declarations,
)

DEFAULT_BIGQUERY_PROJECT = "fantasy-football-498121"
BIGQUERY_PROJECT_ID = (
    os.environ.get("BQ_PROJECT")
    or os.environ.get("GCP_PROJECT")
    or os.environ.get("GOOGLE_CLOUD_PROJECT")
    or DEFAULT_BIGQUERY_PROJECT
)
os.environ.setdefault("BQ_PROJECT", BIGQUERY_PROJECT_ID)
GEMINI_MODEL_NAME = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash")


def use_compat_player_profiles():
    return compat_flag_enabled(USE_COMPAT_PLAYER_PROFILES)


def use_compat_sleeper_watch():
    return compat_flag_enabled(USE_COMPAT_SLEEPER_WATCH)


def use_compat_trade_assets():
    return compat_flag_enabled(USE_COMPAT_TRADE_ASSETS)


def use_compat_trade_player_history():
    return compat_flag_enabled(USE_COMPAT_TRADE_PLAYER_HISTORY)


def use_compat_viewer_team_context():
    return compat_flag_enabled(USE_COMPAT_VIEWER_TEAM_CONTEXT)


def use_cloud_run_jobs_for_data_ops():
    return should_use_cloud_run_jobs_for_data_ops()

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

def create_gemini_client(api_key):
    from google import genai

    return genai.Client(api_key=api_key)

def create_gemini_model(api_key, tools=None, system_instruction=None):
    from google.genai import types

    config_kwargs = {}
    if system_instruction:
        config_kwargs["system_instruction"] = system_instruction
    if tools:
        config_kwargs["tools"] = [types.Tool(function_declarations=tools)]
        config_kwargs["automatic_function_calling"] = types.AutomaticFunctionCallingConfig(disable=True)
    config = types.GenerateContentConfig(**config_kwargs) if config_kwargs else None
    return GeminiModel(create_gemini_client(api_key), GEMINI_MODEL_NAME, config)

class GeminiModel:
    def __init__(self, client, model_name, config=None):
        self.client = client
        self.model_name = model_name
        self.config = config

    def generate_content(self, prompt):
        return self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=self.config,
        )

    def start_chat(self):
        return GeminiChatSession(self.client, self.model_name, self.config)

class GeminiChatSession:
    def __init__(self, client, model_name, config=None):
        self.client = client
        self.model_name = model_name
        self.config = config
        self.contents = []

    def send_message(self, message):
        from google.genai import types

        if isinstance(message, str):
            self.contents.append(types.Content(role="user", parts=[types.Part(text=message)]))
        else:
            self.contents.append(types.Content(role="user", parts=[message]))

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=self.contents,
            config=self.config,
        )
        if response.candidates:
            self.contents.append(response.candidates[0].content)
        return response

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
        from google.api_core.exceptions import NotFound
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
    except NotFound:
        return None
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


def render_cloud_run_jobs_data_ops_panel():
    use_cloud_jobs = use_cloud_run_jobs_for_data_ops()
    trigger_allowed = data_ops_job_trigger_allowed()
    cloud_jobs_enabled = cloud_run_jobs_feature_enabled()

    status_cols = st.columns(3)
    with status_cols[0]:
        st.metric("Cloud Run path", "Enabled" if use_cloud_jobs else "Disabled")
    with status_cols[1]:
        st.metric("Trigger allow flag", "Enabled" if trigger_allowed else "Disabled")
    with status_cols[2]:
        st.metric("Configured jobs", len(list_configured_jobs()))

    st.caption(
        f"`{USE_CLOUD_RUN_JOBS_FOR_DATA_OPS}` is "
        f"{'true' if use_cloud_jobs else 'false'}; `{DATA_OPS_ALLOW_JOB_TRIGGER}` is "
        f"{'true' if trigger_allowed else 'false'}."
    )
    if not cloud_jobs_enabled:
        st.info("Cloud Run Job execution is not active. The local subprocess controls below remain the active Data Ops path.")
    elif not trigger_allowed:
        st.warning("Cloud Run Job previews are enabled, but triggering is blocked until the explicit allow flag is set.")

    jobs = list_configured_jobs()
    st.dataframe(
        [
            {
                "job_name": job["job_name"],
                "required_args": ", ".join(job["required_args"]),
                "allowed_args": ", ".join(job["allowed_args"]),
                "description": job["description"],
            }
            for job in jobs
        ],
        hide_index=True,
        use_container_width=True,
    )

    selected_job = st.selectbox(
        "Cloud Run Job",
        options=[job["job_name"] for job in jobs],
        help="Choose a configured job. Unknown job names are rejected by the helper.",
    )
    args_text = st.text_area(
        "Job args JSON",
        value="{}",
        key=f"cloud_run_job_args_{selected_job}",
        help='Example: {"season": 2026, "week": 1}. Only the selected job allowed args are accepted.',
    )

    args_payload = {}
    preview_error = None
    try:
        args_payload = json.loads(args_text.strip() or "{}")
        if not isinstance(args_payload, dict):
            raise ValueError("Job args JSON must be an object.")
        build_job_overrides(selected_job, args_payload)
        st.markdown("#### Dry-run command preview")
        st.code(command_to_string(trigger_cloud_run_job(selected_job, args_payload, dry_run=True)["command"]), language="bash")
    except Exception as ex:
        preview_error = ex
        st.warning(f"Cloud Run Job preview is unavailable: {ex}")

    confirmed = st.checkbox(
        "I understand this triggers a Cloud Run Job and may incur Cloud Run, BigQuery, API, or external data costs.",
        value=False,
    )
    trigger_disabled = bool(preview_error) or not use_cloud_jobs or not trigger_allowed or not confirmed
    if st.button("Trigger Cloud Run Job", type="primary", disabled=trigger_disabled):
        try:
            result = trigger_cloud_run_job(selected_job, args_payload, dry_run=False)
            st.success(f"Cloud Run Job triggered: {result.get('execution_name') or selected_job}")
        except Exception as ex:
            st.error(f"Cloud Run Job trigger failed: {ex}")

    with st.expander("Recent Cloud Run Job Runs", expanded=False):
        try:
            recent_runs = get_recent_cloud_run_job_runs(limit=25)
            if recent_runs:
                st.dataframe(recent_runs, hide_index=True, use_container_width=True)
            else:
                st.caption("No Cloud Run Job runs recorded yet.")
        except Exception as ex:
            st.caption(f"Recent job status is unavailable: {ex}")


@st.cache_data(ttl=3600, show_spinner=False)
def execute_bq_cached(sql_query: str):
    from google.cloud import bigquery
    bq_client = bigquery.Client(project=BIGQUERY_PROJECT_ID)
    query_job = bq_client.query(sql_query)
    df = query_job.result().to_dataframe()
    return df


def render_data_path_status(label, using_compat):
    mode = "compatibility contract path" if using_compat else "legacy warehouse path"
    st.caption(f"Data path: {label} is using the {mode}.")


def render_compat_metadata(df, label):
    if df is None or df.empty:
        return
    metadata_parts = []
    if "source_freshness_json" in df.columns:
        freshness_values = [value for value in df["source_freshness_json"].dropna().astype(str).unique() if value]
        if freshness_values:
            metadata_parts.append(f"source freshness: `{freshness_values[0][:240]}`")
    if "missing_data_flags" in df.columns:
        flag_values = [value for value in df["missing_data_flags"].dropna().astype(str).unique() if value and value != "[]"]
        if flag_values:
            metadata_parts.append(f"missing flags: `{flag_values[0][:240]}`")
    if metadata_parts:
        st.caption(f"{label} metadata: " + " | ".join(metadata_parts))


def _compat_json_value(value):
    if value is None:
        return {}
    try:
        if hasattr(value, "item"):
            value = value.item()
    except Exception:
        pass
    if isinstance(value, str) and not value.strip():
        return {}
    if isinstance(value, float) and value != value:
        return {}
    if isinstance(value, (dict, list)):
        return value
    try:
        parsed = json.loads(str(value))
    except Exception:
        return {}
    if isinstance(parsed, str):
        try:
            parsed = json.loads(parsed)
        except Exception:
            return {}
    return parsed if isinstance(parsed, (dict, list)) else {}


def _compat_first_object(value):
    parsed = _compat_json_value(value)
    if isinstance(parsed, list):
        return parsed[0] if parsed and isinstance(parsed[0], dict) else {}
    return parsed if isinstance(parsed, dict) else {}


def _compat_column(df, column_name, default=None):
    import pandas as pd

    if column_name in df.columns:
        return df[column_name]
    return pd.Series([default] * len(df), index=df.index)


def _compat_json_field(df, column_name, field_name, default=None, first_object=False):
    parser = _compat_first_object if first_object else _compat_json_value
    return _compat_column(df, column_name).apply(
        lambda value: parser(value).get(field_name, default)
    )


def normalize_compat_player_profiles_data(df):
    import pandas as pd

    if df.empty:
        return df
    out = pd.DataFrame(index=df.index)
    player_id = _compat_column(df, "player_id_internal").combine_first(_compat_column(df, "source_player_key"))
    out["player_id"] = player_id
    out["player_name"] = _compat_column(df, "display_name")
    out["player_display_name"] = _compat_column(df, "display_name")
    out["position"] = _compat_column(df, "position")
    out["team"] = _compat_column(df, "current_team")
    out["birth_date"] = _compat_column(df, "birth_date")
    out["height"] = None
    out["weight"] = None
    out["headshot"] = None
    out["college_name"] = _compat_json_field(df, "college_summary_json", "college_team")
    out["jersey_number"] = None
    out["rookie_season"] = _compat_column(df, "rookie_year")
    out["years_of_experience"] = None
    out["draft_year"] = None
    out["draft_round"] = None
    out["draft_pick"] = None
    out["draft_team"] = None

    out["avg_ppr"] = _compat_column(df, "fantasy_points_per_game_current_season", 0.0).fillna(0.0)
    out["total_targets"] = _compat_column(df, "targets_last_3", 0.0).fillna(0.0)
    out["total_receptions"] = _compat_column(df, "receptions_last_3", 0.0).fillna(0.0)
    out["total_receiving_yards"] = 0.0
    out["total_receiving_tds"] = 0.0
    out["total_carries"] = _compat_column(df, "carries_last_3", 0.0).fillna(0.0)
    out["total_rushing_yards"] = 0.0
    out["total_rushing_tds"] = 0.0
    out["total_pass_attempts"] = 0.0
    out["total_passing_yards"] = 0.0
    out["total_passing_tds"] = 0.0
    out["avg_target_share"] = _compat_column(df, "target_share_last_3", 0.0).fillna(0.0)
    out["avg_wopr"] = _compat_json_field(df, "role_summary_json", "current_season_wopr", 0.0).fillna(
        _compat_json_field(df, "role_summary_json", "wopr_last_3", 0.0)
    )
    out["avg_epa"] = _compat_json_field(df, "epa_summary_json", "avg_total_epa", 0.0).fillna(0.0)
    out["avg_snap_share"] = _compat_column(df, "snap_share_last_3", 0.0).fillna(0.0)
    out["avg_opportunity"] = _compat_json_field(df, "efficiency_summary_json", "avg_opportunity_score", 0.0).fillna(
        _compat_json_field(df, "role_summary_json", "opportunity_score_last_3", 0.0)
    )
    out["avg_efficiency"] = _compat_json_field(df, "efficiency_summary_json", "avg_efficiency_score", 0.0).fillna(0.0)
    out["avg_role_quality"] = _compat_json_field(df, "role_summary_json", "current_season_role_quality", 0.0).fillna(
        _compat_json_field(df, "role_summary_json", "role_quality_score_last_3", 0.0)
    )
    out["avg_role_fragility"] = _compat_json_field(df, "role_summary_json", "current_season_role_fragility", 0.0).fillna(
        _compat_json_field(df, "role_summary_json", "role_fragility_score_last_3", 0.0)
    )
    out["avg_grade"] = _compat_json_field(df, "efficiency_summary_json", "avg_analytical_grade", 0.0).fillna(0.0)
    out["avg_carry_share"] = _compat_column(df, "rush_share_last_3", 0.0).fillna(0.0)
    out["avg_player_run_opportunity_pct"] = _compat_column(df, "rush_share_last_3", 0.0).fillna(0.0)
    out["avg_player_pass_opportunity_pct"] = _compat_column(df, "target_share_last_3", 0.0).fillna(0.0)

    out["contract_value"] = _compat_json_field(df, "contract_summary_json", "contract_value")
    out["contract_apy"] = _compat_json_field(df, "contract_summary_json", "contract_apy")
    out["contract_guaranteed"] = _compat_json_field(df, "contract_summary_json", "contract_guaranteed")
    out["contract_year_signed"] = _compat_json_field(df, "contract_summary_json", "contract_year_signed")
    out["depth_position"] = _compat_json_field(df, "depth_chart_summary_json", "depth_position", first_object=True)
    out["depth_rank"] = _compat_json_field(df, "depth_chart_summary_json", "depth_rank", first_object=True)
    out["college_team"] = _compat_json_field(df, "college_summary_json", "college_team")
    out["college_conf"] = _compat_json_field(df, "college_summary_json", "college_conference")
    out["college_games"] = _compat_json_field(df, "college_summary_json", "college_games")
    out["college_passing_yards"] = _compat_json_field(df, "college_summary_json", "college_passing_yards")
    out["college_passing_tds"] = _compat_json_field(df, "college_summary_json", "college_passing_tds")
    out["college_rushing_yards"] = _compat_json_field(df, "college_summary_json", "college_rushing_yards")
    out["college_rushing_tds"] = _compat_json_field(df, "college_summary_json", "college_rushing_tds")
    out["college_receptions"] = _compat_json_field(df, "college_summary_json", "college_receptions")
    out["college_receiving_yards"] = _compat_json_field(df, "college_summary_json", "college_receiving_yards")
    out["college_receiving_tds"] = _compat_json_field(df, "college_summary_json", "college_receiving_tds")
    out["yards_after_contact_per_attempt"] = _compat_json_field(df, "rookie_scouting_summary_json", "yards_after_contact_per_attempt")
    out["yards_per_route_run"] = _compat_json_field(df, "rookie_scouting_summary_json", "yards_per_route_run")
    out["college_target_share"] = _compat_json_field(df, "rookie_scouting_summary_json", "college_target_share")
    out["catch_radius_grade"] = _compat_json_field(df, "rookie_scouting_summary_json", "catch_radius_grade")
    out["success_rate_vs_man"] = _compat_json_field(df, "rookie_scouting_summary_json", "success_rate_vs_man")
    out["success_rate_vs_zone"] = _compat_json_field(df, "rookie_scouting_summary_json", "success_rate_vs_zone")
    out["success_rate_vs_press"] = _compat_json_field(df, "rookie_scouting_summary_json", "success_rate_vs_press")
    out["avg_separation_inches"] = _compat_json_field(df, "rookie_scouting_summary_json", "avg_separation_inches")
    out["scouting_source"] = _compat_json_field(df, "rookie_scouting_summary_json", "scouting_source")
    out["pos_rank"] = _compat_column(df, "pigskin_rank_position").combine_first(_compat_column(df, "position_rank_by_profile"))
    out["source_freshness_json"] = _compat_column(df, "source_freshness_json")
    out["missing_data_flags"] = _compat_column(df, "missing_data_flags")
    return out


def fetch_compat_player_profiles_data():
    import pandas as pd
    from src.player_profiles import list_player_profiles

    rows = list_player_profiles(limit=5000)
    if not rows:
        return pd.DataFrame()
    return normalize_compat_player_profiles_data(pd.DataFrame(rows))


def normalize_compat_sleeper_watch_data(rows):
    import pandas as pd

    df = pd.DataFrame(rows)
    if df.empty:
        return df
    out = pd.DataFrame(index=df.index)
    out["player_name"] = _compat_column(df, "display_name")
    out["position"] = _compat_column(df, "position")
    out["team"] = _compat_column(df, "team")
    out["opponent_team"] = _compat_column(df, "opponent")
    out["roster_pct"] = _compat_column(df, "rostered_rate", 0.0).fillna(0.0)
    out["rolling_3_week_ppr"] = _compat_column(df, "fantasy_points_last_3", 0.0).fillna(0.0) / 3.0
    out["snap_share"] = _compat_column(df, "snap_share_last_3", 0.0).fillna(0.0)
    out["targets_3w"] = _compat_column(df, "targets_last_3", 0.0).fillna(0.0) / 3.0
    out["carries_3w"] = _compat_column(df, "carries_last_3", 0.0).fillna(0.0) / 3.0
    out["wopr"] = _compat_column(df, "target_share_last_3", 0.0).fillna(0.0)
    out["epa"] = _compat_column(df, "expected_vs_actual_signal", 0.0).fillna(0.0)
    out["opp_def_rank"] = _compat_column(df, "matchup_score", 0.0).fillna(0.0)
    out["sleeper_score"] = _compat_column(df, "streamer_score", 0.0).fillna(0.0)
    out["source_freshness_json"] = _compat_column(df, "source_freshness_json")
    out["missing_data_flags"] = _compat_column(df, "missing_data_flags")
    return out


def fetch_compat_sleeper_watch_candidates_data():
    from src.sleeper_watch import get_sleeper_watch_candidates

    rows = get_sleeper_watch_candidates(limit=250)
    return normalize_compat_sleeper_watch_data(rows)


def load_compat_trade_assets():
    import pandas as pd
    from src.trade_assets import get_trade_assets

    rows = get_trade_assets(limit=250)
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    out = pd.DataFrame(index=df.index)
    out["player_display_name"] = _compat_column(df, "display_name")
    out["position"] = _compat_column(df, "position")
    out["team"] = _compat_column(df, "team")
    out["market_value"] = _compat_column(df, "market_value").combine_first(_compat_column(df, "risk_adjusted_trade_value"))
    out["overall_rank"] = _compat_column(df, "market_value_rank_overall")
    out["position_rank"] = _compat_column(df, "market_value_rank_position")
    out["redraft_value"] = _compat_column(df, "redraft_value_placeholder").combine_first(out["market_value"])
    out["tier"] = _compat_column(df, "market_tier").combine_first(_compat_column(df, "pigskin_tier"))
    out["age"] = _compat_column(df, "age")
    out["source_freshness_json"] = _compat_column(df, "source_freshness_json")
    out["missing_data_flags"] = _compat_column(df, "missing_data_flags")
    out["_data_path"] = "compat"
    return out


def query_compat_trade_player_history(name):
    from src.trade_history import get_trade_player_history

    return get_trade_player_history(player_name=name, limit=10)


def get_compat_sleeper_viewer_team_context(console_context):
    from src.viewer_team_context import get_viewer_team_context

    roster_id = console_context.get("roster_id") or None
    manager_id = console_context.get("manager_id") or None
    if not roster_id and not manager_id:
        return (
            "Viewer-team compatibility context is unavailable.\n"
            "Reason: compat_viewer_team_context requires roster_id or manager_id to avoid selecting the wrong team.\n"
            "Reload the viewer team with a roster ID, or disable USE_COMPAT_VIEWER_TEAM_CONTEXT to use the legacy lookup path."
        )

    context = get_viewer_team_context(
        console_context["league_id"],
        roster_id=roster_id,
        manager_id=manager_id,
    )
    if context.get("unavailable"):
        return (
            "Viewer-team compatibility context is unavailable.\n"
            f"Reason: {context.get('reason', 'unknown')}\n"
            "No legacy viewer-team context was mixed into this flagged path."
        )
    metadata = (
        f"Source freshness: {context.get('source_freshness_json') or 'unknown'}\n"
        f"Missing data flags: {context.get('missing_data_flags') or '[]'}"
    )
    return f"{context.get('packet_text') or 'Viewer-team packet text is empty.'}\n\n{metadata}"

def repair_generated_sql(sql_query: str) -> str:
    import re

    if re.search(r"\banalytics_player_weekly_truth\b", sql_query, flags=re.IGNORECASE):
        sql_query = re.sub(
            r"\bLOWER\s*\(\s*([a-zA-Z_][a-zA-Z0-9_]*\.)?player_name\s*\)",
            lambda match: f"LOWER({match.group(1) or ''}player_full_name)",
            sql_query,
            flags=re.IGNORECASE,
        )

        def replace_full_name_predicate(match):
            value = match.group("value")
            if " " not in value.strip():
                return match.group(0)
            prefix = match.group("prefix") or ""
            return f"{prefix}player_full_name {match.group('operator')} '{value}'"

        sql_query = re.sub(
            r"\b(?P<prefix>[a-zA-Z_][a-zA-Z0-9_]*\.)?player_name\s+(?P<operator>=|LIKE)\s+'(?P<value>[^']+)'",
            replace_full_name_predicate,
            sql_query,
            flags=re.IGNORECASE,
        )

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


def render_sleeper_watch_segment():
    import html
    import os
    import pandas as pd

    st.markdown("### 🕵️ Sleeper Watch Search")
    st.markdown(
        "100% data-driven sleepers and streamers ranked by role, recent volume, efficiency, and opponent defensive matchups."
    )
    using_compat_sleeper_watch = use_compat_sleeper_watch()
    render_data_path_status("Sleeper Watch", using_compat_sleeper_watch)

    try:
        if using_compat_sleeper_watch:
            df = fetch_compat_sleeper_watch_candidates_data()
        else:
            # Ingestion or data availability check
            sql_query = f"""
            WITH latest_week AS (
                SELECT MAX(season) AS max_season, MAX(week) AS max_week
                FROM `{BIGQUERY_PROJECT_ID}.fantasy_football_brain.compat_sleeper_watch_candidates`
            )
            SELECT
                display_name AS player_name,
                position,
                team,
                opponent AS opponent_team,
                rostered_rate AS roster_pct,
                COALESCE(rolling_3_week_ppr, 0.0) AS rolling_3_week_ppr,
                COALESCE(snap_share_last_3, 0.0) AS snap_share,
                COALESCE(targets_last_3, 0.0) / 3.0 AS targets_3w,
                COALESCE(carries_last_3, 0.0) / 3.0 AS carries_3w,
                COALESCE(target_share_last_3, 0.0) AS wopr,
                COALESCE(expected_vs_actual_signal, 0.0) AS epa,
                CAST(COALESCE(matchup_score, 0.0) AS INT64) AS opp_def_rank,
                COALESCE(streamer_score, 0.0) AS sleeper_score
            FROM `{BIGQUERY_PROJECT_ID}.fantasy_football_brain.compat_sleeper_watch_candidates` c, latest_week lw
            WHERE c.season = lw.max_season AND c.week = lw.max_week
            """
            df = execute_bq_cached(sql_query)
    except Exception as e:
        st.info(f"Sleeper Watch data is not materialized yet or the selected data path failed: {e}")
        return

    if df.empty:
        if using_compat_sleeper_watch:
            st.info("Sleeper Watch compatibility candidates are unavailable or empty. Disable USE_COMPAT_SLEEPER_WATCH to use the legacy warehouse path.")
        else:
            st.info("Sleeper Watch has no candidates for the latest loaded week.")
        return
    if using_compat_sleeper_watch:
        render_compat_metadata(df, "Sleeper Watch")

    # Add interactive settings in columns
    col_pct, col_pos, col_limit = st.columns(3)
    with col_pct:
        roster_threshold = st.slider(
            "Max Rostered Percentage (%)",
            min_value=10,
            max_value=100,
            value=50,
            step=5,
            help="Show players rostered in this percentage of loaded leagues or less.",
            key="sleeper_roster_threshold_slider",
        )
    with col_pos:
        pos_filter = st.selectbox(
            "Filter by Position",
            options=["All", "QB", "RB", "WR", "TE"],
            index=0,
            key="sleeper_position_filter_select",
        )
    with col_limit:
        candidates_limit = st.selectbox(
            "Number of Candidates",
            options=[25, 30, 40, 50],
            index=0,
            key="sleeper_candidates_limit_select",
        )

    # Filter data in pandas for instant reactivity
    df_filtered = df.copy()

    # Filter by roster percentage
    df_filtered = df_filtered[
        df_filtered["roster_pct"] <= (roster_threshold / 100.0)
    ]

    # Filter by position
    if pos_filter != "All":
        df_filtered = df_filtered[df_filtered["position"] == pos_filter]

    # Sort and limit
    df_filtered = df_filtered.sort_values(
        by="sleeper_score", ascending=False
    ).head(candidates_limit)

    if df_filtered.empty:
        st.warning("No players matching the selected filters.")
        return

    # Insert Rank column
    df_filtered.insert(0, "Rank", range(1, len(df_filtered) + 1))

    # Format columns for display
    display_df = df_filtered.copy()
    display_df["roster_pct"] = display_df["roster_pct"].apply(
        lambda x: f"{x*100:.1f}%"
    )
    display_df["snap_share"] = display_df["snap_share"].apply(
        lambda x: f"{x:.1f}%" if not pd.isna(x) else "N/A"
    )
    display_df["wopr"] = display_df["wopr"].apply(lambda x: f"{x:.2f}")
    display_df["epa"] = display_df["epa"].apply(lambda x: f"{x:.2f}")
    display_df["rolling_3_week_ppr"] = display_df["rolling_3_week_ppr"].apply(
        lambda x: f"{x:.2f}"
    )
    display_df["sleeper_score"] = display_df["sleeper_score"].apply(
        lambda x: f"{x:.2f}"
    )

    # Rename columns to show-ready labels
    display_df = display_df.rename(
        columns={
            "player_name": "Player",
            "position": "Position",
            "team": "Team",
            "opponent_team": "Opponent",
            "roster_pct": "Rostered %",
            "rolling_3_week_ppr": "3W PPR PPG",
            "snap_share": "Snap Share",
            "targets_3w": "3W Avg Targets",
            "carries_3w": "3W Avg Carries",
            "wopr": "WOPR",
            "epa": "Weekly EPA",
            "opp_def_rank": "Opp Def Rank vs Pos",
            "sleeper_score": "Sleeper Score",
        }
    )

    # Render dataframe
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Opp Def Rank vs Pos": st.column_config.NumberColumn(
                help="Matchup ranking: 1 is best defense (hardest matchup), 32 is worst defense (easiest matchup)."
            ),
            "Sleeper Score": st.column_config.NumberColumn(
                help="AI vs Vibes proprietary formula based on snaps, opportunity, EPA, and matchup favorable rating."
            ),
        },
    )

    # Interactive Pigskin Breakdown
    st.markdown("#### 🧠 Pigskin's Quick Take")
    selected_player = st.selectbox(
        "Select a Sleeper candidate for a data-driven roast/verdict:",
        options=df_filtered["player_name"].tolist(),
        index=0,
        key="sleeper_player_verdict_select",
    )

    if selected_player:
        player_row = df_filtered[
            df_filtered["player_name"] == selected_player
        ].iloc[0]
        active_gemini_key = os.environ.get("GEMINI_API_KEY", "")

        if not active_gemini_key:
            st.info(
                "Enter your Gemini API key in the sidebar to get Pigskin's snarky take."
            )
        else:
            try:
                model = create_gemini_model(active_gemini_key)

                # Construct data summary for prompt
                data_summary = f"""
                Player: {selected_player}
                Position: {player_row['position']}
                Team: {player_row['team']}
                Opponent: {player_row['opponent_team']}
                Rostered % (in loaded Sleeper leagues): {player_row['roster_pct']*100:.1f}%
                Recent snap share: {player_row['snap_share']:.1f}%
                3-Week average targets: {player_row['targets_3w']:.1f}
                3-Week average carries: {player_row['carries_3w']:.1f}
                WOPR: {player_row['wopr']:.2f}
                EPA: {player_row['epa']:.2f}
                Opponent Defensive Rank vs Position (1 to 32, where 32 is easiest): {player_row['opp_def_rank']}
                Sleeper Score: {player_row['sleeper_score']:.2f}
                """

                # Call Gemini
                prompt = f"""
                You are Pigskin, the snarky analytical co-host of AI vs Vibes.
                Write a 1-2 sentence data-driven verdict explaining why {selected_player} is a potential sleeper or streamer for this week based on the metrics below.

                Metrics:
                {data_summary}

                Requirements:
                1. Follow the Pigskin Voice Contract (arrogant, snarky, football-sick, uses slang like cooked, vibes tax, fraud watch, cope naturally).
                2. Be concise (max 2 sentences).
                3. Do not make up facts. Mention the exact stats (e.g. WOPR, snaps, or matchup rank) to justify your claim.
                """
                res = model.generate_content(prompt)

                st.markdown(f"**Pigskin's Verdict on {selected_player}:**")
                st.write(res.text)
            except Exception as ex:
                st.error(f"Failed to generate take: {ex}")


@st.cache_data(ttl=3600, show_spinner="Loading player profiles database...")
def fetch_player_profiles_data():
    if use_compat_player_profiles():
        return fetch_compat_player_profiles_data()

    from google.cloud import bigquery
    sql_query = f"""
    WITH latest_roster_season AS (
        SELECT MAX(season) AS max_season
        FROM `{BIGQUERY_PROJECT_ID}.fantasy_football_brain.player_rosters`
    ),
    active_roster_players AS (
        SELECT
            r.gsis_id AS player_id,
            ANY_VALUE(r.display_name) AS player_name,
            ANY_VALUE(r.display_name) AS player_display_name,
            ANY_VALUE(r.position) AS position,
            ANY_VALUE(r.latest_team) AS team,
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
        FROM `{BIGQUERY_PROJECT_ID}.fantasy_football_brain.player_rosters` r, latest_roster_season lrs
        WHERE r.season = lrs.max_season AND r.gsis_id IS NOT NULL
        GROUP BY r.gsis_id
    ),
    latest_stat_season AS (
        SELECT
            player_id,
            MAX(season) AS max_stat_season
        FROM `{BIGQUERY_PROJECT_ID}.fantasy_football_brain.analytics_player_weekly_truth`
        GROUP BY player_id
    ),
    player_weekly_agg AS (
        SELECT
            t.player_id,
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
            AVG(t.analytical_grade) AS avg_grade,
            AVG(t.carry_share) AS avg_carry_share,
            AVG(t.player_run_opportunity_pct) AS avg_player_run_opportunity_pct,
            AVG(t.player_pass_opportunity_pct) AS avg_player_pass_opportunity_pct
        FROM `{BIGQUERY_PROJECT_ID}.fantasy_football_brain.analytics_player_weekly_truth` t
        JOIN latest_stat_season lss
            ON t.player_id = lss.player_id AND t.season = lss.max_stat_season
        GROUP BY t.player_id
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
    ),
    latest_depth_charts AS (
        SELECT
            gsis_id,
            ANY_VALUE(pos_abb) AS depth_position,
            ANY_VALUE(pos_rank) AS depth_rank
        FROM (
            SELECT
                gsis_id,
                pos_abb,
                pos_rank,
                ROW_NUMBER() OVER(PARTITION BY gsis_id ORDER BY dt DESC) as rn
            FROM `{BIGQUERY_PROJECT_ID}.fantasy_football_brain.depth_charts`
        )
        WHERE rn = 1 AND gsis_id IS NOT NULL
        GROUP BY gsis_id
    ),
    college_stats_agg AS (
        SELECT
            LOWER(player_name) AS clean_name,
            ANY_VALUE(team) AS college_team,
            ANY_VALUE(conference) AS college_conf,
            ANY_VALUE(games) AS college_games,
            ANY_VALUE(passing_yards) AS college_passing_yards,
            ANY_VALUE(passing_tds) AS college_passing_tds,
            ANY_VALUE(rushing_yards) AS college_rushing_yards,
            ANY_VALUE(rushing_tds) AS college_rushing_tds,
            ANY_VALUE(receptions) AS college_receptions,
            ANY_VALUE(receiving_yards) AS college_receiving_yards,
            ANY_VALUE(receiving_tds) AS college_receiving_tds
        FROM `{BIGQUERY_PROJECT_ID}.fantasy_football_brain.college_player_stats`
        GROUP BY LOWER(player_name)
    ),
    rookie_scouting_agg AS (
        SELECT
            LOWER(player_name) AS clean_name,
            ANY_VALUE(yards_after_contact_per_attempt) AS yards_after_contact_per_attempt,
            ANY_VALUE(yards_per_route_run) AS yards_per_route_run,
            ANY_VALUE(college_target_share) AS college_target_share,
            ANY_VALUE(catch_radius_grade) AS catch_radius_grade,
            ANY_VALUE(success_rate_vs_man) AS success_rate_vs_man,
            ANY_VALUE(success_rate_vs_zone) AS success_rate_vs_zone,
            ANY_VALUE(success_rate_vs_press) AS success_rate_vs_press,
            ANY_VALUE(avg_separation_inches) AS avg_separation_inches,
            ANY_VALUE(data_source) AS scouting_source
        FROM `{BIGQUERY_PROJECT_ID}.fantasy_football_brain.rookie_scouting_metrics`
        GROUP BY LOWER(player_name)
    )
    SELECT
        rp.*,
        COALESCE(agg.avg_ppr, 0.0) AS avg_ppr,
        COALESCE(agg.total_targets, 0.0) AS total_targets,
        COALESCE(agg.total_receptions, 0.0) AS total_receptions,
        COALESCE(agg.total_receiving_yards, 0.0) AS total_receiving_yards,
        COALESCE(agg.total_receiving_tds, 0.0) AS total_receiving_tds,
        COALESCE(agg.total_carries, 0.0) AS total_carries,
        COALESCE(agg.total_rushing_yards, 0.0) AS total_rushing_yards,
        COALESCE(agg.total_rushing_tds, 0.0) AS total_rushing_tds,
        COALESCE(agg.total_pass_attempts, 0.0) AS total_pass_attempts,
        COALESCE(agg.total_passing_yards, 0.0) AS total_passing_yards,
        COALESCE(agg.total_passing_tds, 0.0) AS total_passing_tds,
        COALESCE(agg.avg_target_share, 0.0) AS avg_target_share,
        COALESCE(agg.avg_wopr, 0.0) AS avg_wopr,
        COALESCE(agg.avg_epa, 0.0) AS avg_epa,
        COALESCE(agg.avg_snap_share, 0.0) AS avg_snap_share,
        COALESCE(agg.avg_opportunity, 0.0) AS avg_opportunity,
        COALESCE(agg.avg_efficiency, 0.0) AS avg_efficiency,
        COALESCE(agg.avg_role_quality, 0.0) AS avg_role_quality,
        COALESCE(agg.avg_role_fragility, 0.0) AS avg_role_fragility,
        COALESCE(agg.avg_grade, 0.0) AS avg_grade,
        COALESCE(agg.avg_carry_share, 0.0) AS avg_carry_share,
        COALESCE(agg.avg_player_run_opportunity_pct, 0.0) AS avg_player_run_opportunity_pct,
        COALESCE(agg.avg_player_pass_opportunity_pct, 0.0) AS avg_player_pass_opportunity_pct,
        c.contract_value,
        c.contract_apy,
        c.contract_guaranteed,
        c.contract_year_signed,
        dc.depth_position,
        dc.depth_rank,
        col.college_team,
        col.college_conf,
        col.college_games,
        col.college_passing_yards,
        col.college_passing_tds,
        col.college_rushing_yards,
        col.college_rushing_tds,
        col.college_receptions,
        col.college_receiving_yards,
        col.college_receiving_tds,
        rsk.yards_after_contact_per_attempt,
        rsk.yards_per_route_run,
        rsk.college_target_share,
        rsk.catch_radius_grade,
        rsk.success_rate_vs_man,
        rsk.success_rate_vs_zone,
        rsk.success_rate_vs_press,
        rsk.avg_separation_inches,
        rsk.scouting_source,
        RANK() OVER(PARTITION BY rp.position ORDER BY COALESCE(agg.avg_grade, 0.0) DESC) AS pos_rank
    FROM active_roster_players rp
    LEFT JOIN player_weekly_agg agg ON rp.player_id = agg.player_id
    LEFT JOIN contract_meta c ON rp.player_id = c.gsis_id
    LEFT JOIN latest_depth_charts dc ON rp.player_id = dc.gsis_id
    LEFT JOIN college_stats_agg col ON LOWER(rp.player_name) = col.clean_name
    LEFT JOIN rookie_scouting_agg rsk ON LOWER(rp.player_name) = rsk.clean_name
    """
    client = bigquery.Client(project=BIGQUERY_PROJECT_ID)
    df = client.query(sql_query).result().to_dataframe()
    return df


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_pigskin_rankings_data():
    import pandas as pd
    from google.cloud import bigquery

    sql_query = f"""
    SELECT
        player_id,
        position,
        rank AS pigskin_rank,
        tier AS pigskin_tier,
        ranking_score AS pigskin_ranking_score,
        confidence_score AS pigskin_confidence_score,
        sleeper_team,
        sleeper_status,
        sleeper_depth_chart_position,
        sleeper_depth_chart_order,
        raw_ranking_score,
        depth_chart_penalty,
        avg_passing_epa,
        season_passing_epa,
        avg_rushing_epa,
        season_rushing_epa,
        avg_receiving_epa,
        season_receiving_epa,
        latest_season_wopr,
        previous_season_wopr,
        two_years_ago_wopr,
        latest_season_target_share,
        previous_season_target_share,
        latest_season_carry_share,
        previous_season_carry_share,
        candidate_rank,
        candidate_ranking_score,
        rank_source,
        adjudicated_at,
        ranking_eligibility,
        pigskin_verdict,
        rank_rationale,
        risk_flags,
        what_would_change_mind,
        ranking_version,
        generated_at AS ranking_generated_at,
        model_name AS ranking_model_name,
        prompt_version AS ranking_prompt_version,
        data_snapshot_label AS ranking_data_snapshot
    FROM `{BIGQUERY_PROJECT_ID}.fantasy_football_brain.analytics_pigskin_rankings`
    WHERE is_active = TRUE
    """
    try:
        client = bigquery.Client(project=BIGQUERY_PROJECT_ID)
        return client.query(sql_query).result().to_dataframe()
    except Exception as ex:
        logging.getLogger("app.rankings").warning(f"Could not load canonical Pigskin rankings: {ex}")
        return pd.DataFrame()


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
        passing_epa,
        rushing_epa,
        receiving_epa,
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

def fetch_player_season_rankings(player_id: str):
    from google.cloud import bigquery
    sql_query = f"""
    WITH season_averages AS (
        SELECT
            player_id,
            season,
            position,
            AVG(analytical_grade) AS avg_grade
        FROM `{BIGQUERY_PROJECT_ID}.fantasy_football_brain.analytics_player_weekly_truth`
        GROUP BY player_id, season, position
    ),
    season_ranks AS (
        SELECT
            player_id,
            season,
            position,
            avg_grade,
            RANK() OVER(PARTITION BY season, position ORDER BY COALESCE(avg_grade, 0.0) DESC) AS pos_rank
        FROM season_averages
    )
    SELECT
        season,
        pos_rank,
        avg_grade
    FROM season_ranks
    WHERE player_id = @player_id
    ORDER BY season ASC
    """
    client = bigquery.Client(project=BIGQUERY_PROJECT_ID)
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("player_id", "STRING", player_id)
        ]
    )
    df = client.query(sql_query, job_config=job_config).result().to_dataframe()
    return df

def calculate_player_comps(player_row, df, limit=5):
    import pandas as pd
    import numpy as np

    pos = player_row["position"]
    pos_df = df[df["position"] == pos].copy()
    
    # Exclude target player
    pos_df = pos_df[pos_df["player_id"] != player_row["player_id"]]
    if pos_df.empty:
        return []

    # Features to use for similarity
    features = ["avg_ppr", "avg_opportunity", "avg_efficiency", "avg_grade", "avg_snap_share"]
    
    # Fill NaN values with 0.0 before calculation
    pos_df[features] = pos_df[features].fillna(0.0)
    player_features = player_row[features].fillna(0.0)
    
    # Normalization (Min-Max)
    # Stack the player row on top of pos_df to normalize together
    temp_df = pd.concat([pos_df, pd.DataFrame([player_features])], ignore_index=True)
    target_idx = len(pos_df)
    
    for feat in features:
        min_val = temp_df[feat].min()
        max_val = temp_df[feat].max()
        if pd.isna(min_val) or pd.isna(max_val) or max_val == min_val:
            temp_df[feat + "_norm"] = 0.0
        else:
            temp_df[feat + "_norm"] = (temp_df[feat] - min_val) / (max_val - min_val)
            
    target_vector = temp_df.iloc[target_idx][[f + "_norm" for f in features]].values.astype(float)
    
    comps = []
    for idx in range(len(pos_df)):
        row = temp_df.iloc[idx]
        vec = row[[f + "_norm" for f in features]].values.astype(float)
        
        # Euclidean distance
        dist = np.sqrt(np.sum((target_vector - vec) ** 2))
        max_dist = np.sqrt(len(features))
        
        # Match % calculation
        match_pct = max(0.0, 100.0 * (1.0 - (dist / max_dist)))
        
        # Check if match_pct is NaN
        if pd.isna(match_pct):
            match_pct = 0.0
            
        comps.append({
            "player_id": row["player_id"],
            "player_display_name": row["player_display_name"],
            "position": row["position"],
            "team": row["team"],
            "avg_grade": row["avg_grade"],
            "avg_ppr": row["avg_ppr"],
            "headshot": row["headshot"],
            "match_pct": match_pct
        })
        
    # Sort by match_pct descending
    comps = sorted(comps, key=lambda x: x["match_pct"], reverse=True)
    return comps[:limit]

def render_player_profiles_tab():
    import pandas as pd
    import os

    st.markdown("### 👤 Player Profiles Directory")
    st.markdown(
        "Player profiles directory and scouting profiles powered by advanced metrics, contracts, and Pigskin AI analysis."
    )
    using_compat_profiles = use_compat_player_profiles()
    render_data_path_status("Player Profiles", using_compat_profiles)

    try:
        df = fetch_player_profiles_data()
    except Exception as e:
        st.info(f"Player profiles database is not fully materialized or query failed: {e}")
        return

    if df.empty:
        if using_compat_profiles:
            st.warning("Player Profiles compatibility data is unavailable or empty. Disable USE_COMPAT_PLAYER_PROFILES to use the legacy warehouse path.")
            return
        st.warning("No player profile metrics found in the data warehouse.")
        return
    if using_compat_profiles:
        render_compat_metadata(df, "Player Profiles")

    rankings_df = fetch_pigskin_rankings_data()
    if not rankings_df.empty:
        df = df.merge(rankings_df, on=["player_id", "position"], how="left")

    ranking_defaults = {
        "pigskin_rank": pd.NA,
        "pigskin_tier": pd.NA,
        "pigskin_ranking_score": pd.NA,
        "pigskin_confidence_score": pd.NA,
        "pigskin_verdict": pd.NA,
        "rank_rationale": pd.NA,
        "risk_flags": pd.NA,
        "what_would_change_mind": pd.NA,
        "ranking_version": pd.NA,
        "ranking_generated_at": pd.NA,
        "ranking_model_name": pd.NA,
        "ranking_prompt_version": pd.NA,
        "ranking_data_snapshot": pd.NA,
        "sleeper_team": pd.NA,
        "sleeper_status": pd.NA,
        "sleeper_depth_chart_position": pd.NA,
        "sleeper_depth_chart_order": pd.NA,
        "raw_ranking_score": pd.NA,
        "depth_chart_penalty": pd.NA,
        "avg_passing_epa": pd.NA,
        "season_passing_epa": pd.NA,
        "avg_rushing_epa": pd.NA,
        "season_rushing_epa": pd.NA,
        "avg_receiving_epa": pd.NA,
        "season_receiving_epa": pd.NA,
        "latest_season_wopr": pd.NA,
        "previous_season_wopr": pd.NA,
        "two_years_ago_wopr": pd.NA,
        "latest_season_target_share": pd.NA,
        "previous_season_target_share": pd.NA,
        "latest_season_carry_share": pd.NA,
        "previous_season_carry_share": pd.NA,
        "candidate_rank": pd.NA,
        "candidate_ranking_score": pd.NA,
        "rank_source": pd.NA,
        "adjudicated_at": pd.NA,
        "ranking_eligibility": pd.NA,
    }
    for col_name, default_value in ranking_defaults.items():
        if col_name not in df.columns:
            df[col_name] = default_value

    pigskin_rank_series = pd.to_numeric(df["pigskin_rank"], errors="coerce")
    legacy_rank_series = pd.to_numeric(df["pos_rank"], errors="coerce")
    pigskin_score_series = pd.to_numeric(df["pigskin_ranking_score"], errors="coerce")
    legacy_score_series = pd.to_numeric(df["avg_grade"], errors="coerce")
    df["display_rank"] = pigskin_rank_series.combine_first(legacy_rank_series)
    df["display_score"] = pigskin_score_series.combine_first(legacy_score_series)
    has_pigskin_rankings = df["pigskin_rank"].notna().any()

    if has_pigskin_rankings:
        version_values = df["ranking_version"].dropna().unique()
        version_label = str(version_values[0]) if len(version_values) else "unknown"
        st.caption(f"Canonical Pigskin rankings loaded from `analytics_pigskin_rankings`, version `{version_label}`.")
    else:
        st.warning(
            "Canonical Pigskin rankings are not materialized yet. Showing legacy analytical grade order until Data Ops publishes Pigskin rankings."
        )

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

        # Depth chart details
        depth_pos = player_row["depth_position"] if (player_row["depth_position"] and not pd.isna(player_row["depth_position"])) else "N/A"
        depth_rank_val = f"Rank {int(player_row['depth_rank'])}" if (player_row["depth_rank"] and not pd.isna(player_row["depth_rank"])) else "Rank N/A"
        depth_str_display = f"Depth Chart: {depth_pos} ({depth_rank_val})"

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
                    <span class="profile-meta-badge" style="background-color: #2563eb; color: white;">{depth_str_display}</span>
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

        # Opportunity Splits Section
        run_pct = (player_row["avg_player_run_opportunity_pct"] or 0.0) * 100
        pass_pct = (player_row["avg_player_pass_opportunity_pct"] or 0.0) * 100
        carry_share_pct = (player_row["avg_carry_share"] or 0.0) * 100
        target_share_pct = (player_row["avg_target_share"] or 0.0) * 100

        st.markdown("### 📈 Run/Pass Opportunity & Team Shares")
        col_splits, col_shares = st.columns(2)
        with col_splits:
            st.markdown(f"**Weekly Run/Pass Split** (Player's own touches/throws/targets)")
            st.markdown(f"- 🏃 Rushing / Carries: **{run_pct:.1f}%**")
            st.markdown(f"- 🏈 Targets / Throws: **{pass_pct:.1f}%**")
            st.progress(float(player_row["avg_player_run_opportunity_pct"]) if not pd.isna(player_row["avg_player_run_opportunity_pct"]) else 0.0)
        with col_shares:
            st.markdown(f"**Team Volume Shares** (When active on field)")
            if player_row["position"] == "RB":
                st.markdown(f"- 🏃 Team Carry Share: **{carry_share_pct:.1f}%**")
            st.markdown(f"- 🎯 Team Target Share: **{target_share_pct:.1f}%**")
            st.markdown(f"- ⏱ Snap Share: **{(player_row['avg_snap_share'] or 0.0)*100:.1f}%**")

        # College & Rookie Scouting Metrics Section
        has_college_stats = (player_row["college_team"] and not pd.isna(player_row["college_team"])) or (player_row["college_receptions"] and player_row["college_receptions"] > 0)
        has_rookie_metrics = (player_row["scouting_source"] and not pd.isna(player_row["scouting_source"]))

        if has_college_stats or has_rookie_metrics:
            st.markdown("### 🎓 Prospect & College Scouting Profile")
            col_col_stats, col_adv_metrics = st.columns(2)
            with col_col_stats:
                if has_college_stats:
                    st.markdown(f"**College Career Stats ({player_row['college_team']} - {player_row['college_conf']})**")
                    st.markdown(f"- 📅 Games: **{int(player_row['college_games'])}**" if not pd.isna(player_row["college_games"]) else "- Games: N/A")
                    if player_row["position"] == "QB":
                        st.markdown(f"- 🏈 Passing: **{player_row['college_passing_yards']:.0f} yds**, **{player_row['college_passing_tds']:.0f} TDs**" if not pd.isna(player_row["college_passing_yards"]) else "")
                    st.markdown(f"- 🏃 Rushing: **{player_row['college_rushing_yards']:.0f} yds**, **{player_row['college_rushing_tds']:.0f} TDs**" if not pd.isna(player_row["college_rushing_yards"]) else "")
                    st.markdown(f"- 👐 Receptions: **{player_row['college_receptions']:.0f} rec**, **{player_row['college_receiving_yards']:.0f} yds**, **{player_row['college_receiving_tds']:.0f} TDs**" if not pd.isna(player_row["college_receptions"]) else "")
                else:
                    st.write("College stats not available.")
            with col_adv_metrics:
                if has_rookie_metrics:
                    st.markdown(f"**Advanced Scouting Metrics ({player_row['scouting_source']})**")
                    if player_row["position"] in ("WR", "TE"):
                        st.markdown(f"- Yards Per Route Run (YPRR): **{player_row['yards_per_route_run']:.2f}**" if not pd.isna(player_row["yards_per_route_run"]) else "")
                        st.markdown(f"- College Target Share: **{player_row['college_target_share']:.1f}%**" if not pd.isna(player_row["college_target_share"]) else "")
                        st.markdown(f"- Catch Radius Grade: **{player_row['catch_radius_grade']:.1f}/100**" if not pd.isna(player_row["catch_radius_grade"]) else "")
                        st.markdown(f"- Success vs. Man Coverage: **{player_row['success_rate_vs_man']:.1f}%**" if not pd.isna(player_row["success_rate_vs_man"]) else "")
                        st.markdown(f"- Success vs. Zone Coverage: **{player_row['success_rate_vs_zone']:.1f}%**" if not pd.isna(player_row["success_rate_vs_zone"]) else "")
                        st.markdown(f"- Success vs. Press Coverage: **{player_row['success_rate_vs_press']:.1f}%**" if not pd.isna(player_row["success_rate_vs_press"]) else "")
                    elif player_row["position"] == "RB":
                        st.markdown(f"- Yards After Contact/Att: **{player_row['yards_after_contact_per_attempt']:.2f}**" if not pd.isna(player_row["yards_after_contact_per_attempt"]) else "")
                    else:
                        st.markdown(f"- Yards Per Route Run: **{player_row['yards_per_route_run']:.2f}**" if not pd.isna(player_row["yards_per_route_run"]) else "")
                else:
                    st.write("Advanced scouting metrics not available.")

        # Scouting Ratings Grid
        st.markdown("### 📊 Player Grades & Ratings")
        col_grade, col_traits = st.columns([1, 2])

        with col_grade:
            has_player_pigskin_rank = not pd.isna(player_row.get("pigskin_rank"))
            grade_val = player_row["display_score"] if not pd.isna(player_row["display_score"]) else 0.0
            rank_val = player_row["display_rank"] if not pd.isna(player_row["display_rank"]) else player_row["pos_rank"]
            rank_label = f"#{int(float(rank_val))} {player_row['position']}" if not pd.isna(rank_val) else "Unranked"
            grade_title = "Pigskin Score" if has_player_pigskin_rank else "Overall Grade"
            st.markdown(f"""
            <div class="grade-badge-container">
                <div class="grade-badge-title">{grade_title}</div>
                <div class="grade-badge-circle">{grade_val:.1f}</div>
                <div style="margin-top: 10px; font-weight: 700; color: #1e3a8a;">Rank: {rank_label}</div>
            </div>
            """, unsafe_allow_html=True)

        with col_traits:
            opp_score = player_row["avg_opportunity"] if not pd.isna(player_row["avg_opportunity"]) else 0.0
            eff_score = player_row["avg_efficiency"] if not pd.isna(player_row["avg_efficiency"]) else 0.0
            fragility = player_row["avg_role_fragility"] if not pd.isna(player_row["avg_role_fragility"]) else 0.0
            stability_score = max(0.0, min(100.0, 100.0 - fragility))

            traits = [
                ("Opportunity Rating (Volume)", opp_score, "Workload volume relative to position group (derived from targets, carries, snap shares, and team opportunity shares)."),
                ("Efficiency Rating (EPA/Pts)", eff_score, "Productivity and value added per touch, based on Expected Points Added (EPA) and points scored relative to position group norms."),
                ("Role Stability Rating (Usage)", stability_score, "Reliability and consistency of weekly role usage (higher = lower risk of sudden usage drops)."),
            ]

            st.markdown('<div class="scouting-traits-container">', unsafe_allow_html=True)
            for trait_name, trait_val, trait_desc in traits:
                st.markdown(f"""
                <div class="scouting-trait-row" style="margin-bottom: 12px;">
                    <div class="scouting-trait-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 3px;">
                        <span style="font-weight: 700; font-size: 13px; color: inherit;">{trait_name}</span>
                        <span style="font-weight: 800; font-size: 14px; color: #2563eb;">{trait_val:.1f}/100</span>
                    </div>
                    <div class="trait-progress-bar" style="background: rgba(148, 163, 184, 0.2); border-radius: 999px; height: 8px; overflow: hidden; margin-bottom: 3px;">
                        <div class="trait-progress-fill" style="background: #2563eb; height: 100%; border-radius: 999px; width: {trait_val}%;"></div>
                    </div>
                    <div style="font-size: 11px; opacity: 0.75; color: inherit; line-height: 1.25; font-style: italic;">{trait_desc}</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        if not pd.isna(player_row.get("pigskin_rank")):
            st.markdown("### 🏆 Canonical Pigskin Ranking")
            confidence_val = player_row.get("pigskin_confidence_score")
            confidence_display = float(confidence_val) if not pd.isna(confidence_val) else 0.0
            depth_order = player_row.get("sleeper_depth_chart_order")
            depth_display = f"#{int(float(depth_order))}" if not pd.isna(depth_order) else "unknown"
            sleeper_team = player_row.get("sleeper_team") if not pd.isna(player_row.get("sleeper_team")) else "unknown"
            sleeper_status = player_row.get("sleeper_status") if not pd.isna(player_row.get("sleeper_status")) else "unknown"
            penalty_val = player_row.get("depth_chart_penalty")
            penalty_display = float(penalty_val) if not pd.isna(penalty_val) else 0.0
            rank_source = player_row.get("rank_source") if not pd.isna(player_row.get("rank_source")) else "candidate fallback"
            st.markdown(
                f"**{rank_label}** · **{player_row.get('pigskin_tier', 'tier unknown')}** · "
                f"confidence **{confidence_display:.1f}/100**"
            )
            st.caption(
                f"Sleeper eligibility: {sleeper_team}, {sleeper_status}, "
                f"depth {depth_display}, penalty {penalty_display:.1f}, source {rank_source}"
            )
            if not pd.isna(player_row.get("pigskin_verdict")):
                st.info(str(player_row["pigskin_verdict"]))
            if not pd.isna(player_row.get("rank_rationale")):
                st.markdown(f"**Why Pigskin owns the rank:** {player_row['rank_rationale']}")
            if not pd.isna(player_row.get("risk_flags")):
                st.markdown(f"**Risk flags:** {player_row['risk_flags']}")
            if not pd.isna(player_row.get("what_would_change_mind")):
                st.markdown(f"**What would change the rank:** {player_row['what_would_change_mind']}")

        # Pigskin's AI Scouting Report
        st.markdown("### 🧠 Pigskin's Scouting Report")
        active_gemini_key = os.environ.get("GEMINI_API_KEY", "")
        report_cache_key = f"scouting_report_{player_id}"

        if report_cache_key not in st.session_state:
            if not active_gemini_key:
                st.session_state[report_cache_key] = f"""
                No Gemini API key detected in the sidebar. Standard statistics indicate that {player_row['player_display_name']} averages {player_row['avg_ppr']:.1f} PPR points per game on a snap share of {player_row['avg_snap_share']*100:.1f}%.
                His average analytical grade is {player_row['avg_grade']:.1f} and he carries an opportunity score of {player_row['avg_opportunity']:.1f}.
                - **Depth Chart**: {depth_pos} (Rank {int(player_row['depth_rank']) if not pd.isna(player_row['depth_rank']) else 'N/A'})
                - **Opportunity Splits**: {run_pct:.1f}% Run / {pass_pct:.1f}% Pass/Targets
                """
            else:
                try:
                    model = create_gemini_model(active_gemini_key)

                    prompt = f"""
                    You are Pigskin, the snarky analytical co-host of AI vs Vibes.
                    Write a 1-paragraph scouting report for the NFL player {player_row['player_display_name']}.

                    Player Metrics:
                    - Position: {player_row['position']}
                    - Canonical Pigskin ranking: {rank_label}
                    - Canonical Pigskin tier: {player_row.get('pigskin_tier', 'not materialized')}
                    - Canonical Pigskin verdict: {player_row.get('pigskin_verdict', 'not materialized')}
                    - Canonical rank rationale: {player_row.get('rank_rationale', 'not materialized')}
                    - College: {player_row['college_name']}
                    - Draft: Round {player_row['draft_round']}, Pick {player_row['draft_pick']} (Year {player_row['draft_year']})
                    - Experience: {player_row['years_of_experience']} years
                    - Average PPR PPG: {player_row['avg_ppr']:.2f}
                    - Analytical Grade (1-100): {player_row['avg_grade']:.2f}
                    - Opportunity Rating (1-100): {player_row['avg_opportunity']:.2f}
                    - Efficiency Rating (1-100): {player_row['avg_efficiency']:.2f}
                    - Role Stability Rating (1-100): {100 - player_row['avg_role_fragility']:.2f}
                    - Contract APY: {format_currency(player_row['contract_apy'])}
                    - Team Website-scraped Depth Position: {depth_pos} (Rank {int(player_row['depth_rank']) if not pd.isna(player_row['depth_rank']) else 'N/A'})
                    - Run/Pass Split: {run_pct:.1f}% Runs / {pass_pct:.1f}% Throws/Targets
                    - Carry Share: {carry_share_pct:.1f}%
                    - Target Share: {target_share_pct:.1f}%
                    - College Stats (if available): {player_row['college_team']} ({player_row['college_conf']}), Games: {player_row['college_games']}, Passing Yds: {player_row['college_passing_yards']}, Rushing Yds: {player_row['college_rushing_yards']}, Receptions: {player_row['college_receptions']}, Receiving Yds: {player_row['college_receiving_yards']}
                    - Advanced Prospect metrics (if available): YPRR = {player_row['yards_per_route_run']}, Yards after contact/att = {player_row['yards_after_contact_per_attempt']}, Success rate vs Man = {player_row['success_rate_vs_man']}, Success rate vs press = {player_row['success_rate_vs_press']}, Catch radius = {player_row['catch_radius_grade']}

                    Scouting report requirements:
                    1. Deliver the report in the Pigskin voice contract (arrogant, analytical, highly critical of vibes-based scouting, uses slang like "cooked", "vibes tax").
                    2. Do not contradict the canonical Pigskin ranking if it is materialized. Defend it, criticize its risk, or explain what would change it.
                    3. Write a brief overview (3-4 sentences), making sure to touch on their depth chart status, run/pass opportunity splits, and college prospect profile or rookie metrics where relevant.
                    4. Output a section for "KEY STRENGTHS" and "KEY WEAKNESSES", listing exactly 2 bullet points for each based on their actual numbers. Do not include markdown headers inside the bulleted text, just write it as standard bold bullets.
                    """
                    res = model.generate_content(prompt)
                    st.session_state[report_cache_key] = res.text
                except Exception as ex:
                    st.session_state[report_cache_key] = f"Error generating report: {ex}"

        st.write(st.session_state[report_cache_key])

        # Weekly Stats & Trends
        history_df = fetch_player_weekly_history(player_id)
        
        # 1. Performance Trends: Career Position Rank by Season
        rank_df = fetch_player_season_rankings(player_id)
        if not rank_df.empty:
            st.markdown("### 📈 Career Position Rank Trends")
            
            # Format DataFrame for Altair
            chart_df = rank_df.copy()
            chart_df["Season"] = chart_df["season"].astype(str)
            chart_df["Rank"] = chart_df["pos_rank"].astype(int)
            chart_df["Grade"] = chart_df["avg_grade"].round(1)
            
            import altair as alt
            
            chart = alt.Chart(chart_df).mark_line(point=True, strokeWidth=3, color="#2563eb").encode(
                x=alt.X("Season:O", title="NFL Season"),
                y=alt.Y("Rank:Q", title="Position Rank (Rank #1 is top)", scale=alt.Scale(reverse=True, zero=False)),
                tooltip=["Season", "Rank", "Grade"]
            ).properties(
                height=220,
            )
            
            st.altair_chart(chart, use_container_width=True)

        # 2. Season History
        if not history_df.empty:
            st.markdown("### 📅 Career Season History")
            season_summary_data = []
            for season, group in history_df.groupby("season"):
                games_played = len(group)
                total_ppr = group["fantasy_points_ppr"].sum()
                avg_ppr = group["fantasy_points_ppr"].mean()
                avg_snap = group["snap_share"].mean()
                total_targets = group["targets"].sum()
                total_receptions = group["receptions"].sum()
                total_receiving_yds = group["receiving_yards"].sum()
                total_receiving_tds = group["receiving_tds"].sum()
                total_carries = group["carries"].sum()
                total_rushing_yds = group["rushing_yards"].sum()
                total_rushing_tds = group["rushing_tds"].sum()
                total_passing_yds = group["passing_yards"].sum()
                total_passing_tds = group["passing_tds"].sum()
                total_epa = group["total_epa"].sum()
                
                season_summary_data.append({
                    "Season": int(season),
                    "Games": int(games_played),
                    "Total PPR": round(total_ppr, 1),
                    "PPR PPG": round(avg_ppr, 2),
                    "Avg Snap Share": f"{avg_snap * 100:.1f}%" if not pd.isna(avg_snap) else "0.0%",
                    "Targets": int(total_targets),
                    "Rec": int(total_receptions),
                    "Rec Yards": int(total_receiving_yds),
                    "Rec TDs": int(total_receiving_tds),
                    "Carries": int(total_carries),
                    "Rush Yards": int(total_rushing_yds),
                    "Rush TDs": int(total_rushing_tds),
                    "Pass Yards": int(total_passing_yds),
                    "Pass TDs": int(total_passing_tds),
                    "Total EPA": round(total_epa, 1),
                })
                
            season_summary_df = pd.DataFrame(season_summary_data).sort_values(by="Season", ascending=False)
            st.dataframe(season_summary_df, use_container_width=True, hide_index=True)

            # 3. Game Log dropdown
            st.markdown("#### 📋 Seasonal Game Logs")
            available_seasons = sorted(history_df["season"].unique(), reverse=True)
            if available_seasons:
                selected_season = st.selectbox(
                    "Select Season to view weekly game logs:",
                    options=available_seasons,
                    key=f"gamelog_season_select_{player_id}"
                )
                
                season_game_log = history_df[history_df["season"] == selected_season].sort_values(by="week").copy()
                st.dataframe(
                    season_game_log[["week", "opponent_team", "fantasy_points_ppr", "snap_share", "targets", "receptions", "receiving_yards", "receiving_tds", "carries", "rushing_yards", "rushing_tds", "total_epa"]].rename(
                        columns={
                            "week": "Week",
                            "opponent_team": "Opponent",
                            "fantasy_points_ppr": "PPR Points",
                            "snap_share": "Snap Share",
                            "targets": "Targets",
                            "receptions": "Rec",
                            "receiving_yards": "Rec Yards",
                            "receiving_tds": "Rec TDs",
                            "carries": "Carries",
                            "rushing_yards": "Rush Yards",
                            "rushing_tds": "Rush TDs",
                            "total_epa": "EPA",
                        }
                    ),
                    use_container_width=True,
                    hide_index=True
                )

        # --- SIMILAR PLAYER COMPS ---
        st.markdown("### 👥 Similar Player Comparisons (Comps)")
        comps = calculate_player_comps(player_row, df)
        if comps:
            cols_comps = st.columns(len(comps))
            for idx, comp in enumerate(comps):
                with cols_comps[idx]:
                    comp_headshot = comp["headshot"] if (comp["headshot"] and not pd.isna(comp["headshot"])) else "https://www.nfl.com/static/content/public/static/wildcat/assets/images/application-logos/share/nfl-share.png"
                    st.markdown(f"""
                    <div style="border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; text-align: center; background-color: #f8fafc; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-bottom: 10px;">
                        <img src="{comp_headshot}" style="width: 65px; height: 65px; border-radius: 50%; object-fit: cover; border: 2px solid #2563eb; margin-bottom: 8px;">
                        <div style="font-weight: 700; font-size: 14px; color: #1e293b; height: 38px; overflow: hidden; display: flex; align-items: center; justify-content: center;">{comp['player_display_name']}</div>
                        <div style="font-size: 12px; color: #64748b; margin-bottom: 4px;">{comp['position']} - {comp['team']}</div>
                        <div style="font-size: 13px; font-weight: 600; color: #2563eb; margin-bottom: 4px;">Match: {comp['match_pct']:.1f}%</div>
                        <div style="font-size: 11px; color: #0284c7;">Grade: {comp['avg_grade']:.1f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("🔍 View Profile", key=f"comp_jump_{comp['player_id']}", use_container_width=True):
                        st.session_state.selected_player_id = comp["player_id"]
                        st.session_state.global_profile_search = comp["player_display_name"]
                        st.rerun()
        else:
            st.info("No similar player comparisons found.")

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
        if has_pigskin_rankings:
            df_pos = df_pos[df_pos["pigskin_rank"].notna()]

        df_pos["display_rank_sort"] = pd.to_numeric(df_pos["display_rank"], errors="coerce").fillna(9999)
        df_pos["display_score_sort"] = pd.to_numeric(df_pos["display_score"], errors="coerce").fillna(0)
        if selected_pos == "All":
            df_pos = df_pos.sort_values(by=["position", "display_rank_sort", "display_score_sort"], ascending=[True, True, False])
        else:
            df_pos = df_pos.sort_values(by=["display_rank_sort", "display_score_sort"], ascending=[True, False])

        if df_pos.empty:
            st.info("No players found matching the selected position.")
            return

        # Format columns for rankings display
        display_ranks = df_pos.copy()
        display_ranks["display_rank"] = display_ranks["display_rank"].apply(lambda x: f"{int(float(x))}" if not pd.isna(x) else "N/A")
        display_ranks["display_score"] = display_ranks["display_score"].apply(lambda x: f"{x:.1f}" if not pd.isna(x) else "N/A")
        display_ranks["pigskin_tier"] = display_ranks["pigskin_tier"].fillna("legacy grade")
        display_ranks["pigskin_verdict"] = display_ranks["pigskin_verdict"].fillna("Pigskin ranking not materialized yet.")
        display_ranks["avg_ppr"] = display_ranks["avg_ppr"].apply(lambda x: f"{x:.1f}" if not pd.isna(x) else "N/A")
        display_ranks["contract_apy"] = display_ranks["contract_apy"].apply(format_currency)
        display_ranks["height"] = display_ranks["height"].apply(format_height)
        display_ranks["weight"] = display_ranks["weight"].apply(lambda x: f"{int(float(x))} lbs" if (x and not pd.isna(x)) else "N/A")

        display_ranks = display_ranks.rename(columns={
            "display_rank": "Rank",
            "player_display_name": "Player",
            "team": "Team",
            "college_name": "College",
            "display_score": "Pigskin Score",
            "pigskin_tier": "Tier",
            "pigskin_verdict": "Pigskin Verdict",
            "avg_ppr": "Avg PPR",
            "contract_apy": "Salary APY",
            "height": "Height",
            "weight": "Weight"
        })

        st.dataframe(
            display_ranks[["Rank", "Player", "Team", "College", "Pigskin Score", "Tier", "Pigskin Verdict", "Avg PPR", "Salary APY", "Height", "Weight"]],
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

def render_versus_finder_tab():
    import pandas as pd
    import numpy as np
    import os

    st.markdown("### 🔍 Versus Finder")
    st.markdown(
        "Compare two players side-by-side on volume, efficiency, physical profile, opportunity share, and financial contracts, with a Pigskin AI synthesis."
    )
    using_compat_profiles = use_compat_player_profiles()
    render_data_path_status("Versus Finder profiles", using_compat_profiles)

    try:
        df = fetch_player_profiles_data()
    except Exception as e:
        st.info(f"Database query failed: {e}")
        return

    if df.empty:
        if using_compat_profiles:
            st.warning("Player Profiles compatibility data is unavailable or empty. Disable USE_COMPAT_PLAYER_PROFILES to use the legacy warehouse path.")
            return
        st.warning("No player profiles found in the data warehouse.")
        return
    if using_compat_profiles:
        render_compat_metadata(df, "Versus Finder profiles")

    # Select box options
    all_player_names = sorted([name for name in df["player_display_name"].unique() if isinstance(name, str) and name])
    
    col_a, col_b = st.columns(2)
    with col_a:
        player_a_name = st.selectbox(
            "Select Player A:",
            options=all_player_names,
            index=0 if all_player_names else None,
            key="vs_player_a"
        )
    with col_b:
        # Default player B to second player if available
        default_b_idx = 1 if len(all_player_names) > 1 else 0
        player_b_name = st.selectbox(
            "Select Player B:",
            options=all_player_names,
            index=default_b_idx,
            key="vs_player_b"
        )

    if not player_a_name or not player_b_name:
        st.info("Please select two players to compare.")
        return

    row_a = df[df["player_display_name"] == player_a_name].iloc[0]
    row_b = df[df["player_display_name"] == player_b_name].iloc[0]

    # Render head-to-head header
    headshot_a = row_a["headshot"] if (row_a["headshot"] and not pd.isna(row_a["headshot"])) else "https://www.nfl.com/static/content/public/static/wildcat/assets/images/application-logos/share/nfl-share.png"
    headshot_b = row_b["headshot"] if (row_b["headshot"] and not pd.isna(row_b["headshot"])) else "https://www.nfl.com/static/content/public/static/wildcat/assets/images/application-logos/share/nfl-share.png"

    # Helpers for formatting
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

    def format_age(birth_date_str):
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

    def format_pct(val):
        if val is None or pd.isna(val):
            return "0.0%"
        return f"{float(val) * 100:.1f}%"

    def format_val(val):
        if val is None or pd.isna(val):
            return "0.0"
        return f"{float(val):.1f}"

    def format_exp(val):
        if val is None or pd.isna(val):
            return "Rookie"
        try:
            exp = int(float(val))
            return "Rookie" if exp == 0 else f"{exp} yrs"
        except Exception:
            return str(val)

    st.markdown(f"""
    <div style="display: flex; justify-content: space-around; align-items: center; border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 12px; padding: 20px; background-color: #f8fafc; margin-bottom: 25px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);">
        <div style="text-align: center; width: 40%;">
            <img src="{headshot_a}" style="width: 100px; height: 100px; border-radius: 50%; object-fit: cover; border: 4px solid #2563eb; margin-bottom: 12px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
            <div style="font-size: 20px; font-weight: 800; color: #1e293b;">{row_a['player_display_name']}</div>
            <div style="font-size: 14px; color: #64748b; font-weight: 600; margin-top: 4px;">{row_a['position']} - {row_a['team']}</div>
            <div style="display: inline-block; background-color: #2563eb; color: white; padding: 4px 12px; border-radius: 999px; font-size: 14px; font-weight: 700; margin-top: 10px; box-shadow: 0 2px 4px rgba(37,99,235,0.2);">Rating: {row_a['avg_grade']:.1f}</div>
        </div>
        <div style="font-size: 28px; font-weight: 900; color: #94a3b8; font-style: italic;">VS</div>
        <div style="text-align: center; width: 40%;">
            <img src="{headshot_b}" style="width: 100px; height: 100px; border-radius: 50%; object-fit: cover; border: 4px solid #f59e0b; margin-bottom: 12px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
            <div style="font-size: 20px; font-weight: 800; color: #1e293b;">{row_b['player_display_name']}</div>
            <div style="font-size: 14px; color: #64748b; font-weight: 600; margin-top: 4px;">{row_b['position']} - {row_b['team']}</div>
            <div style="display: inline-block; background-color: #f59e0b; color: white; padding: 4px 12px; border-radius: 999px; font-size: 14px; font-weight: 700; margin-top: 10px; box-shadow: 0 2px 4px rgba(245,158,11,0.2);">Rating: {row_b['avg_grade']:.1f}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Comparison rows
    rows_html = []
    
    def make_comparison_row(metric_name, val_a, val_b, format_fn, higher_is_better=True, highlight=True):
        style_a = "padding: 10px 15px; text-align: center; border-bottom: 1px solid #e2e8f0; color: #475569;"
        style_b = "padding: 10px 15px; text-align: center; border-bottom: 1px solid #e2e8f0; color: #475569;"
        
        try:
            num_a = float(val_a) if val_a is not None and not pd.isna(val_a) else None
            num_b = float(val_b) if val_b is not None and not pd.isna(val_b) else None
        except Exception:
            num_a = None
            num_b = None
            
        highlight_style_a = "background-color: #eff6ff; color: #1e40af; font-weight: 700; border-bottom: 1px solid #e2e8f0; border-left: 2px solid #2563eb;"
        highlight_style_b = "background-color: #fffbeb; color: #854d0e; font-weight: 700; border-bottom: 1px solid #e2e8f0; border-right: 2px solid #f59e0b;"
        
        if highlight and num_a is not None and num_b is not None:
            if num_a != num_b:
                if (num_a > num_b and higher_is_better) or (num_a < num_b and not higher_is_better):
                    style_a = f"padding: 10px 15px; text-align: center; {highlight_style_a}"
                else:
                    style_b = f"padding: 10px 15px; text-align: center; {highlight_style_b}"
                    
        str_a = format_fn(val_a)
        str_b = format_fn(val_b)
        
        return f"""
        <tr>
            <td style="padding: 10px 15px; font-weight: 600; color: #334155; border-bottom: 1px solid #e2e8f0; background-color: #fafafa; width: 40%;">{metric_name}</td>
            <td style="{style_a}">{str_a}</td>
            <td style="{style_b}">{str_b}</td>
        </tr>
        """

    # Build Comparison HTML Table
    rows_html.append(make_comparison_row("Age", row_a["birth_date"], row_b["birth_date"], format_age, higher_is_better=False, highlight=True))
    rows_html.append(make_comparison_row("Height", row_a["height"], row_b["height"], format_height, higher_is_better=True, highlight=False))
    rows_html.append(make_comparison_row("Weight", row_a["weight"], row_b["weight"], lambda x: f"{int(float(x))} lbs" if (x and not pd.isna(x)) else "N/A", higher_is_better=True, highlight=False))
    rows_html.append(make_comparison_row("Experience", row_a["years_of_experience"], row_b["years_of_experience"], format_exp, higher_is_better=True, highlight=False))
    rows_html.append(make_comparison_row("Contract APY", row_a["contract_apy"], row_b["contract_apy"], format_currency, higher_is_better=True, highlight=True))
    rows_html.append(make_comparison_row("Total Contract Value", row_a["contract_value"], row_b["contract_value"], format_currency, higher_is_better=True, highlight=True))
    rows_html.append(make_comparison_row("Overall Rating / Grade", row_a["avg_grade"], row_b["avg_grade"], format_val, higher_is_better=True, highlight=True))
    rows_html.append(make_comparison_row("Avg PPR PPG", row_a["avg_ppr"], row_b["avg_ppr"], format_val, higher_is_better=True, highlight=True))
    rows_html.append(make_comparison_row("Average Snap Share", row_a["avg_snap_share"], row_b["avg_snap_share"], format_pct, higher_is_better=True, highlight=True))
    rows_html.append(make_comparison_row("Team Target Share", row_a["avg_target_share"], row_b["avg_target_share"], format_pct, higher_is_better=True, highlight=True))
    
    if row_a["position"] == "RB" or row_b["position"] == "RB":
        rows_html.append(make_comparison_row("Team Carry Share", row_a["avg_carry_share"], row_b["avg_carry_share"], format_pct, higher_is_better=True, highlight=True))
        
    rows_html.append(make_comparison_row("Opportunity split (Runs)", row_a["avg_player_run_opportunity_pct"], row_b["avg_player_run_opportunity_pct"], format_pct, higher_is_better=True, highlight=False))
    rows_html.append(make_comparison_row("Opportunity split (Passes)", row_a["avg_player_pass_opportunity_pct"], row_b["avg_player_pass_opportunity_pct"], format_pct, higher_is_better=True, highlight=False))
    rows_html.append(make_comparison_row("Opportunity Rating", row_a["avg_opportunity"], row_b["avg_opportunity"], format_val, higher_is_better=True, highlight=True))
    rows_html.append(make_comparison_row("Efficiency Rating", row_a["avg_efficiency"], row_b["avg_efficiency"], format_val, higher_is_better=True, highlight=True))
    rows_html.append(make_comparison_row("Role Fragility Rating", row_a["avg_role_fragility"], row_b["avg_role_fragility"], format_val, higher_is_better=False, highlight=True))

    st.markdown(f"""
    <table style="width: 100%; border-collapse: collapse; font-family: sans-serif; border: 1px solid #cbd5e1; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
        <thead>
            <tr style="background-color: #f1f5f9; border-bottom: 2px solid #cbd5e1;">
                <th style="padding: 12px 15px; text-align: left; font-weight: 700; color: #475569; width: 40%;">Stat Feature</th>
                <th style="padding: 12px 15px; text-align: center; font-weight: 700; color: #2563eb; width: 30%;">{row_a['player_display_name']}</th>
                <th style="padding: 12px 15px; text-align: center; font-weight: 700; color: #f59e0b; width: 30%;">{row_b['player_display_name']}</th>
            </tr>
        </thead>
        <tbody>
            {"".join(rows_html)}
        </tbody>
    </table>
    """, unsafe_allow_html=True)

    st.write("")

    # AI VS CO-HOST SYNTESIS
    st.markdown("### 🧠 Pigskin's Head-to-Head Breakdown")
    active_gemini_key = os.environ.get("GEMINI_API_KEY", "")
    vs_cache_key = f"versus_report_{row_a['player_id']}_{row_b['player_id']}"

    if vs_cache_key not in st.session_state:
        if not active_gemini_key:
            st.session_state[vs_cache_key] = f"""
            **Pigskin analytical comparison**:
            - **{row_a['player_display_name']}** vs **{row_b['player_display_name']}**.
            - Overall grades: {row_a['avg_grade']:.1f} vs {row_b['avg_grade']:.1f}.
            - Fantasy PPR PPG: {row_a['avg_ppr']:.1f} vs {row_b['avg_ppr']:.1f}.
            - Please configure a Gemini API key in the sidebar to get a full Pigskin AI roast and analytical breakdown of this comparison.
            """
        else:
            try:
                model = create_gemini_model(active_gemini_key)
                prompt = f"""
                You are Pigskin, the snarky analytical co-host of AI vs Vibes.
                Evaluate a side-by-side comparison between NFL players {row_a['player_display_name']} and {row_b['player_display_name']}.
                
                Player A details ({row_a['player_display_name']}):
                - Position: {row_a['position']} | Team: {row_a['team']}
                - Overall Rating: {row_a['avg_grade']:.1f}
                - Avg PPR PPG: {row_a['avg_ppr']:.1f}
                - Snap Share: {format_pct(row_a['avg_snap_share'])}
                - Target Share: {format_pct(row_a['avg_target_share'])}
                - Carry Share: {format_pct(row_a['avg_carry_share'])}
                - Opportunity Score: {row_a['avg_opportunity']:.1f}
                - Efficiency Score: {row_a['avg_efficiency']:.1f}
                - Role Fragility: {row_a['avg_role_fragility']:.1f}
                - Run/Pass Split: {format_pct(row_a['avg_player_run_opportunity_pct'])} Run / {format_pct(row_a['avg_player_pass_opportunity_pct'])} Pass
                - Salary APY: {format_currency(row_a['contract_apy'])}
                
                Player B details ({row_b['player_display_name']}):
                - Position: {row_b['position']} | Team: {row_b['team']}
                - Overall Rating: {row_b['avg_grade']:.1f}
                - Avg PPR PPG: {row_b['avg_ppr']:.1f}
                - Snap Share: {format_pct(row_b['avg_snap_share'])}
                - Target Share: {format_pct(row_b['avg_target_share'])}
                - Carry Share: {format_pct(row_b['avg_carry_share'])}
                - Opportunity Score: {row_b['avg_opportunity']:.1f}
                - Efficiency Score: {row_b['avg_efficiency']:.1f}
                - Role Fragility: {row_b['avg_role_fragility']:.1f}
                - Run/Pass Split: {format_pct(row_b['avg_player_run_opportunity_pct'])} Run / {format_pct(row_b['avg_player_pass_opportunity_pct'])} Pass
                - Salary APY: {format_currency(row_b['contract_apy'])}

                Scouting breakdown requirements:
                1. Deliver the comparison in the Pigskin voice contract (arrogant, analytical, highly critical of vibes-based drafting/trading, uses words like "cooked", "vibes tax", "opportunity merchant", "efficiency god").
                2. Write a 2-paragraph analysis. In the first paragraph, compare their workloads and opportunity metrics (opportunity scores, snap/target shares). In the second paragraph, compare their efficiencies and contracts, and declare a definitive, analytical verdict on who is the superior fantasy football asset to roster.
                """
                res = model.generate_content(prompt)
                st.session_state[vs_cache_key] = res.text
            except Exception as ex:
                st.session_state[vs_cache_key] = f"Error generating comparison breakdown: {ex}"

    st.write(st.session_state[vs_cache_key])

@st.cache_data(ttl=3600, show_spinner=False)
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

        active_project_id = BIGQUERY_PROJECT_ID
        pigskin_context_tools = get_pigskin_context_tool_declarations()
        pigskin_context_tool_names = {tool["name"] for tool in pigskin_context_tools}
        context_tool_protocol = """

    ### Context Tool Protocol ###
    You must use only the provided parameterized context tools for warehouse-backed evidence.
    You cannot write or execute SQL, request table access, invent table names, or describe unavailable warehouse tables as usable data.
    Use curated packets, marts, rankings, history, Fraud Watch candidates, trade history, comparison packets, and context leads through tools.
    If a tool fails, stop and say the curated context tool failed instead of giving a fake data-backed take.
    If curated data is unavailable or a tool returns no rows, say the curated data is unavailable and name the missing packet, identity match, ranking, or materialization needed.
    Do not invent stats, injury claims, rankings, transactions, source freshness, or evidence.
    Treat stored external context and search results as leads, not verified truth, unless the linked source clearly supports the claim.
    Prefer `model_run_id`, `ranking_version`, `source_freshness_json`, and `missing_data_flags` when a tool provides them.
    """
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
    Do not expose project internals to the user unless needed to explain a missing-data problem.
    {context_tool_protocol}
    {render_pigskin_chat_schema()}

    ### The Analytical Filter Protocol ###
    You are mandated to use curated context tools before making player, ranking, trade, projection, roster, or causal claims.
    For any question about rankings, positional rank, projections, draft price, Player Profiles, "why did you rank", "defend your ranking", or rank disagreements, call `get_rankings_slice`, `get_player_context_packet`, or `search_players` first.
    If active ranking context contains the player, acknowledge the rank directly. Never say "I did not rank him there" when the curated Pigskin ranking context says Pigskin did.
    For non-ranking player analysis, prefer `get_player_context_packet`, `compare_players`, and `get_trade_player_history`.
    For Fraud Watch analysis, use `get_fraud_watch_candidates` before making the take.
    For player-name ambiguity, use `search_players` rather than guessing.
    For viewer roster criticism, use available curated packets and clearly state when viewer-team context is not materialized yet.
    For offseason or current roster context, use current team and roster-status fields from the tools. Never describe a historical stat-week team as a player's current team.
    For receiver analysis, use available QB split or packet context before blaming the player. Separate player role from QB environment.
    For game-specific or matchup-specific projections, use available game-environment context. Indoor or closed-roof games should not get weather downgrades. Future weather outside a reliable forecast window is unknown.
    For any causal claim involving injuries, coaching, play-calling, offensive line, weather, benching, training camp reports, usage splits, or transaction intent, call `get_context_event_leads` first.
    If context events are missing or user asks for outside verification, treat stored external leads as leads and clearly label them until source support is verified.

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
            model = create_gemini_model(
                active_gemini_key,
                tools=pigskin_context_tools,
                system_instruction=system_prompt
            )
            st.session_state.chat_session = model.start_chat()

        # Display chat history
        for msg in st.session_state.messages:
            if msg["role"] == "tool_status":
                with st.status(
                    msg["status_msg"],
                    state=msg.get("state", "complete"),
                    expanded=msg.get("expanded", False),
                ):
                    st.code(msg["code"], language=msg.get("language", "text"))
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
                    response = st.session_state.chat_session.send_message(prompt)

                    def get_fc(resp):
                        if getattr(resp, "function_calls", None):
                            return resp.function_calls[0]
                        try:
                            return resp.candidates[0].content.parts[0].function_call
                        except (AttributeError, IndexError):
                            return None

                    # Manual tool calling loop
                    fc = get_fc(response)
                    while fc:
                        if fc.name not in pigskin_context_tool_names:
                            break
                        tool_args = dict(fc.args or {})
                        tool_payload = {
                            "tool_name": fc.name,
                            "args": tool_args,
                        }
                        tool_message = {
                            "role": "tool_status",
                            "status_msg": f"🤖 Pigskin is loading curated context with `{fc.name}`...",
                            "code": json.dumps(tool_payload, indent=2, sort_keys=True, default=str),
                            "language": "json",
                            "state": "running",
                            "expanded": True,
                        }
                        st.session_state.messages.append(tool_message)
                        with st.status(tool_message["status_msg"], expanded=True) as status:
                            st.code(tool_message["code"], language="json")
                            try:
                                tool_result = execute_pigskin_context_tool(fc.name, tool_args)
                                result = tool_result.get("result", {})
                                row_count = result.get("row_count")
                                row_label = f" ({row_count} rows retrieved)" if row_count is not None else ""
                                status.update(label=f"🤖 Curated context loaded{row_label}", state="complete")
                            except Exception as e:
                                error_text = str(e)
                                status.update(label="❌ Context tool failed", state="error", expanded=True)
                                st.error(error_text)
                                tool_message.update({
                                    "status_msg": "❌ Context tool failed",
                                    "state": "error",
                                    "expanded": True,
                                    "error": error_text,
                                })
                                failure_text = (
                                    "I've got a problem: Pigskin's curated context tool failed. "
                                    "I am stopping here instead of giving you a fake data-backed take. "
                                    "The failed tool call and error are shown above."
                                )
                                st.error(failure_text)
                                st.session_state.messages.append({"role": "assistant", "content": failure_text})
                                return

                        tool_message.update({
                            "status_msg": "🤖 Curated context loaded",
                            "state": "complete",
                            "expanded": False,
                        })

                        from google.genai import types
                        tool_response = types.Part.from_function_response(
                            name=fc.name,
                            response=tool_result,
                        )
                        response = st.session_state.chat_session.send_message(tool_response)
                        fc = get_fc(response)

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
                    logging.getLogger("app.ai").exception("Error communicating with AI Co-Host")
                    failure_text = (
                        f"Pigskin connection failed before a usable answer. "
                        f"Model `{GEMINI_MODEL_NAME}` raised: {e}"
                    )
                    st.error(failure_text)
                    st.session_state.messages.append({"role": "assistant", "content": failure_text})

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
        if use_compat_trade_assets():
            try:
                compat_df = load_compat_trade_assets()
                if compat_df is not None and not compat_df.empty:
                    return compat_df
                st.warning("Trade Assets compatibility data is unavailable or empty. Falling back to the legacy warehouse path.")
            except Exception as compat_error:
                st.warning(f"Trade Assets compatibility path failed. Falling back to the legacy warehouse path. Error: {compat_error}")

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
    using_compat_trade_assets = "_data_path" in market_df.columns and (market_df["_data_path"] == "compat").any()
    render_data_path_status("Trade Assets", using_compat_trade_assets)
    if use_compat_trade_assets() and not using_compat_trade_assets:
        st.caption("Trade Assets compatibility flag is enabled, but this view is using the documented legacy fallback.")
    if using_compat_trade_assets and "source_freshness_json" in market_df.columns:
        render_compat_metadata(market_df, "Trade Assets")

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
    render_data_path_status("Trade Player History", use_compat_trade_player_history())

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
                        if use_compat_trade_player_history():
                            try:
                                return query_compat_trade_player_history(name)
                            except Exception as compat_error:
                                st.warning(f"Trade Player History compatibility path failed. Falling back to the legacy warehouse path. Error: {compat_error}")

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

                    model = create_gemini_model(active_gemini_key)

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
    st.sidebar.caption(f"Gemini model: `{GEMINI_MODEL_NAME}`")
    if st.sidebar.button("Test Gemini connection", key="test_gemini_connection"):
        try:
            model = create_gemini_model(gemini_api_key)
            response = model.generate_content("Reply with exactly: OK")
            response_text = getattr(response, "text", "").strip()
            if response_text == "OK":
                st.sidebar.success("Gemini connection OK.")
            else:
                st.sidebar.warning(f"Gemini replied, but unexpectedly: {response_text[:80]}")
        except Exception as ex:
            st.sidebar.error(f"Gemini connection failed: {ex}")
else:
    gemini_key_input = st.sidebar.text_input(
        "Gemini API Key",
        type="password",
        placeholder="e.g. AIzaSy...",
        help="Google AI Studio Gemini API Key for the data assistant."
    )
    if gemini_key_input:
        os.environ["GEMINI_API_KEY"] = gemini_key_input
        st.sidebar.caption(f"Gemini model: `{GEMINI_MODEL_NAME}`")

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
tab_pigskin, tab_show_prep, tab_player_profiles, tab_versus_finder, tab_viewer_lab, tab_trade_lab, tab_data_ops = st.tabs([
    "💬 Pigskin Studio",
    "🎙️ Show Prep",
    "👤 Player Profiles",
    "🔍 Versus Finder",
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
    if use_compat_viewer_team_context():
        return get_compat_sleeper_viewer_team_context(console_context)

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
    render_data_path_status("Viewer Team Context", use_compat_viewer_team_context())

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
            model = create_gemini_model(active_gemini_key)
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
        ("Cloud Jobs", "cloud-run-jobs"),
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
        "Cloud Run Jobs",
        "cloud-run-jobs",
        "Preview and optionally trigger Cloud Run Jobs while local subprocess controls remain available.",
    )
    with st.container(border=True):
        render_cloud_run_jobs_data_ops_panel()

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
        st.markdown("#### Sleeper Player Status, News, and Trending")
        st.caption("Refresh the global Sleeper player map plus real-time add/drop vectors used by rankings and context.")
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

        st.markdown("#### Publish Pigskin Rankings")
        st.caption("Generate LLM-authored Pigskin rankings from curated BigQuery evidence, then append a rankings-history snapshot.")
        render_last_success("pigskin_rankings")
        if st.button("🏆 Generate Pigskin Rankings", type="secondary"):
            cmd_args = ["-m", "src.generate_pigskin_rankings", "--refresh-sleeper"]

            exec_env = {}
            if gcp_key_path:
                exec_env["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.abspath(gcp_key_path)
            if gemini_api_key:
                exec_env["GEMINI_API_KEY"] = gemini_api_key

            if run_subprocess_live(cmd_args, custom_env=exec_env) == 0:
                mark_successful_run("pigskin_rankings")

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
        ("Sleeper Watch", "sleeper-watch"),
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
    render_section_header(
        "Sleeper Watch Search",
        "sleeper-watch",
        "Find and rank under-rostered sleepers and weekly streamers based on underlying workload, target/carry share, efficiency, and opponent defensive matchups.",
    )
    render_sleeper_watch_segment()

# --- PLAYER PROFILES ---
with tab_player_profiles:
    render_player_profiles_tab()

# --- VERSUS FINDER ---
with tab_versus_finder:
    render_versus_finder_tab()

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

st.markdown(
    """
    <footer style="margin-top: 3rem; padding: 1.25rem 0 0.5rem; border-top: 1px solid rgba(148, 163, 184, 0.22); text-align: center; font-size: 0.85rem; color: rgba(226, 232, 240, 0.72);">
        <a href="http://sputnikfx.com/" target="_blank" rel="noopener noreferrer" style="color: inherit; text-decoration: none;">
            &copy; 2026 Sputnik Digital
        </a>
    </footer>
    """,
    unsafe_allow_html=True,
)
