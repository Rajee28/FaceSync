import streamlit as st
import database
import alerts
import config
from datetime import datetime

st.set_page_config(page_title="FaceSync", page_icon="📍", layout="wide")

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

st.title("FaceSync: Smart Staff Attendance Tracker")

st.sidebar.title("Navigation")
st.sidebar.info("Select a page from the usage menu above.")

st.markdown(
    """
### Welcome using Face Recognition Attendance System
This system allows you to:
- **Register Staff**: Capture face and details.
- **Mark Attendance**: Punch In/Out using Face Recognition.
- **View Reports**: Analyze attendance data.
- **Admin**: Manage staff and settings.

**Deployment**: Zero-cost on Streamlit Community Cloud.
"""
)

# Show some quick stats if DB is ready
try:
    conn = database.get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM staff")
    staff_count = c.fetchone()[0]

    today = datetime.now().date()
    c.execute("SELECT COUNT(*) FROM attendance WHERE punch_date = ?", (today,))
    attendance_count = c.fetchone()[0]

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Staff", staff_count)
    with col2:
        st.metric("Present Today", attendance_count)
    conn.close()
except Exception as e:
    st.warning("Database not ready yet.")
