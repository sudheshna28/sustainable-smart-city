import streamlit as st
from PIL import Image
import io
import base64
import json
from datetime import datetime
import torch
from diffusers import StableDiffusionPipeline
import pandas as pd
import numpy as np
import altair as alt

# --- Page Config ---
st.set_page_config(page_title="Sustainable Smart City Assistant", layout="wide")

# --- Background Image Function ---
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
set_background("background..jpg")  # Ensure this file exists

# --- Session State Initialization ---
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'generated_images' not in st.session_state:
    st.session_state.generated_images = []

# --- Load Stable Diffusion Model ---
@st.cache_resource
def load_local_model():
    model_id = "CompVis/stable-diffusion-v1-4"
    pipe = StableDiffusionPipeline.from_pretrained(
        model_id,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
    )
    pipe = pipe.to("cuda" if torch.cuda.is_available() else "cpu")
    return pipe

pipe = load_local_model()

# --- Utility Functions ---
def generate_image_locally(prompt):
    with st.spinner("🔄 Generating image..."):
        image = pipe(prompt).images[0]
    return image

def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def add_to_chat_history(prompt, image):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {
        "timestamp": timestamp,
        "prompt": prompt,
        "image_base64": image_to_base64(image),
        "success": True
    }
    st.session_state.chat_history.append(entry)
    st.session_state.generated_images.append({
        "prompt": prompt,
        "image": image,
        "timestamp": timestamp
    })

def create_download_button(image, filename):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    st.download_button("📥 Download Image", buffered.getvalue(), file_name=filename, mime="image/png")

def export_chat_history():
    if st.session_state.chat_history:
        json_data = json.dumps(st.session_state.chat_history, indent=2)
        st.download_button("📄 Download Chat History", data=json_data, file_name="chat_history.json", mime="application/json")

# --- Sidebar Navigation ---
st.sidebar.title("🌐 Smart City Menu")
section = st.sidebar.radio("Navigate to", ["🏠 Home", "🎨 Image Generation", "📊 City Health Dashboard", "🏙️ City Comparison", "♻️ Recycle Management", "❓ Problems & Solutions"])

st.sidebar.markdown("---")
st.metric("Total Prompts", len(st.session_state.chat_history))
st.metric("Images Generated", len(st.session_state.generated_images))
export_chat_history()

if st.sidebar.button("🗑️ Clear History", key="clear_sidebar"):
    st.session_state.chat_history = []
    st.session_state.generated_images = []
    st.success("History cleared.")
    st.rerun()

# --- Main Content ---
if section == "🏠 Home":
    st.title("🏙️ Welcome to the Sustainable Smart City Assistant")
    st.write("""
        Use the menu on the left to explore features:
        - 🎨 Generate smart city images
        - 📊 View real-time city health dashboards
        - 🏙️ Compare performance of two cities
        - ♻️ Recycle management guidance
        - ❓ Ask problems and get possible solutions
    """)

elif section == "🎨 Image Generation":
    st.title("🎨 Text to Image Generator")
    st.markdown("Generate photorealistic **smart city concepts** using the local model **Stable Diffusion v1.4**.")

    user_prompt = st.text_area("📝 Describe your smart city image", height=100)

    if st.button("🎨 Generate Image", key="generate_button"):
        if user_prompt.strip():
            image = generate_image_locally(user_prompt.strip())
            add_to_chat_history(user_prompt.strip(), image)
            st.image(image, caption="Generated Image", use_container_width=True)
            create_download_button(image, f"smartcity_{datetime.now().strftime('%H%M%S')}.png")
        else:
            st.warning("⚠️ Please enter a description to generate an image.")

    if st.session_state.generated_images:
        st.header("🖼️ Recently Generated Images")
        for img_data in reversed(st.session_state.generated_images[-3:]):
            st.image(img_data['image'], caption=img_data['prompt'], use_container_width=True)
            st.caption(f"{img_data['timestamp']}")
            create_download_button(img_data['image'], f"recent_{img_data['timestamp'].replace(':','-')}.png")

    if st.session_state.chat_history:
        st.header("📜 Chat History")
        with st.expander("View Full Prompt and Image History"):
            for idx, entry in enumerate(reversed(st.session_state.chat_history)):
                st.markdown(f"**{entry['timestamp']}** - {entry['prompt']}")
                image = Image.open(io.BytesIO(base64.b64decode(entry['image_base64'])))
                st.image(image, use_container_width=True)
                create_download_button(image, f"history_{idx}.png")

elif section == "📊 City Health Dashboard":
    st.title("📊 City Health Dashboard – Kakinada")

    np.random.seed(42)
    days = pd.date_range(end=pd.Timestamp.today(), periods=7)
    data = {
        "Date": days,
        "Air Quality Index": np.random.randint(50, 150, size=7),
        "Water Usage (liters)": np.random.randint(100000, 200000, size=7),
        "Electricity Consumption (kWh)": np.random.randint(5000, 10000, size=7),
        "Waste Generated (tons)": np.random.uniform(20, 50, size=7).round(2)
    }
    df = pd.DataFrame(data)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Today's AQI", f"{df['Air Quality Index'].iloc[-1]}")
    col2.metric("Water Usage", f"{df['Water Usage (liters)'].iloc[-1]:,} L")
    col3.metric("Power Usage", f"{df['Electricity Consumption (kWh)'].iloc[-1]:,} kWh")
    col4.metric("Waste Collected", f"{df['Waste Generated (tons)'].iloc[-1]} tons")

    st.subheader("📈 Weekly Trends")
    chart = alt.Chart(df).transform_fold(
        ['Air Quality Index', 'Water Usage (liters)', 'Electricity Consumption (kWh)', 'Waste Generated (tons)']
    ).mark_line(point=True).encode(
        x='Date:T',
        y='value:Q',
        color='key:N'
    ).properties(width=800, height=400)

    st.altair_chart(chart, use_container_width=True)
    st.subheader("📋 Raw Data")
    st.dataframe(df)

elif section == "🏙️ City Comparison":
    st.title("🏙️ Compare Performance of Two Cities")
    cities = ["Kakinada", "Visakhapatnam", "Hyderabad", "Delhi", "Bangalore"]
    city1 = st.selectbox("Select First City", cities, key="city1")
    city2 = st.selectbox("Select Second City", cities, key="city2")

    if city1 == city2:
        st.warning("⚠️ Please choose two different cities to compare.")
    else:
        df_compare = pd.DataFrame({
            "Metrics": ["Air Quality Index", "Water Usage (liters)", "Electricity Consumption (kWh)", "Waste Generated (tons)"],
            city1: np.random.randint(50, 150, 4),
            city2: np.random.randint(50, 150, 4)
        })
        st.bar_chart(df_compare.set_index("Metrics"))

elif section == "♻️ Recycle Management":
    st.title("♻️ Recycle Management")
    st.markdown("Here are some sustainable recycling tips:")
    st.markdown("- ✅ Segregate wet and dry waste at the source")
    st.markdown("- ♻️ Use reusable bags, bottles, and containers")
    st.markdown("- 📦 Compost biodegradable kitchen waste")
    st.markdown("- 🚯 Avoid single-use plastic")
    st.markdown("- 🧠 Educate others about the importance of recycling")

elif section == "❓ Problems & Solutions":
    st.title("❓ Report Problems and Get Suggestions")
    problem = st.text_area("Describe an urban issue or smart city challenge:")
    if st.button("💡 Get Solutions"):
        if problem.strip():
            st.success("Here are some suggested solutions:")
            st.markdown("- Deploy smart sensors to monitor and report the issue")
            st.markdown("- Leverage citizen feedback platforms")
            st.markdown("- Use AI to predict and prevent recurrence")
            st.markdown("- Collaborate with NGOs or city councils")
        else:
            st.warning("⚠️ Please describe a problem to get solutions.")
