<<<<<<< HEAD
import streamlit as st
import services
from datetime import datetime

st.set_page_config(page_title="Attendance Reports", page_icon="📊")

st.header("Attendance Reports")

tab1, tab2 = st.tabs(["Daily Attendance", "Staff History"])

with tab1:
    st.subheader("Daily Attendance Log")
    date_sel = st.date_input("Select Date", datetime.now())

    df = services.AttendanceService.get_daily_attendance(date_sel)

    if not df.empty:
        st.dataframe(df)

        # Stats
        present_count = df[df["status"].str.contains("Present")].shape[0]
        st.info(f"Total Present: {present_count}")
    else:
        st.warning("No records found for this date.")

with tab2:
    st.subheader("Individual Staff History")

    # Get staff list
    staff_df = services.StaffService.get_all_staff()
    if not staff_df.empty:
        staff_list = staff_df["staff_id"].astype(str) + " - " + staff_df["name"]
        selected_staff = st.selectbox("Select Staff", staff_list)

        if selected_staff:
            staff_id = selected_staff.split(" - ")[0]

            # Fetch History
            hist_df = services.AttendanceService.get_staff_history(staff_id)

            st.dataframe(hist_df)

            # Fetch Counters
            month_str = datetime.now().strftime("%Y-%m")
            counts = services.AttendanceService.get_staff_counters(staff_id, month_str)

            if counts:
                c1, c2, c3 = st.columns(3)
                c1.metric("Grace Used", f"{counts[0]}/5")
                c2.metric("Late Used", f"{counts[1]}/2")
                c3.metric("Permissions Used", f"{counts[2]}/2")
            else:
                st.info("No counters initialized for this month.")
=======
import streamlit as st
import services
from datetime import datetime

st.set_page_config(page_title="Attendance Reports", page_icon="📊")

st.header("Attendance Reports")

tab1, tab2 = st.tabs(["Daily Attendance", "Staff History"])

with tab1:
    st.subheader("Daily Attendance Log")
    date_sel = st.date_input("Select Date", datetime.now())

    df = services.AttendanceService.get_daily_attendance(date_sel)

    if not df.empty:
        st.dataframe(df)

        # Stats
        present_count = df[df["status"].str.contains("Present")].shape[0]
        st.info(f"Total Present: {present_count}")
    else:
        st.warning("No records found for this date.")

with tab2:
    st.subheader("Individual Staff History")

    # Get staff list
    staff_df = services.StaffService.get_all_staff()
    if not staff_df.empty:
        staff_list = staff_df["staff_id"].astype(str) + " - " + staff_df["name"]
        selected_staff = st.selectbox("Select Staff", staff_list)

        if selected_staff:
            staff_id = selected_staff.split(" - ")[0]

            # Fetch History
            hist_df = services.AttendanceService.get_staff_history(staff_id)

            st.dataframe(hist_df)

            # Fetch Counters
            month_str = datetime.now().strftime("%Y-%m")
            counts = services.AttendanceService.get_staff_counters(staff_id, month_str)

            if counts:
                c1, c2, c3 = st.columns(3)
                c1.metric("Grace Used", f"{counts[0]}/5")
                c2.metric("Late Used", f"{counts[1]}/2")
                c3.metric("Permissions Used", f"{counts[2]}/2")
            else:
                st.info("No counters initialized for this month.")
>>>>>>> f56354bff23c57e9dbb309990488effecb6c4ad5
