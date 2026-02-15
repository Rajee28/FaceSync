import streamlit as st
import services
import alerts
import config

st.set_page_config(page_title="Admin Panel", page_icon="⚙️")

# Simple Password Protection (Hardcoded for demo, use env vars in prod)
if "admin_logged_in" not in st.session_state:
    st.session_state["admin_logged_in"] = False

if not st.session_state["admin_logged_in"]:
    pwd = st.text_input("Enter Admin Password", type="password")
    if st.button("Login"):
        if pwd == config.ADMIN_PASSWORD:
            st.session_state["admin_logged_in"] = True
            st.rerun()
        else:
            st.error("Invalid Password")
    st.stop()

st.header("Admin Panel")

st.subheader("Manage Staff")
staff_df = services.StaffService.get_all_staff()
st.dataframe(staff_df)

if st.button("Refresh Data"):
    st.rerun()

st.subheader("Force Update Attendance (Correction)")
with st.expander("Update Attendance Record"):
    with st.form("manual_update"):
        u_staff_id = st.text_input("Staff ID")
        u_date = st.date_input("Date")
        u_in_time = st.time_input("In Time")
        u_status = st.selectbox(
            "Status",
            [
                "Present",
                "Absent",
                "Late",
                "Permission",
                "Half Day Leave - Forenoon",
                "Half Day Leave - Afternoon",
            ],
        )

        submit_upd = st.form_submit_button("Update Record")

        if submit_upd and u_staff_id:
            success, message = services.AttendanceService.update_attendance_record(
                u_staff_id, u_date, u_in_time, u_status
            )
            if success:
                st.success(message)
            else:
                st.warning(message)

st.subheader("Send Custom Alerts")
with st.expander("Send Alert to Staff"):
    with st.form("alert_form"):
        alert_subject = st.text_input("Alert Subject", value="Important Notice")
        alert_message = st.text_area(
            "Alert Message", height=100, placeholder="Enter your message here..."
        )

        # Get staff list for selection
        staff_list = services.StaffService.get_all_staff()
        selected_staff = st.multiselect(
            "Select Staff to Alert",
            options=staff_list["staff_id"].tolist(),
            format_func=lambda x: f"{x} - {staff_list[staff_list['staff_id']==x]['name'].iloc[0]}",
        )

        send_alert_btn = st.form_submit_button("Send Alert")

        if send_alert_btn:
            if not alert_message.strip():
                st.error("Please enter a message for the alert.")
            elif not selected_staff:
                st.error("Please select at least one staff member.")
            else:
                with st.spinner("Sending alerts..."):
                    try:
                        result = alerts.send_custom_alert(
                            staff_ids=selected_staff,
                            message=alert_message,
                            subject=alert_subject,
                        )

                        if result.get("success", False):
                            st.success("Alerts sent successfully!")

                            # Show details
                            with st.expander("Alert Details"):
                                st.json(result)
                        else:
                            st.error("Failed to send alerts. Check configuration.")
                            st.json(result)

                    except Exception as e:
                        st.error(f"Error sending alerts: {str(e)}")

st.subheader("Alert Configuration Test")
with st.expander("Test Alert Setup"):
    if st.button("Test Alert Configuration"):
        with st.spinner("Testing configuration..."):
            try:
                test_result = alerts.test_alert_configuration()

                st.subheader("Test Results:")

                for platform, result in test_result.items():
                    if platform == "timestamp":
                        continue
                    status = (
                        "✅ Configured"
                        if result.get("success")
                        else "❌ Not Configured"
                    )
                    st.write(f"**{platform.upper()}:** {status}")
                    if result.get("message"):
                        st.write(f"   {result['message']}")

                st.info(
                    "Note: Test messages are sent to the admin email and phone number (if configured)."
                )

            except Exception as e:
                st.error(f"Error testing configuration: {str(e)}")
