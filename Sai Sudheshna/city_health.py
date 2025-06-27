# ✅ Updated Streamlit Dashboard with Feature 3 Integration and City Health Dashboard
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

# Uncomment the line below if you have a background image
# bg_base64 = get_base64_bg("background.jpg")  # Make sure this image exists

st.set_page_config(
    page_title="AI Assistant Hub",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Updated CSS with conditional background image
st.markdown(f"""
<style>
    .main {{
        background: linear-gradient(135deg, #1e3c72, #2a5298);
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
    .stTextInput input {{
        background: rgba(0,0,0,0.8); color: white; border: 2px solid #4caf50;
    }}
    .stButton > button {{
        background: linear-gradient(135deg,#4caf50,#81c784); color: white;
        font-weight: bold; border: none; box-shadow: 0 4px 8px rgba(0,0,0,0.3);
    }}
    .dashboard-metric {{
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        color: white;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        backdrop-filter: blur(10px);
    }}
    .dashboard-title {{
        color: white;
        text-align: center;
        margin-bottom: 30px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }}
</style>
""", unsafe_allow_html=True)

# ---------------- FastAPI Configs ---------------- #
FASTAPI_CONFIGS = {
    "feature_1": "http://localhost:8001",
    "feature_2": "http://localhost:8002",
    "feature_3": "http://localhost:8003",
    "feature_4": "http://your-friends-domain.com"
}

# ---------------- Streamlit State ---------------- #
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_feature" not in st.session_state:
    st.session_state.selected_feature = "Dashboard"

# ---------------- Dashboard Data Generation ---------------- #
@st.cache_data
def generate_dashboard_data():
    """Generate simulated city health data"""
    np.random.seed(42)
    days = pd.date_range(end=pd.Timestamp.today(), periods=7)
    data = {
        "Date": days,
        "Air Quality Index": np.random.randint(50, 150, size=7),
        "Water Usage (liters)": np.random.randint(100000, 200000, size=7),
        "Electricity Consumption (kWh)": np.random.randint(5000, 10000, size=7),
        "Waste Generated (tons)": np.random.uniform(20, 50, size=7).round(2)
    }
    return pd.DataFrame(data)

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
    st.markdown("<h1 class='dashboard-title'>🌆 City Health Dashboard - Kakinada</h1>", unsafe_allow_html=True)
    
    # Generate dashboard data
    df = generate_dashboard_data()
    
    # KPI Cards
    st.markdown("### 📊 Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class='dashboard-metric'>
            <h3>🌬️ Today's AQI</h3>
            <h2>{df['Air Quality Index'].iloc[-1]}</h2>
            <p>Air Quality Index</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='dashboard-metric'>
            <h3>💧 Water Usage</h3>
            <h2>{df['Water Usage (liters)'].iloc[-1]:,}</h2>
            <p>Liters consumed</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='dashboard-metric'>
            <h3>⚡ Power Usage</h3>
            <h2>{df['Electricity Consumption (kWh)'].iloc[-1]:,}</h2>
            <p>kWh consumed</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class='dashboard-metric'>
            <h3>🗑️ Waste Collected</h3>
            <h2>{df['Waste Generated (tons)'].iloc[-1]}</h2>
            <p>Tons collected</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Line Chart
    st.markdown("### 📈 Trends Over the Past Week")
    chart = alt.Chart(df).transform_fold(
        ['Air Quality Index', 'Water Usage (liters)', 'Electricity Consumption (kWh)', 'Waste Generated (tons)']
    ).mark_line(point=True, strokeWidth=3).encode(
        x=alt.X('Date:T', title='Date'),
        y=alt.Y('value:Q', title='Value'),
        color=alt.Color('key:N', title='Metric', scale=alt.Scale(scheme='category10')),
        tooltip=['Date:T', 'key:N', 'value:Q']
    ).properties(
        width=800, 
        height=400,
        title="City Health Metrics Trend Analysis"
    ).resolve_scale(
        y='independent'
    )
    
    st.altair_chart(chart, use_container_width=True)
    
    # Additional Analytics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Weekly Summary")
        summary_data = {
            "Metric": ["AQI", "Water Usage", "Power Usage", "Waste"],
            "Average": [
                df['Air Quality Index'].mean(),
                df['Water Usage (liters)'].mean(),
                df['Electricity Consumption (kWh)'].mean(),
                df['Waste Generated (tons)'].mean()
            ],
            "Trend": [
                "📈" if df['Air Quality Index'].iloc[-1] > df['Air Quality Index'].iloc[0] else "📉",
                "📈" if df['Water Usage (liters)'].iloc[-1] > df['Water Usage (liters)'].iloc[0] else "📉",
                "📈" if df['Electricity Consumption (kWh)'].iloc[-1] > df['Electricity Consumption (kWh)'].iloc[0] else "📉",
                "📈" if df['Waste Generated (tons)'].iloc[-1] > df['Waste Generated (tons)'].iloc[0] else "📉"
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True)
    
    with col2:
        st.markdown("### 📋 Raw Data")
        st.dataframe(df, use_container_width=True)

# ---------------- Feature 2: Village Comparator ---------------- #
elif st.session_state.selected_feature == "Feature 2":
    st.markdown("<h1 style='text-align:center; color:white;'>🏨️ Village Sustainability Comparator</h1>", unsafe_allow_html=True)
    api_url = FASTAPI_CONFIGS.get("feature_2")
    with st.form("compare_form"):
        village1 = st.text_input("Enter First Village Name")
        village2 = st.text_input("Enter Second Village Name")
        submitted = st.form_submit_button("Compare 🅾")
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

# ---------------- Feature 3: Smart City RAG Solver ---------------- #
elif st.session_state.selected_feature == "Feature 3":
    st.markdown("<h1 style='text-align:center; color:white;'>🔧 Smart City Problem Solver</h1>", unsafe_allow_html=True)
    api_url = FASTAPI_CONFIGS.get("feature_3")

    with st.form("solve_problem_form"):
        user_query = st.text_area("Describe your Smart City Problem")
        submitted = st.form_submit_button("Solve 🚀")

    if submitted and user_query:
        try:
            with st.spinner("Solving smart city issue..."):
                res = requests.post(f"{api_url}/solve", json={"query": user_query})
            if res.status_code == 200:
                data = res.json()
                st.success(f"Problem Category: {data['category']} ({data['confidence_score']:.2f})")
                st.markdown(f"<div class='chat-message bot-message'><strong>Steps:</strong><ul>" + "".join([f"<li>{s}</li>" for s in data['steps']]) + "</ul></div>", unsafe_allow_html=True)
                st.markdown("<h4 style='color:white;'>🔗 Retrieved Solutions</h4>", unsafe_allow_html=True)
                for sol in data["original_solutions"]:
                    st.markdown(f"<div class='chat-message'><b>Source:</b> {sol['source']}<br><b>Content:</b> {sol['text']}</div>", unsafe_allow_html=True)
            else:
                st.error(f"❌ Error {res.status_code}: {res.text}")
        except Exception as e:
            st.error(f"🔌 Error contacting Feature 3 API: {str(e)}")

# ---------------- Other Features ---------------- #
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
    <em>Multi-feature, multi-endpoint AI integration with City Health Analytics</em>
</div>
""", unsafe_allow_html=True)