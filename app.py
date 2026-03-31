import streamlit as st
import database
import alerts
import config
import ui
from datetime import datetime

st.set_page_config(page_title="FaceSync", page_icon="📍", layout="wide")
ui.apply_global_styles(
    "FaceSync: Smart Staff Attendance Tracker",
    "Modern attendance monitoring with face recognition, faster workflows, and cleaner insights.",
)

# Initialize DB on first load (safe to call multiple times)
if "db_initialized" not in st.session_state:
    try:
        database.init_db()
        st.session_state["db_initialized"] = True
    except Exception as e:
        st.error(f"Database Initialization Failed: {e}")


# Start background scheduler (ensures it runs only once per server instance)
@st.cache_resource
def start_scheduler_service():
    try:
        alerts.start_background_scheduler()
        return True
    except Exception as e:
        print(f"Failed to start scheduler: {e}")
        return False


start_scheduler_service()

st.sidebar.markdown(
    """
    <h2 style="color:#f8d27a; margin-bottom: 0.25rem;">Navigation</h2>
    """,
    unsafe_allow_html=True,
)
st.sidebar.info("Choose a page from the menu above.")

c1, c2, c3 = st.columns(3)
with c1:
    ui.glass_info_card(
        "Register Staff",
        "Capture staff details and face profile once, then use fast recognition for daily attendance.",
    )
with c2:
    ui.glass_info_card(
        "Mark Attendance",
        "Use camera-based recognition for quick punch in/out with automatic status classification.",
    )
with c3:
    ui.glass_info_card(
        "Reports & Admin",
        "Review logs, track usage counters, and manage staff records from a single panel.",
    )

# Show some quick stats if DB is ready
try:
    conn = database.get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM staff")
    staff_count = c.fetchone()[0]

    today = datetime.now().date()
    c.execute(
        "SELECT COUNT(DISTINCT staff_id) FROM attendance WHERE punch_date = ?",
        (today,),
    )
    present_count = c.fetchone()[0]
    absent_count = max(staff_count - present_count, 0)

    st.markdown("### Live Snapshot")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Staff", staff_count)
    with col2:
        st.metric("Present Today", present_count)
    with col3:
        st.metric("Absent Today", absent_count)
    conn.close()
except Exception as e:
    st.warning("Database not ready yet.")
