import streamlit as st
from PIL import Image
import io
import base64
import json
from datetime import datetime
import torch
from diffusers import StableDiffusionPipeline

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

# --- Load Model Locally Once ---
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

# --- Generate Image ---
def generate_image_locally(prompt):
    with st.spinner("🔄 Generating image..."):
        image = pipe(prompt).images[0]
    return image

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
        "image_base64": image_to_base64(image),
        "success": True
    }
    st.session_state.chat_history.append(entry)
    st.session_state.generated_images.append({
        "prompt": prompt,
        "image": image,
        "timestamp": timestamp
    })

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
    st.header("🧠 Local Model Info")
    st.info("Model: CompVis/stable-diffusion-v1-4\n\nRunning locally. No token needed.")
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
st.markdown("Generate photorealistic **smart city concepts** using the local model **Stable Diffusion v1.4**.")

user_prompt = st.text_area("📝 Describe your smart city image (e.g., 'solar-powered buildings with drone deliveries')", height=100)

if st.button("🎨 Generate Image"):
    if user_prompt.strip():
        image = generate_image_locally(user_prompt.strip())
        add_to_chat_history(user_prompt.strip(), image)
        st.image(image, caption="Generated Image", use_container_width=True)
        create_download_button(image, f"smartcity_{datetime.now().strftime('%H%M%S')}.png")
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
            image = Image.open(io.BytesIO(base64.b64decode(entry['image_base64'])))
            st.image(image, use_container_width=True)
            create_download_button(image, f"history_{idx}.png")

