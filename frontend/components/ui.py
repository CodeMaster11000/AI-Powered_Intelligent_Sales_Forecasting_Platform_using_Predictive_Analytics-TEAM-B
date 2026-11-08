"""Reusable presentational building blocks.

Every function escapes its inputs, so callers can pass raw lead data safely.
"""
from __future__ import annotations

from typing import Iterable

import streamlit as st

from frontend.utils.helpers import PRIORITY_META, clamp, esc, initials, priority_for


def html(markup: str) -> None:
    st.markdown(markup, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = "") -> None:
    sub = f"<p class='sg-subtitle'>{esc(subtitle)}</p>" if subtitle else ""
    html(f"<div class='sg-page-head'><h3 class='sg-title'>{esc(title)}</h3>{sub}</div>")


def card_title(text: str, eyebrow: str | None = None) -> None:
    eb = f"<div class='sg-eyebrow'>{esc(eyebrow)}</div>" if eyebrow else ""
    html(f"{eb}<div class='sg-card-title'>{esc(text)}</div>")


def pill(text: str, kind: str = "slate") -> str:
    return f"<span class='sg-pill sg-pill-{esc(kind)}'>{esc(text)}</span>"


def priority_pill(priority: str, score: float | int | None = None) -> str:
    meta = PRIORITY_META.get(priority, PRIORITY_META["unscored"])
    label = f"{meta['icon']} {int(score)} {meta['label']}" if score is not None and priority != "unscored" \
        else f"{meta['icon']} {meta['label']}"
    return pill(label, meta["css"])


def kpi_card(label: str, value: str, sub: str = "", tone: str = "") -> None:
    sub_html = f"<div class='sg-kpi-sub {esc(tone)}'>{esc(sub)}</div>" if sub else ""
    html(
        f"<div class='sg-kpi'><div class='sg-eyebrow'>{esc(label)}</div>"
        f"<div class='sg-kpi-value'>{esc(value)}</div>{sub_html}</div>"
    )


def empty_state(icon: str, title: str, sub: str = "") -> None:
    sub_html = f"<div class='sub'>{esc(sub)}</div>" if sub else ""
    html(f"<div class='sg-empty'><div class='ico'>{esc(icon)}</div><div class='ttl'>{esc(title)}</div>{sub_html}</div>")


def callout(text: str, kind: str = "") -> None:
    html(f"<div class='sg-callout {esc(kind)}'>{esc(text)}</div>")


def progress_bar(label: str, value: float, maximum: float = 100, note: str = "") -> None:
    pct = clamp(value / maximum if maximum else 0) * 100
    note_html = f"<div class='sg-bar-note'>{esc(note)}</div>" if note else ""
    html(
        f"<div class='sg-bar-row'><div class='sg-bar-head'><span>{esc(label)}</span>"
        f"<span>{esc(f'{value:g}')} / {esc(f'{maximum:g}')} pts</span></div>"
        f"<div class='sg-bar' role='progressbar' aria-valuenow='{pct:.0f}' aria-valuemin='0' aria-valuemax='100'>"
        f"<i style='width:{pct:.1f}%'></i></div>{note_html}</div>"
    )


def score_ring(score: float | int | None, size: int = 92) -> str:
    """Return an inline-SVG circular gauge (theme-aware via CSS variables)."""
    tier = priority_for(score)
    color = {"hot": "var(--sg-hot)", "warm": "var(--sg-warm)", "cold": "var(--sg-cold)"}.get(tier, "var(--sg-cold)")
    r, c = 38, 2 * 3.14159 * 38
    frac = clamp((score or 0) / 100)
    text = "—" if score is None else f"{score:g}"
    return (
        f"<svg width='{size}' height='{size}' viewBox='0 0 92 92' role='img' aria-label='Score {esc(text)} of 100'>"
        f"<circle cx='46' cy='46' r='{r}' fill='none' stroke='var(--sg-cold-bg)' stroke-width='9'/>"
        f"<circle cx='46' cy='46' r='{r}' fill='none' stroke='{color}' stroke-width='9' stroke-linecap='round' "
        f"stroke-dasharray='{c * frac:.1f} {c:.1f}' transform='rotate(-90 46 46)'/>"
        f"<text x='46' y='51' text-anchor='middle' font-size='22' font-weight='700' fill='var(--sg-text)'>{esc(text)}</text></svg>"
    )


def info_grid(items: Iterable[tuple[str, object]]) -> None:
    cells = "".join(f"<div class='sg-info'><span class='sg-eyebrow'>{esc(k)}</span><b>{esc(v)}</b></div>" for k, v in items)
    html(f"<div class='sg-info-grid'>{cells}</div>")


def chips(values: Iterable[object], kind: str = "slate") -> None:
    values = [v for v in values if v]
    if values:
        html("<div class='sg-chips'>" + "".join(pill(str(v), kind) for v in values) + "</div>")


def avatar(name: str | None) -> str:
    return f"<span class='sg-avatar'>{esc(initials(name), '?')}</span>"


def backend_error(what: str = "data") -> None:
    html(
        f"<div class='sg-callout danger'><b>Couldn't load {esc(what)}.</b> "
        "Make sure the FastAPI backend is running, then use <b>Refresh</b>.</div>"
    )
