import streamlit as st
from PIL import Image
import base64

# --- Background Image ---
def set_background(image_file):
    with open(image_file, "rb") as image:
        encoded = base64.b64encode(image.read()).decode()
    bg_css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{encoded}");
        background-size: cover;
        background-position: center;
    }}
    </style>
    """
    st.markdown(bg_css, unsafe_allow_html=True)

# Set background
set_background("background.jpg")  # ✅ Ensure the correct file name

# --- Sidebar ---
st.sidebar.markdown("## 📊 Dashboard")
st.sidebar.markdown("## 💬 New Chat")
st.sidebar.markdown("## 🔍 Search Chat")
st.sidebar.markdown("## 🕓 History")

# --- Header ---
st.markdown("""
    <div style="text-align: center;">
        <img src="https://img.icons8.com/ios-filled/50/228B22/plant-under-sun.png" width="40"/>
        <h1 style="display: inline-block; color: #145A32; font-weight: 800;">🌿 Sustainable Smart City</h1>
    </div>
""", unsafe_allow_html=True)

# --- Input Area ---
st.markdown("")

col1, col2, col3 = st.columns([1, 8, 1])

# ---- ➕ PLUS ICON with camera/upload menu ----
with col1:
    if st.button("➕", help="Click to add image or take photo"):
        st.session_state.show_options = not st.session_state.get("show_options", False)
if st.session_state.get("show_options", False):
    col1a, col1b = st.columns([1, 3])
    with col1b:
        st.markdown("**Select an image option:**")
        image_choice = st.radio("", ["📸 Take Photo", "🖼️ Upload Image"], label_visibility="collapsed")
        if image_choice == "📸 Take Photo":
            camera_image = st.camera_input("Capture Image")
            if camera_image:
                st.image(camera_image, caption="📷 Captured Photo", use_column_width=True)
        elif image_choice == "🖼️ Upload Image":
            upload_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
            if upload_image:
                st.image(upload_image, caption="🖼️ Uploaded Image", use_column_width=True)

# ---- Chat Input and Dropdown ----
with col2:
    with st.form("chat_form", clear_on_submit=True):
        dropdown = st.selectbox("Choose topic", [
            "Recycle Management",
            "Image Generation",
            "Common Between Two Cities",
            "Problems and Solutions"
        ])
        text = st.text_input("", placeholder="Ask about sustainability")
        submitted = st.form_submit_button("Submit")
        if submitted:
            st.success(f"✅ Topic: {dropdown} | Message: {text}")

# ---- Mic Placeholder ----
with col3:
    st.markdown("### 🎤")
