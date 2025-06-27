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
    page_title="AI Assistant Hub",
    page_icon="🌿",
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
</style>
""", unsafe_allow_html=True)

# ---------------- FastAPI Configs ---------------- #
FASTAPI_CONFIGS = {
    "feature_1": "http://localhost:8001",
    "feature_2": "http://localhost:8002",
    "feature_3": "http://localhost:8003",  # Now used for City Problem Solver
    "feature_4": "http://your-friends-domain.com"  # Optional placeholder
}

# ---------------- Streamlit State ---------------- #
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_feature" not in st.session_state:
    st.session_state.selected_feature = "Dashboard"

# ---------------- Sidebar ---------------- #
with st.sidebar:
    st.markdown("<h1 style='color:white; text-align:center;'>🌿 AI Hub</h1>", unsafe_allow_html=True)
    feature_options = ["Dashboard"] + [f.replace('_', ' ').title() for f in FASTAPI_CONFIGS.keys()]
    selected_feature = st.selectbox("Select Feature:", feature_options, index=feature_options.index(st.session_state.selected_feature))
    st.session_state.selected_feature = selected_feature

    st.markdown("---")
    st.markdown("### 🔌 API Status", unsafe_allow_html=True)

    def check_api_status(url):
        try:
            response = requests.get(f"{url}/health", timeout=2)
            return "🟢 Online" if response.status_code == 200 else "🔴 Offline"
        except:
            return "🔴 Offline"

    for name, url in FASTAPI_CONFIGS.items():
        status = check_api_status(url)
        st.markdown(f"**{name.replace('_',' ').title()}**: {status}", unsafe_allow_html=True)

    st.markdown("---")
    temperature = st.slider("Response Temperature", 0.0, 1.0, 0.7)
    max_tokens = st.slider("Max Tokens", 50, 500, 150)

    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# ---------------- Dashboard ---------------- #
if st.session_state.selected_feature == "Dashboard":
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
            'Feature': [f.replace("_", " ").title() for f in FASTAPI_CONFIGS.keys()],
            'Usage': [30, 25, 25, 20]
        })
        fig = px.pie(feature_data, values='Usage', names='Feature', title='🔧 Feature Usage Distribution')
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0.6)', font_color='white')
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("📋 Raw Data")
    st.dataframe(city_df)

    # Logs
    st.markdown("<h2 style='color:white;'>🕒 Recent Activity</h2>", unsafe_allow_html=True)
    logs = [
        {"time": "2m", "user": "User123", "feature": "Feature 1", "query": "Summarize"},
        {"time": "5m", "user": "User456", "feature": "Feature 2", "query": "Compare villages"},
    ]
    for log in logs:
        st.markdown(f"""<div class='chat-message'><b>{log['time']} ago</b> - {log['user']} used <b>{log['feature']}</b><br><em>\"{log['query']}\"</em></div>""", unsafe_allow_html=True)

# ---------------- Feature 2: Village Comparator ---------------- #
elif st.session_state.selected_feature == "Feature 2":
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
                st.markdown(f"""<div class='chat-message bot-message'><strong>Result:</strong><br>{comparison}</div>""", unsafe_allow_html=True)
            else:
                st.error(f"❌ Error {res.status_code}: {res.text}")
        except Exception as e:
            st.error(f"🔌 Failed to connect to Feature 2: {str(e)}")

# ---------------- Feature 3: City Problem Solver ---------------- #
elif st.session_state.selected_feature == "Feature 3":
    st.markdown("<h1 style='text-align:center; color:white;'>🏙️ City Problem Solver</h1>", unsafe_allow_html=True)
    api_url = FASTAPI_CONFIGS.get("feature_3")

    with st.form("problem_form"):
        problem_desc = st.text_area("Describe the Problem")
        submitted = st.form_submit_button("Get Solution 💡")

    if submitted and problem_desc:
        try:
            with st.spinner("Fetching solutions..."):
                res = requests.post(f"{api_url}/solve", json={
                    "problem": problem_desc,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }, timeout=20)
            if res.status_code == 200:
                solution = res.json().get("solution", "No solution returned.")
                st.success("Solution generated!")
                st.markdown(f"""<div class='chat-message bot-message'><strong>Solution:</strong><br>{solution}</div>""", unsafe_allow_html=True)
            else:
                st.error(f"❌ Error {res.status_code}: {res.text}")
        except Exception as e:
            st.error(f"🔌 Failed to connect to Feature 3: {str(e)}")

# ---------------- Fallback Chat Features ---------------- #
else:
    feature_key = st.session_state.selected_feature.lower().replace(" ", "_")
    api_url = FASTAPI_CONFIGS.get(feature_key)

    st.markdown(f"<h1 style='text-align:center; color:white;'>🤖 {st.session_state.selected_feature} Chat</h1>", unsafe_allow_html=True)
    for msg in st.session_state.messages:
        css_class = "user-message" if msg["role"] == "user" else "bot-message"
        sender = "You" if msg["role"] == "user" else f"🤖 {st.session_state.selected_feature}"
        st.markdown(f"""<div class='chat-message {css_class}'><strong>{sender}:</strong><br>{msg['content']}</div>""", unsafe_allow_html=True)

    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([6, 1])
        with col1:
            user_input = st.text_input("Type your message...")
        with col2:
            send = st.form_submit_button("Send 🚀")

        if send and user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            payload = {
                "message": user_input,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "timestamp": datetime.now().isoformat()
            }
            try:
                with st.spinner("Processing..."):
                    res = requests.post(f"{api_url}/chat", json=payload, timeout=20)
                if res.status_code == 200:
                    reply = res.json().get("response", "No response")
                else:
                    reply = f"❌ Error {res.status_code}: {res.text}"
            except Exception as e:
                reply = f"🔌 Connection error to {st.session_state.selected_feature}.\n\n{str(e)}"
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.rerun()

# ---------------- Footer ---------------- #
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("""
<div class='chat-message' style='text-align:center; margin-top:20px;'>
    <strong>🌿 AI Assistant Hub - Powered by Streamlit & FastAPI</strong><br>
    <em>Multi-feature, multi-endpoint AI integration</em>
</div>
""", unsafe_allow_html=True)
