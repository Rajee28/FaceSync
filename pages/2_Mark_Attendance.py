import streamlit as st
import services
from datetime import datetime
import ui

st.set_page_config(page_title="Mark Attendance", page_icon="📝")
ui.apply_global_styles(
    "Mark Attendance",
    "Fast facial check-in and check-out with real-time recognition status.",
)

ui.glass_info_card(
    "How to Use",
    "Look straight at the camera, keep your face centered, and wait for identification confirmation.",
)

# Camera Input
picture = st.camera_input("Look at the camera to punch in/out")

if picture:
    with st.spinner("Recognizing..."):
        # Recognize face
        result, error = services.FaceRecognitionService.recognize_face(picture)

        if error:
            st.error(error)
        else:
            staff_id, name = result
            st.success(f"Identified: **{name}** ({staff_id})")

            # Process Attendance
            now = datetime.now()
            current_date = now.date()
            current_time = now.time()

            success, message = services.AttendanceService.mark_attendance(
                staff_id, name, current_date, current_time
            )
            if success:
                st.balloons()
                st.success(message)
            else:
                st.info(message)
