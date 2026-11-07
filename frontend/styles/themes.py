"""Design tokens + global CSS for the SalesGenie Streamlit UI.

All colours live in CSS custom properties (``--sg-*``). Components never hard-code
hex values; they use ``var(--sg-...)`` so dark/light switching works everywhere,
including inline SVG.
"""
import streamlit as st

THEME_TOKENS = {
    "dark": {
        "canvas": "#0E1626", "surface": "#162238", "surface_alt": "#1B2A42",
        "border": "#2A3A55", "text": "#F4F7FB", "text_muted": "#9FB0C6",
        "accent": "#2DD4BF", "accent_strong": "#0F766E", "accent_hover": "#14B8A6",
        "accent_soft": "#123B40", "accent_border": "#1C6A6B",
        "hot": "#34D399", "hot_bg": "#0F3B2E", "hot_border": "#1E6B52",
        "warm": "#FBBF24", "warm_bg": "#3D2F0B", "warm_border": "#7A5C12",
        "cold": "#93A4BC", "cold_bg": "#1E2A3D", "cold_border": "#3A4A63",
        "danger": "#F87171", "danger_bg": "#3B1618", "info": "#60A5FA", "info_bg": "#12294A",
        "shadow": "0 1px 2px rgba(0,0,0,.35)",
    },
    "light": {
        "canvas": "#F3F5F8", "surface": "#FFFFFF", "surface_alt": "#F8FAFC",
        "border": "#E2E8F0", "text": "#0F172A", "text_muted": "#64748B",
        "accent": "#0F766E", "accent_strong": "#0F766E", "accent_hover": "#115E59",
        "accent_soft": "#ECFDF5", "accent_border": "#A7F3D0",
        "hot": "#047857", "hot_bg": "#ECFDF5", "hot_border": "#A7F3D0",
        "warm": "#B45309", "warm_bg": "#FEF3C7", "warm_border": "#FCD34D",
        "cold": "#475569", "cold_bg": "#F1F5F9", "cold_border": "#CBD5E1",
        "danger": "#B91C1C", "danger_bg": "#FEE2E2", "info": "#1D4ED8", "info_bg": "#DBEAFE",
        "shadow": "0 1px 2px rgba(15,23,42,.06)",
    },
}


def get_tokens() -> dict:
    return THEME_TOKENS[st.session_state.get("theme_mode", "dark")]


_BASE_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
  background: var(--sg-canvas) !important;
  color: var(--sg-text) !important;
  font-family: 'Inter', -apple-system, 'Segoe UI', sans-serif !important;
}
header[data-testid="stHeader"], .stDeployButton, #MainMenu, footer { display: none !important; }
.block-container { max-width: 1280px !important; padding: 1rem 1.25rem 3rem !important; }

/* readable text in both themes (Streamlit base theme is dark) */
.stApp p, .stApp li, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5,
[data-testid="stMarkdownContainer"], [data-testid="stWidgetLabel"] p { color: var(--sg-text); }
.stApp [data-testid="stCaptionContainer"], .stApp small { color: var(--sg-text-muted) !important; }
.stApp hr { border-color: var(--sg-border) !important; margin: 14px 0 !important; }
.stApp code { background: var(--sg-surface-alt); color: var(--sg-accent); border-radius: 4px; padding: 1px 5px; }

/* accessibility: visible keyboard focus */
.stApp button:focus-visible, .stApp input:focus-visible, .stApp textarea:focus-visible,
.stApp [role="tab"]:focus-visible, .stApp label:focus-within {
  outline: 2px solid var(--sg-accent) !important; outline-offset: 2px;
}

/* ---------- containers ---------- */
[data-testid="stVerticalBlockBorderWrapper"] {
  background: var(--sg-surface) !important; border-color: var(--sg-border) !important;
  border-radius: 12px !important; box-shadow: var(--sg-shadow);
}

/* ---------- top bar ---------- */
.sg-topbar {
  display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap;
  background: var(--sg-surface); border: 1px solid var(--sg-border); border-radius: 12px;
  padding: 10px 16px; box-shadow: var(--sg-shadow);
}
.sg-brand { display: flex; align-items: center; gap: 10px; font-weight: 700; font-size: 15px; }
.sg-logo { width: 28px; height: 28px; border-radius: 8px; display: grid; place-items: center;
  background: linear-gradient(135deg, var(--sg-accent-strong), var(--sg-accent)); color: #fff; font-size: 15px; }
.sg-user { display: flex; align-items: center; gap: 8px; font-size: 13px; }
.sg-avatar { width: 28px; height: 28px; border-radius: 50%; display: grid; place-items: center;
  background: var(--sg-accent-soft); border: 1px solid var(--sg-accent-border);
  color: var(--sg-accent); font-weight: 700; font-size: 11px; flex: none; }
.sg-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; margin-right: 6px; }
.sg-dot.on { background: var(--sg-hot); box-shadow: 0 0 0 3px var(--sg-hot-bg); }
.sg-dot.off { background: var(--sg-warm); box-shadow: 0 0 0 3px var(--sg-warm-bg); }

/* ---------- headings ---------- */
.sg-title { font-size: 20px; font-weight: 700; margin: 0; color: var(--sg-text) !important; }
.sg-subtitle { font-size: 13.5px; margin: 4px 0 0; color: var(--sg-text-muted) !important; }
.sg-page-head { margin: 4px 0 14px; }
.sg-card-title { font-size: 14.5px; font-weight: 600; margin: 0 0 8px; color: var(--sg-text); }
.sg-eyebrow { font-size: 11px; font-weight: 600; letter-spacing: .05em; text-transform: uppercase;
  color: var(--sg-text-muted); }

/* ---------- KPI cards ---------- */
.sg-kpi { background: var(--sg-surface); border: 1px solid var(--sg-border); border-radius: 12px;
  padding: 14px 16px; box-shadow: var(--sg-shadow); height: 100%; }
.sg-kpi-value { font-size: 26px; font-weight: 700; line-height: 1.15; margin-top: 4px; }
.sg-kpi-sub { font-size: 12px; margin-top: 4px; color: var(--sg-text-muted); }
.sg-kpi-sub.good { color: var(--sg-hot); } .sg-kpi-sub.bad { color: var(--sg-danger); }

/* ---------- pills ---------- */
.sg-pill { display: inline-flex; align-items: center; gap: 4px; padding: 2px 9px; border-radius: 999px;
  font-size: 11px; font-weight: 600; white-space: nowrap; border: 1px solid transparent; }
.sg-pill-teal, .sg-pill-hot { background: var(--sg-hot-bg); color: var(--sg-hot); border-color: var(--sg-hot-border); }
.sg-pill-teal { background: var(--sg-accent-soft); color: var(--sg-accent); border-color: var(--sg-accent-border); }
.sg-pill-warm { background: var(--sg-warm-bg); color: var(--sg-warm); border-color: var(--sg-warm-border); }
.sg-pill-slate, .sg-pill-cold, .sg-pill-none { background: var(--sg-cold-bg); color: var(--sg-cold); border-color: var(--sg-cold-border); }
.sg-pill-danger { background: var(--sg-danger-bg); color: var(--sg-danger); }
.sg-pill-info { background: var(--sg-info-bg); color: var(--sg-info); }

/* ---------- lists / rows ---------- */
.sg-lead-row { display: flex; align-items: center; gap: 10px; padding: 8px 10px; border-radius: 10px;
  border: 1px solid transparent; }
.sg-lead-row.selected { background: var(--sg-accent-soft); border-color: var(--sg-accent-border); }
.sg-lead-main { min-width: 0; flex: 1; }
.sg-lead-name { font-weight: 600; font-size: 13.5px; line-height: 1.25; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.sg-lead-meta { font-size: 11.5px; color: var(--sg-text-muted); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.sg-score-chip { min-width: 38px; text-align: center; font-weight: 700; font-size: 13px; border-radius: 8px; padding: 4px 6px;
  border: 1px solid var(--sg-border); }
.sg-score-chip.hot { background: var(--sg-hot-bg); color: var(--sg-hot); border-color: var(--sg-hot-border); }
.sg-score-chip.warm { background: var(--sg-warm-bg); color: var(--sg-warm); border-color: var(--sg-warm-border); }
.sg-score-chip.cold, .sg-score-chip.none { background: var(--sg-cold-bg); color: var(--sg-cold); border-color: var(--sg-cold-border); }

/* ---------- progress bars ---------- */
.sg-bar-row { margin: 10px 0 4px; }
.sg-bar-head { display: flex; justify-content: space-between; font-size: 12.5px; margin-bottom: 5px; }
.sg-bar-head span:last-child { color: var(--sg-text-muted); font-variant-numeric: tabular-nums; }
.sg-bar { height: 8px; border-radius: 999px; background: var(--sg-cold-bg); overflow: hidden; }
.sg-bar > i { display: block; height: 100%; border-radius: 999px; background: linear-gradient(90deg, var(--sg-accent-strong), var(--sg-accent)); }
.sg-bar-note { font-size: 11.5px; color: var(--sg-text-muted); margin-top: 4px; }

/* ---------- callouts / empty ---------- */
.sg-callout { border-radius: 10px; padding: 11px 14px; font-size: 13px; line-height: 1.5;
  background: var(--sg-surface-alt); border: 1px solid var(--sg-border); border-left: 3px solid var(--sg-accent); }
.sg-callout.warn { border-left-color: var(--sg-warm); }
.sg-callout.danger { border-left-color: var(--sg-danger); }
.sg-empty { text-align: center; padding: 28px 16px; color: var(--sg-text-muted); }
.sg-empty .ico { font-size: 30px; margin-bottom: 6px; }
.sg-empty .ttl { font-size: 14.5px; font-weight: 600; color: var(--sg-text); }
.sg-empty .sub { font-size: 12.5px; margin-top: 4px; }

/* ---------- detail grids ---------- */
.sg-info-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; }
.sg-info { background: var(--sg-surface-alt); border: 1px solid var(--sg-border); border-radius: 10px; padding: 10px 12px; min-width: 0; }
.sg-info b { display: block; font-size: 13.5px; margin-top: 3px; overflow-wrap: anywhere; }
.sg-opp { background: var(--sg-surface-alt); border: 1px solid var(--sg-border); border-radius: 10px; padding: 11px 13px; margin-bottom: 10px; }
.sg-opp-title { font-weight: 600; font-size: 13.5px; }
.sg-opp-meta { font-size: 12px; color: var(--sg-text-muted); margin-top: 3px; }
.sg-opp-body { font-size: 13px; margin-top: 6px; line-height: 1.5; }
.sg-chips { display: flex; flex-wrap: wrap; gap: 6px; }
.sg-gauge-wrap { display: flex; align-items: center; gap: 14px; }

/* ---------- next-best-action ---------- */
.nba-heading { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; margin-bottom: 10px; }
.nba-heading h5 { margin: 2px 0 0; font-size: 16px; font-weight: 700; }
.nba-kicker, .nba-label, .nba-section-label { color: var(--sg-text-muted); font-size: 11px; font-weight: 600; letter-spacing: .04em; text-transform: uppercase; }
.nba-badge { color: var(--sg-accent); background: var(--sg-accent-soft); border: 1px solid var(--sg-accent-border); border-radius: 999px; padding: 4px 9px; font-size: 11px; white-space: nowrap; }
.nba-action { background: var(--sg-surface-alt); border: 1px solid var(--sg-border); border-left: 3px solid var(--sg-accent); border-radius: 10px; padding: 13px 15px; font-size: 15px; font-weight: 600; line-height: 1.45; margin-bottom: 14px; }
.nba-details { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; margin-bottom: 16px; }
.nba-detail { background: var(--sg-surface); border: 1px solid var(--sg-border); border-radius: 10px; min-width: 0; padding: 11px 12px; }
.nba-detail strong { display: block; font-size: 14px; line-height: 1.35; margin-top: 5px; overflow-wrap: anywhere; }
.nba-section-label { margin: 4px 0 7px; }
.nba-channel { font-size: 13px; line-height: 1.4; padding: 4px 0; }
.nba-channel span { color: var(--sg-accent); font-weight: 700; margin-right: 8px; }
.nba-content { font-size: 13px; line-height: 1.55; margin-bottom: 4px; }

/* ---------- navigation: radio -> segmented control ---------- */
div[data-testid="stRadio"] > label { display: none !important; }
div[data-testid="stRadio"] [role="radiogroup"] {
  display: flex !important; flex-wrap: wrap; gap: 4px;
  background: var(--sg-surface); border: 1px solid var(--sg-border); border-radius: 12px; padding: 4px; width: fit-content; max-width: 100%;
}
div[data-testid="stRadio"] input[type="radio"],
div[data-testid="stRadio"] [data-baseweb="radio"] > div:first-child { display: none !important; }
div[data-testid="stRadio"] label[data-baseweb="radio"] { margin: 0 !important; padding: 7px 14px !important; border-radius: 8px !important; cursor: pointer; transition: background .15s; }
div[data-testid="stRadio"] label[data-baseweb="radio"]:hover { background: var(--sg-surface-alt) !important; }
div[data-testid="stRadio"] label p { font-size: 13px !important; font-weight: 500 !important; color: var(--sg-text-muted) !important; }
div[data-testid="stRadio"] label:has(input:checked) { background: var(--sg-accent-soft) !important; box-shadow: inset 0 0 0 1px var(--sg-accent-border); }
div[data-testid="stRadio"] label:has(input:checked) p { color: var(--sg-accent) !important; font-weight: 600 !important; }

/* ---------- inputs ---------- */
div[data-baseweb="input"], div[data-baseweb="base-input"], div[data-baseweb="textarea"],
div[data-baseweb="select"] > div {
  background: var(--sg-surface-alt) !important; border: 1px solid var(--sg-border) !important; border-radius: 8px !important; }
div[data-baseweb="input"]:focus-within, div[data-baseweb="textarea"]:focus-within,
div[data-baseweb="select"] > div:focus-within { border-color: var(--sg-accent) !important; }
.stApp input, .stApp textarea { color: var(--sg-text) !important; -webkit-text-fill-color: var(--sg-text) !important; background: transparent !important; }
.stApp input::placeholder, .stApp textarea::placeholder { color: var(--sg-text-muted) !important; -webkit-text-fill-color: var(--sg-text-muted) !important; opacity: .8; }
div[data-baseweb="select"] span, div[data-baseweb="select"] div { color: var(--sg-text) !important; }
div[data-baseweb="select"] svg { fill: var(--sg-text-muted) !important; }
div[data-baseweb="popover"] ul, div[data-baseweb="popover"] li { background: var(--sg-surface) !important; color: var(--sg-text) !important; }
div[data-baseweb="popover"] li:hover { background: var(--sg-surface-alt) !important; }
[data-baseweb="tag"] { background: var(--sg-accent-soft) !important; }
[data-baseweb="tag"] span { color: var(--sg-accent) !important; }

[data-testid="stFileUploaderDropzone"] { background: var(--sg-surface-alt) !important; border: 1.5px dashed var(--sg-border) !important; border-radius: 12px !important; }
[data-testid="stFileUploaderDropzone"] * { color: var(--sg-text-muted) !important; }
[data-testid="stFileUploaderDropzone"]:hover { border-color: var(--sg-accent) !important; }

/* ---------- tabs ---------- */
.stTabs [data-baseweb="tab-list"] { gap: 6px; border-bottom: 1px solid var(--sg-border); margin-bottom: 1rem; }
.stTabs [data-baseweb="tab"] { font-size: 13.5px !important; font-weight: 600 !important; color: var(--sg-text-muted) !important; padding: 8px 14px !important; background: transparent !important; }
.stTabs [aria-selected="true"] { color: var(--sg-accent) !important; }
[data-baseweb="tab-highlight"] { background: var(--sg-accent) !important; height: 2px !important; }
[data-baseweb="tab-border"] { background: transparent !important; }

/* ---------- buttons ---------- */
.stApp button[kind="primary"], .stApp [data-testid="stBaseButton-primary"], .stApp [data-testid="stFormSubmitButton"] button {
  background: var(--sg-accent-strong) !important; border: 1px solid var(--sg-accent-strong) !important; color: #fff !important; font-weight: 600 !important; border-radius: 8px !important; }
.stApp button[kind="primary"]:hover, .stApp [data-testid="stBaseButton-primary"]:hover { background: var(--sg-accent-hover) !important; border-color: var(--sg-accent-hover) !important; }
.stApp button[kind="secondary"], .stApp [data-testid="stBaseButton-secondary"], .stApp [data-testid="stDownloadButton"] button {
  background: var(--sg-surface) !important; border: 1px solid var(--sg-border) !important; color: var(--sg-text) !important; font-weight: 500 !important; border-radius: 8px !important; }
.stApp button[kind="secondary"]:hover, .stApp [data-testid="stDownloadButton"] button:hover { border-color: var(--sg-accent) !important; color: var(--sg-accent) !important; }
.stApp button:disabled { opacity: .45 !important; cursor: not-allowed !important; }

/* ---------- misc native widgets ---------- */
[data-testid="stMetric"] { background: var(--sg-surface-alt); border: 1px solid var(--sg-border); border-radius: 10px; padding: 10px 12px; }
[data-testid="stMetricLabel"] p { color: var(--sg-text-muted) !important; font-size: 12px !important; }
[data-testid="stMetricValue"] { color: var(--sg-text) !important; }
[data-testid="stExpander"] { border: 1px solid var(--sg-border) !important; border-radius: 10px !important; background: var(--sg-surface) !important; }
[data-testid="stExpander"] summary p { font-weight: 600; }
[data-testid="stAlert"] { border-radius: 10px !important; }
[data-testid="stDataFrame"] { border: 1px solid var(--sg-border); border-radius: 10px; overflow: hidden; }
[data-testid="stProgress"] > div > div > div { background: var(--sg-accent) !important; }

/* ---------- responsive ---------- */
@media (max-width: 900px) {
  .block-container { padding: .75rem .75rem 2.5rem !important; }
  .sg-kpi-value { font-size: 22px; }
}
@media (max-width: 640px) {
  .nba-details { grid-template-columns: 1fr; }
  .sg-user .who-role { display: none; }
}
@media (prefers-reduced-motion: reduce) { * { transition: none !important; animation: none !important; } }
"""


def _css_variables(t: dict) -> str:
    return ":root{" + "".join(f"--sg-{k.replace('_', '-')}:{v};" for k, v in t.items()) + "}"


def apply_theme() -> None:
    """Inject the active theme. Call once, near the top of ``app.py``."""
    st.markdown(f"<style>{_css_variables(get_tokens())}{_BASE_CSS}</style>", unsafe_allow_html=True)
