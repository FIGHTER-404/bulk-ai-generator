import streamlit as st
import os
import zipfile
import io
import requests
import time

# Page Config for Mobile View
st.set_page_config(page_title="Bulk Cinematic Image Generator", layout="centered")

st.title("🎨 Bulk Cinematic Image Generator (HD)")
st.markdown("Hugging Face AI engine ke zariye high-quality, watermark-free images bulk mein generate karein.")

# --- Step 1: API Key Input ---
st.subheader("1. Hugging Face API Token")
hf_token = st.text_input("Apna Hugging Face Access Token yahan daalein:", type="password", placeholder="hf_...")

# --- Step 2: Bulk Prompts Input ---
st.subheader("2. Enter Prompts (Max 30)")
prompts_input = st.text_area(
    "Apne prompts yahan paste karein (Har prompt nayi line mein ho):",
    height=200,
    placeholder="A cinematic shot of an ancient Chinese palace, highly detailed...\nA dark mystical forest with glowing blue light..."
)

# --- Step 3: Generation Trigger ---
if st.button("🚀 Generate HD Images", type="primary"):
    if not hf_token.strip():
        st.error("Kripya apni Hugging Face API Key zaroor daalein!")
    elif not prompts_input.strip():
        st.error("Kripya kam az kam ek prompt zaroor daalein!")
    else:
        prompts = [p.strip() for p in prompts_input.split("\n") if p.strip()]
        
        output_dir = "generated_images"
        os.makedirs(output_dir, exist_ok=True)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        successful_images = []
        
        # Using Stable Diffusion XL (SDXL) for high quality cinematic output
        API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
        headers = {"Authorization": f"Bearer {hf_token}"}
        
        for i, prompt in enumerate(prompts):
            status_text.text(f"Generating HD image {i+1} of {len(prompts)}...")
            
            payload = {"inputs": prompt}
            success = False
            
            for attempt in range(3):
                try:
                    response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
                    
                    if response.status_code == 200:
                        image_path = os.path.join(output_dir, f"image_{i+1}.jpg")
                        with open(image_path, "wb") as f:
                            f.write(response.content)
                        successful_images.append(image_path)
                        success = True
                        break
                    elif response.status_code == 503:
                        # Model is loading on HF server, wait and retry
                        time.sleep(10)
                    else:
                        time.sleep(3)
                except Exception as e:
                    time.sleep(3)
            
            if not success:
                st.warning(f"Prompt {i+1} generate nahi ho saka.")
                
            progress_bar.progress((i + 1) / len(prompts))
            time.sleep(2) # Smooth gap between requests
            
        status_text.text("✅ Process complete ho gaya hai!")
        
        # --- Step 4: Bulk Download (ZIP) ---
        if successful_images:
            st.success(f"Total {len(successful_images)} HD images ban gayi hain!")
            
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                for img_path in successful_images:
                    zip_file.write(img_path, os.path.basename(img_path))
            
            zip_buffer.seek(0)
            
            st.download_button(
                label="📦 Download All HD Images (ZIP)",
                data=zip_buffer,
                file_name="bulk_hd_images.zip",
                mime="application/zip",
                type="primary"
            )
