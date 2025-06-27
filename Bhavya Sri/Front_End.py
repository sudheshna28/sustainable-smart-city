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
set_background("background..jpg")  # Ensure this file is in the same folder

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

# --- Chat Area Placeholder ---
st.write("")  # Just spacing for now

# --- Input Area ---
st.markdown("### ")

col1, col2, col3 = st.columns([1, 8, 1])

with col1:
    st.markdown("### ➕")

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
            st.success(f"Selected: {dropdown} | Question: {text}")

with col3:
    st.markdown("### 🎤")