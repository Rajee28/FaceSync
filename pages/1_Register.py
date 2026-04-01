import streamlit as st
import face_utils
import numpy as np
import services
import ui

st.set_page_config(page_title="Register Staff", page_icon="👤")
ui.check_auth()
ui.apply_global_styles(
    "Register New Staff",
    "Create a clean staff profile with facial identity for reliable attendance automation.",
)
ui.theme_toggle()

tip1, tip2 = st.columns(2)
with tip1:
    ui.glass_info_card(
        "Photo Quality Tip",
        "Use clear front-facing lighting and keep only one person in the frame for best results.",
    )
with tip2:
    ui.glass_info_card(
        "Data Tip",
        "Keep staff IDs short and consistent, for example S001, S002, and so on.",
    )

with st.form("register_form"):
    col1, col2 = st.columns(2)
    with col1:
        staff_id = st.text_input("Staff ID (Unique)", placeholder="e.g., S001")
        name = st.text_input("Full Name")
        mobile = st.text_input("Mobile Number")
    with col2:
        email = st.text_input("Email")
        dept = st.selectbox(
            "Department",
            [
                "Computer Science",
                "Data Science",
                "Artificial Intelligence",
                "Computer Application",
                "Commerce",
                "Home Science",
                "English",
                "Tamil",
                "Maths",
                "Physics",
                "Chemistry",
            ],
        )
        role = st.text_input("Role/Designation")

    # Face Capture
    st.markdown("<h3 style='text-align: center;'>Facial Registration</h3>", unsafe_allow_html=True)
    
    _, col_cam, _ = st.columns([1, 2, 1])
    with col_cam:
        picture = st.camera_input("Capture Face using Webcam")
        uploaded_file = st.file_uploader("Or provide a high-quality photo", type=["jpg", "png", "jpeg"])
        
        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("Register New Staff", use_container_width=True)

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
