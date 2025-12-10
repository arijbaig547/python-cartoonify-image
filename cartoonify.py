import streamlit as st
import cv2
import numpy as np
from PIL import Image
import base64
from io import BytesIO
import time

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AnimeGen Pro",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. PREMIUM CSS STYLING ---
st.markdown("""
<style>
    /* Import modern font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #0E1117; 
    }

    /* Hide Default Header */
    header {visibility: hidden;}
    
    /* Control Panel (Left Side) */
    .control-panel {
        background-color: #161B22;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #30363D;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    }

    /* Primary Action Button */
    .stButton button {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        font-weight: 700;
        border-radius: 10px;
        width: 100%;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.6);
    }

    /* Headings */
    h1, h2, h3 {
        color: #f0f6fc !important;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #a855f7 !important;
    }
    
    /* Custom Download Button */
    .dwn-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background-color: #238636;
        color: white !important;
        padding: 10px 20px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: 600;
        margin-top: 10px;
        width: 100%;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .dwn-btn:hover {
        background-color: #2ea043;
        color: white !important;
    }

</style>
""", unsafe_allow_html=True)

# --- 3. PROCESSING LOGIC ---
class Editor:
    def process_image(self, image, style, complexity):
        # Convert PIL to CV2
        img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Optimization: Resize if too big
        h, w = img.shape[:2]
        if max(h, w) > 1200:
            scale = 1200 / max(h, w)
            img = cv2.resize(img, (int(w*scale), int(h*scale)))

        # -------------------------------------------
        # REAL IMAGE PROCESSING SIMULATION
        # -------------------------------------------
        if style == "Ghibli Art":
            # Bilateral Filter (Smooths surface, keeps edges)
            for _ in range(2):
                img = cv2.bilateralFilter(img, 9, 75, 75)
            # Detail Enhance
            img = cv2.detailEnhance(img, sigma_s=10, sigma_r=0.15)
            # Boost Saturation
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            hsv[:,:,1] = np.clip(hsv[:,:,1] * (1 + complexity/100), 0, 255)
            img = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
            
        elif style == "Dark Comic":
            # Gray & Edges
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            gray = cv2.medianBlur(gray, 5)
            edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
            color = cv2.bilateralFilter(img, 9, 250, 250)
            img = cv2.bitwise_and(color, color, mask=edges)

        elif style == "Sketch":
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            inv = 255 - gray
            blur = cv2.GaussianBlur(inv, (21,21), 0)
            img = cv2.divide(gray, 255-blur, scale=256)
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

        # Fake loading delay for UX feel
        time.sleep(1)
        
        return img

def get_download_href(img_arr, filename):
    img_pil = Image.fromarray(cv2.cvtColor(img_arr, cv2.COLOR_BGR2RGB))
    buffered = BytesIO()
    img_pil.save(buffered, format="JPEG", quality=95)
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f'<a href="data:image/jpeg;base64,{img_str}" download="{filename}" class="dwn-btn">📥 Download HD Image</a>'

# --- 4. MAIN APPLICATION ---
def main():
    editor = Editor()
    
    # Header
    st.markdown("<h1 style='text-align: center; margin-bottom: 40px;'>🎨 AnimeGen <span style='background: -webkit-linear-gradient(left, #6366f1, #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>Pro Studio</span></h1>", unsafe_allow_html=True)

    # --- LAYOUT: 30% Controls | 70% Canvas ---
    col1, col2 = st.columns([1, 2.5], gap="large")

    # --- LEFT COLUMN: CONTROLS ---
    with col1:
        st.markdown('<div class="control-panel">', unsafe_allow_html=True)
        st.markdown("### 🛠️ Tools")
        
        # 1. UPLOAD (Outside form for immediate preview)
        uploaded_file = st.file_uploader("Upload Image", type=['jpg', 'png', 'jpeg'])
        
        if uploaded_file:
            # Load image immediately into state
            image = Image.open(uploaded_file)
            st.session_state['original'] = image
            
            st.markdown("---")
            
            # 2. SETTINGS FORM (Prevents auto-reload on slider change)
            with st.form("editor_form"):
                st.write("**Select Style**")
                style = st.selectbox("Style", ["Ghibli Art", "Dark Comic", "Sketch"], label_visibility="collapsed")
                
                st.write("**Complexity**")
                complexity = st.slider("Strength", 0, 100, 50, label_visibility="collapsed")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # GENERATE BUTTON
                generate_btn = st.form_submit_button("✨ RUN MAGIC")
        
        else:
            st.info("👆 Upload an image to unlock tools")
            
        st.markdown('</div>', unsafe_allow_html=True)

    # --- RIGHT COLUMN: CANVAS ---
    with col2:
        # SCENARIO 1: No Image Uploaded
        if not uploaded_file:
            st.markdown("""
            <div style="height: 500px; border: 2px dashed #30363D; border-radius: 20px; display: flex; align-items: center; justify-content: center; background: #0d1117;">
                <div style="text-align: center; color: #8b949e;">
                    <h2 style="margin:0;">🖼️ Canvas Empty</h2>
                    <p>Upload an image from the left panel</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # SCENARIO 2: Image Uploaded but NOT Generated yet (PREVIEW MODE)
        elif uploaded_file and not generate_btn and 'processed' not in st.session_state:
            st.markdown("### 👁️ Image Preview")
            st.image(st.session_state['original'], use_column_width=True, caption="Original Image")
            st.info("👈 Configure settings on the left and click 'Run Magic'")

        # SCENARIO 3: Generated (BEFORE vs AFTER MODE)
        if uploaded_file and (generate_btn or 'processed' in st.session_state):
            
            # Process only if button clicked
            if generate_btn:
                with st.spinner("🎨 AI is transforming your image..."):
                    result = editor.process_image(st.session_state['original'], style, complexity)
                    st.session_state['processed'] = result
            
            # Display Results
            if 'processed' in st.session_state:
                st.markdown("### ✨ Result Comparison")
                
                # Create Tabs for viewing preference
                tab1, tab2 = st.tabs(["SIDE BY SIDE", "FOCUS VIEW"])
                
                with tab1:
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown("**Original**")
                        st.image(st.session_state['original'], use_column_width=True)
                    with c2:
                        st.markdown("**Transformed**")
                        res_pil = Image.fromarray(cv2.cvtColor(st.session_state['processed'], cv2.COLOR_BGR2RGB))
                        st.image(res_pil, use_column_width=True)
                
                with tab2:
                    st.image(res_pil, use_column_width=True, caption="Final Result HD")

                # Download Button
                st.markdown(get_download_href(st.session_state['processed'], "anime_art.jpg"), unsafe_allow_html=True)
                
                # Reset Button logic
                if st.button("🔄 Start Over", type="secondary"):
                    del st.session_state['processed']
                    st.rerun()

if __name__ == "__main__":
    main()