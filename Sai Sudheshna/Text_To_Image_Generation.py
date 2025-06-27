import streamlit as st
from PIL import Image
import io
import base64
import json
import requests
from datetime import datetime

# --- Streamlit Page Config ---
st.set_page_config(
    page_title="Smart City Image Generator",
    page_icon="🏙️",
    layout="wide"
)

# --- Initialize Session State ---
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'generated_images' not in st.session_state:
    st.session_state.generated_images = []
if 'hf_token' not in st.session_state:
    st.session_state.hf_token = ""

# --- Hugging Face Image Generation ---
def generate_image_with_huggingface(prompt, hf_token):
    model_id =  "black-forest-labs/FLUX.1-schnell"
    api_url = f"https://api-inference.huggingface.co/models/{model_id}"
    headers = {"Authorization": f"Bearer {hf_token}"}
    payload = {"inputs": prompt}

    with st.spinner("🔄 Generating image..."):
        response = requests.post(api_url, headers=headers, json=payload)
        if response.status_code == 200:
            image_bytes = response.content
            return Image.open(io.BytesIO(image_bytes))
        elif response.status_code == 403:
            st.error("🚫 Access Denied: Make sure you've accepted the model license on Hugging Face.")
        elif response.status_code in [503, 429]:
            st.warning("⚠️ Model is busy or rate limited. Try again shortly.")
        else:
            st.error(f"❌ Unexpected error: {response.status_code} - {response.reason}")
    return None

# --- Convert Image to base64 ---
def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# --- Save to Chat History ---
def add_to_chat_history(prompt, image):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {
        "timestamp": timestamp,
        "prompt": prompt,
        "image_base64": image_to_base64(image) if image else None,
        "success": image is not None
    }
    st.session_state.chat_history.append(entry)
    if image:
        st.session_state.generated_images.append({"prompt": prompt, "image": image, "timestamp": timestamp})

# --- Download Button ---
def create_download_button(image, filename):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    st.download_button("📥 Download Image", buffered.getvalue(), file_name=filename, mime="image/png")

# --- Export Chat History ---
def export_chat_history():
    if st.session_state.chat_history:
        json_data = json.dumps(st.session_state.chat_history, indent=2)
        st.download_button("📄 Download Chat History", data=json_data, file_name="chat_history.json", mime="application/json")

# --- Sidebar ---
with st.sidebar:
    st.header("🔐 API Configuration")
    token = st.text_input("Hugging Face API Token", type="password", key="hf_token")
    if token:
        st.success("✅ API Token saved.")
    else:
        st.warning("⚠️ Please enter your Hugging Face API Token.")

    st.metric("Total Prompts", len(st.session_state.chat_history))
    st.metric("Images Generated", len(st.session_state.generated_images))
    export_chat_history()

    if st.button("🗑️ Clear History"):
        st.session_state.chat_history = []
        st.session_state.generated_images = []
        st.success("History cleared.")
        st.rerun()

# --- Main UI ---
st.title("🏙️ Sustainable Smart City Assistant - Text to Image Generator")
st.markdown("Generate photorealistic **smart city concepts** using the Hugging Face model **FLUX.1-dev**.")

user_prompt = st.text_area("📝 Describe your smart city image (e.g., 'solar-powered buildings with drone deliveries')", height=100)

if st.button("🎨 Generate Image"):
    if not st.session_state.get("hf_token"):
        st.error("❌ Please enter your Hugging Face API Token in the sidebar.")
    elif user_prompt.strip():
        image = generate_image_with_huggingface(user_prompt.strip(), st.session_state.hf_token)
        if image:
            add_to_chat_history(user_prompt.strip(), image)
            st.image(image, caption="Generated Image", use_container_width=True)
            create_download_button(image, f"smartcity_{datetime.now().strftime('%H%M%S')}.png")
        else:
            add_to_chat_history(user_prompt.strip(), None)
            st.error("❌ Image generation failed.")
    else:
        st.warning("⚠️ Please enter a description to generate an image.")

# --- Recent Images Section ---
if st.session_state.generated_images:
    st.header("🖼️ Recently Generated Images")
    for img_data in reversed(st.session_state.generated_images[-3:]):
        st.image(img_data['image'], caption=img_data['prompt'], use_container_width=True)
        st.caption(f"{img_data['timestamp']}")
        create_download_button(img_data['image'], f"recent_{img_data['timestamp'].replace(':','-')}.png")

# --- Chat History Section ---
if st.session_state.chat_history:
    st.header("📜 Chat History")
    with st.expander("View Full Prompt and Image History"):
        for idx, entry in enumerate(reversed(st.session_state.chat_history)):
            st.markdown(f"**{entry['timestamp']}** - {entry['prompt']}")
            if entry['success'] and entry['image_base64']:
                image = Image.open(io.BytesIO(base64.b64decode(entry['image_base64'])))
                st.image(image, use_container_width=True)
                create_download_button(image, f"history_{idx}.png")
            else:
                st.warning("⚠️ Image generation failed.")

