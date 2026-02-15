import streamlit as st
import face_utils
import numpy as np
import services

st.set_page_config(page_title="Register Staff", page_icon="👤")

st.header("Register New Staff")

with st.form("register_form"):
    col1, col2 = st.columns(2)
    with col1:
        staff_id = st.text_input("Staff ID (Unique)", placeholder="e.g., S001")
        name = st.text_input("Full Name")
        mobile = st.text_input("Mobile Number")
    with col2:
        email = st.text_input("Email")
        dept = st.selectbox(
            "Department", ["IT", "HR", "Sales", "Operations", "Management"]
        )
        role = st.text_input("Role/Designation")

    # Face Capture
    st.subheader("Face Registration")
    picture = st.camera_input("Take a picture")
    uploaded_file = st.file_uploader("Or upload an image", type=["jpg", "png", "jpeg"])

    submitted = st.form_submit_button("Register Staff")

if submitted:
    if not (staff_id and name):
        st.error("Staff ID and Name are required!")
    else:
        # Process Image
        image_data = None
        if picture:
            image_data = picture
        elif uploaded_file:
            image_data = uploaded_file

        if image_data:
            with st.spinner("Processing Face..."):
                try:
                    # Convert to numpy array
                    img = face_utils.load_image_file(image_data)
                    encodings = face_utils.get_face_encodings(img)

                    if len(encodings) == 0:
                        st.error(
                            "No face detected! Please try again with a clear photo."
                        )
                    elif len(encodings) > 1:
                        st.error(
                            "Multiple faces detected! Please ensure only the staff member is in frame."
                        )
                    else:
                        encoding = encodings[0]

                        # Register staff
                        success, message = services.StaffService.register_staff(
                            staff_id, name, mobile, email, dept, role, encoding
                        )
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
                except Exception as e:
                    st.error(f"Error processing image: {e}")
        else:
            st.error("Please provide a photo for facial recognition setup.")
