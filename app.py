import streamlit as st
import os
import zipfile
import io
import requests
import urllib.parse
import time

# Page Config for Mobile View
st.set_page_config(page_title="Bulk AI Image Generator", layout="centered")

st.title("🎨 Bulk Cinematic Image Generator")
st.markdown("Apne 30 prompts daalein aur ek click par 16:9 cinematic images bulk mein download karein.")

# --- Step 1: Bulk Prompts Input ---
st.subheader("Enter Prompts (Max 30)")
prompts_input = st.text_area(
    "Apne prompts yahan paste karein (Har prompt nayi line mein ho):",
    height=200,
    placeholder="A cinematic shot of an ancient Chinese palace, highly detailed...\nA dark mystical forest with glowing blue light..."
)

# --- Step 2: Generation Trigger ---
if st.button("🚀 Generate All Images", type="primary"):
    if not prompts_input.strip():
        st.error("Kripya kam az kam ek prompt zaroor daalein!")
    else:
        prompts = [p.strip() for p in prompts_input.split("\n") if p.strip()]
        
        output_dir = "generated_images"
        os.makedirs(output_dir, exist_ok=True)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        successful_images = []
        
        for i, prompt in enumerate(prompts):
            status_text.text(f"Generating image {i+1} of {len(prompts)}...")
            
            try:
                # URL encode the prompt for Pollinations AI API
                encoded_prompt = urllib.parse.quote(prompt)
                # 16:9 cinematic aspect ratio configuration
                image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1280&height=720&nologo=true"
                
                # Fetch image from API
                response = requests.get(image_url, timeout=60)
                
                if response.status_code == 200:
                    image_path = os.path.join(output_dir, f"image_{i+1}.jpg")
                    with open(image_path, "wb") as f:
                        f.write(response.content)
                    successful_images.append(image_path)
                else:
                    st.warning(f"Prompt {i+1} generate karne mein masla hua (Status: {response.status_code})")
                
            except Exception as e:
                st.error(f"Error on prompt {i+1}: {e}")
                
            progress_bar.progress((i + 1) / len(prompts))
            time.sleep(0.5) # Chota sa pause taaki server par load na pade
            
        status_text.text("✅ Saari images successfully generate ho chuki hain!")
        
        # --- Step 3: Bulk Download (ZIP) ---
        if successful_images:
            st.success(f"Total {len(successful_images)} images ban gayi hain!")
            
            # Create Zip in memory
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                for img_path in successful_images:
                    zip_file.write(img_path, os.path.basename(img_path))
            
            zip_buffer.seek(0)
            
            st.download_button(
                label="📦 Download All Images (ZIP)",
                data=zip_buffer,
                file_name="bulk_images.zip",
                mime="application/zip",
                type="primary"
            )
            
