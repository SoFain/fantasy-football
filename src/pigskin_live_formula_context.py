"""Static v1.0 live-ranking formula context for Pigskin chat."""

from __future__ import annotations

from pathlib import Path


CONTEXT_PATH = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "rebuild"
    / "pigskin-live-ranking-formula-context.md"
)

FALLBACK_CONTEXT = """
### Pigskin Live Ranking Formula Context ###

Current Pigskin is the active v1.0 ranking source for Standard, Half PPR, PPR,
and GNG Keeper across QB, RB, WR, and TE. No formula champion is active.
BQML, NGS, Stats02, PBP, injury, and availability lanes are not live formulas.
Do not claim a BQML model or formula champion is active.
"""


def load_pigskin_live_formula_context() -> str:
    """Load static formula policy context for Pigskin chat."""

    try:
        text = CONTEXT_PATH.read_text(encoding="utf-8").strip()
    except OSError:
        return FALLBACK_CONTEXT.strip()
    return text or FALLBACK_CONTEXT.strip()
