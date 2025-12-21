import streamlit as st
import torch
import torchvision.transforms as T
from PIL import Image
import io
import time

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="🎨 AI Anime Generator",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---------------- CLEAN & VISIBLE CSS ----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background-color: #0A0A0A;
    }
    
    /* HEADER STYLES - VISIBLE */
    .main-title {
        color: #FFFFFF;
        text-align: center;
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .subtitle {
        color: #CCCCCC;
        text-align: center;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    /* UPLOAD BOX - CLEAR VISIBLE */
    .upload-container {
        background: #1A1A1A;
        border-radius: 16px;
        padding: 2rem;
        border: 2px dashed #4ECDC4;
        margin-bottom: 2rem;
    }
    
    /* BUTTON - BRIGHT & VISIBLE */
    .stButton > button {
        background: linear-gradient(90deg, #FF6B6B, #FF8E53) !important;
        color: white !important;
        border: none !important;
        padding: 14px 28px !important;
        border-radius: 12px !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        width: 100%;
        transition: transform 0.2s !important;
    }
    
    .stButton > button:hover {
        transform: scale(1.02) !important;
        box-shadow: 0 6px 20px rgba(255, 107, 107, 0.3) !important;
    }
    
    /* CARDS - CLEAR VISIBLE */
    .result-card {
        background: #1A1A1A;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid #333333;
    }
    
    .card-title {
        color: #FFFFFF;
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    /* TEXT COLORS - VISIBLE */
    h1, h2, h3, h4 {
        color: #FFFFFF !important;
    }
    
    p, label, div {
        color: #CCCCCC !important;
    }
    
    /* PROGRESS BAR */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #4ECDC4, #FF6B6B);
    }
    
    /* DOWNLOAD BUTTON */
    .download-btn {
        background: linear-gradient(90deg, #4ECDC4, #44A08D) !important;
    }
    
    /* TIPS BOX */
    .tip-box {
        background: #1A1A1A;
        border-left: 4px solid #FF6B6B;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    /* DIVIDER */
    hr {
        border-color: #333333;
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- MODEL LOAD ----------------
@st.cache_resource
def load_model():
    try:
        model = torch.hub.load(
            "bryandlee/animegan2-pytorch:main",
            "generator",
            pretrained="face_paint_512_v2",
            trust_repo=True
        )
        model.eval()
        return model
    except Exception as e:
        st.error(f"Model loading failed: {str(e)}")
        return None

# ---------------- PROGRESS ANIMATION ----------------
def show_progress():
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i in range(100):
        progress = i + 1
        progress_bar.progress(progress)
        if progress < 30:
            status_text.text("🔄 Loading AI model...")
        elif progress < 60:
            status_text.text("🎨 Processing image...")
        elif progress < 90:
            status_text.text("✨ Applying anime style...")
        else:
            status_text.text("✅ Finalizing...")
        time.sleep(0.01)
    
    progress_bar.empty()
    status_text.empty()

# ---------------- IMAGE PROCESS ----------------
def anime_transform(image: Image.Image):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = load_model()
    if model is None:
        return None

    # --- Resize longest side to 512 (SAFE) ---
    w, h = image.size
    scale = 512 / max(w, h)
    new_w, new_h = int(w * scale), int(h * scale)
    image = image.resize((new_w, new_h), Image.BICUBIC)

    # --- Padding calculation (guaranteed non-negative) ---
    pad_left = (512 - new_w) // 2
    pad_top = (512 - new_h) // 2
    pad_right = 512 - new_w - pad_left
    pad_bottom = 512 - new_h - pad_top

    image = T.Pad(
        padding=(pad_left, pad_top, pad_right, pad_bottom),
        fill=0
    )(image)

    transform = T.Compose([
        T.ToTensor(),
        T.Normalize([0.5]*3, [0.5]*3)
    ])

    input_tensor = transform(image).unsqueeze(0).to(device)
    model = model.to(device)

    with torch.no_grad():
        output = model(input_tensor)

    output = output.squeeze(0).cpu()
    output = output * 0.5 + 0.5
    output = output.clamp(0, 1)

    return T.ToPILImage()(output)

    
   

# ---------------- HEADER ----------------
st.markdown('<h1 class="main-title">🎨 AI Anime Generator</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Upload a photo to transform it into anime style instantly</p>', unsafe_allow_html=True)

# ---------------- MAIN UPLOAD SECTION ----------------
st.markdown('<div class="upload-container">', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 📸 Upload Photo")
    st.markdown("""
    **Supported:** JPG, PNG, JPEG  
    **Best for:** Portraits, Selfies
    """)

with col2:
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed"
    )

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- PREVIEW UPLOADED IMAGE ----------------
if uploaded_file is not None:
    try:
        image = Image.open(uploaded_file).convert("RGB")
        
        st.markdown("### 📷 Preview")
        col_pre1, col_pre2, col_pre3 = st.columns([1, 2, 1])
        with col_pre2:
            st.image(image, use_container_width=True, caption="Original Image")
    except:
        st.error("❌ Error loading image. Please try another file.")

# ---------------- GENERATE BUTTON ----------------
if uploaded_file is not None:
    st.markdown("---")
    
    generate_col1, generate_col2, generate_col3 = st.columns([1, 2, 1])
    with generate_col2:
        generate_clicked = st.button(
            "🚀 **Generate Anime Version**",
            use_container_width=True,
            type="primary"
        )
    
    if generate_clicked:
        with st.spinner("Processing..."):
            show_progress()
            
            try:
                result = anime_transform(image)
                
                if result is not None:
                    # Display Results
                    st.markdown("## ✨ Results")
                    
                    col_res1, col_res2 = st.columns(2)
                    
                    with col_res1:
                        st.markdown('<div class="result-card">', unsafe_allow_html=True)
                        st.markdown('<p class="card-title">📸 Original</p>', unsafe_allow_html=True)
                        st.image(image, use_container_width=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with col_res2:
                        st.markdown('<div class="result-card">', unsafe_allow_html=True)
                        st.markdown('<p class="card-title">🎭 Anime Version</p>', unsafe_allow_html=True)
                        st.image(result, use_container_width=True)
                        
                        # Download button
                        buf = io.BytesIO()
                        result.save(buf, format="PNG", quality=95)
                        
                        st.download_button(
                            label="📥 **Download Image**",
                            data=buf.getvalue(),
                            file_name="anime_version.png",
                            mime="image/png",
                            use_container_width=True,
                            key="download_result"
                        )
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Success message
                    st.success("✅ **Transformation successful!**")
                    st.balloons()
                    
            except Exception as e:
                st.error(f"❌ Error during transformation: {str(e)}")
                st.info("💡 Try with a different image or check the file format.")

# ---------------- TIPS SECTION ----------------
st.markdown("---")
st.markdown("## 💡 Tips for Best Results")

tips_col1, tips_col2 = st.columns(2)

with tips_col1:
    st.markdown("""
    <div class="tip-box">
    <h4>🖼️ Image Quality</h4>
    • Use clear, well-lit photos<br>
    • Avoid blurry images<br>
    • Higher resolution = Better results
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="tip-box">
    <h4>👤 Face Photos</h4>
    • Front-facing portraits work best<br>
    • Keep face clearly visible<br>
    • Avoid extreme angles
    </div>
    """, unsafe_allow_html=True)

with tips_col2:
    st.markdown("""
    <div class="tip-box">
    <h4>🎨 Style Tips</h4>
    • Natural lighting recommended<br>
    • Simple backgrounds help<br>
    • Single subject preferred
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="tip-box">
    <h4>⚡ Processing</h4>
    • First run may take longer<br>
    • GPU speeds up processing<br>
    • Results save automatically
    </div>
    """, unsafe_allow_html=True)

# ---------------- FOOTER ----------------
st.markdown("---")
footer_col1, footer_col2, footer_col3 = st.columns([1, 2, 1])
with footer_col2:
    st.markdown("""
    <div style="text-align: center; padding: 1rem;">
        <p style="color: #888; font-size: 0.9rem;">
        Built with ❤️ using AnimeGAN2 • Powered by PyTorch
        </p>
        <p style="color: #666; font-size: 0.8rem;">
        Upload a photo to see the magic!
        </p>
    </div>
    """, unsafe_allow_html=True)

# ---------------- SIDEBAR INFO ----------------
with st.sidebar:
    st.markdown("### ℹ️ Info")
    st.markdown("""
    **Model:** AnimeGAN2 v2  
    **Style:** Face Paint 512  
    **Output:** 512×512 px
    """)
    
    st.markdown("---")
    st.markdown("### ⚙️ System")
    
    if torch.cuda.is_available():
        st.success("✅ GPU Available")
        device_info = "GPU (CUDA)"
    else:
        st.info("💻 Using CPU")
        device_info = "CPU"
    
    st.markdown(f"**Device:** {device_info}")
    st.markdown(f"**Torch:** {torch.__version__}")
    
    if st.button("Clear Cache", use_container_width=True):
        st.cache_resource.clear()
        st.rerun()