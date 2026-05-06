import streamlit as st
import tensorflow as tf
import numpy as np
from PIL import Image
import plotly.express as px
from tensorflow.keras.applications.efficientnet import preprocess_input
import pandas as pd

# --- Configuration ---
st.set_page_config(
    page_title="Image Tagging AI",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Stunning Design ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Global Background */
    .stApp {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        color: #ffffff;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {background: transparent !important;}

    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }

    /* Titles */
    h1 {
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #00C9FF, #92FE9D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0px !important;
    }
    .subtitle {
        text-align: center;
        color: #b0c4de;
        font-size: 1.2rem;
        margin-bottom: 40px;
    }

    /* File Uploader Customization */
    [data-testid="stFileUploadDropzone"] {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 2px dashed rgba(255,255,255,0.2) !important;
        border-radius: 16px !important;
    }
    [data-testid="stFileUploadDropzone"]:hover {
        border-color: #00C9FF !important;
        background: rgba(0, 201, 255, 0.05) !important;
    }
    
    /* Sidebar Customization */
    [data-testid="stSidebar"] {
        background: rgba(15, 32, 39, 0.95);
        border-right: 1px solid rgba(255,255,255,0.05);
    }
    
    /* Custom Prediction Tag */
    .pred-tag {
        font-size: 2.5rem;
        font-weight: 800;
        text-align: center;
        padding: 20px;
        border-radius: 12px;
        background: linear-gradient(90deg, rgba(0,201,255,0.2), rgba(146,254,157,0.2));
        border: 1px solid rgba(0,201,255,0.3);
        margin-top: 20px;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# --- Constants & Classes ---
MODEL_PATH = 'Task1/Model/best_model_final.keras'
CLASSES = ['Buildings 🏢', 'Forest 🌲', 'Mountain ⛰️', 'Sea 🌊', 'Street 🛣️']

# --- Load Model (Cached) ---
@st.cache_resource
def load_model():
    return tf.keras.models.load_model(MODEL_PATH)

try:
    model = load_model()
except Exception as e:
    st.error(f"Error loading model: {e}")
    st.stop()

# --- Helper Functions ---
def predict_image(image, model):
    # Convert PIL Image to RGB if it has an alpha channel
    if image.mode != "RGB":
        image = image.convert("RGB")
    
    # Resize image to target size 224x224
    img_resized = image.resize((224, 224))
    
    # Convert to array and preprocess
    arr = tf.keras.utils.img_to_array(img_resized)
    arr = preprocess_input(arr)
    arr = np.expand_dims(arr, axis=0)
    
    # Predict
    probs = model.predict(arr, verbose=0)[0]
    return probs

# --- Sidebar ---
with st.sidebar:
    st.image("sidebar_image.png", use_container_width=True)
    
    st.markdown("## 🧠 About the Project")
    st.markdown("""
        <div class="glass-card" style="padding: 15px;">
            This application uses a fine-tuned <b>EfficientNetB0</b> model to classify natural scene images into 5 distinct categories.
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📊 Metrics")
    st.markdown("""
        - **Accuracy:** 96.81%
        - **Precision:** 96.83%
        - **Recall:** 96.81%
        - **F1-Score:** 96.82%
    """)
    
    st.markdown("---")
    st.markdown("### 👤 Author")
    st.markdown("**Abdul Hafeez**", unsafe_allow_html=True)

# --- Main Interface ---
st.markdown("<h1>Image Tagging AI</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Instantly classify natural scenes using Deep Learning</p>", unsafe_allow_html=True)

# File Uploader
uploaded_file = st.file_uploader("Drop an image here (JPG, PNG)", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    # Read Image
    image = Image.open(uploaded_file)
    
    # Layout using Columns
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### 🖼️ Uploaded Image")
        st.image(image, use_container_width=True, output_format="PNG")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### 🎯 Prediction Results")
        
        with st.spinner("Analyzing image..."):
            probs = predict_image(image, model)
            
            # Get max probability and class
            max_idx = np.argmax(probs)
            pred_class = CLASSES[max_idx]
            confidence = probs[max_idx] * 100
            
            st.markdown(f"""
                <div class='pred-tag'>
                    {pred_class}<br>
                    <span style='font-size: 1.2rem; font-weight: 400; color: #92FE9D;'>{confidence:.2f}% Confidence</span>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br><b>Detailed Probabilities:</b>", unsafe_allow_html=True)
            
            # Create a Plotly Bar Chart for Probabilities
            df = pd.DataFrame({
                'Class': CLASSES,
                'Probability': probs * 100
            })
            
            fig = px.bar(
                df, x='Probability', y='Class', orientation='h',
                color='Probability', color_continuous_scale=['#0f2027', '#00C9FF', '#92FE9D'],
                text_auto='.2f'
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                xaxis=dict(showgrid=False, range=[0, 100], title="Probability (%)"),
                yaxis=dict(showgrid=False, title="", categoryorder='total ascending'),
                margin=dict(l=0, r=0, t=0, b=0),
                height=250,
                coloraxis_showscale=False
            )
            st.plotly_chart(fig, use_container_width=True)
            
        st.markdown("</div>", unsafe_allow_html=True)
else:
    # Initial state when no image is uploaded
    st.markdown("""
        <div class='glass-card' style='text-align: center; padding: 40px;'>
            <h3>👆 Upload an image to get started!</h3>
            <p style='color: #b0c4de;'>Supports buildings, forest, mountain, sea, and street scenes.</p>
        </div>
    """, unsafe_allow_html=True)
