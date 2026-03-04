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
# load current staff data
staff_df = services.StaffService.get_all_staff()

# show editable table (face_encoding disabled) with dynamic rows.  Use whichever API is available.
editor_func = None
if hasattr(st, "data_editor"):
    editor_func = st.data_editor
elif hasattr(st, "experimental_data_editor"):
    editor_func = st.experimental_data_editor

if editor_func:
    edited_df = editor_func(
        staff_df,
        num_rows="dynamic",
        use_container_width=True,
        disabled=["face_encoding"],
        key="staff_editor",
    )
else:
    st.warning(
        "Your Streamlit version does not support an editable data editor. Upgrade to a newer release to enable inline editing."
    )
    edited_df = staff_df.copy()

# save changes button (only show when data editor exists)
if editor_func and st.button("Save Staff Changes"):
    # compare original and edited dataframes
    original = staff_df.fillna("")
    edited = edited_df.fillna("")

    orig_records = original.to_dict("records")
    new_records = edited.to_dict("records")

    orig_by_id = {r.get("staff_id"): r for r in orig_records if r.get("staff_id")}
    new_by_id = {r.get("staff_id"): r for r in new_records if r.get("staff_id")}

    added = [r for sid, r in new_by_id.items() if sid not in orig_by_id]
    removed = [r for sid, r in orig_by_id.items() if sid not in new_by_id]
    updated = []

    # check intersection for modifications (excluding face_encoding)
    for sid in set(orig_by_id.keys()) & set(new_by_id.keys()):
        orig_r = orig_by_id[sid].copy()
        new_r = new_by_id[sid].copy()
        # drop face_encoding since we don't edit it here
        orig_r.pop("face_encoding", None)
        new_r.pop("face_encoding", None)
        if orig_r != new_r:
            updated.append((orig_r, new_r))

    messages = []
    # perform removals
    for r in removed:
        sid = r.get("staff_id")
        success, msg = services.StaffService.delete_staff(sid)
        messages.append(f"Removed {sid}: {msg}")
    # perform additions
    for r in added:
        sid = r.get("staff_id")
        # ensure we have required fields
        name = r.get("name", "")
        mobile = r.get("mobile_number", "")
        email = r.get("email", "")
        dept = r.get("department", "")
        role = r.get("role", "")
        # face_encoding left blank
        success, msg = services.StaffService.register_staff(
            sid, name, mobile, email, dept, role, None
        )
        messages.append(f"Added {sid}: {msg}")
    # perform updates
    for orig_r, new_r in updated:
        sid = orig_r.get("staff_id")
        # if staff_id changed, treat as delete+add
        if orig_r.get("staff_id") != new_r.get("staff_id"):
            # delete old
            services.StaffService.delete_staff(orig_r.get("staff_id"))
            # add new
            success, msg = services.StaffService.register_staff(
                new_r.get("staff_id"),
                new_r.get("name", ""),
                new_r.get("mobile_number", ""),
                new_r.get("email", ""),
                new_r.get("department", ""),
                new_r.get("role", ""),
                None,
            )
            messages.append(
                f"Replaced {orig_r.get('staff_id')} with {new_r.get('staff_id')}: {msg}"
            )
        else:
            success, msg = services.StaffService.update_staff(
                sid,
                new_r.get("name", ""),
                new_r.get("mobile_number", ""),
                new_r.get("email", ""),
                new_r.get("department", ""),
                new_r.get("role", ""),
            )
            messages.append(f"Updated {sid}: {msg}")

    if messages:
        st.success("Staff table updated")
        for m in messages:
            st.write(m)
    else:
        st.info("No changes detected.")

    # refresh page to reload data
    st.experimental_rerun()

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
