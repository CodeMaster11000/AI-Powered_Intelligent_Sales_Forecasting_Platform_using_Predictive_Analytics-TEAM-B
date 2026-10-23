import streamlit as st

THEME_TOKENS = {
    "dark": {
        "canvas_bg": "#101827",
        "card_bg": "#172235",
        "card_border": "#2A3850",
        "text_primary": "#F4F7FB",
        "text_secondary": "#A9B6C8",
        "accent": "#2DD4BF",
        "btn_primary_bg": "#0F766E",
        "btn_primary_hover": "#14B8A6",
        "btn_sec_bg": "#1E2A3D",
        "btn_sec_border": "#3A4A63",
        "btn_sec_text": "#E6EDF5",
        "input_bg": "#1B2A40",
        "input_border": "#3A4A63",
        "input_text": "#F4F7FB",
        "input_placeholder": "#8B9AB0",
        "nav_bg": "#172235",
        "nav_border": "#2A3850",
        "nav_active_bg": "#22314A",
        "nav_active_text": "#2DD4BF",
        "pill_teal_bg": "#123B40",
        "pill_teal_text": "#2DD4BF",
        "pill_teal_border": "#1C6A6B",
        "pill_slate_bg": "#1E2A3D",
        "pill_slate_text": "#A9B6C8",
        "pill_slate_border": "#3A4A63",
    },
    "light": {
        "canvas_bg": "#F4F5F7",
        "card_bg": "#FFFFFF",
        "card_border": "#E5E7EB",
        "text_primary": "#111827",
        "text_secondary": "#6B7280",
        "accent": "#0F766E",
        "btn_primary_bg": "#0F766E",
        "btn_primary_hover": "#115E59",
        "btn_sec_bg": "#FFFFFF",
        "btn_sec_border": "#D1D5DB",
        "btn_sec_text": "#374151",
        "input_bg": "#FFFFFF",
        "input_border": "#D1D5DB",
        "input_text": "#111827",
        "input_placeholder": "#9CA3AF",
        "nav_bg": "#FFFFFF",
        "nav_border": "#E5E7EB",
        "nav_active_bg": "#F3F4F6",
        "nav_active_text": "#0F766E",
        "pill_teal_bg": "#ECFDF5",
        "pill_teal_text": "#047857",
        "pill_teal_border": "#A7F3D0",
        "pill_slate_bg": "#F1F5F9",
        "pill_slate_text": "#475569",
        "pill_slate_border": "#E2E8F0",
    },
}


def apply_theme():
    """Injects high-specificity CSS rules covering radio-as-tabs, inputs, dropzones, and tables."""
    mode = st.session_state.get("theme_mode", "dark")
    t = THEME_TOKENS[mode]

    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        /* 1. Global Reset & Canvas */
        [data-testid="stAppViewContainer"], 
        [data-testid="stHeader"],
        .stApp {{
            background-color: {t['canvas_bg']} !important;
            font-family: 'Inter', -apple-system, sans-serif !important;
            color: {t['text_primary']} !important;
        }}

        header[data-testid="stHeader"], .stDeployButton, #MainMenu, footer {{
            display: none !important;
            visibility: hidden !important;
        }}

        .block-container {{
            max-width: 1240px !important;
            padding-top: 1.25rem !important;
            padding-bottom: 3rem !important;
        }}

        /* 2. Top Executive Navbar */
        .sg-nav-container {{
            background: {t['nav_bg']};
            border: 1px solid {t['nav_border']};
            border-radius: 8px;
            padding: 8px 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        }}
        .sg-nav-brand {{
            font-size: 15px;
            font-weight: 700;
            color: {t['text_primary']};
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        /* 3. Cards & Border Containers */
        [data-testid="stVerticalBlockBorderWrapper"],
        [data-testid="stVerticalBlockBorderWrapper"] > div {{
            background-color: {t['card_bg']} !important;
            border-color: {t['card_border']} !important;
            border-radius: 10px !important;
        }}

        /* 4. TRANSFORM RADIO BUTTONS INTO SLEEK SEGMENTED TABS (No circles!) */
        div[data-testid="stRadio"] {{
            background: {t['nav_bg']} !important;
            border: 1px solid {t['card_border']} !important;
            border-radius: 8px !important;
            padding: 4px !important;
            width: fit-content !important;
            margin-bottom: 12px !important;
        }}
        div[data-testid="stRadio"] > div {{
            gap: 4px !important;
            display: flex !important;
            flex-direction: row !important;
            align-items: center !important;
        }}
        /* Hide the ugly circular radio dots completely */
        div[data-testid="stRadio"] input[type="radio"],
        div[data-testid="stRadio"] [data-baseweb="radio"] div:first-child {{
            display: none !important;
        }}
        /* Style the labels as clean segmented buttons */
        div[data-testid="stRadio"] label {{
            background: transparent !important;
            border: none !important;
            border-radius: 6px !important;
            padding: 6px 14px !important;
            margin: 0 !important;
            cursor: pointer !important;
            transition: all 0.15s ease-in-out !important;
        }}
        div[data-testid="stRadio"] label p,
        div[data-testid="stRadio"] label span {{
            font-size: 13px !important;
            font-weight: 500 !important;
            color: {t['text_secondary']} !important;
        }}
        /* Highlight active segmented tab */
        div[data-testid="stRadio"] label:has(input:checked) {{
            background: {t['nav_active_bg']} !important;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2) !important;
        }}
        div[data-testid="stRadio"] label:has(input:checked) p,
        div[data-testid="stRadio"] label:has(input:checked) span {{
            color: {t['accent']} !important;
            font-weight: 600 !important;
        }}

        /* 5. FIX THE BLINDING WHITE FILE UPLOADER */
        [data-testid="stFileUploader"] {{
            background: transparent !important;
        }}
        [data-testid="stFileUploader"] section,
        [data-testid="stFileUploaderDropzone"],
        [data-testid="stFileUploaderDropzone"] > div {{
            background: {t['input_bg']} !important;
            border: 1px dashed {t['card_border']} !important;
            border-radius: 8px !important;
            color: {t['text_secondary']} !important;
        }}
        [data-testid="stFileUploaderDropzone"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stFileUploaderDropzone"] span,
        [data-testid="stFileUploaderDropzone"] small {{
            color: {t['text_secondary']} !important;
        }}
        [data-testid="stFileUploader"] button {{
            background: {t['btn_sec_bg']} !important;
            border: 1px solid {t['btn_sec_border']} !important;
            color: {t['btn_sec_text']} !important;
            border-radius: 6px !important;
        }}

        /* 6. FIX THE BLINDING WHITE SELECTBOX / DROPDOWN */
        [data-testid="stSelectbox"] div[data-baseweb="select"] > div,
        div[data-baseweb="select"] > div {{
            background-color: {t['input_bg']} !important;
            border: 1px solid {t['input_border']} !important;
            color: {t['input_text']} !important;
            border-radius: 6px !important;
        }}
        div[data-baseweb="select"] span,
        div[data-baseweb="select"] div {{
            color: {t['input_text']} !important;
        }}
        div[data-baseweb="select"] svg {{
            fill: {t['text_secondary']} !important;
        }}

        /* 7. TEXT INPUTS */
        div[data-baseweb="input"],
        div[data-baseweb="base-input"] {{
            background-color: {t['input_bg']} !important;
            border: 1px solid {t['input_border']} !important;
            border-radius: 6px !important;
        }}
        [data-testid="stTextInput"] input {{
            background-color: transparent !important;
            color: {t['input_text']} !important;
            -webkit-text-fill-color: {t['input_text']} !important;
            font-size: 14px !important;
        }}
        [data-testid="stTextInput"] input::placeholder {{
            color: {t['input_placeholder']} !important;
            -webkit-text-fill-color: {t['input_placeholder']} !important;
        }}

        /* 8. FIX RED TAB UNDERLINE (Replace with Teal) */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 12px;
            border-bottom: 1px solid {t['card_border']};
            margin-bottom: 1rem;
        }}
        .stTabs [data-baseweb="tab"] {{
            font-size: 14px !important;
            font-weight: 600 !important;
            color: {t['text_secondary']} !important;
            padding: 8px 14px !important;
        }}
        .stTabs [aria-selected="true"] {{
            color: {t['accent']} !important;
        }}
        [data-baseweb="tab-highlight"] {{
            background-color: {t['accent']} !important;
            height: 2px !important;
        }}

        /* 9. BADGES & PILLS */
        .sg-title {{
            color: {t['text_primary']} !important;
            font-size: 22px;
            font-weight: 700;
            margin: 0;
        }}
        .sg-subtitle {{
            color: {t['text_secondary']} !important;
            font-size: 14px;
            margin: 4px 0 0 0;
        }}
        .sg-metric-accent {{
            color: {t['accent']} !important;
            font-size: 12px;
            font-weight: 500;
        }}
        .sg-pill {{
            display: inline-flex;
            align-items: center;
            padding: 2px 8px;
            border-radius: 9999px;
            font-size: 11px;
            font-weight: 600;
        }}
        .sg-pill-teal {{
            background-color: {t['pill_teal_bg']} !important;
            color: {t['pill_teal_text']} !important;
            border: 1px solid {t['pill_teal_border']} !important;
        }}
        .sg-pill-slate {{
            background-color: {t['pill_slate_bg']} !important;
            color: {t['pill_slate_text']} !important;
            border: 1px solid {t['pill_slate_border']} !important;
        }}

        /* 10. BUTTONS */
        button[kind="primary"] {{
            background-color: {t['btn_primary_bg']} !important;
            border: 1px solid {t['btn_primary_bg']} !important;
            color: #FFFFFF !important;
            font-weight: 600 !important;
            border-radius: 6px !important;
        }}
        button[kind="primary"]:hover {{
            background-color: {t['btn_primary_hover']} !important;
            border-color: {t['btn_primary_hover']} !important;
        }}
        button[kind="secondary"] {{
            background-color: {t['btn_sec_bg']} !important;
            border: 1px solid {t['btn_sec_border']} !important;
            color: {t['btn_sec_text']} !important;
            font-weight: 500 !important;
            border-radius: 6px !important;
        }}
        button[kind="secondary"]:hover {{
            border-color: {t['accent']} !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )