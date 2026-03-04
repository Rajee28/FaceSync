<<<<<<< HEAD
import streamlit as st
import services
from datetime import datetime

st.set_page_config(page_title="Mark Attendance", page_icon="📝")

st.header("Mark Attendance")

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
=======
import streamlit as st
import services
from datetime import datetime

st.set_page_config(page_title="Mark Attendance", page_icon="📝")

st.header("Mark Attendance")

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
>>>>>>> f56354bff23c57e9dbb309990488effecb6c4ad5
