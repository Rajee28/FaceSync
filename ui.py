import streamlit as st


def apply_global_styles(page_title: str, subtitle: str = "") -> None:
    """Apply a consistent visual theme and render a reusable hero header."""
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

            :root {
                --brand-deep: #083344;
                --brand-mid: #0f766e;
                --brand-accent: #14b8a6;
                --brand-warm: #f59e0b;
                --brand-soft: #d7f7f3;
                --text-main: #102a43;
                --text-soft: #486581;
                --text-muted: #6b7f95;
                --surface: rgba(255, 255, 255, 0.9);
                --surface-strong: #ffffff;
                --surface-soft: rgba(255, 255, 255, 0.72);
                --shadow: 0 12px 30px rgba(8, 51, 68, 0.14);
                --border: rgba(15, 118, 110, 0.2);
                --border-strong: rgba(15, 118, 110, 0.33);
                --focus-ring: 0 0 0 3px rgba(20, 184, 166, 0.24);
            }

            html, body, .stApp {
                font-family: 'Outfit', sans-serif;
                color: var(--text-main);
                line-height: 1.45;
            }

            [data-testid="stAppViewContainer"] {
                background:
                    radial-gradient(circle at 14% 18%, rgba(20, 184, 166, 0.22), transparent 32%),
                    radial-gradient(circle at 85% 8%, rgba(245, 158, 11, 0.17), transparent 24%),
                    linear-gradient(135deg, #f5fffd 0%, #ebf8f7 52%, #fff7ea 100%);
            }

            [data-testid="stHeader"] {
                background: transparent !important;
                border-bottom: none !important;
                backdrop-filter: none !important;
                -webkit-backdrop-filter: none !important;
            }

            [data-testid="stDecoration"] {
                background: linear-gradient(90deg, rgba(8, 51, 68, 0.52), rgba(15, 118, 110, 0.45)) !important;
            }

            [data-testid="stHeader"] * {
                color: #f4fbff !important;
            }

            header[data-testid="stHeader"] {
                background: transparent !important;
            }

            [data-testid="stToolbar"] {
                right: 0.85rem;
            }

            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #083344 0%, #0a4b5b 100%);
                border-right: 1px solid rgba(255, 255, 255, 0.08);
            }

            [data-testid="stSidebar"] * {
                color: #effcf9 !important;
            }

            [data-testid="stSidebar"] h1,
            [data-testid="stSidebar"] h2,
            [data-testid="stSidebar"] h3,
            [data-testid="stSidebar"] h4,
            [data-testid="stSidebar"] h5,
            [data-testid="stSidebar"] h6,
            [data-testid="stSidebar"] p,
            [data-testid="stSidebar"] label,
            [data-testid="stSidebar"] span {
                color: #effcf9 !important;
            }

            .main > div {
                padding-top: 1.3rem;
            }

            .block-container {
                max-width: 1120px;
                padding-top: 1.15rem;
                padding-bottom: 2.2rem;
            }

            .hero-card {
                background: linear-gradient(120deg, rgba(8, 51, 68, 0.95), rgba(15, 118, 110, 0.92));
                border: 1px solid rgba(255, 255, 255, 0.18);
                border-radius: 20px;
                box-shadow: var(--shadow);
                padding: 1.4rem 1.5rem 1.2rem;
                color: #ffffff;
                margin-bottom: 1.1rem;
                animation: fadeSlide .45s ease-out;
            }

            .hero-title {
                font-weight: 800;
                letter-spacing: 0.3px;
                font-size: clamp(1.35rem, 2.5vw, 2rem);
                line-height: 1.2;
                margin-bottom: 0.28rem;
            }

            .hero-subtitle {
                color: rgba(236, 253, 245, 0.96) !important;
                font-size: 1rem;
                line-height: 1.35;
                margin: 0;
            }

            .glass-card {
                background: var(--surface);
                border: 1px solid rgba(8, 51, 68, 0.12);
                border-radius: 16px;
                box-shadow: var(--shadow);
                padding: 1rem 1rem 0.85rem;
                margin: 0.62rem 0;
                animation: fadeSlide .42s ease-out;
            }

            .glass-card h3 {
                color: var(--text-main);
                margin: 0 0 0.35rem 0;
                font-size: 1.08rem;
                font-weight: 700;
            }

            .glass-card p {
                margin: 0;
                color: var(--text-soft);
                font-size: 0.95rem;
                line-height: 1.45;
            }

            div[data-testid="stMetric"] {
                background: var(--surface-strong);
                border: 1px solid var(--border);
                border-radius: 14px;
                padding: 0.8rem 1rem;
                box-shadow: 0 8px 20px rgba(8, 51, 68, 0.08);
            }

            div[data-testid="stMetric"] label,
            div[data-testid="stMetric"] p,
            div[data-testid="stMetric"] span {
                color: var(--text-main) !important;
            }

            div[data-testid="stMetricLabel"] {
                color: var(--text-soft) !important;
                font-weight: 650 !important;
            }

            div[data-testid="stMetricValue"] {
                color: var(--text-main) !important;
                font-weight: 800 !important;
                line-height: 1.1 !important;
            }

            div[data-testid="stMetricDelta"] {
                color: var(--text-muted) !important;
            }

            .stTextInput > div > div > input,
            .stTextArea textarea,
            .stDateInput input,
            .stTimeInput input,
            .stNumberInput input,
            .stSelectbox [data-baseweb="select"] > div,
            [data-testid="stMultiSelect"] [data-baseweb="select"] > div {
                background: rgba(255, 255, 255, 0.97) !important;
                border: 1.4px solid var(--border-strong) !important;
                border-radius: 11px !important;
                color: var(--text-main) !important;
                min-height: 2.7rem;
                box-shadow: none !important;
            }

            .stTextInput > div > div > input:focus,
            .stTextArea textarea:focus,
            .stDateInput input:focus,
            .stTimeInput input:focus,
            .stNumberInput input:focus {
                border-color: var(--brand-accent) !important;
                box-shadow: var(--focus-ring) !important;
                outline: none !important;
            }

            .stTextInput > label,
            .stTextArea > label,
            .stDateInput > label,
            .stTimeInput > label,
            .stNumberInput > label,
            .stSelectbox > label,
            .stMultiSelect > label,
            .stFileUploader > label,
            .stCameraInput > label {
                color: var(--text-soft) !important;
                font-weight: 600 !important;
                font-size: 0.9rem !important;
                margin-bottom: 0.28rem !important;
            }

            .stSelectbox [data-baseweb="select"] > div:hover,
            [data-testid="stMultiSelect"] [data-baseweb="select"] > div:hover {
                border-color: var(--brand-accent) !important;
            }

            [data-baseweb="menu"] {
                background: #ffffff !important;
                border: 1px solid var(--border) !important;
                border-radius: 10px !important;
            }

            [data-baseweb="menu"] [role="option"] {
                color: var(--text-main) !important;
                background: #ffffff !important;
            }

            [data-baseweb="menu"] [role="option"][aria-selected="true"],
            [data-baseweb="menu"] [role="option"]:hover {
                background: rgba(20, 184, 166, 0.14) !important;
            }

            [data-testid="stFileUploadDropzone"] {
                background: rgba(255, 255, 255, 0.86) !important;
                border: 1.8px dashed var(--border-strong) !important;
                border-radius: 14px !important;
                color: var(--text-main) !important;
            }

            [data-testid="stFileUploadDropzone"]:hover {
                border-color: var(--brand-accent) !important;
                background: rgba(215, 247, 243, 0.42) !important;
            }

            [data-testid="stCameraInput"] {
                background: var(--surface-soft);
                border: 1px solid var(--border);
                border-radius: 14px;
                padding: 0.45rem;
            }

            .stButton > button {
                border: none;
                color: #ffffff;
                font-weight: 650;
                border-radius: 12px;
                padding: 0.52rem 1.05rem;
                background: linear-gradient(90deg, var(--brand-mid), var(--brand-accent));
                box-shadow: 0 8px 18px rgba(15, 118, 110, 0.28);
                transition: transform .15s ease, box-shadow .2s ease, filter .2s ease;
                font-family: 'Outfit', sans-serif;
            }

            .stButton > button:hover {
                transform: translateY(-1px);
                box-shadow: 0 12px 24px rgba(15, 118, 110, 0.34);
                filter: saturate(1.06);
            }

            .stButton > button:active {
                transform: translateY(0);
            }

            [data-testid="stDataFrame"],
            [data-testid="stDataEditor"] {
                border: 1px solid var(--border) !important;
                border-radius: 12px !important;
                overflow: hidden !important;
                box-shadow: 0 8px 20px rgba(8, 51, 68, 0.06);
            }

            [data-testid="stDataFrame"] [role="grid"],
            [data-testid="stDataEditor"] [role="grid"] {
                background: rgba(255, 255, 255, 0.98) !important;
                color: var(--text-main) !important;
            }

            [data-testid="stDataFrame"] [role="columnheader"],
            [data-testid="stDataEditor"] [role="columnheader"] {
                background: linear-gradient(90deg, rgba(15, 118, 110, 0.16), rgba(20, 184, 166, 0.1)) !important;
                color: var(--text-main) !important;
                font-weight: 700 !important;
                border-bottom: 1px solid var(--border) !important;
            }

            [data-testid="stDataFrame"] [role="gridcell"],
            [data-testid="stDataEditor"] [role="gridcell"] {
                color: var(--text-main) !important;
                background: rgba(255, 255, 255, 0.98) !important;
                border-color: rgba(15, 118, 110, 0.09) !important;
            }

            .stTabs [data-baseweb="tab-list"] {
                gap: 0.35rem;
                border-bottom: 1px solid var(--border) !important;
            }

            .stTabs [data-baseweb="tab"] {
                background: rgba(8, 51, 68, 0.06) !important;
                border-radius: 10px 10px 0 0 !important;
                color: var(--text-main) !important;
                font-weight: 620 !important;
                border: none !important;
                transition: all 0.25s ease;
            }

            .stTabs [data-baseweb="tab"]:hover {
                background: rgba(8, 51, 68, 0.12) !important;
            }

            .stTabs [aria-selected="true"] {
                background: linear-gradient(90deg, rgba(20, 184, 166, 0.25), rgba(20, 184, 166, 0.15)) !important;
                border-bottom: 3px solid var(--brand-accent) !important;
                color: var(--text-main) !important;
            }

            [data-testid="stForm"] {
                border: 1px solid var(--border) !important;
                border-radius: 16px !important;
                padding: 1.2rem !important;
                background: rgba(255, 255, 255, 0.55) !important;
                box-shadow: 0 8px 18px rgba(8, 51, 68, 0.06) !important;
            }

            h1, h2, h3, h4, h5, h6 {
                color: var(--text-main) !important;
                font-family: 'Outfit', sans-serif !important;
                line-height: 1.28 !important;
                letter-spacing: 0.1px;
                margin-top: 0.45rem !important;
                margin-bottom: 0.45rem !important;
            }

            [data-testid="stMarkdownContainer"] h1,
            [data-testid="stMarkdownContainer"] h2,
            [data-testid="stMarkdownContainer"] h3,
            [data-testid="stMarkdownContainer"] h4,
            [data-testid="stMarkdownContainer"] h5,
            [data-testid="stMarkdownContainer"] h6 {
                color: var(--text-main) !important;
            }

            p {
                color: var(--text-soft) !important;
                line-height: 1.5 !important;
            }

            [data-testid="stWidgetLabel"] p,
            [data-testid="stWidgetLabel"] span,
            [data-testid="stMarkdownContainer"] label,
            .stTextInput label,
            .stTextArea label,
            .stSelectbox label,
            .stMultiSelect label,
            .stDateInput label,
            .stTimeInput label {
                color: var(--text-soft) !important;
                font-weight: 600 !important;
                line-height: 1.28 !important;
            }

            [data-testid="stExpander"] {
                border: 1px solid var(--border) !important;
                border-radius: 12px !important;
                background: rgba(255, 255, 255, 0.6) !important;
                overflow: hidden;
            }

            [data-testid="stExpander"] button {
                color: var(--text-main) !important;
                font-weight: 600 !important;
            }

            [data-testid="stAlert"] {
                border-radius: 12px !important;
                border-width: 1px !important;
            }

            [data-testid="stNotificationContentSuccess"] {
                background: rgba(16, 185, 129, 0.08) !important;
            }

            [data-testid="stSpinner"] {
                color: var(--brand-accent) !important;
            }

            [data-testid="column"] {
                gap: 0.75rem;
            }

            [data-testid="stMarkdownContainer"] p {
                margin-top: 0.32rem;
                margin-bottom: 0.48rem;
            }

            [data-testid="stVerticalBlock"] {
                gap: 0.48rem;
            }

            @keyframes fadeSlide {
                from { opacity: 0; transform: translateY(8px); }
                to { opacity: 1; transform: translateY(0px); }
            }

            @media (max-width: 768px) {
                .block-container {
                    padding-top: 0.65rem;
                    padding-left: 0.9rem;
                    padding-right: 0.9rem;
                }

                .hero-card {
                    padding: 1.05rem 1rem;
                    border-radius: 16px;
                }

                .hero-title {
                    font-size: 1.42rem;
                }

                .glass-card {
                    border-radius: 14px;
                    padding: 0.9rem;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    hero_html = f"""
        <section class=\"hero-card\">
            <div class=\"hero-title\">{page_title}</div>
            {f'<p class=\"hero-subtitle\">{subtitle}</p>' if subtitle else ''}
        </section>
    """
    st.markdown(hero_html, unsafe_allow_html=True)


def glass_info_card(title: str, description: str) -> None:
    st.markdown(
        f"""
        <div class=\"glass-card\">
            <h3>{title}</h3>
            <p>{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
