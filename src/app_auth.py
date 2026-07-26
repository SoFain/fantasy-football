"""Small Streamlit login gate backed by hashed environment credentials."""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
import re
import secrets
from collections.abc import Mapping, MutableMapping


APP_AUTH_ENABLED = "APP_AUTH_ENABLED"
APP_AUTH_USERS = "APP_AUTH_USERS"
AUTHENTICATED_KEY = "app_auth_authenticated"
AUTHENTICATED_USER_KEY = "app_auth_user"
AUTH_FAILED_KEY = "app_auth_failed"
HASH_SCHEME = "pbkdf2_sha256"
DEFAULT_ITERATIONS = 260_000
TRUE_VALUES = {"1", "true", "yes", "y", "on"}


def app_auth_enabled(environ: Mapping[str, str] | None = None) -> bool:
    env = environ if environ is not None else os.environ
    return str(env.get(APP_AUTH_ENABLED, "false")).strip().lower() in TRUE_VALUES


def hash_password(password: str, *, salt: bytes | None = None, iterations: int = DEFAULT_ITERATIONS) -> str:
    if iterations <= 0:
        raise ValueError("iterations must be positive")
    salt_bytes = salt if salt is not None else secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt_bytes, iterations)
    salt_b64 = base64.b64encode(salt_bytes).decode("ascii")
    digest_b64 = base64.b64encode(digest).decode("ascii")
    return f"{HASH_SCHEME}${iterations}${salt_b64}${digest_b64}"


def verify_password(password: str, encoded_hash: str) -> bool:
    try:
        scheme, iterations_raw, salt_b64, digest_b64 = encoded_hash.split("$", 3)
        if scheme != HASH_SCHEME:
            return False
        iterations = int(iterations_raw)
        salt = base64.b64decode(salt_b64.encode("ascii"), validate=True)
        expected = base64.b64decode(digest_b64.encode("ascii"), validate=True)
    except (ValueError, TypeError):
        return False

    actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(actual, expected)


def parse_auth_users(users_value: str | None) -> dict[str, str]:
    if not users_value:
        return {}

    users: dict[str, str] = {}
    for raw_item in re.split(r"[,;]", users_value):
        item = raw_item.strip()
        if not item:
            continue
        if ":" not in item:
            continue
        username, encoded_hash = item.split(":", 1)
        username = username.strip()
        encoded_hash = encoded_hash.strip()
        if username and encoded_hash:
            users[username] = encoded_hash
    return users


def authenticate_user(username: str, password: str, users_value: str | None) -> bool:
    users = parse_auth_users(users_value)
    encoded_hash = users.get(username.strip())
    if not encoded_hash:
        return False
    return verify_password(password, encoded_hash)


def session_is_authenticated(session_state: Mapping[str, object]) -> bool:
    return bool(session_state.get(AUTHENTICATED_KEY))


def clear_auth_session(session_state: MutableMapping[str, object]) -> None:
    session_state.pop(AUTHENTICATED_KEY, None)
    session_state.pop(AUTHENTICATED_USER_KEY, None)
    session_state.pop(AUTH_FAILED_KEY, None)


def render_login_gate(st_module, environ: Mapping[str, str] | None = None) -> bool:
    """Render a login gate and return whether the app body may render."""

    env = environ if environ is not None else os.environ
    if not app_auth_enabled(env):
        return True

    if session_is_authenticated(st_module.session_state):
        return True

    st_module.markdown("### Data Studio Login")
    st_module.caption("Sign in to continue.")
    with st_module.form("app_login_form"):
        username = st_module.text_input("Username", key="app_auth_username")
        password = st_module.text_input("Password", type="password", key="app_auth_password")
        submitted = st_module.form_submit_button("Log in")

    if submitted:
        if authenticate_user(username, password, env.get(APP_AUTH_USERS)):
            st_module.session_state[AUTHENTICATED_KEY] = True
            st_module.session_state[AUTHENTICATED_USER_KEY] = username.strip()
            st_module.session_state.pop(AUTH_FAILED_KEY, None)
            st_module.session_state.pop("app_auth_password", None)
            st_module.rerun()
        else:
            st_module.session_state[AUTH_FAILED_KEY] = True

    if st_module.session_state.get(AUTH_FAILED_KEY):
        st_module.error("Username or password incorrect.")

    return False


def render_logout_control(st_module, environ: Mapping[str, str] | None = None) -> None:
    env = environ if environ is not None else os.environ
    if not app_auth_enabled(env) or not session_is_authenticated(st_module.session_state):
        return

    username = str(st_module.session_state.get(AUTHENTICATED_USER_KEY, "authenticated user"))
    st_module.sidebar.caption(f"Signed in as `{username}`")
    if st_module.sidebar.button("Log out", key="app_auth_logout_btn", width="stretch"):
        clear_auth_session(st_module.session_state)
        st_module.rerun()
