"""Default-off compatibility rollout flags for Streamlit UI reads."""

from __future__ import annotations

import os
from collections.abc import Mapping


USE_COMPAT_PLAYER_PROFILES = "USE_COMPAT_PLAYER_PROFILES"
USE_COMPAT_SLEEPER_WATCH = "USE_COMPAT_SLEEPER_WATCH"
USE_COMPAT_TRADE_ASSETS = "USE_COMPAT_TRADE_ASSETS"
USE_COMPAT_TRADE_PLAYER_HISTORY = "USE_COMPAT_TRADE_PLAYER_HISTORY"
USE_COMPAT_VIEWER_TEAM_CONTEXT = "USE_COMPAT_VIEWER_TEAM_CONTEXT"

COMPAT_FLAG_NAMES = (
    USE_COMPAT_PLAYER_PROFILES,
    USE_COMPAT_SLEEPER_WATCH,
    USE_COMPAT_TRADE_ASSETS,
    USE_COMPAT_TRADE_PLAYER_HISTORY,
    USE_COMPAT_VIEWER_TEAM_CONTEXT,
)

TRUE_VALUES = {"1", "true", "yes", "y", "on"}


def compat_flag_enabled(
    flag_name: str,
    environ: Mapping[str, str] | None = None,
) -> bool:
    """Return whether a compatibility flag is enabled."""

    if flag_name not in COMPAT_FLAG_NAMES:
        raise ValueError(f"Unknown compatibility flag: {flag_name}")
    env = environ if environ is not None else os.environ
    return str(env.get(flag_name, "false")).strip().lower() in TRUE_VALUES
