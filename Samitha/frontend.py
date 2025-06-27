import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.express as px
import requests
from datetime import datetime
import base64

# ---------------- Background Image Setup ---------------- #
@st.cache_data
def get_base64_bg(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

bg_base64 = get_base64_bg("background.jpg")  # Ensure this file exists

st.set_page_config(
    page_title="Avenir - Reimagining Cities",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(f"""
<style>
    .main {{
        background-image: url("data:image/jpg;base64,{bg_base64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-blend-mode: darken;
    }}
    .stApp > header {{ background-color: transparent; }}
    .stSidebar > div:first-child {{
        background: linear-gradient(180deg, rgba(46,125,50,0.95), rgba(76,175,80,0.95));
        backdrop-filter: blur(10px);
    }}
    .chat-message, .metric-card {{
        background: rgba(0,0,0,0.8); color: white; border-radius: 10px;
        padding: 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.3); backdrop-filter: blur(10px);
    }}
    .user-message {{ background: rgba(76,175,80,0.9); margin-left: 50px; }}
    .bot-message {{ background: rgba(0,0,0,0.85); margin-right: 50px; }}
    .app-header {{
        text-align: center;
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
        margin-bottom: 20px;
    }}
    .tagline {{
        font-style: italic;
        font-size: 1.2em;
        color: #81C784;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
    }}
</style>
""", unsafe_allow_html=True)

# ---------------- FastAPI Configs ---------------- #
FASTAPI_CONFIGS = {
    "feature_1": "http://localhost:8001",   # Recycle DIY Ideas
    "feature_2": "http://localhost:8002",   # Village Comparator
    "feature_3": "http://localhost:8003",   # City Problem Solver
    "feature_4": "http://192.168.29.157:8004"  # Dream City Generator (Friend's IP)
}

# Human‑friendly names mapped to the keys above
FEATURE_LABELS = {
    "feature_1": "Recycle DIY Ideas ♻️",
    "feature_2": "Village Comparator 🏘️",
    "feature_3": "City Problem Solver 🏙️",
    "feature_4": "Dream City Generator 🏗️"
}

# Reverse mapping for convenience
LABEL_TO_KEY = {v: k for k, v in FEATURE_LABELS.items()}

# ---------------- Streamlit State ---------------- #
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_feature_label" not in st.session_state:
    st.session_state.selected_feature_label = "Dashboard"

# ---------------- Main App Header ---------------- #
st.markdown("""
<div class='app-header'>
    <h1>🏗️ Avenir</h1>
    <p class='tagline'>Reimagining Cities Through Innovation and Sustainability</p>
</div>
""", unsafe_allow_html=True)

# ---------------- Sidebar ---------------- #
with st.sidebar:
    st.markdown("<h1 style='color:white; text-align:center;'>🌿 Avenir Hub</h1>", unsafe_allow_html=True)

    feature_options = ["Dashboard"] + list(FEATURE_LABELS.values())
    selected_feature_label = st.selectbox(
        "Select Feature:",
        feature_options,
        index=feature_options.index(st.session_state.selected_feature_label)
    )
    st.session_state.selected_feature_label = selected_feature_label
    selected_feature_key = LABEL_TO_KEY.get(selected_feature_label, None)

    st.markdown("---")
    st.markdown("### 🔌 API Status", unsafe_allow_html=True)

    def check_api_status(url):
        try:
            response = requests.get(f"{url}/health", timeout=2)
            return "🟢 Online" if response.status_code == 200 else "🔴 Offline"
        except:  # noqa: E722
            return "🔴 Offline"

    for key, url in FASTAPI_CONFIGS.items():
        status = check_api_status(url)
        name = FEATURE_LABELS.get(key, key)
        st.markdown(f"**{name}**: {status}", unsafe_allow_html=True)

    st.markdown("---")
    temperature = st.slider("Response Temperature", 0.0, 1.0, 0.7)
    max_tokens = st.slider("Max Tokens", 50, 500, 150)

    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# ---------------- Dashboard ---------------- #
if st.session_state.selected_feature_label == "Dashboard":
    st.markdown("<h1 style='text-align:center; color:white;'>🌆 City Health Dashboard - Kakinada</h1>", unsafe_allow_html=True)

    # Simulated Data
    np.random.seed(42)
    days = pd.date_range(end=pd.Timestamp.today(), periods=7)
    city_df = pd.DataFrame({
        "Date": days,
        "Air Quality Index": np.random.randint(50, 150, size=7),
        "Water Usage (liters)": np.random.randint(100000, 200000, size=7),
        "Electricity Consumption (kWh)": np.random.randint(5000, 10000, size=7),
        "Waste Generated (tons)": np.random.uniform(20, 50, size=7).round(2)
    })

    # KPI Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Today's AQI", f"{city_df['Air Quality Index'].iloc[-1]}")
    col2.metric("Water Usage", f"{city_df['Water Usage (liters)'].iloc[-1]:,} L")
    col3.metric("Power Usage", f"{city_df['Electricity Consumption (kWh)'].iloc[-1]:,} kWh")
    col4.metric("Waste Collected", f"{city_df['Waste Generated (tons)'].iloc[-1]} tons")

    # Trend Chart
    st.subheader("📈 Trends Over the Past Week")
    alt_chart = alt.Chart(city_df).transform_fold(
        ['Air Quality Index', 'Water Usage (liters)', 'Electricity Consumption (kWh)', 'Waste Generated (tons)']
    ).mark_line(point=True).encode(
        x='Date:T',
        y='value:Q',
        color='key:N'
    ).properties(width=800, height=400)
    st.altair_chart(alt_chart, use_container_width=True)

    # Usage Data
    col5, col6 = st.columns(2)
    with col5:
        usage_data = pd.DataFrame({
            'Date': pd.date_range(start='2024-01-01', periods=7),
            'Queries': [45, 52, 48, 61, 55, 67, 58]
        })
        fig = px.line(usage_data, x='Date', y='Queries', title='📈 Daily Usage Trend')
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0.6)', font_color='white')
        st.plotly_chart(fig, use_container_width=True)

    with col6:
        feature_data = pd.DataFrame({
            'Feature': list(FEATURE_LABELS.values()),
            'Usage': [30, 25, 25, 20]
        })
        fig = px.pie(feature_data, values='Usage', names='Feature', title='🔧 Feature Usage Distribution')
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0.6)', font_color='white')
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("📋 Raw Data")
    st.dataframe(city_df)

    # Logs (example)
    st.markdown("<h2 style='color:white;'>🕒 Recent Activity</h2>", unsafe_allow_html=True)
    logs = [
        {"time": "2m", "user": "User123", "feature": "Recycle DIY Ideas ♻️", "query": "Ideas for glass bottle"},
        {"time": "5m", "user": "User456", "feature": "Village Comparator 🏘️", "query": "Compare XYZ vs ABC"},
        {"time": "8m", "user": "User789", "feature": "Dream City Generator 🏗️", "query": "Sustainable smart city with parks"},
    ]
    for log in logs:
        st.markdown(
            f"""<div class='chat-message'><b>{log['time']} ago</b> - {log['user']} used <b>{log['feature']}</b><br><em>\"{log['query']}\"</em></div>""",
            unsafe_allow_html=True
        )

# ---------------- Feature 1: Recycle DIY Ideas ---------------- #
elif selected_feature_key == "feature_1":
    st.markdown("<h1 style='text-align:center; color:white;'>♻️ Recycle DIY Idea Generator</h1>", unsafe_allow_html=True)
    api_url = FASTAPI_CONFIGS.get("feature_1")

    with st.form("recycle_form"):
        material = st.text_area("Enter recyclable material (e.g., plastic bottle, cardboard)")
        submitted = st.form_submit_button("Get DIY Ideas 💡")

    if submitted and material:
        try:
            with st.spinner("Generating DIY ideas..."):
                res = requests.post(
                    f"{api_url}/diy",
                    json={
                        "material": material,
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    },
                    timeout=20
                )
            if res.status_code == 200:
                ideas = res.json().get("ideas", "No ideas returned.")
                st.success("DIY ideas generated!")
                st.markdown(
                    f"""<div class='chat-message bot-message'><strong>DIY Ideas:</strong><br>{ideas}</div>""",
                    unsafe_allow_html=True
                )
            else:
                st.error(f"❌ Error {res.status_code}: {res.text}")
        except Exception as e:  # noqa: E722
            st.error(f"🔌 Failed to connect to Recycle DIY Ideas API.\n\n{str(e)}")

# ---------------- Feature 2: Village Comparator ---------------- #
elif selected_feature_key == "feature_2":
    st.markdown("<h1 style='text-align:center; color:white;'>🏘️ Village Sustainability Comparator</h1>", unsafe_allow_html=True)
    api_url = FASTAPI_CONFIGS.get("feature_2")

    with st.form("compare_form"):
        village1 = st.text_input("Enter First Village Name")
        village2 = st.text_input("Enter Second Village Name")
        submitted = st.form_submit_button("Compare 🆚")

    if submitted and village1 and village2:
        try:
            with st.spinner("Comparing villages..."):
                res = requests.post(f"{api_url}/compare", json={"village1": village1, "village2": village2})
            if res.status_code == 200:
                comparison = res.json().get("comparison")
                st.success("Comparison complete!")
                st.markdown(
                    f"""<div class='chat-message bot-message'><strong>Result:</strong><br>{comparison}</div>""",
                    unsafe_allow_html=True
                )
            else:
                st.error(f"❌ Error {res.status_code}: {res.text}")
        except Exception as e:  # noqa: E722
            st.error(f"🔌 Failed to connect to Village Comparator API.\n\n{str(e)}")

# ---------------- Feature 3: City Problem Solver ---------------- #
elif selected_feature_key == "feature_3":
    st.markdown("<h1 style='text-align:center; color:white;'>🏙️ City Problem Solver</h1>", unsafe_allow_html=True)
    api_url = FASTAPI_CONFIGS.get("feature_3")

    with st.form("problem_form"):
        problem_desc = st.text_area("Describe the Problem")
        submitted = st.form_submit_button("Get Solution 💡")

    if submitted and problem_desc:
        try:
            with st.spinner("Fetching solutions..."):
                res = requests.post(
                    f"{api_url}/solve",
                    json={
                        "problem": problem_desc,
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    },
                    timeout=20
                )
            if res.status_code == 200:
                solution = res.json().get("solution", "No solution returned.")
                st.success("Solution generated!")
                st.markdown(
                    f"""<div class='chat-message bot-message'><strong>Solution:</strong><br>{solution}</div>""",
                    unsafe_allow_html=True
                )
            else:
                st.error(f"❌ Error {res.status_code}: {res.text}")
        except Exception as e:  # noqa: E722
            st.error(f"🔌 Failed to connect to City Problem Solver API.\n\n{str(e)}")

# ---------------- Feature 4: Dream City Generator (Friend's API) ---------------- #
elif selected_feature_key == "feature_4":
    st.markdown("<h1 style='text-align:center; color:white;'>🏗️ Dream City Generator</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#81C784; font-style:italic;'>Powered by Innovation & Sustainability AI</p>", unsafe_allow_html=True)
    
    api_url = FASTAPI_CONFIGS.get("feature_4")

    # Show connection status specifically for friend's API
    st.info(f"🔗 Connecting to friend's API at: {api_url}")

    with st.form("dream_city_form"):
        st.markdown("### 🌟 Design Your Sustainable Future City")
        dream_desc = st.text_area(
            "Describe your dream city:",
            placeholder="e.g., 'A carbon-neutral city with vertical gardens, smart transportation, renewable energy, and community spaces that promote well-being'",
            height=120
        )
        
        col1, col2 = st.columns(2)
        with col1:
            city_size = st.selectbox("City Size:", ["Small Town", "Medium City", "Large Metropolis"])
        with col2:
            focus_area = st.selectbox("Focus Area:", ["Sustainability", "Technology", "Community", "Mixed"])
        
        submitted = st.form_submit_button("🌆 Generate Dream City Plan")

    if submitted and dream_desc:
        try:
            with st.spinner("🏗️ Designing your dream city with sustainable innovation..."):
                # Enhanced payload for the friend's API
                payload = {
                    "description": dream_desc,
                    "city_size": city_size,
                    "focus_area": focus_area,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "app_name": "Avenir",
                    "theme": "sustainability_innovation"
                }
                
                res = requests.post(
                    f"{api_url}/dream",
                    json=payload,
                    timeout=30  # Increased timeout for complex generation
                )
                
            if res.status_code == 200:
                response_data = res.json()
                dream_output = response_data.get("city_plan", "No plan returned.")
                
                st.success("🎉 Your dream city plan has been generated!")
                
                # Enhanced display with sections
                st.markdown("### 🏗️ Your Sustainable City Vision")
                st.markdown(
                    f"""<div class='chat-message bot-message'>
                    <strong>🌟 City Plan for "{city_size}" with "{focus_area}" Focus:</strong><br><br>
                    {dream_output}
                    </div>""",
                    unsafe_allow_html=True
                )
                
                # Add some additional context
                st.markdown("---")
                st.markdown("### 💡 Next Steps")
                st.info("Your city plan incorporates cutting-edge sustainability principles and innovative urban design. Consider sharing this vision with urban planners and community leaders!")
                
            else:
                st.error(f"❌ API Error {res.status_code}: {res.text}")
                st.warning("💡 Make sure your friend's Dream City Generator API is running and accessible.")
                
        except requests.exceptions.Timeout:
            st.error("⏱️ Request timed out. The Dream City Generator might be processing complex requests.")
        except requests.exceptions.ConnectionError:
            st.error(f"🔌 Failed to connect to Dream City Generator API at {api_url}")
            st.warning("Please verify that your friend's API is running and the IP address is correct.")
        except Exception as e:
            st.error(f"🔧 Unexpected error: {str(e)}")

# ---------------- Fallback Chat for unsupported selections ---------------- #
else:
    # Generic chat fallback for any unimplemented feature key
    api_url = FASTAPI_CONFIGS.get(selected_feature_key)
    st.markdown(
        f"<h1 style='text-align:center; color:white;'>🤖 {st.session_state.selected_feature_label} Chat</h1>",
        unsafe_allow_html=True
    )

    for msg in st.session_state.messages:
        css_class = "user-message" if msg["role"] == "user" else "bot-message"
        st.markdown(
            f"""<div class='chat-message {css_class}'><strong>{msg['role'].capitalize()}:</strong><br>{msg['content']}</div>""",
            unsafe_allow_html=True
        )

    with st.form("fallback_chat_form", clear_on_submit=True):
        user_input = st.text_area("Ask something...")
        submitted = st.form_submit_button("Send 🚀")

    if submitted and user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        try:
            with st.spinner("Getting response..."):
                res = requests.post(
                    f"{api_url}/chat",
                    json={
                        "query": user_input,
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    },
                    timeout=20
                )
            if res.status_code == 200:
                bot_reply = res.json().get("response", "No response.")
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                st.rerun()
            else:
                st.error(f"❌ Error {res.status_code}: {res.text}")
        except Exception as e:
            st.error(f"🔌 Failed to connect to {st.session_state.selected_feature_label} API.\n\n{str(e)}")