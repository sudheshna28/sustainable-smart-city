# --- FIXED VERSION OF STREAMLIT APP INCLUDING FEATURE 2 VILLAGE COMPARISON ---

import streamlit as st
import requests
from datetime import datetime
import pandas as pd
import plotly.express as px
import base64

# ---------------- Background Image Setup ---------------- #
@st.cache_data
def get_base64_bg(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

bg_base64 = get_base64_bg("background.jpg")

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
        background-color: rgba(0, 0, 0, 0.3);
        background-blend-mode: darken;
    }}
    .stApp > header {{ background-color: transparent; }}
    .stSidebar > div:first-child {{
        background: linear-gradient(180deg, rgba(46,125,50,0.95), rgba(76,175,80,0.95), rgba(129,199,132,0.95));
        backdrop-filter: blur(10px);
    }}
    .chat-message, .metric-card {{
        background: rgba(0,0,0,0.8); color: white; border-radius: 10px;
        padding: 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.3); backdrop-filter: blur(10px);
    }}
    .user-message {{ background: rgba(76,175,80,0.9); margin-left: 50px; }}
    .bot-message {{ background: rgba(0,0,0,0.85); margin-right: 50px; }}
    .stTextInput input {{
        background: rgba(0,0,0,0.8); color: white; border: 2px solid #4caf50;
    }}
    .stButton > button {{
        background: linear-gradient(135deg,#4caf50,#81c784); color: white;
        font-weight: bold; border: none; box-shadow: 0 4px 8px rgba(0,0,0,0.3);
    }}
</style>
""", unsafe_allow_html=True)

# ---------------- FastAPI Backends ---------------- #
FASTAPI_CONFIGS = {
    "feature_1": "http://localhost:8001",
    "feature_2": "http://localhost:8002",
    "feature_3": "http://localhost:8003",
    "feature_4": "http://your-friends-domain.com"
}

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
    st.markdown("<h1 style='text-align:center; color:white;'>🌿 AI Assistant Dashboard</h1>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""<div class='metric-card'><h3>📊 Total Queries</h3><h2>1,247</h2><p style='color:#4caf50;'>↗️ +12%</p></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class='metric-card'><h3>⚡ Active Features</h3><h2>{len(FASTAPI_CONFIGS)}</h2><p style='color:#4caf50;'>All Online</p></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""<div class='metric-card'><h3>⏱️ Avg Response</h3><h2>1.2s</h2><p style='color:#4caf50;'>↗️ Improved</p></div>""", unsafe_allow_html=True)
    with col4:
        st.markdown("""<div class='metric-card'><h3>👥 Active Users</h3><h2>89</h2><p style='color:#4caf50;'>↗️ +5</p></div>""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        usage_data = pd.DataFrame({
            'Date': pd.date_range(start='2024-01-01', periods=7),
            'Queries': [45, 52, 48, 61, 55, 67, 58]
        })
        fig = px.line(usage_data, x='Date', y='Queries', title='📈 Daily Usage Trend')
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0.6)', font_color='white')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        feature_data = pd.DataFrame({
            'Feature': [f.replace("_", " ").title() for f in FASTAPI_CONFIGS.keys()],
            'Usage': [30, 25, 25, 20]
        })
        fig = px.pie(feature_data, values='Usage', names='Feature', title='🔧 Feature Usage Distribution')
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0.6)', font_color='white')
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<h2 style='color:white;'>📋 Recent Activity</h2>", unsafe_allow_html=True)
    logs = [
        {"time": "2m", "user": "User123", "feature": "Feature 1", "query": "Summarize"},
        {"time": "5m", "user": "User456", "feature": "Feature 2", "query": "Compare villages"},
    ]
    for act in logs:
        st.markdown(f"""<div class='chat-message'><b>{act['time']} ago</b> - {act['user']} used <b>{act['feature']}</b><br><em>"{act['query']}"</em></div>""", unsafe_allow_html=True)

# ---------------- Feature 2: Village Comparison ---------------- #
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

# ---------------- Other Features Use Chat ---------------- #
else:
    feature_key = st.session_state.selected_feature.lower().replace(" ", "_")
    api_url = FASTAPI_CONFIGS.get(feature_key)
    st.markdown(f"<h1 style='text-align:center; color:white;'>🤖 {st.session_state.selected_feature} Chat</h1>", unsafe_allow_html=True)

    with st.container():
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
