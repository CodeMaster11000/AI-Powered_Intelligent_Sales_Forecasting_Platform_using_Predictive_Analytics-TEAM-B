import streamlit as st

THEME_TOKENS = {
    "dark": {
        # Layered blue-slate surfaces with a low-saturation teal accent.
        "canvas_bg": "#101827",
        "card_bg": "#172235",
        "card_border": "#2A3850",
        "text_primary": "#F4F7FB",
        "text_secondary": "#A9B6C8",
        "accent": "#5EEAD4",
        "btn_primary_bg": "#0F766E",
        "btn_primary_hover": "#14B8A6",
        "btn_sec_bg": "#1E2A3D",
        "btn_sec_border": "#3A4A63",
        "btn_sec_text": "#E6EDF5",
        # Form inputs use a distinct surface so they remain easy to scan.
        "input_bg": "#1B2A40",
        "input_border": "#3A4A63",
        "input_text": "#F4F7FB",
        "input_placeholder": "#8B9AB0",
        # Muted teal tags preserve emphasis without glowing against the canvas.
        "tag_bg": "#123B40",
        "tag_text": "#7DE3D1",
        "tag_border": "#1C6A6B",
        # Pills & Banners
        "pill_teal_bg": "#123B40",
        "pill_teal_text": "#7DE3D1",
        "pill_teal_border": "#1C6A6B",
        "pill_slate_bg": "#1E2A3D",
        "pill_slate_text": "#A9B6C8",
        "pill_slate_border": "#3A4A63",
        "banner_bg": "#123B40",
        "banner_border": "#1C6A6B",
        "banner_text": "#7DE3D1",
        # Top Navbar
        "nav_bg": "#172235",
        "nav_border": "#2A3850",
        "nav_active_bg": "#22314A",
        "nav_active_text": "#7DE3D1",
    },
    "light": {
        # Canvas & Cards
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
        # Form Inputs (Clean White)
        "input_bg": "#FFFFFF",
        "input_border": "#D1D5DB",
        "input_text": "#111827",
        "input_placeholder": "#9CA3AF",
        # Multiselect Tags (Soft Sky Blue)
        "tag_bg": "#E0F2FE",
        "tag_text": "#0369A1",
        "tag_border": "#BAE6FD",
        # Pills & Banners
        "pill_teal_bg": "#ECFDF5",
        "pill_teal_text": "#047857",
        "pill_teal_border": "#A7F3D0",
        "pill_slate_bg": "#F1F5F9",
        "pill_slate_text": "#475569",
        "pill_slate_border": "#E2E8F0",
        "banner_bg": "#F0FDFA",
        "banner_border": "#CCFBF1",
        "banner_text": "#0F766E",
        # Top Navbar
        "nav_bg": "#FFFFFF",
        "nav_border": "#E5E7EB",
        "nav_active_bg": "#F3F4F6",
        "nav_active_text": "#0F766E",
    },
}


def apply_theme():
    """Injects high-specificity CSS rules covering all inputs, cards, and tags."""
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

        /* Shared Streamlit text defaults */
        [data-testid="stAppViewContainer"] p,
        [data-testid="stAppViewContainer"] span,
        [data-testid="stAppViewContainer"] label,
        [data-testid="stAppViewContainer"] [data-testid="stCaptionContainer"] {{
            color: {t['text_primary']};
        }}
        [data-testid="stCaptionContainer"],
        [data-testid="stCaptionContainer"] p,
        [data-testid="stWidgetLabel"] label,
        [data-testid="stWidgetLabel"] p {{
            color: {t['text_secondary']} !important;
        }}

        /* 2. Top Navigation Bar */
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
        .sg-nav-links {{
            display: flex;
            gap: 8px;
        }}
        .sg-nav-link {{
            font-size: 13px;
            font-weight: 500;
            color: {t['text_secondary']};
            padding: 5px 12px;
            border-radius: 6px;
            text-decoration: none;
        }}
        .sg-nav-active {{
            color: {t['nav_active_text']} !important;
            background-color: {t['nav_active_bg']} !important;
            font-weight: 600;
        }}

        /* 3. Cards & Border Containers */
        [data-testid="stVerticalBlockBorderWrapper"],
        [data-testid="stVerticalBlockBorderWrapper"] > div {{
            background-color: {t['card_bg']} !important;
            border-color: {t['card_border']} !important;
            border-radius: 10px !important;
        }}

        /* 4. Complete Form Input Styling (Fixes the white blocks in Dark Mode) */
        /* Text input outer wrappers & inner elements */
        div[data-baseweb="input"],
        div[data-baseweb="base-input"],
        [data-testid="stTextInput"] div[data-baseweb="input"],
        [data-testid="stTextInput"] div[data-baseweb="base-input"] {{
            background-color: {t['input_bg']} !important;
            border-color: {t['input_border']} !important;
            box-shadow: inset 0 0 0 1px {t['input_border']} !important;
            border-radius: 6px !important;
        }}
        
        /* The actual <input> element text and background */
        [data-testid="stTextInput"] input,
        div[data-baseweb="input"] input,
        div[data-baseweb="base-input"] input {{
            background-color: {t['input_bg']} !important;
            color: {t['input_text']} !important;
            -webkit-text-fill-color: {t['input_text']} !important;
            font-size: 14px !important;
        }}
        
        [data-testid="stTextInput"] input::placeholder,
        div[data-baseweb="input"] input::placeholder {{
            color: {t['input_placeholder']} !important;
            -webkit-text-fill-color: {t['input_placeholder']} !important;
        }}

        /* Selectboxes (Dropdowns) */
        div[data-baseweb="select"],
        div[data-baseweb="select"] > div,
        div[data-baseweb="select"] [aria-expanded] {{
            background-color: {t['input_bg']} !important;
            border-color: {t['input_border']} !important;
            color: {t['input_text']} !important;
            box-shadow: inset 0 0 0 1px {t['input_border']} !important;
            border-radius: 6px !important;
        }}
        div[data-baseweb="select"] *,
        div[data-baseweb="select"] input {{
            background-color: transparent !important;
            color: {t['input_text']} !important;
        }}
        div[data-baseweb="select"] svg {{
            fill: {t['text_secondary']} !important;
        }}

        /* Dropdown menus render in a portal outside the widget container. */
        [data-baseweb="popover"],
        [data-baseweb="menu"],
        ul[role="listbox"],
        div[role="listbox"] {{
            background-color: {t['card_bg']} !important;
            border: 1px solid {t['card_border']} !important;
            color: {t['text_primary']} !important;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.28) !important;
        }}
        [data-baseweb="popover"] [role="option"],
        [data-baseweb="menu"] [role="option"],
        ul[role="listbox"] [role="option"],
        div[role="listbox"] [role="option"] {{
            background-color: {t['card_bg']} !important;
            color: {t['text_primary']} !important;
        }}
        [data-baseweb="popover"] [role="option"]:hover,
        [data-baseweb="menu"] [role="option"]:hover,
        ul[role="listbox"] [role="option"]:hover,
        div[role="listbox"] [role="option"]:hover,
        [role="option"][aria-selected="true"] {{
            background-color: {t['nav_active_bg']} !important;
            color: {t['text_primary']} !important;
        }}
        [data-baseweb="popover"] [role="option"] *,
        [data-baseweb="menu"] [role="option"] *,
        [role="listbox"] [role="option"] * {{
            background-color: transparent !important;
            color: inherit !important;
        }}

        /* Multiselect container */
        [data-testid="stMultiSelect"] div[data-baseweb="select"] > div {{
            background-color: {t['input_bg']} !important;
            border-color: {t['input_border']} !important;
        }}

        /* Multiselect tags/chips */
        div[data-baseweb="tag"],
        span[data-baseweb="tag"] {{
            background-color: {t['tag_bg']} !important;
            border: 1px solid {t['tag_border']} !important;
            border-radius: 4px !important;
            color: {t['tag_text']} !important;
        }}
        div[data-baseweb="tag"] *,
        span[data-baseweb="tag"] * {{
            background-color: transparent !important;
            color: {t['tag_text']} !important;
            fill: {t['tag_text']} !important;
        }}

        /* Input Labels & Captions */
        div[data-testid="stWidgetLabel"] label,
        div[data-testid="stWidgetLabel"] p {{
            color: {t['text_secondary']} !important;
            font-size: 13px !important;
            font-weight: 500 !important;
        }}
        [data-testid="stTextInput"] input:focus,
        [data-testid="stSelectbox"] [data-baseweb="select"]:focus-within,
        [data-testid="stMultiSelect"] [data-baseweb="select"]:focus-within {{
            border-color: {t['accent']} !important;
            box-shadow: inset 0 0 0 1px {t['accent']}, 0 0 0 1px {t['accent']} !important;
        }}

        /* 5. File uploader */
        [data-testid="stFileUploader"] {{
            color: {t['text_primary']} !important;
        }}
        [data-testid="stFileUploader"] section,
        [data-testid="stFileUploaderDropzone"] {{
            background: {t['input_bg']} !important;
            border: 1px dashed {t['input_border']} !important;
            border-radius: 8px !important;
            padding: 1.25rem !important;
        }}
        [data-testid="stFileUploader"] section:hover,
        [data-testid="stFileUploaderDropzone"]:hover {{
            background: {t['nav_active_bg']} !important;
            border-color: {t['accent']} !important;
        }}
        [data-testid="stFileUploader"] section *,
        [data-testid="stFileUploaderDropzone"] * {{
            color: {t['text_secondary']} !important;
        }}
        [data-testid="stFileUploader"] small,
        [data-testid="stFileUploader"] [data-testid="stMarkdownContainer"] p {{
            color: {t['text_secondary']} !important;
        }}
        [data-testid="stFileUploader"] button {{
            background: {t['btn_sec_bg']} !important;
            border: 1px solid {t['btn_sec_border']} !important;
            color: {t['btn_sec_text']} !important;
        }}
        [data-testid="stFileUploader"] button:hover {{
            background: {t['nav_active_bg']} !important;
            border-color: {t['accent']} !important;
            color: {t['text_primary']} !important;
        }}
        [data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] {{
            background: {t['card_bg']} !important;
            border: 1px solid {t['card_border']} !important;
            color: {t['text_primary']} !important;
        }}
        [data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] * {{
            color: {t['text_primary']} !important;
        }}

        /* 6. Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 12px;
            border-bottom: 1px solid {t['card_border']};
            margin-bottom: 1.25rem;
        }}
        .stTabs [data-baseweb="tab"] {{
            font-size: 14px !important;
            font-weight: 600 !important;
            color: {t['text_secondary']} !important;
            padding: 8px 16px !important;
        }}
        .stTabs [aria-selected="true"] {{
            color: {t['accent']} !important;
        }}
        [data-baseweb="tab-highlight"] {{
            background-color: {t['accent']} !important;
        }}

        /* 7. Typography & Pills */
        .sg-title {{
            color: {t['text_primary']};
            font-size: 24px;
            font-weight: 700;
            margin: 0;
        }}
        .sg-subtitle {{
            color: {t['text_secondary']};
            font-size: 14px;
            margin: 4px 0 0 0;
        }}
        .sg-metric-accent {{
            color: {t['accent']};
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
            background-color: {t['pill_teal_bg']};
            color: {t['pill_teal_text']};
            border: 1px solid {t['pill_teal_border']};
        }}
        .sg-pill-slate {{
            background-color: {t['pill_slate_bg']};
            color: {t['pill_slate_text']};
            border: 1px solid {t['pill_slate_border']};
        }}
        .sg-file-banner {{
            background: {t['banner_bg']};
            border: 1px solid {t['banner_border']};
            color: {t['banner_text']};
            padding: 8px 12px;
            border-radius: 6px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 14px 0;
        }}

        /* 8. Buttons */
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
        </style>
        """,
        unsafe_allow_html=True,
    )