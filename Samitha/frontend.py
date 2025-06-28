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
    try:
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        # Return empty string if background image not found
        return ""

# Try to load background image, fallback to no background
try:
    bg_base64 = get_base64_bg("background.jpg")
    background_style = f'background-image: url("data:image/jpg;base64,{bg_base64}");' if bg_base64 else ""
except:
    background_style = ""

st.set_page_config(
    page_title="Avenir - Reimagining Cities",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(f"""
<style>
    .main {{
        {background_style}
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-blend-mode: darken;
        background-color: #1e1e1e;
    }}
    .stApp > header {{ background-color: transparent; }}
    .stSidebar > div:first-child {{
        background: linear-gradient(180deg, rgba(46,125,50,0.95), rgba(76,175,80,0.95));
        backdrop-filter: blur(10px);
    }}
    .chat-message, .metric-card {{
        background: rgba(0,0,0,0.8); 
        color: white; 
        border-radius: 10px;
        padding: 15px; 
        box-shadow: 0 4px 8px rgba(0,0,0,0.3); 
        backdrop-filter: blur(10px);
        margin: 10px 0;
    }}
    .user-message {{ 
        background: rgba(76,175,80,0.9); 
        margin-left: 50px; 
    }}
    .bot-message {{ 
        background: rgba(0,0,0,0.85); 
        margin-right: 50px; 
    }}
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
    .error-message {{
        background: rgba(244,67,54,0.9);
        color: white;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }}
    .success-message {{
        background: rgba(76,175,80,0.9);
        color: white;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
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

# ---------------- Helper Functions ---------------- #
def make_api_request(url, payload, timeout=20):
    """Make API request with proper error handling"""
    try:
        response = requests.post(url, json=payload, timeout=timeout)
        return response
    except requests.exceptions.Timeout:
        return None, "Request timed out. The service might be busy."
    except requests.exceptions.ConnectionError:
        return None, f"Failed to connect to service at {url}"
    except Exception as e:
        return None, f"Unexpected error: {str(e)}"

def check_api_status(url):
    """Check if API is online"""
    try:
        response = requests.get(f"{url}/health", timeout=2)
        return "🟢 Online" if response.status_code == 200 else "🔴 Offline"
    except:
        return "🔴 Offline"

def display_response(content, title="Response"):
    """Display API response in a formatted way"""
    st.markdown(
        f"""<div class='chat-message bot-message'>
        <strong>{title}:</strong><br>{content}
        </div>""",
        unsafe_allow_html=True
    )

def display_error(error_msg):
    """Display error message in a formatted way"""
    st.markdown(
        f"""<div class='error-message'>
        <strong>❌ Error:</strong><br>{error_msg}
        </div>""",
        unsafe_allow_html=True
    )

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
            f"""<div class='chat-message'><b>{log['time']} ago</b> - {log['user']} used <b>{log['feature']}</b><br><em>"{log['query']}"</em></div>""",
            unsafe_allow_html=True
        )

# ---------------- Feature 1: Recycle DIY Ideas (Fixed) ---------------- #
elif selected_feature_key == "feature_1":
    st.markdown("<h1 style='text-align:center; color:white;'>♻️ Sustainability Advisor</h1>", unsafe_allow_html=True)
    api_url = FASTAPI_CONFIGS.get("feature_1")

    with st.form("recycle_form"):
        material = st.text_area(
            "Enter waste material for sustainability advice:", 
            placeholder="e.g., plastic bottle, cardboard box, glass jar, aluminum can, old clothes",
            help="Describe the waste material and get sustainability advice and recycling ideas!"
        )
        submitted = st.form_submit_button("Get Sustainability Advice 💡")

    if submitted and material.strip():
        with st.spinner("🔄 Getting sustainability advice..."):
            # Fixed payload to match your API
            payload = {
                "message": material.strip(),  # Changed from "material" to "message"
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            response = make_api_request(f"{api_url}/chat", payload)  # Using /chat endpoint
            
            if isinstance(response, tuple):  # Error case
                display_error(response[1])
            elif response and response.status_code == 200:
                try:
                    result = response.json()
                    advice = result.get("response", "No advice returned.")
                    feature_name = result.get("feature_name", "Sustainability Advisor")
                    
                    st.markdown('<div class="success-message">✅ Sustainability advice generated successfully!</div>', unsafe_allow_html=True)
                    display_response(advice, f"♻️ {feature_name}")
                    
                    # Add material info
                    st.info(f"💡 Advice for: **{material}**")
                    
                except Exception as e:
                    display_error(f"Failed to parse response: {str(e)}")
            else:
                error_msg = f"API returned status {response.status_code}"
                if response:
                    try:
                        error_detail = response.json().get("detail", response.text)
                        error_msg = f"{error_msg}: {error_detail}"
                    except:
                        error_msg = f"{error_msg}: {response.text}"
                display_error(error_msg)
    elif submitted:
        st.warning("⚠️ Please enter a waste material to get sustainability advice.")

# ---------------- Feature 2: Village Comparator ---------------- #
elif selected_feature_key == "feature_2":
    st.markdown("<h1 style='text-align:center; color:white;'>🏘️ Village Sustainability Comparator</h1>", unsafe_allow_html=True)
    api_url = FASTAPI_CONFIGS.get("feature_2")

    with st.form("compare_form"):
        col1, col2 = st.columns(2)
        with col1:
            village1 = st.text_input("First Village Name", placeholder="e.g., Green Valley")
        with col2:
            village2 = st.text_input("Second Village Name", placeholder="e.g., Eco Hills")
        
        submitted = st.form_submit_button("Compare Villages 🆚")

    if submitted and village1.strip() and village2.strip():
        with st.spinner("🔄 Comparing villages..."):
            payload = {
                "village1": village1.strip(),
                "village2": village2.strip()
            }
            
            response = make_api_request(f"{api_url}/compare", payload)
            
            if isinstance(response, tuple):  # Error case
                display_error(response[1])
            elif response and response.status_code == 200:
                try:
                    result = response.json()
                    comparison = result.get("comparison", "No comparison available.")
                    
                    st.markdown('<div class="success-message">✅ Village comparison completed!</div>', unsafe_allow_html=True)
                    display_response(comparison, f"🏘️ {village1} vs {village2}")
                    
                except Exception as e:
                    display_error(f"Failed to parse response: {str(e)}")
            else:
                error_msg = f"API returned status {response.status_code}"
                if response:
                    try:
                        error_detail = response.json().get("detail", response.text)
                        error_msg = f"{error_msg}: {error_detail}"
                    except:
                        error_msg = f"{error_msg}: {response.text}"
                display_error(error_msg)
    elif submitted:
        st.warning("⚠️ Please enter both village names to compare.")

# ---------------- Feature 3: City Problem Solver (Fixed) ---------------- #
# Replace your existing Feature 3 section with this:

elif selected_feature_key == "feature_3":
    st.markdown("<h1 style='text-align:center; color:white;'>🏙️ Smart City Problem Solver</h1>", unsafe_allow_html=True)
    api_url = FASTAPI_CONFIGS.get("feature_3")

    # Debug section
    with st.expander("🔧 Debug Information"):
        if st.button("Test API Connection"):
            try:
                health_response = requests.get(f"{api_url}/health", timeout=5)
                if health_response.status_code == 200:
                    health_data = health_response.json()
                    st.success("✅ API is responding!")
                    st.json(health_data)
                else:
                    st.error(f"❌ Health check failed: {health_response.status_code}")
            except Exception as e:
                st.error(f"❌ Connection failed: {str(e)}")
        
        if st.button("Test Debug Endpoint"):
            try:
                debug_payload = {"query": "test traffic congestion problem"}
                debug_response = requests.post(f"{api_url}/debug", json=debug_payload, timeout=10)
                st.write("Debug Response Status:", debug_response.status_code)
                st.json(debug_response.json())
            except Exception as e:
                st.error(f"Debug test failed: {str(e)}")

    with st.form("problem_form"):
        problem_desc = st.text_area(
            "Describe the Smart City Problem:",
            placeholder="e.g., Traffic congestion in downtown area, waste management issues, air pollution",
            height=120,
            help="Describe any urban challenge you're facing and we'll provide smart city solutions!"
        )
        
        problem_category = st.selectbox(
            "Problem Category (Optional):",
            ["General", "Traffic & Transportation", "Environment", "Waste Management", "Energy", "Housing", "Public Safety", "Digital Infrastructure"]
        )
        
        submitted = st.form_submit_button("Get Smart Solution 💡")

    if submitted and problem_desc.strip():
        with st.spinner("🔄 Analyzing problem and generating smart solutions..."):
            # Include category in the problem description if selected
            enhanced_problem = problem_desc.strip()
            if problem_category != "General":
                enhanced_problem = f"[{problem_category}] {enhanced_problem}"
            
            # Payload to match your API exactly
            payload = {"query": enhanced_problem}
            
            try:
                st.info(f"🔄 Sending request to: {api_url}/solve")
                st.info(f"📝 Query: {enhanced_problem}")
                
                response = requests.post(f"{api_url}/solve", json=payload, timeout=30)
                
                st.info(f"📡 Response Status: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        result = response.json()
                        st.success("✅ Smart city solution generated!")
                        
                        # Display results
                        col1, col2 = st.columns(2)
                        with col1:
                            st.info(f"🎯 **Category:** {result.get('category', 'Unknown')}")
                        with col2:
                            st.info(f"🎲 **Confidence:** {result.get('confidence_score', 0.0):.2f}")
                        
                        # Display solution steps
                        steps = result.get("steps", [])
                        if steps:
                            st.markdown("### 🔧 Recommended Solution Steps:")
                            solution_text = ""
                            for i, step in enumerate(steps, 1):
                                solution_text += f"**Step {i}:** {step}\n\n"
                            display_response(solution_text, "🏙️ Smart City Solutions")
                        else:
                            st.warning("No solution steps were generated.")
                        
                        # Display original solutions
                        original_solutions = result.get("original_solutions", [])
                        if original_solutions:
                            st.markdown("### 📚 Related Solutions:")
                            for i, sol in enumerate(original_solutions[:3], 1):
                                if isinstance(sol, dict):
                                    title = sol.get('title', f'Solution {i}')
                                    content = sol.get('content', 'No content available')
                                else:
                                    title = f'Solution {i}'
                                    content = str(sol)
                                
                                with st.expander(f"💡 {title}"):
                                    st.write(content)
                        
                        # Show timestamp
                        timestamp = result.get("timestamp", "")
                        if timestamp:
                            st.caption(f"📅 Processed at: {timestamp}")
                        
                    except Exception as e:
                        st.error(f"❌ Failed to parse response: {str(e)}")
                        st.error(f"Raw response: {response.text}")
                        
                elif response.status_code == 400:
                    try:
                        error_detail = response.json().get("detail", "Problem not related to smart cities")
                        st.warning(f"⚠️ {error_detail}")
                        st.info("💡 Try describing urban challenges like traffic, pollution, or infrastructure issues.")
                    except:
                        st.warning("⚠️ The query doesn't seem to be related to smart city problems.")
                        
                elif response.status_code == 500:
                    st.error("❌ Internal server error occurred.")
                    try:
                        error_detail = response.json().get("detail", "Unknown server error")
                        st.error(f"Server error: {error_detail}")
                    except:
                        st.error(f"Server returned: {response.text}")
                    
                    st.info("🔧 Try using the debug section above to troubleshoot.")
                        
                else:
                    st.error(f"❌ API returned status {response.status_code}")
                    try:
                        error_detail = response.json().get("detail", "Unknown error")
                        st.error(f"Error: {error_detail}")
                    except:
                        st.error(f"Response: {response.text}")
                        
            except requests.exceptions.Timeout:
                st.error("⏰ Request timed out. The service might be busy.")
                
            except requests.exceptions.ConnectionError:
                st.error(f"🔌 Failed to connect to {api_url}")
                st.info("Make sure your FastAPI service is running on the correct port.")
                
            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")
                
    elif submitted:
        st.warning("⚠️ Please describe a city problem to get smart solutions.")
        
    # Example problems
    with st.expander("💡 Example Problems"):
        st.markdown("""
        **Try these examples:**
        - Traffic congestion during rush hours
        - High air pollution levels in the city
        - Waste management inefficiencies
        - Power outages in residential areas
        - Poor public transportation connectivity
        - Urban heat island effect
        - Water scarcity issues
        - Lack of green spaces
        """)

    # API status
    st.markdown("---")
    try:
        health_response = requests.get(f"{api_url}/health", timeout=2)
        if health_response.status_code == 200:
            health_data = health_response.json()
            solver_status = "✅ Loaded" if health_data.get("solver_loaded") else "❌ Not Loaded"
            st.success(f"🔌 API Status: Online | Solver: {solver_status}")
        else:
            st.error("🔌 API Status: Error")
    except:
        st.error("🔌 API Status: Offline")
        st.info("Start with: `python -m uvicorn feature_3:app --host 0.0.0.0 --port 8003 --reload`")

# ---------------- Feature 4: Dream City Generator (Friend's API) ---------------- #

elif selected_feature_key == "feature_4":
    st.markdown("<h1 style='text-align:center; color:white;'>🏗️ Dream City Generator</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#81C784; font-style:italic;'>Powered by Innovation & Sustainability AI</p>", unsafe_allow_html=True)
    
    api_url = FASTAPI_CONFIGS.get("feature_4")
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

    if submitted and dream_desc.strip():
        with st.spinner("🏗️ Designing your dream city with sustainable innovation..."):
            payload = {
                "description": dream_desc.strip(),
                "city_size": city_size,
                "focus_area": focus_area,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "app_name": "Avenir",
                "theme": "sustainability_innovation"
            }
            
            response = make_api_request(f"{api_url}/dream", payload, timeout=30)
            
            if isinstance(response, tuple):  # Error case
                display_error(response[1])
                st.warning("💡 Make sure your friend's Dream City Generator API is running and accessible.")
            elif response and response.status_code == 200:
                try:
                    result = response.json()
                    city_plan = result.get("city_plan", "No plan returned.")
                    
                    st.markdown('<div class="success-message">🎉 Your dream city plan has been generated!</div>', unsafe_allow_html=True)
                    
                    # Enhanced display with sections
                    st.markdown("### 🏗️ Your Sustainable City Vision")
                    display_response(city_plan, f"🌟 {city_size} City Plan with {focus_area} Focus")
                    
                    # Add some additional context
                    st.markdown("---")
                    st.markdown("### 💡 Next Steps")
                    st.info("Your city plan incorporates cutting-edge sustainability principles and innovative urban design. Consider sharing this vision with urban planners and community leaders!")
                    
                except Exception as e:
                    display_error(f"Failed to parse response: {str(e)}")
            else:
                error_msg = f"API returned status {response.status_code}"
                if response:
                    try:
                        error_detail = response.json().get("detail", response.text)
                        error_msg = f"{error_msg}: {error_detail}"
                    except:
                        error_msg = f"{error_msg}: {response.text}"
                display_error(error_msg)
    elif submitted:
        st.warning("⚠️ Please describe your dream city to generate a plan.")

# ---------------- Fallback Chat for unsupported selections ---------------- #
else:
    # Generic chat fallback for any unimplemented feature key
    api_url = FASTAPI_CONFIGS.get(selected_feature_key)
    st.markdown(
        f"<h1 style='text-align:center; color:white;'>🤖 {st.session_state.selected_feature_label} Chat</h1>",
        unsafe_allow_html=True
    )

    # Display chat history
    for msg in st.session_state.messages:
        css_class = "user-message" if msg["role"] == "user" else "bot-message"
        st.markdown(
            f"""<div class='chat-message {css_class}'><strong>{msg['role'].capitalize()}:</strong><br>{msg['content']}</div>""",
            unsafe_allow_html=True
        )

    with st.form("fallback_chat_form", clear_on_submit=True):
        user_input = st.text_area("Ask something...")
        submitted = st.form_submit_button("Send 🚀")

    if submitted and user_input.strip():
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        with st.spinner("🔄 Getting response..."):
            payload = {
                "query": user_input.strip(),
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            response = make_api_request(f"{api_url}/chat", payload)
            
            if isinstance(response, tuple):  # Error case
                bot_reply = f"Sorry, I encountered an error: {response[1]}"
            elif response and response.status_code == 200:
                try:
                    result = response.json()
                    bot_reply = result.get("response", "No response received.")
                except Exception as e:
                    bot_reply = f"Failed to parse response: {str(e)}"
            else:
                bot_reply = f"API error: {response.status_code if response else 'No response'}"
            
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            st.rerun()

# ---------------- Footer ---------------- #
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#81C784; margin-top:50px;'>🌿 Avenir - Building Sustainable Cities for Tomorrow 🌿</div>",
    unsafe_allow_html=True
)