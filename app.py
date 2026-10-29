import streamlit as st
import os
import zipfile
import io
from google import genai
from google.genai import errors

# Page Config for Mobile View
st.set_page_config(page_title="Bulk AI Image Generator", layout="centered")

st.title("🎨 Bulk AI Image Generator")
st.markdown("API keys rotate karte hue bulk mein images generate karein.")

# --- Step 1: API Keys Input ---
st.subheader("1. Enter API Keys")
api_keys_input = st.text_area(
    "Apni Google AI API Keys daalein (Ek line mein ek, ya comma se alag karein):",
    placeholder="AIzaSy...\nAIzaSy..."
)

# --- Step 2: Bulk Prompts Input ---
st.subheader("2. Enter Prompts (Max 30)")
prompts_input = st.text_area(
    "Apne prompts yahan paste karein (Har prompt nayi line mein ho):",
    height=200,
    placeholder="A cinematic shot of an ancient Chinese palace...\nA dark mystical forest..."
)

# --- Helper Function: Round-Robin API Key Rotator ---
class KeyRotator:
    def __init__(self, keys_str):
        # Clean and split keys
        self.keys = [k.strip() for k in keys_str.replace(",", "\n").split("\n") if k.strip()]
        self.current_index = 0

    def get_client(self):
        if not self.keys:
            raise ValueError("Koi valid API key nahi mili!")
        key = self.keys[self.current_index]
        return genai.Client(api_key=key)

    def rotate(self):
        if len(self.keys) <= 1:
            return False # Rotate karne ke liye doosri key hi nahi hai
        self.current_index = (self.current_index + 1) % len(self.keys)
        st.warning(f"⚠️ Limit cross hui! Agli API key par switch kar rahe hain (Key Index: {self.current_index})")
        return True

# --- Step 3: Generation Trigger ---
if st.button("🚀 Generate All Images", type="primary"):
    if not api_keys_input.strip():
        st.error("Kripya kam az kam ek API key zaroor daalein!")
    elif not prompts_input.strip():
        st.error("Kripya kam az kam ek prompt zaroor daalein!")
    else:
        prompts = [p.strip() for p in prompts_input.split("\n") if p.strip()]
        rotator = KeyRotator(api_keys_input)
        
        output_dir = "generated_images"
        os.makedirs(output_dir, exist_ok=True)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        successful_images = []
        
        for i, prompt in enumerate(prompts):
            status_text.text(f"Generating image {i+1} of {len(prompts)}...")
            
            generated = False
            attempts = 0
            max_attempts = len(rotator.keys) * 2 # Safety limit for loops
            
            while not generated and attempts < max_attempts:
                try:
                    client = rotator.get_client()
                    
                    # Google GenAI SDK call for Imagen
                    result = client.models.generate_images(
                        model='imagen-3.0-generate-002',
                        prompt=prompt,
                        config=dict(
                            number_of_images=1,
                            output_mime_type="image/jpeg",
                            aspect_ratio="16:9", # Aapke workflow ke mutabiq 16:9 cinematic
                        )
                    )
                    
                    for generated_image in result.generated_images:
                        image_path = os.path.join(output_dir, f"image_{i+1}.jpg")
                        with open(image_path, "wb") as f:
                            f.write(generated_image.image.image_bytes)
                        successful_images.append(image_path)
                        
                    generated = True
                except Exception as e:
                    # Agar rate limit ya quota error aaye toh key rotate karo
                    error_msg = str(e)
                    if "RESOURCE_EXHAUSTED" in error_msg or "rate limit" in error_msg.lower() or "quota" in error_msg.lower():
                        rotated = rotator.rotate()
                        if not rotated:
                            st.error(f"Error on prompt {i+1}: {e} (Aur koi key nahi bachi rotation ke liye)")
                            break
                    else:
                        st.error(f"Error on prompt {i+1}: {e}")
                        break
                attempts += 1
                
            progress_bar.progress((i + 1) / len(prompts))
            
        status_text.text("✅ Saari images successfully generate ho chuki hain!")
        
        # --- Step 4: Bulk Download (ZIP) ---
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
            