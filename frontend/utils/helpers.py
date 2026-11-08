"""Small, dependency-free helpers shared by every frontend component."""
from __future__ import annotations

import html
from typing import Any

PRIORITY_META = {
    "hot": {"label": "HOT", "icon": "🔥", "css": "hot"},
    "warm": {"label": "WARM", "icon": "🌤️", "css": "warm"},
    "cold": {"label": "COLD", "icon": "❄️", "css": "cold"},
    "unscored": {"label": "UNSCORED", "icon": "⚪", "css": "none"},
}


def esc(value: Any, default: str = "—") -> str:
    """HTML-escape any value before it goes into an ``unsafe_allow_html`` block.

    Lead data comes from CSV files and web forms, so it must never be trusted.
    """
    if value is None or (isinstance(value, str) and not value.strip()):
        return html.escape(default)
    return html.escape(str(value))


def priority_for(score: float | int | None) -> str:
    """Mirror of the backend tiering rule (>=75 hot, >=40 warm, else cold)."""
    if score is None:
        return "unscored"
    return "hot" if score >= 75 else "warm" if score >= 40 else "cold"


def fmt_pct(value: Any, digits: int = 1, default: str = "—") -> str:
    try:
        return f"{float(value):.{digits}f}%"
    except (TypeError, ValueError):
        return default


def fmt_int(value: Any, default: str = "—") -> str:
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return default


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def initials(name: str | None) -> str:
    parts = [p for p in (name or "").replace("(", " ").split() if p]
    if not parts:
        return "?"
    return (parts[0][0] + (parts[-1][0] if len(parts) > 1 else "")).upper()
