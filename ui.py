import streamlit as st

def theme_toggle():
    """Render a theme switcher toggle in the sidebar."""
    if "theme" not in st.session_state:
        st.session_state["theme"] = "light"
    
    label = "🌙 Vibrant Night" if st.session_state.theme == "dark" else "☀️ Vibrant Day"
    
    # st.toggle returns True if toggled on. We'll say True = Light, False = Dark
    is_light = st.session_state.theme == "light"
    changed = st.sidebar.toggle(label, value=is_light, key="theme_toggle_widget")
    
    new_theme = "light" if changed else "dark"
    
    if new_theme != st.session_state.theme:
        st.session_state.theme = new_theme
        st.rerun()


def apply_global_styles(page_title: str, subtitle: str = "") -> None:
    """Apply the Vibrant Non-Monochrome Dual-theme."""
    if "theme" not in st.session_state:
        st.session_state["theme"] = "light"
        
    theme = st.session_state.theme

    if theme == "dark":
        # Ultra-Vibrant Dark: Deep Navy & Amber/Gold
        primary = "#f59e0b"           # Amber
        primary_hover = "#fbbf24"
        secondary = "#3b82f6"         # Electric Blue
        bg_main = "#0f172a"           # Deep Slate/Navy Background
        bg_card = "#1e3a8a"           # Royal Blue Cards
        bg_border = "#3b82f6"         # Blue border
        text_main = "#eff6ff"         # Ice blue text
        text_soft = "#93c5fd"         # Light blue text
        card_shadow = "0 8px 30px rgba(15,23,42,0.6)"
        glow = "0 0 15px rgba(245, 158, 11, 0.4)"
        grid_bg = "#1e3a8a"
        hero_start = "#3b82f6"
        hero_end = "#f59e0b"
        header_bg = "rgba(59, 130, 246, 0.2)"
        grad_color1 = "rgba(59, 130, 246, 0.08)"
        grad_color2 = "rgba(245, 158, 11, 0.06)"
        table_filter = "none"
    else:
        # Ultra-Vibrant Light: Indigo Wash & Magenta
        primary = "#ec4899"           # Vibrant Pink/Magenta
        primary_hover = "#f472b6"
        secondary = "#4338ca"         # Deep Indigo
        bg_main = "#e0e7ff"           # Periwinkle/Indigo wash
        bg_card = "#c7d2fe"           # Solid pastel Indigo
        bg_border = "#a5b4fc"
        text_main = "#1e1b4b"         # Extremely dark violet
        text_soft = "#312e81"         # Dark violet
        card_shadow = "0 4px 20px rgba(67, 56, 202, 0.15)"
        glow = "0 0 15px rgba(236, 72, 153, 0.4)"
        grid_bg = "#c7d2fe"
        hero_start = "#4338ca"
        hero_end = "#ec4899"
        header_bg = "rgba(236, 72, 153, 0.1)"
        grad_color1 = "rgba(67, 56, 202, 0.06)"
        grad_color2 = "rgba(236, 72, 153, 0.06)"
        # Streamlit draws data tables with canvas based on config.toml (which is dark). 
        # By inverting the entire dataframe in light mode, the black canvas becomes white exactly matching the theme.
        table_filter = "invert(0.9) hue-rotate(180deg) brightness(1.2) contrast(0.9)"

    st.markdown(
        f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

            :root {{
                --brand-primary: {primary};
                --brand-primary-hover: {primary_hover};
                --brand-secondary: {secondary};
                --bg-main: {bg_main};
                --bg-card: {bg_card};
                --bg-border: {bg_border};
                --text-main: {text_main};
                --text-soft: {text_soft};
                --shadow: {card_shadow};
                --shadow-glow: {glow};
                --border: 1px solid var(--bg-border);
                --grid-bg: {grid_bg};
                --header-bg: {header_bg};
                --hero-start: {hero_start};
                --hero-end: {hero_end};
                --table-filter: {table_filter};
            }}

            html, body, .stApp {{
                font-family: 'Outfit', sans-serif !important;
                color: var(--text-main);
                line-height: 1.5;
            }}

            [data-testid="stAppViewContainer"] {{
                background: radial-gradient(circle at 15% 50%, {grad_color1}, transparent 25%),
                            radial-gradient(circle at 85% 30%, {grad_color2}, transparent 25%),
                            var(--bg-main) !important;
            }}

            /* Override Streamlit Defaults with Important */
            [data-testid="stHeader"] {{
                background: transparent !important;
            }}

            [data-testid="stDecoration"] {{
                background: linear-gradient(90deg, var(--hero-start), var(--hero-end)) !important;
                height: 4px !important;
            }}

            [data-testid="stSidebar"] {{
                background: var(--bg-card) !important;
                border-right: var(--border) !important;
            }}

            [data-testid="stSidebar"] * {{
                color: var(--text-main) !important;
            }}

            /* Fonts */
            h1, h2, h3, h4, h5, h6 {{
                color: var(--text-main) !important;
                font-family: 'Outfit', sans-serif !important;
                letter-spacing: -0.01em !important;
            }}
            p, span, label, div {{
                color: var(--text-main);
            }}

            /* Custom Components */
            .hero-card {{
                background: linear-gradient(135deg, var(--hero-start), var(--hero-end));
                border-radius: 16px;
                box-shadow: 0 10px 25px -5px rgba(0,0,0,0.3);
                padding: 2.5rem 2rem;
                margin-bottom: 2rem;
                color: #FFFFFF !important;
                position: relative;
                overflow: hidden;
            }}
            
            /* Animated scan line effect */
            .hero-card::after {{
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 50%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
                animation: scan 3s infinite linear;
            }}
            @keyframes scan {{
                0% {{ left: -100%; }}
                100% {{ left: 200%; }}
            }}

            .hero-title {{
                font-weight: 800;
                font-size: clamp(1.8rem, 3vw, 2.5rem);
                margin-bottom: 0.5rem;
                color: #FFFFFF !important;
            }}

            .hero-subtitle {{
                color: rgba(255, 255, 255, 0.9) !important;
                font-size: 1.1rem;
                margin: 0;
            }}

            /* Custom Cards */
            .glass-card {{
                background: var(--bg-card);
                border: var(--border);
                border-radius: 16px;
                box-shadow: var(--shadow);
                padding: 1.5rem;
                margin: 0.5rem 0;
                transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
                height: 100%;
            }}
            .glass-card:hover {{
                transform: translateY(-3px);
                box-shadow: var(--shadow-glow);
                border-color: var(--brand-primary);
            }}
            .glass-card h3 {{
                color: var(--text-main) !important;
                margin: 0 0 0.5rem 0;
                font-size: 1.2rem;
                font-weight: 700;
            }}
            .glass-card p {{
                margin: 0;
                color: var(--text-soft) !important;
                font-size: 0.95rem;
            }}

            /* Metrics */
            div[data-testid="stMetric"] {{
                background: var(--bg-card);
                border: var(--border);
                border-radius: 16px;
                padding: 1.5rem;
                box-shadow: var(--shadow);
            }}
            div[data-testid="stMetricLabel"] {{
                color: var(--text-soft) !important;
            }}
            div[data-testid="stMetricValue"] {{
                color: var(--brand-primary) !important;
            }}

            /* EXTREME OVERRIDE: Inputs (Text, Date, Time, Select) */
            /* This fixes the black Time Input and input shadows */
            .stTextInput input, .stTextArea textarea, .stDateInput input, 
            .stTimeInput input, .stNumberInput input, 
            [data-baseweb="input"], [data-baseweb="base-input"],
            [data-baseweb="select"] > div, [data-testid="stTimeInput"] > div > div {{
                background-color: var(--grid-bg) !important;
                background: var(--grid-bg) !important;
                border: var(--border) !important;
                border-radius: 10px !important;
                color: var(--text-main) !important;
                box-shadow: none !important; 
                -webkit-box-shadow: none !important;
            }}
            input:focus, textarea:focus, [data-baseweb="select"] > div:focus {{
                border-color: var(--brand-primary) !important;
                box-shadow: 0 0 0 2px var(--brand-primary) !important;
            }}

            /* Dropdown Menus (Popovers) */
            div[data-baseweb="popover"] > div, div[data-baseweb="popover"] ul, [data-baseweb="menu"], ul[role="listbox"] {{
                background-color: var(--grid-bg) !important;
                border: var(--border) !important;
                border-radius: 8px !important;
            }}
            [data-baseweb="select"] span {{ color: var(--text-main) !important; }}
            li[role="option"] {{
                background-color: transparent !important;
                color: var(--text-main) !important;
            }}
            li[role="option"]:hover, li[role="option"][aria-selected="true"] {{
                background-color: var(--brand-primary) !important;
                color: #FFFFFF !important;
            }}

            /* EXTREME OVERRIDE: Expanders */
            /* This fixes the black expander headers */
            [data-testid="stExpander"], 
            [data-testid="stExpander"] > details, 
            [data-testid="stExpander"] summary,
            [data-testid="stExpander"] div[data-testid="stExpanderDetails"] {{
                background-color: var(--grid-bg) !important;
                background: var(--grid-bg) !important;
                border-color: var(--bg-border) !important;
            }}
            [data-testid="stExpander"] summary {{
                color: var(--brand-primary) !important;
                font-weight: 600 !important;
                padding: 1rem !important;
            }}
            div[data-testid="stExpander"] * {{
                color: var(--text-main);
            }}

            /* Tabs */
            button[data-baseweb="tab"] {{ background-color: transparent !important; color: var(--text-soft) !important; }}
            button[data-baseweb="tab"][aria-selected="true"] {{ color: var(--brand-primary) !important; }}
            div[data-baseweb="tab-highlight"] {{ background-color: var(--brand-primary) !important; }}

            /* EXTREME OVERRIDE: ALL Buttons (Primary, Secondary, Form Submit, Download) */
            /* This fixes the pale secondary buttons */
            .stButton > button, .stDownloadButton > button, .stFormSubmitButton > button,
            button[kind="primary"], button[kind="secondary"], 
            button[data-testid="baseButton-secondary"], button[data-testid="baseButton-primary"] {{
                background: linear-gradient(90deg, var(--brand-primary), var(--brand-secondary)) !important;
                color: #FFFFFF !important;
                font-weight: 600 !important;
                border: none !important;
                border-radius: 10px !important;
                padding: 0.6rem 1.5rem !important;
                box-shadow: var(--shadow-glow) !important;
                transition: transform 0.2s ease !important;
            }}
            button:hover {{ transform: translateY(-2px) !important; filter: brightness(1.2) !important; }}

            /* Camera Input inner buttons ONLY */
            [data-testid="stCameraInput"] button {{
                background: var(--bg-card) !important;
                color: var(--text-main) !important;
                border: var(--border) !important;
                box-shadow: none !important;
            }}
            
            /* Checkboxes, Radios, Sliders, MultiSelect */
            [data-testid="stCheckbox"] span, [data-testid="stRadio"] span {{ color: var(--text-main) !important; }}
            div[data-baseweb="checkbox"] > div:first-child, div[data-baseweb="radio"] > div:first-child {{ border-color: var(--brand-primary) !important; }}
            div[data-baseweb="checkbox"] > div:first-child[data-checked="true"], 
            div[data-baseweb="radio"] > div:first-child[data-checked="true"] {{ background-color: var(--brand-primary) !important; }}
            [data-baseweb="slider"] div[role="slider"] {{ background-color: var(--brand-primary) !important; }}
            [data-baseweb="tag"] {{ background-color: var(--brand-primary) !important; color: #FFFFFF !important; }}
            [data-baseweb="tag"] span {{ color: #FFFFFF !important; }}

            /* Table HTML overrides */
            div[data-testid="stTable"], th, td {{
                background: var(--grid-bg) !important;
                background-color: var(--grid-bg) !important;
                color: var(--text-main) !important;
            }}
            
            [data-testid="stDataFrame"], [data-testid="stDataEditor"], div[data-testid="stDataEditor"] {{
                 filter: var(--table-filter) !important;
                 transition: filter 0.3s ease;
            }}
            
            /* File Dropzone */
            [data-testid="stFileUploadDropzone"] {{
                background: var(--grid-bg) !important;
                border: 2px dashed var(--brand-primary) !important;
            }}
            
            code {{ background-color: var(--grid-bg) !important; color: var(--brand-secondary) !important; border: var(--border) !important; }}
            div[data-testid="stToast"] {{ background-color: var(--bg-card) !important; border: 1px solid var(--brand-primary) !important; color: var(--text-main) !important; box-shadow: var(--shadow-glow) !important; }}

        </style>
        """,
        unsafe_allow_html=True,
    )

    hero_html = f"""
        <section class="hero-card">
            <div class="hero-title">{page_title}</div>
            {f'<p class="hero-subtitle">{subtitle}</p>' if subtitle else ''}
        </section>
    """
    st.markdown(hero_html, unsafe_allow_html=True)


def glass_info_card(title: str, description: str) -> None:
    st.markdown(
        f"""
        <div class="glass-card">
            <h3>{title}</h3>
            <p>{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

def check_auth():
    """Security wrapper to redirect if not app_logged_in."""
    if not st.session_state.get("app_logged_in", False):
        if hasattr(st, "switch_page"):
            st.switch_page("app.py")
        else:
            st.error("Authentication required. Please return to the main Login Page.")
            st.stop()

def render_login_bg():
    """Render the fullscreen login UI background and hide sidebar."""
    import os
    import base64
    bg_file = "login.png"
    bg_css = ""
    if os.path.exists(bg_file):
        with open(bg_file, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode()
        bg_css = f"""
        [data-testid="stAppViewContainer"] {{
            background-image: url("data:image/png;base64,{encoded_string}") !important;
            background-size: cover !important;
            background-position: center !important;
            background-repeat: no-repeat !important;
        }}
        """
        
    st.markdown(f"""
        <style>
        {bg_css}
        /* Hide sidebar unconditionally on login screen */
        [data-testid="stSidebar"] {{
            display: none !important;
        }}
        /* Hide header */
        [data-testid="stHeader"] {{
            display: none !important;
        }}
        /* Hide the hero card injected by apply_global_styles */
        .hero-card {{
            display: none !important;
        }}
        
        /* Centered Elegant Layout */
        .stApp {{
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            background-color: transparent !important;
        }}
        
        /* Make sure the main layout container centers children */
        [data-testid="stMain"] {{
            background-color: transparent !important;
        }}

        .block-container {{
            width: 100% !important;
            max-width: 450px !important;
            min-width: 320px !important;
            margin: auto !important;
            padding: 2rem !important;
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
            position: relative;
            z-index: 999;
        }}
        
        /* Glassmorphism Elegant Form Styling */
        [data-testid="stForm"] {{
            background: rgba(15, 23, 42, 0.75) !important; /* Elegant dark navy glass */
            backdrop-filter: blur(16px) saturate(180%) !important;
            -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
            border-radius: 24px !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            padding: 40px !important;
            width: 100% !important;
            max-width: 450px !important;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5) !important;
            margin: 0 auto !important;
        }}
        
        /* Typography */
        .login-title {{
            text-align: center;
            color: #ffffff !important;
            font-weight: 800;
            font-size: 28px;
            margin-bottom: 5px;
            letter-spacing: 0.5px;
        }}
        .login-subtitle {{
            text-align: center;
            color: #94a3b8 !important; /* slate-400 */
            font-weight: 500;
            font-size: 16px;
            margin-bottom: 30px;
        }}
        .login-footer {{
            text-align: center;
            color: #94a3b8 !important;
            font-size: 14px;
            margin-top: 20px;
            margin-bottom: 0;
            padding-bottom: 0;
        }}
        .login-footer a {{
            color: #3b82f6 !important; /* blue-500 */
            text-decoration: none;
            font-weight: 600;
            transition: color 0.2s;
        }}
        .login-footer a:hover {{
            color: #60a5fa !important; /* blue-400 */
        }}
        
        /* EXTREME OVERRIDE: Solid translucent input fields */
        [data-testid="stForm"] .stTextInput {{
            margin-bottom: 15px !important;
        }}
        [data-testid="stForm"] .stTextInput input, 
        [data-testid="stForm"] [data-baseweb="input"], 
        [data-testid="stForm"] [data-baseweb="base-input"] {{
            background-color: rgba(255, 255, 255, 0.05) !important;
            background: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 12px !important;
            box-shadow: none !important;
            color: #ffffff !important;
            font-size: 15px !important;
            transition: all 0.2s ease !important;
            height: 48px !important;
        }}
        [data-testid="stForm"] input::placeholder {{
            color: rgba(255,255,255,0.4) !important;
            opacity: 1;
        }}
        [data-testid="stForm"] input:focus,
        [data-testid="stForm"] [data-baseweb="input"]:focus-within {{
            border-color: #3b82f6 !important; /* blue-500 */
            background-color: rgba(255, 255, 255, 0.1) !important;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2) !important;
        }}
        
        /* Submit Button Styling */
        [data-testid="stForm"] .stButton > button, 
        [data-testid="stForm"] .stFormSubmitButton > button {{
            background: #3b82f6 !important; /* solid pleasant blue */
            color: #ffffff !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 12px !important;
            font-weight: 700 !important;
            font-size: 16px !important;
            letter-spacing: 0.5px !important;
            width: 100% !important;
            margin-top: 15px !important;
            transition: all 0.2s ease !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06) !important;
            height: 48px !important;
        }}
        [data-testid="stForm"] .stButton > button:hover,
        [data-testid="stForm"] .stFormSubmitButton > button:hover {{
            background: #2563eb !important; /* darker blue */
            box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.4) !important;
            transform: translateY(-2px) !important;
            filter: none !important;
        }}
        
        </style>
    """, unsafe_allow_html=True)
