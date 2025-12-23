import streamlit as st
import json
import google.generativeai as genai
from datetime import datetime
from typing import Dict, List, Any
import os

# Page configuration
st.set_page_config(
    page_title="ArtRestorer AI - Cultural Heritage Preservation",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================== GEMINI API CONFIGURATION ====================
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]  # ✅ Reads from .streamlit/secrets.toml
except KeyError:
    st.error("❌ API Key not found! Please add GEMINI_API_KEY to .streamlit/secrets.toml")
    st.stop()

if not GEMINI_API_KEY:
    st.error("❌ GEMINI_API_KEY is empty! Please add your valid API key to .streamlit/secrets.toml")
    st.stop()

try:
    genai.configure(api_key=GEMINI_API_KEY)
    # Use the latest stable model
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"❌ API Configuration Error: {str(e)}\nPlease check your API key validity.")
    st.stop()

# ==================== TRANSLATIONS ====================


# Custom CSS - Exact replica of your HTML styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Lato:wght@300;400;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #FFF8DC 0%, #FAEBD7 100%);
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    .main-header {
        background: linear-gradient(135deg, #8B4513 0%, #A0522D 100%);
        color: white;
        padding: 2rem 1rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        border-radius: 0;
        margin: -6rem -6rem 2rem -6rem;
    }
    
    .main-title {
        font-family: 'Playfair Display', serif;
        font-size: 3rem;
        margin: 0 0 0.5rem 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .subtitle {
        font-size: 1.2rem;
        font-weight: 300;
        margin: 0;
        opacity: 0.95;
    }
    
    .card {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 6px 20px rgba(0,0,0,0.1);
        border-left: 6px solid #8B4513;
    }
    
    .card h2 {
        font-family: 'Playfair Display', serif;
        color: #8B4513;
        margin-top: 0;
        font-size: 2rem;
    }
    
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        padding: 0.8rem;
        border: 2px solid #D2B48C;
        border-radius: 8px;
        font-size: 1rem;
        font-family: 'Lato', sans-serif;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #8B4513;
        box-shadow: 0 0 0 3px rgba(139, 69, 19, 0.1);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #8B4513 0%, #A0522D 100%);
        color: white;
        border: none;
        padding: 1.2rem 3rem;
        font-size: 1.3rem;
        font-weight: bold;
        border-radius: 12px;
        cursor: pointer;
        box-shadow: 0 6px 20px rgba(0,0,0,0.2);
        font-family: 'Lato', sans-serif;
        width: 100%;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
    }
    
    .feature-selector {
        background: linear-gradient(135deg, #FFF8DC 0%, #FAEBD7 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        border-left: 6px solid #CD853F;
    }
    
    .feature-selector h3 {
        color: #8B4513;
        margin-top: 0;
        font-family: 'Playfair Display', serif;
    }
    
    .user-greeting {
        background: linear-gradient(135deg, #8B4513 0%, #A0522D 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .user-greeting h2 {
        margin: 0;
        color: white;
    }
    
    .result-box {
        background: linear-gradient(135deg, #FFFEF7 0%, #FFF8E1 100%);
        padding: 2.5rem;
        border-radius: 20px;
        margin-top: 2rem;
        box-shadow: 0 8px 30px rgba(0,0,0,0.15);
        border: 4px solid #D2691E;
    }
    
    .result-box h3 {
        color: #8B4513;
        font-family: 'Playfair Display', serif;
        font-size: 2rem;
        margin-top: 0;
    }
    
    .result-text {
        line-height: 2;
        color: #333;
        font-family: 'Lato', sans-serif;
        font-size: 1.05rem;
    }
    
    .result-text h2 {
        color: #8B4513;
        font-family: 'Playfair Display', serif;
        margin-top: 2rem;
        margin-bottom: 1rem;
        font-size: 1.8rem;
    }
    
    .result-text h3 {
        color: #A0522D;
        font-family: 'Playfair Display', serif;
        margin-top: 1.5rem;
        margin-bottom: 0.8rem;
        font-size: 1.5rem;
    }
    
    .result-text strong {
        color: #8B4513;
        font-weight: 600;
    }
    
    .result-text ul, .result-text li {
        margin: 0.5rem 0;
        line-height: 1.8;
    }
    
    .footer {
        background: linear-gradient(135deg, #8B4513 0%, #A0522D 100%);
        color: white;
        text-align: center;
        padding: 2rem 1rem;
        margin-top: 3rem;
        border-radius: 0;
    }
    
    .footer h3 {
        font-family: 'Playfair Display', serif;
        margin: 0 0 0.5rem 0;
    }
    
    .slider-container {
        background: linear-gradient(135deg, #FFFEF7 0%, #FFF8E1 50%, #FFF3E0 100%);
        padding: 2.5rem;
        border-radius: 25px;
        border: 4px solid #D2691E;
        margin: 2rem 0;
        box-shadow: 0 10px 35px rgba(0,0,0,0.15);
        position: relative;
        overflow: hidden;
    }
    
    .slider-container::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(139, 69, 19, 0.05) 0%, transparent 70%);
        animation: rotate 20s linear infinite;
    }
    
    @keyframes rotate {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .slider-container > * {
        position: relative;
        z-index: 1;
    }
    
    /* Streamlit Slider Customization */
    .stSlider > div > div > div > div {
        background: linear-gradient(90deg, #8B4513, #CD853F, #D2691E) !important;
        height: 10px !important;
        border-radius: 10px !important;
    }
    
    .stSlider > div > div > div > div > div {
        background: white !important;
        border: 4px solid #8B4513 !important;
        width: 28px !important;
        height: 28px !important;
        box-shadow: 0 4px 12px rgba(139, 69, 19, 0.4) !important;
    }
    
    .stSlider > div > div > div > div > div:hover {
        transform: scale(1.2);
        box-shadow: 0 6px 18px rgba(139, 69, 19, 0.6) !important;
    }
    
    .temperature-indicator {
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        font-weight: bold;
        margin-top: 1.5rem;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        transition: all 0.3s ease;
        border: 3px solid rgba(255,255,255,0.5);
    }
    
    .temperature-indicator:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 35px rgba(0,0,0,0.2);
    }
    
    .conservative {
        background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
        color: #1976D2;
        border-color: #1976D2;
    }
    
    .balanced {
        background: linear-gradient(135deg, #FFF3E0 0%, #FFE0B2 100%);
        color: #F57C00;
        border-color: #F57C00;
    }
    
    .creative {
        background: linear-gradient(135deg, #F3E5F5 0%, #E1BEE7 100%);
        color: #7B1FA2;
        border-color: #7B1FA2;
    }
    
    .feature-gallery {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
        gap: 2rem;
    }
    
    .feature-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border-left: 5px solid #8B4513;
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.2);
    }
    
    .feature-card h3 {
        color: #8B4513;
        font-family: 'Playfair Display', serif;
        margin-top: 0;
        font-size: 1.5rem;
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        display: block;
    }
    
    label {
        font-weight: bold;
        color: #8B4513;
        font-size: 1.1rem;
        font-family: 'Lato', sans-serif;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        justify-content: center;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: white;
        border: 2px solid #8B4513;
        color: #8B4513;
        padding: 0.8rem 1.5rem;
        font-size: 1rem;
        font-weight: bold;
        border-radius: 10px;
        font-family: 'Lato', sans-serif;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #8B4513 0%, #A0522D 100%);
        color: white;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    
    /* Landing Page Styles */
    .hero-section {
        background: linear-gradient(135deg, #8B4513 0%, #A0522D 100%);
        color: white;
        padding: 5rem 2rem;
        text-align: center;
        border-radius: 25px;
        margin: 2rem 0 4rem 0;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        position: relative;
        overflow: hidden;
    }
    
    .hero-section::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: pulse 15s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 0.5; }
        50% { transform: scale(1.1); opacity: 0.3; }
    }
    
    .hero-title {
        font-family: 'Playfair Display', serif;
        font-size: 4.5rem;
        margin: 0 0 1.5rem 0;
        text-shadow: 4px 4px 8px rgba(0,0,0,0.5);
        position: relative;
        z-index: 1;
    }
    
    .hero-subtitle {
        font-size: 1.8rem;
        margin: 0 0 2rem 0;
        opacity: 0.95;
        position: relative;
        z-index: 1;
    }
    
    .features-showcase {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 2.5rem;
        margin: 4rem 0;
        padding: 0 2rem;
    }
    
    @media (max-width: 1200px) {
        .features-showcase {
            grid-template-columns: repeat(2, 1fr);
        }
    }
    
    @media (max-width: 768px) {
        .features-showcase {
            grid-template-columns: 1fr;
        }
    }
    
    .feature-showcase-card {
        background: white;
        padding: 2.5rem 2rem;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
        border: 3px solid transparent;
        background-clip: padding-box;
        position: relative;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        overflow: hidden;
    }
    
    .feature-showcase-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 6px;
        background: linear-gradient(90deg, #8B4513, #D2691E, #CD853F);
        transform: scaleX(0);
        transition: transform 0.4s ease;
    }
    
    .feature-showcase-card:hover {
        transform: translateY(-12px) scale(1.02);
        box-shadow: 0 15px 50px rgba(139, 69, 19, 0.3);
        border-color: #8B4513;
    }
    
    .feature-showcase-card:hover::before {
        transform: scaleX(1);
    }
    
    .feature-showcase-icon {
        font-size: 5rem;
        margin-bottom: 1.5rem;
        display: block;
        filter: drop-shadow(0 4px 8px rgba(0,0,0,0.1));
        transition: transform 0.3s ease;
    }
    
    .feature-showcase-card:hover .feature-showcase-icon {
        transform: scale(1.2) rotate(5deg);
    }
    
    .feature-showcase-card h3 {
        color: #8B4513;
        font-family: 'Playfair Display', serif;
        font-size: 1.8rem;
        margin: 1rem 0 0.8rem 0;
        font-weight: 700;
    }
    
    .feature-showcase-card p {
        color: #666;
        font-size: 1.05rem;
        line-height: 1.6;
        margin: 0;
    }
    
    .features-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 2rem;
        margin: 3rem 0;
    }
    
    .feature-box {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border-top: 5px solid #8B4513;
        transition: all 0.3s ease;
    }
    
    .feature-box:hover {
        transform: translateY(-10px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
    }
    
    .feature-box-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
    }
    
    .feature-box h3 {
        color: #8B4513;
        font-family: 'Playfair Display', serif;
        font-size: 1.5rem;
        margin: 1rem 0;
    }
    
    .cta-section {
        text-align: center;
        margin: 5rem 0 3rem 0;
        padding: 3rem;
        background: linear-gradient(135deg, #FFF8DC 0%, #FAEBD7 100%);
        border-radius: 20px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.1);
    }
    
    .cta-button {
        background: linear-gradient(135deg, #8B4513 0%, #A0522D 100%);
        color: white;
        border: none;
        padding: 1.5rem 4rem;
        font-size: 1.5rem;
        font-weight: bold;
        border-radius: 50px;
        cursor: pointer;
        box-shadow: 0 8px 30px rgba(139, 69, 19, 0.4);
        transition: all 0.3s ease;
        font-family: 'Lato', sans-serif;
    }
    
    .cta-button:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(139, 69, 19, 0.5);
    }
    
    /* Feedback Form Styles */
    .feedback-button-section {
        text-align: center;
        margin: 4rem 0 2rem 0;
        padding: 2rem;
    }
    
    .feedback-modal {
        display: none;
        position: fixed;
        z-index: 1000;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0,0,0,0.6);
        animation: fadeIn 0.3s ease;
    }
    
    .feedback-modal.active {
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    .feedback-modal-content {
        background: linear-gradient(135deg, #FFF8DC 0%, #FAEBD7 100%);
        border-radius: 20px;
        padding: 2.5rem;
        max-width: 700px;
        width: 90%;
        max-height: 90vh;
        overflow-y: auto;
        box-shadow: 0 15px 50px rgba(0,0,0,0.3);
        border: 4px solid #8B4513;
        animation: slideUp 0.4s ease;
        position: relative;
    }
    
    @keyframes slideUp {
        from { transform: translateY(50px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    
    .feedback-close {
        position: absolute;
        right: 1.5rem;
        top: 1.5rem;
        font-size: 2rem;
        color: #8B4513;
        cursor: pointer;
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        background: white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    
    .feedback-close:hover {
        transform: rotate(90deg) scale(1.1);
        background: #8B4513;
        color: white;
    }
    
    .feedback-form-card {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        margin-top: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border-left: 5px solid #8B4513;
    }
    
    .feedback-button {
        background: linear-gradient(135deg, #8B4513 0%, #A0522D 100%);
        color: white;
        border: none;
        padding: 1.2rem 3rem;
        font-size: 1.3rem;
        font-weight: bold;
        border-radius: 50px;
        cursor: pointer;
        box-shadow: 0 6px 20px rgba(139, 69, 19, 0.4);
        transition: all 0.3s ease;
        font-family: 'Lato', sans-serif;
    }
    
    .feedback-button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(139, 69, 19, 0.5);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'landing'
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}
if 'result_text' not in st.session_state:
    st.session_state.result_text = ""

# Feature descriptions
feature_descriptions = {
    'period': 'Expert restoration guidance for Baroque and Renaissance artworks using historically accurate techniques',
    'cultural': 'Restore and enhance traditional patterns from Mughal, Islamic, Celtic, Asian, and indigenous arts',
    'sculptural': 'Reconstruct eroded or damaged features in sculptures, statues, and three-dimensional artifacts',
    'textile': 'Expert restoration for tapestries, embroidery, historical fabrics, and woven artifacts',
    'abstract': 'Restore contemporary, abstract, expressionist, and modern artworks',
    'manuscript': 'Restore illuminated manuscripts, scrolls, codices, and historical documents',
    'mural': 'Restore wall paintings, cave art, frescoes, and architectural murals',
    'ceramic': 'Restore pottery, porcelain, ceramic vessels, and glazed artifacts',
    'symbol': 'Decode and restore symbolic elements, religious imagery, inscriptions, and cultural icons',
    'educational': 'Create engaging museum descriptions, exhibition content, and educational materials'
}

# Landing Page
if st.session_state.page == 'landing':
    st.markdown("""
    <div class="main-header">
        <h1 class="main-title">🎨 ArtRestorer AI</h1>
        <p class="subtitle">AI-Powered Smart Assistance for Art Restoration & Cultural Heritage Preservation</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="hero-section">
        <h2 class="hero-title">🖼️ Preserve History with AI</h2>
        <p class="hero-subtitle">Advanced AI technology meets centuries of artistic heritage</p>
        <p style="font-size: 1.3rem; margin-top: 2rem; line-height: 1.8; position: relative; z-index: 1;">
            Transform the way you approach art restoration with cutting-edge artificial intelligence.<br>
            From Renaissance masterpieces to modern abstract art, our AI provides expert guidance<br>
            for conservators, curators, historians, and art enthusiasts worldwide.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<h2 style="text-align: center; font-family: \'Playfair Display\', serif; color: #8B4513; font-size: 3rem; margin: 3rem 0 2rem 0;">✨ Powerful Restoration Features</h2>', unsafe_allow_html=True)
    
    features_showcase = [
        {"icon": "🎭", "title": "Period-Specific Restoration", "desc": "Baroque, Renaissance, Gothic & more with historically accurate techniques"},
        {"icon": "🕌", "title": "Cultural Patterns", "desc": "Mughal, Islamic, Celtic traditions with authentic design restoration"},
        {"icon": "🗿", "title": "Sculptural Reconstruction", "desc": "3D artifacts & statues with detailed erosion analysis"},
        {"icon": "🧵", "title": "Textile & Tapestry", "desc": "Historical fabrics, embroidery & woven artifacts repair"},
        {"icon": "🎨", "title": "Modern Art Recovery", "desc": "Abstract & contemporary works with innovative approaches"},
        {"icon": "📜", "title": "Manuscript Conservation", "desc": "Ancient scrolls, illuminated texts & documents"},
        {"icon": "🏛️", "title": "Mural & Fresco", "desc": "Cave paintings, frescoes & architectural murals"},
        {"icon": "🏺", "title": "Ceramic Restoration", "desc": "Pottery, porcelain & glazed artifacts reconstruction"},
        {"icon": "🔯", "title": "Symbol Interpretation", "desc": "Religious imagery, inscriptions & cultural icons"}
    ]
    
    # Display in 3-column grid
    for i in range(0, len(features_showcase), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(features_showcase):
                feature = features_showcase[i + j]
                with cols[j]:
                    st.markdown(f"""
                    <div class="feature-showcase-card">
                        <span class="feature-showcase-icon">{feature['icon']}</span>
                        <h3>{feature['title']}</h3>
                        <p>{feature['desc']}</p>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Why Choose ArtRestorer AI Section
    st.markdown('<div class="card" style="margin: 4rem 0;">', unsafe_allow_html=True)
    st.markdown("""
    <h2 style="text-align: center; font-family: 'Playfair Display', serif; color: #8B4513; font-size: 3rem; margin-bottom: 3rem;">
        💎 Why Choose ArtRestorer AI?
    </h2>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 3rem 2rem; background: linear-gradient(135deg, #FFF8DC 0%, #FFFEF7 100%); border-radius: 20px; box-shadow: 0 6px 20px rgba(0,0,0,0.1); transition: all 0.3s ease; border: 2px solid #D2B48C;">
            <div style="font-size: 5rem; margin-bottom: 2rem; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.15));">🔬</div>
            <h3 style="color: #8B4513; font-family: 'Playfair Display', serif; font-size: 2rem; margin-bottom: 1rem;">Expert Analysis</h3>
            <p style="color: #666; font-size: 1.15rem; line-height: 1.8;">AI-powered insights based on historical research and conservation best practices</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 3rem 2rem; background: linear-gradient(135deg, #FFF8DC 0%, #FFFEF7 100%); border-radius: 20px; box-shadow: 0 6px 20px rgba(0,0,0,0.1); transition: all 0.3s ease; border: 2px solid #D2B48C;">
            <div style="font-size: 5rem; margin-bottom: 2rem; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.15));">⚡</div>
            <h3 style="color: #8B4513; font-family: 'Playfair Display', serif; font-size: 2rem; margin-bottom: 1rem;">Instant Results</h3>
            <p style="color: #666; font-size: 1.15rem; line-height: 1.8;">Get comprehensive restoration guidance in seconds, not hours or days</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 3rem 2rem; background: linear-gradient(135deg, #FFF8DC 0%, #FFFEF7 100%); border-radius: 20px; box-shadow: 0 6px 20px rgba(0,0,0,0.1); transition: all 0.3s ease; border: 2px solid #D2B48C;">
            <div style="font-size: 5rem; margin-bottom: 2rem; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.15));">🌍</div>
            <h3 style="color: #8B4513; font-family: 'Playfair Display', serif; font-size: 2rem; margin-bottom: 1rem;">Global Heritage</h3>
            <p style="color: #666; font-size: 1.15rem; line-height: 1.8;">Support for diverse cultural traditions from around the world</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # CTA Section at the bottom
    st.markdown("""
    <div style="background: linear-gradient(135deg, #FFF8DC 0%, #FAEBD7 100%); border-radius: 25px; padding: 4rem 2rem; margin: 4rem 0 2rem 0; text-align: center; box-shadow: 0 10px 40px rgba(0,0,0,0.15); border: 3px solid #8B4513;">
        <h2 style="font-family: 'Playfair Display', serif; color: #8B4513; font-size: 3rem; margin-bottom: 1.5rem;">Ready to Begin Your Restoration Journey?</h2>
        <p style="color: #666; font-size: 1.3rem; margin-bottom: 2.5rem; line-height: 1.7;">Join conservators and art enthusiasts worldwide in preserving cultural heritage</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🚀 Continue to Application", key="landing_continue", use_container_width=True):
            st.session_state.page = 'welcome'
            st.rerun()

# Welcome Page
elif st.session_state.page == 'welcome':
    st.markdown("""
    <div class="main-header">
        <h1 class="main-title">🎨 ArtRestorer AI</h1>
        <p class="subtitle">AI-Powered Smart Assistance for Art Restoration & Cultural Heritage Preservation</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="card" style="max-width: 700px; margin: 0 auto;">', unsafe_allow_html=True)
    st.markdown('<h2 style="text-align: center; font-size: 2.5rem; font-family: \'Playfair Display\', serif; color: #8B4513;">Welcome to ArtRestorer AI</h2>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666; margin-bottom: 2rem;">Let\'s get started with your art restoration journey</p>', unsafe_allow_html=True)
    
    user_name = st.text_input("👤 What is your name?", placeholder="Enter your full name", key="name_input")
    
    artwork_type = st.selectbox(
        "🎨 What type of artwork are you working with?",
        ["", "Painting (Oil, Acrylic, Watercolor)", "Sculpture (Stone, Bronze, Wood)", 
         "Textile (Tapestry, Fabric, Embroidery)", "Manuscript (Scrolls, Books, Documents)",
         "Mural/Fresco (Wall Painting)", "Ceramic/Pottery (Vessels, Tiles)",
         "Mixed Media/Contemporary Art", "Other Heritage Artifact"],
        key="artwork_input"
    )
    
    user_role = st.selectbox(
        "👔 What is your role?",
        ["", "Professional Conservator/Restorer", "Museum Curator", "Art Historian/Researcher",
         "Student (Art/Conservation)", "Private Collector", "Artist", 
         "Art Enthusiast/Hobbyist", "Educator/Teacher"],
        key="role_input"
    )
    
    user_goal = st.selectbox(
        "🎯 What is your primary goal?",
        ["", "Physical restoration guidance", "Digital restoration/reconstruction",
         "Artwork analysis and documentation", "Educational content creation",
         "Academic research", "Preventive conservation", "Exhibition planning"],
        key="goal_input"
    )
    
    if st.button("🚀 Begin Restoration Analysis", key="begin_btn"):
        if user_name and artwork_type and user_role and user_goal:
            st.session_state.user_data = {
                'name': user_name,
                'artwork_type': artwork_type,
                'role': user_role,
                'goal': user_goal
            }
            st.session_state.page = 'main'
            st.rerun()
        else:
            st.error("Please fill in all fields before proceeding!")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Main Application
elif st.session_state.page == 'main':
    st.markdown("""
    <div class="main-header">
        <h1 class="main-title">🎨 ArtRestorer AI</h1>
        <p class="subtitle">AI-Powered Smart Assistance for Art Restoration & Cultural Heritage Preservation</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🖼️ Restoration Assistant", "📚 Feature Gallery", "🏛️ Cultural Insights", "💰 Conservation Cost Calculator"])
    
    with tab1:
        # User Greeting
        st.markdown(f"""
        <div class="user-greeting">
            <h2>Hello, {st.session_state.user_data['name']}! 👋</h2>
            <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem;">Working on: {st.session_state.user_data['artwork_type']} | Role: {st.session_state.user_data['role']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h2>Art Restoration Analysis</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📸 Upload Artwork Image (Optional)**")
            uploaded_file = st.file_uploader("", type=['png', 'jpg', 'jpeg'], key="image_upload", label_visibility="collapsed")
            if uploaded_file is not None:
                st.image(uploaded_file, caption="Uploaded Artwork", use_container_width=True)
        
        with col2:
            artwork_description = st.text_area(
                "✍️ Artwork Description",
                placeholder="Example: A Renaissance oil painting featuring a noblewoman in elaborate dress. The lower right section shows significant fading, possibly due to water damage...",
                height=200,
                key="description_input"
            )
        
        # Feature Selector
        st.markdown('<div class="feature-selector">', unsafe_allow_html=True)
        st.markdown('<h3>🎯 Select Analysis Type</h3>', unsafe_allow_html=True)
        
        feature_select = st.selectbox(
            "Select Feature",
            [
                "1. 🎭 Period-Specific Restoration (Baroque/Renaissance)",
                "2. 🕌 Cultural Pattern Enhancement (Traditional Arts)",
                "3. 🗿 Sculptural Reconstruction",
                "4. 🧵 Textile & Tapestry Repair",
                "5. 🎨 Abstract & Modern Art Recovery",
                "6. 📜 Ancient Manuscript Conservation",
                "7. 🏛️ Mural & Fresco Revival",
                "8. 🏺 Ceramic & Pottery Reconstruction",
                "9. 🔯 Symbol & Iconography Interpretation",
                "10. 🎓 Educational Content Generation"
            ],
            key="feature_select",
            label_visibility="collapsed"
        )
        
        feature_key = ['period', 'cultural', 'sculptural', 'textile', 'abstract', 'manuscript', 'mural', 'ceramic', 'symbol', 'educational'][int(feature_select[0]) - 1]
        st.markdown(f'<p style="margin-top: 1rem; color: #666; font-style: italic;">{feature_descriptions[feature_key]}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Form inputs
        col3, col4, col5 = st.columns(3)
        
        with col3:
            art_style_options = [
                "Baroque", "Renaissance", "Gothic", "Neoclassical", "Rococo",
                "Romantic", "Impressionist", "Expressionist", "Art Deco", "Art Nouveau",
                "Indian Mughal", "Indian Rajput", "Indian Pahari", "Indian Madhubani",
                "Persian Miniature", "Islamic Geometric", "Byzantine", "Japanese Ukiyo-e",
                "Chinese Ming Dynasty", "Aboriginal", "Egyptian", "Greek/Roman Classical"
            ]
            art_style = st.selectbox(
                "🎨 Art Style/Period",
                [""] + art_style_options,
                key="style_input"
            )
        
        with col4:
            damage_type_options = [
                "Water damage/stains", "Fire damage/smoke residue", 
                "Fading from sunlight/UV exposure", "Erosion/weathering",
                "Cracks/structural damage", "Flaking/peeling paint",
                "Mold/biological growth", "Scratches/surface abrasions",
                "Missing sections/losses", "Discoloration/yellowing",
                "Torn fabric/textile damage", "Broken/fragmented pieces",
                "Oxidation/corrosion", "Insect damage", "Previous poor restoration"
            ]
            damage_type = st.selectbox(
                "💔 Damage Type",
                [""] + damage_type_options,
                key="damage_input"
            )
        
        with col5:
            cultural_context_options = [
                "Italian Renaissance", "French Baroque", "Spanish Colonial",
                "Flemish/Dutch", "British Victorian", "Indian Mughal",
                "Indian Rajput", "Indian Temple Art", "Persian/Iranian",
                "Ottoman Turkish", "Chinese Imperial", "Japanese Edo Period",
                "Egyptian Pharaonic", "Greek Classical", "Roman Imperial",
                "Byzantine Eastern Orthodox", "African Tribal", "Native American"
            ]
            cultural_context = st.selectbox(
                "🌍 Cultural Context",
                [""] + cultural_context_options,
                key="context_input"
            )
        
        # Temperature Slider
        st.markdown('<div class="slider-container">', unsafe_allow_html=True)
        st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
            <h3 style="color: #8B4513; font-family: 'Playfair Display', serif; font-size: 2rem; margin: 0; display: flex; align-items: center; gap: 0.5rem;">
                🎨 AI Creativity Level
            </h3>
            <div style="background: linear-gradient(135deg, #8B4513 0%, #A0522D 100%); color: white; padding: 0.6rem 1.8rem; border-radius: 30px; font-weight: bold; font-size: 1.4rem; box-shadow: 0 4px 12px rgba(0,0,0,0.2);">
                <span id="tempDisplay">0.60</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        temperature = st.slider(
            "Creativity Level",
            0.0, 1.0, 0.6, 0.05,
            key="temp_slider",
            label_visibility="collapsed"
        )
        
        if temperature <= 0.3:
            indicator_class = "conservative"
            indicator_icon = "🎯"
            indicator_title = "Highly Conservative"
            indicator_subtitle = "Strict Historical Accuracy"
            description_text = "Ultra-precise restoration focusing purely on documented historical evidence and proven conservation techniques. Minimal creative interpretation."
            bg_gradient = "linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%)"
            border_color = "#1976D2"
        elif temperature <= 0.5:
            indicator_class = "conservative"
            indicator_icon = "📐"
            indicator_title = "Conservative & Methodical"
            indicator_subtitle = "Evidence-Based Approach"
            description_text = "Careful restoration based on historical research and comparative analysis. Sticks closely to documented evidence with minimal speculation."
            bg_gradient = "linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%)"
            border_color = "#1976D2"
        elif temperature <= 0.7:
            indicator_class = "balanced"
            indicator_icon = "⚖️"
            indicator_title = "Balanced & Professional"
            indicator_subtitle = "Art + Science"
            description_text = "Balanced approach combining historical accuracy with thoughtful creative suggestions. Ideal for most restoration projects."
            bg_gradient = "linear-gradient(135deg, #FFF3E0 0%, #FFE0B2 100%)"
            border_color = "#F57C00"
        elif temperature <= 0.85:
            indicator_class = "creative"
            indicator_icon = "🎨"
            indicator_title = "Creative & Exploratory"
            indicator_subtitle = "Artistic Interpretation"
            description_text = "Imaginative restoration suggestions based on period style and artistic intuition. Explores multiple creative possibilities while respecting historical context."
            bg_gradient = "linear-gradient(135deg, #F3E5F5 0%, #E1BEE7 100%)"
            border_color = "#7B1FA2"
        else:
            indicator_class = "creative"
            indicator_icon = "✨"
            indicator_title = "Highly Creative & Innovative"
            indicator_subtitle = "Bold Artistic Vision"
            description_text = "Maximum creativity with bold artistic interpretations. Generates innovative restoration ideas that push boundaries while maintaining cultural sensitivity."
            bg_gradient = "linear-gradient(135deg, #F3E5F5 0%, #E1BEE7 100%)"
            border_color = "#7B1FA2"
        
        st.markdown(f"""
        <div style="background: {bg_gradient}; padding: 3rem; border-radius: 25px; text-align: center; margin-top: 2rem; border: 5px solid {border_color}; box-shadow: 0 10px 35px rgba(0,0,0,0.2); transition: all 0.3s ease;">
            <div style="font-size: 4.5rem; margin-bottom: 1.5rem; filter: drop-shadow(0 6px 12px rgba(0,0,0,0.25));">{indicator_icon}</div>
            <div style="font-size: 2.2rem; font-weight: bold; margin-bottom: 0.8rem; color: {border_color}; font-family: 'Playfair Display', serif;">{indicator_title}</div>
            <div style="font-size: 1.3rem; opacity: 0.95; color: {border_color}; font-weight: 600; letter-spacing: 0.5px;">{indicator_subtitle}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="margin-top: 2rem; padding: 2rem; background: white; border-radius: 18px; color: #666; font-size: 1.1rem; line-height: 2; box-shadow: 0 6px 20px rgba(0,0,0,0.12); border-left: 6px solid {border_color};">
            <div style="display: flex; align-items: center; gap: 0.8rem; margin-bottom: 1rem;">
                <span style="font-size: 1.8rem;">💡</span>
                <strong style="color: {border_color}; font-size: 1.2rem;">What this means:</strong>
            </div>
            <p style="margin: 0; color: #555;">{description_text}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Update temperature display
        st.markdown(f"""
        <script>
            document.getElementById('tempDisplay').textContent = '{temperature:.2f}';
        </script>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Generate Button
        if st.button("🎨 Generate AI Restoration Analysis", key="generate_btn"):
            if artwork_description:
                with st.spinner("🔄 Analyzing artwork and generating expert restoration suggestions..."):
                    import time
                    time.sleep(3)
                    
                    st.session_state.page = 'results'
                    
                    # Generate analysis
                    creativity_level = ["highly conservative", "conservative and methodical", "balanced and professional", "creative and exploratory", "highly creative and innovative"][min(int(temperature / 0.2), 4)]
                    
                    st.session_state.result_text = f"""COMPREHENSIVE RESTORATION ANALYSIS
═══════════════════════════════════════════════════════

ARTWORK DETAILS:
{artwork_description}

STYLE/PERIOD: {art_style or 'Not specified'}
DAMAGE TYPE: {damage_type or 'general wear'}
CULTURAL CONTEXT: {cultural_context or 'Not specified'}
ANALYSIS TYPE: {feature_select}
AI CREATIVITY LEVEL: {temperature} ({creativity_level})
ANALYSIS APPROACH: {creativity_level.upper()}

═══════════════════════════════════════════════════════

EXPERT RESTORATION GUIDANCE:

1. HISTORICAL CONTEXT & SIGNIFICANCE
   
   Based on the provided description and the {art_style or 'specified'} period, this artwork represents a significant example of its time. The {cultural_context or 'general'} cultural context suggests traditional techniques and materials that were commonly employed during this era.

2. CONDITION ASSESSMENT

   The {damage_type or 'general wear'} presents specific challenges that require careful consideration:
   
   • Primary concerns include structural integrity and aesthetic coherence
   • Surface analysis reveals patterns consistent with environmental exposure
   • Original materials and techniques must be preserved where possible
   • Documentation of current state is essential before intervention

3. RESTORATION METHODOLOGY

   Step-by-step approach for conservation:

   a) DOCUMENTATION PHASE
      - Comprehensive photography (visible light, UV, infrared)
      - Detailed condition mapping
      - Material analysis and identification
      - Historical research and comparative studies

   b) STABILIZATION PHASE
      - Consolidation of loose or flaking areas
      - Structural support where needed
      - Environmental stabilization
      - Protection from further deterioration

   c) CLEANING PHASE
      - Surface cleaning using appropriate methods
      - Removal of discolored varnish or overpainting
      - pH testing and adjustment
      - Gradual approach with constant monitoring

   d) RESTORATION PHASE
      - Loss compensation using reversible materials
      - Color matching to original palette
      - Texture recreation matching original techniques
      - Integration with surrounding original material

4. MATERIALS & TECHNIQUES

   Recommended conservation-grade materials:
   
   • Adhesives: Reversible synthetic polymers (appropriate for substrate)
   • Consolidants: Tested for compatibility with original materials
   • Inpainting media: Watercolors or conservation acrylics
   • Protective coatings: UV-filtering, breathable varnishes

   Traditional techniques to consider:
   • Period-appropriate brushwork patterns
   • Layering methodology consistent with {art_style or 'period'} style
   • Color mixing using historically accurate pigment knowledge
   • Surface finish matching original aesthetic

5. CULTURAL & HISTORICAL CONSIDERATIONS

   Respect for {cultural_context or 'the artwork\'s'} traditions:
   • Consultation with cultural heritage experts
   • Understanding of symbolic and religious significance
   • Preservation of authentic character and patina
   • Balance between restoration and historical integrity

6. TECHNICAL SPECIFICATIONS

   Color Palette Recommendations:
   • Earth tones: Raw umber, burnt sienna, yellow ochre
   • Primary colors adjusted for period accuracy
   • Consideration of natural pigment aging
   • Matching existing color temperature and saturation

   Application Techniques:
   • Brushstroke direction following original patterns
   • Layering sequence respecting traditional methods
   • Glazing techniques for depth and luminosity
   • Texture recreation using appropriate tools

7. CONSERVATION CHALLENGES & SOLUTIONS

   Anticipated difficulties:

   Challenge 1: {damage_type or 'damage'} extent
   Solution: Gradual intervention with regular assessment, using minimally invasive techniques

   Challenge 2: Material compatibility
   Solution: Comprehensive testing on sample areas, consultation with materials scientists

   Challenge 3: Color matching aged surfaces
   Solution: Create reference samples, account for natural aging, use reversible media

   Challenge 4: Maintaining authenticity
   Solution: Document all interventions, use distinguishable but harmonious restoration

8. PREVENTIVE CONSERVATION

   Long-term preservation recommendations:
   
   Environmental Controls:
   • Temperature: 18-22°C (64-72°F)
   • Relative humidity: 45-55%
   • Light levels: <150 lux for sensitive materials
   • UV filtration on all light sources

   Handling & Display:
   • Proper mounting and support systems
   • Protection from physical contact
   • Regular monitoring and condition checks
   • Emergency response planning

9. ETHICAL CONSIDERATIONS

   Following international conservation ethics (ICOM-CC, AIC):
   • Minimal intervention principle
   • Reversibility of all treatments
   • Documentation of all procedures
   • Respect for original artist's intent
   • Transparency in restoration decisions

10. DOCUMENTATION & REPORTING

    Essential records to maintain:
    • Before, during, and after treatment photographs
    • Written treatment reports
    • Material samples and analysis results
    • Technical drawings and diagrams
    • Conservation decision rationale

═══════════════════════════════════════════════════════

CONCLUSION:

This restoration project requires a balanced approach combining historical accuracy, technical expertise, and cultural sensitivity. The {damage_type or 'damage'} can be addressed through systematic conservation methods while preserving the artwork's integrity and significance within its {cultural_context or 'cultural'} context.

All treatments should prioritize long-term stability and maintain the artwork's research and cultural value. Consultation with specialists in {art_style or 'period'} art and {cultural_context or 'relevant'} cultural heritage is strongly recommended before proceeding with physical intervention.

═══════════════════════════════════════════════════════

IMPORTANT DISCLAIMER:
This analysis is advisory only. All physical restoration work must be performed by certified professional conservators following appropriate institutional guidelines and conservation ethics codes.

═══════════════════════════════════════════════════════
"""
                    st.rerun()
            else:
                st.error("Please provide an artwork description!")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h2>📚 Complete Feature Gallery</h2>', unsafe_allow_html=True)
        st.markdown('<p>Explore all 10 AI-powered restoration features with detailed use cases:</p>', unsafe_allow_html=True)
        
        features = [
            {
                "icon": "🎭",
                "title": "Period-Specific Restoration",
                "desc": "Expert restoration guidance for Baroque and Renaissance artworks using historically accurate techniques",
                "cases": [
                    "Renaissance portraits with sfumato technique",
                    "Baroque paintings with dramatic chiaroscuro",
                    "Dutch Golden Age realistic lighting",
                    "Rococo delicate pastels and gold leaf"
                ]
            },
            {
                "icon": "🕌",
                "title": "Cultural Pattern Enhancement",
                "desc": "Restore and enhance traditional patterns from Mughal, Islamic, Celtic, Asian, and indigenous arts",
                "cases": [
                    "Mughal miniature floral borders",
                    "Islamic geometric tessellations",
                    "Celtic knotwork patterns",
                    "Japanese ukiyo-e wave patterns"
                ]
            },
            {
                "icon": "🗿",
                "title": "Sculptural Reconstruction",
                "desc": "Reconstruct eroded or damaged features in sculptures, statues, and three-dimensional artifacts",
                "cases": [
                    "Greek/Roman marble statues",
                    "Indian temple sculptures",
                    "Egyptian hieroglyphic carvings",
                    "Mayan stele reconstructions"
                ]
            },
            {
                "icon": "🧵",
                "title": "Textile & Tapestry Repair",
                "desc": "Expert restoration for tapestries, embroidery, historical fabrics, and woven artifacts",
                "cases": [
                    "Medieval tapestries (Bayeux style)",
                    "Chinese silk embroidery",
                    "Indian Banarasi sarees",
                    "Persian carpets"
                ]
            },
            {
                "icon": "🎨",
                "title": "Abstract & Modern Art Recovery",
                "desc": "Restore contemporary, abstract, expressionist, and modern artworks",
                "cases": [
                    "Pollock drip paintings",
                    "Rothko color fields",
                    "Abstract impressionism texture recovery",
                    "Minimalist hard-edge works"
                ]
            },
            {
                "icon": "📜",
                "title": "Ancient Manuscript Conservation",
                "desc": "Restore illuminated manuscripts, scrolls, codices, and historical documents",
                "cases": [
                    "Book of Kells style illuminations",
                    "Arabic/Persian calligraphy scrolls",
                    "Sanskrit palm leaf manuscripts",
                    "Dead Sea Scrolls preservation"
                ]
            },
            {
                "icon": "🏛️",
                "title": "Mural & Fresco Revival",
                "desc": "Restore wall paintings, cave art, frescoes, and architectural murals",
                "cases": [
                    "Ajanta/Ellora cave paintings",
                    "Roman Pompeii frescoes",
                    "Mexican muralism (Diego Rivera style)",
                    "Aboriginal rock art"
                ]
            },
            {
                "icon": "🏺",
                "title": "Ceramic & Pottery Reconstruction",
                "desc": "Restore pottery, porcelain, ceramic vessels, and glazed artifacts",
                "cases": [
                    "Chinese Ming dynasty porcelain",
                    "Greek amphoras and pottery",
                    "Native American pottery",
                    "Japanese raku ceramics"
                ]
            },
            {
                "icon": "🔯",
                "title": "Symbol & Iconography Interpretation",
                "desc": "Decode and restore symbolic elements, religious imagery, inscriptions, and cultural icons",
                "cases": [
                    "Egyptian hieroglyphics interpretation",
                    "Christian iconography (Byzantine style)",
                    "Hindu temple symbolism",
                    "Mayan glyph decoding"
                ]
            },
            {
                "icon": "🎓",
                "title": "Educational Content Generation",
                "desc": "Create engaging museum descriptions, exhibition content, and educational materials",
                "cases": [
                    "Museum placard content",
                    "Virtual exhibition descriptions",
                    "Educational tour scripts",
                    "Accessibility-friendly art explanations"
                ]
            }
        ]
        
        st.markdown('<div class="feature-gallery">', unsafe_allow_html=True)
        for feature in features:
            cases_html = "".join([f"<li>{case}</li>" for case in feature['cases']])
            st.markdown(f"""
            <div class="feature-card">
                <span class="feature-icon">{feature['icon']}</span>
                <h3>{feature['title']}</h3>
                <p><strong>Description:</strong> {feature['desc']}</p>
                <p><strong>Use Cases:</strong></p>
                <ul>
                    {cases_html}
                </ul>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("""
        <h2 style="text-align: center; color: #8B4513; font-family: 'Playfair Display', serif; font-size: 2.5rem; margin-bottom: 2rem;">
            🏛️ Cultural & Historical Insights
        </h2>
        <p style="text-align: center; color: #666; font-size: 1.2rem; margin-bottom: 3rem;">
            Explore the rich history and cultural significance of different art periods and traditions
        </p>
        """, unsafe_allow_html=True)
        
        # Cultural Insights Selection
        st.markdown('<div style="background: linear-gradient(135deg, #FFF8DC 0%, #FAEBD7 100%); padding: 2rem; border-radius: 15px; border-left: 6px solid #8B4513; margin-bottom: 2rem;">', unsafe_allow_html=True)
        
        insight_type = st.selectbox(
            "🎨 Select Art Period or Cultural Tradition",
            [
                "Renaissance (Italian)",
                "Baroque (European)",
                "Rococo (French)",
                "Indian Mughal Art",
                "Indian Rajput Painting",
                "Islamic Art & Calligraphy",
                "Japanese Ukiyo-e",
                "Chinese Ming Dynasty",
                "Byzantine Art",
                "Egyptian Art",
                "Greek Classical Art",
                "Aboriginal Australian Art"
            ],
            key="cultural_insight_select"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Cultural Insights Content
        cultural_insights = {
            "Renaissance (Italian)": {
                "emoji": "🎨",
                "period": "14th-17th Century",
                "background": "The Renaissance marked a cultural rebirth in Europe, emphasizing humanism, naturalism, and classical learning. Artists like Leonardo da Vinci, Michelangelo, and Raphael revolutionized art with techniques like linear perspective, sfumato, and anatomical accuracy.",
                "importance": "Renaissance art represents a pivotal shift from medieval symbolism to realistic representation. It laid the foundation for Western art and introduced techniques still used today. The period's emphasis on individual expression and scientific observation changed how humans viewed themselves and their world.",
                "restoration": "Renaissance paintings require extreme care due to fragile egg tempera and oil layers. Restoration must preserve original glazing techniques, gold leaf applications, and the delicate balance of light and shadow. Modern conservators use non-invasive imaging (X-ray, infrared) before any intervention.",
                "techniques": ["Linear Perspective", "Sfumato (Leonardo's technique)", "Chiaroscuro (light/shadow)", "Contrapposto (natural poses)", "Oil glazing layers"],
                "famous_works": ["Mona Lisa", "The Last Supper", "Sistine Chapel Ceiling", "The Birth of Venus"]
            },
            "Baroque (European)": {
                "emoji": "✨",
                "period": "17th-18th Century",
                "background": "Baroque art emerged as a dramatic, emotional response to the Protestant Reformation. Characterized by intense emotion, movement, and theatrical lighting, it was used by the Catholic Church to inspire faith through grandeur and spectacle.",
                "importance": "Baroque art revolutionized emotional expression in painting and sculpture. Artists like Caravaggio, Rembrandt, and Rubens created works with unprecedented drama and realism, influencing everything from architecture to music.",
                "restoration": "Baroque works often feature heavy impasto, dramatic chiaroscuro, and dark varnish layers. Restoration requires careful varnish removal to reveal original colors while preserving the intentional darkness that creates dramatic effects.",
                "techniques": ["Tenebrism (dramatic contrast)", "Dynamic composition", "Rich color palette", "Emotional intensity", "Movement and energy"],
                "famous_works": ["The Night Watch", "Ecstasy of Saint Teresa", "Las Meninas", "The Calling of St Matthew"]
            },
            "Indian Mughal Art": {
                "emoji": "🕌",
                "period": "16th-19th Century",
                "background": "Mughal miniature paintings blend Persian, Indian, and Islamic artistic traditions. Created for royal courts, these intricate works depicted historical events, court life, flora, and fauna with meticulous detail and vibrant colors.",
                "importance": "Mughal art represents a unique synthesis of diverse cultural influences. It documented historical events, preserved literary traditions, and showcased the sophistication of Mughal court culture. The delicate brushwork and natural pigments demonstrate extraordinary craftsmanship.",
                "restoration": "Mughal miniatures are painted on paper with natural pigments and gold. Restoration must address insect damage, pigment fading, and paper deterioration while preserving delicate gold leaf work and fine brushstrokes. Humidity control is critical.",
                "techniques": ["Fine brushwork (single hair brushes)", "Natural mineral pigments", "Gold leaf application", "Intricate border patterns", "Layered composition"],
                "famous_works": ["Hamzanama manuscripts", "Akbarnama", "Padshahnama", "Baburnama illustrations"]
            },
            "Indian Rajput Painting": {
                "emoji": "🎭",
                "period": "16th-19th Century",
                "background": "Rajput paintings from various royal courts (Mewar, Bundi, Kishangarh) depicted Hindu mythology, poetry, and courtly life. These works are known for bold colors, emotional expression, and spiritual themes, particularly illustrations of Krishna and Radha's love story.",
                "importance": "Rajput art preserved Hindu religious narratives and courtly culture. Each school developed distinctive styles, contributing to India's diverse artistic heritage. The paintings express deep devotion (bhakti) and romantic love (shringar).",
                "restoration": "Similar to Mughal art but with distinctive regional techniques. Rajput works often use more vibrant colors and thicker paper. Conservation must respect religious symbolism and regional aesthetic conventions.",
                "techniques": ["Bold flat colors", "Expressive faces and gestures", "Symbolic use of color", "Poetry-inspired compositions", "Regional stylistic variations"],
                "famous_works": ["Bani Thani (Kishangarh)", "Ragamala paintings", "Krishna Lila series", "Mewar Ramayana"]
            },
            "Islamic Art & Calligraphy": {
                "emoji": "🕌",
                "period": "7th Century-Present",
                "background": "Islamic art emphasizes geometric patterns, arabesques, and calligraphy due to religious restrictions on figurative representation. Quranic verses become art through elaborate scripts like Kufic, Naskh, and Thuluth.",
                "importance": "Islamic art demonstrates how religious principles can inspire mathematical precision and aesthetic beauty. Calligraphy elevates written language to divine art, while geometric patterns reflect the infinite nature of Allah.",
                "restoration": "Islamic manuscripts and architectural decorations require specialized knowledge of Arabic scripts and geometric principles. Gold and lapis lazuli pigments need careful conservation. Symmetry and pattern integrity must be preserved.",
                "techniques": ["Sacred geometry", "Arabesque patterns", "Illuminated manuscripts", "Tilework (zellige)", "Various calligraphic scripts"],
                "famous_works": ["Blue Quran", "Alhambra decorations", "Topkapi manuscripts", "Isfahan mosque tiles"]
            },
            "Japanese Ukiyo-e": {
                "emoji": "🎌",
                "period": "17th-19th Century",
                "background": "Ukiyo-e (\"pictures of the floating world\") are woodblock prints depicting kabuki actors, beautiful women, landscapes, and everyday life in Edo-period Japan. Artists like Hokusai and Hiroshige created iconic works that influenced Western Impressionism.",
                "importance": "Ukiyo-e democratized art in Japan and profoundly influenced European artists like Van Gogh and Monet. The prints showcase masterful composition, color gradation, and the Japanese aesthetic principle of capturing fleeting moments.",
                "restoration": "Woodblock prints are vulnerable to light damage, foxing (brown spots), and paper degradation. Restoration requires understanding of traditional Japanese papermaking, natural dyes, and printing techniques. Flattening and backing must be done carefully.",
                "techniques": ["Woodblock printing", "Bokashi (color gradation)", "Bold outlines", "Flat color areas", "Asymmetric composition"],
                "famous_works": ["The Great Wave", "Thirty-Six Views of Mt. Fuji", "Fifty-Three Stations of Tokaido", "Beauties of the Yoshiwara"]
            },
            "Chinese Ming Dynasty": {
                "emoji": "🐉",
                "period": "14th-17th Century",
                "background": "Ming Dynasty art revived classical Chinese traditions after Mongol rule. Known for blue and white porcelain, landscape paintings, and calligraphy, Ming artists emphasized harmony between humans and nature, following principles of Daoism and Confucianism.",
                "importance": "Ming art represents the pinnacle of Chinese ceramic production and landscape painting. The period's artistic output influenced global trade and aesthetic preferences, with Ming porcelain becoming prized worldwide.",
                "restoration": "Ming ceramics require specialized knowledge of high-fire techniques and cobalt pigments. Paintings on silk demand extreme care due to material fragility. Restoration must respect Daoist philosophical principles embedded in compositions.",
                "techniques": ["Blue and white porcelain", "Monochrome ink landscapes", "Calligraphic painting", "Scholar's rocks", "Court painting traditions"],
                "famous_works": ["Ming vases", "Shen Zhou landscapes", "Tang Yin paintings", "Imperial porcelain"]
            },
            "Byzantine Art": {
                "emoji": "☦️",
                "period": "4th-15th Century",
                "background": "Byzantine art served the Eastern Orthodox Church, creating iconic religious images with gold backgrounds, frontal poses, and spiritual symbolism. Mosaics and icons were designed to inspire devotion and represent divine reality rather than earthly appearance.",
                "importance": "Byzantine art preserved classical traditions through the medieval period and established the visual language of Orthodox Christianity. The stylized forms and gold backgrounds created a sense of the sacred that transcends naturalism.",
                "restoration": "Byzantine mosaics and icons require specialized conservation of gold leaf, tempera on wood panels, and glass tesserae. Religious protocols must be observed, and restorations should maintain the spiritual character of the work.",
                "techniques": ["Gold leaf backgrounds", "Egg tempera", "Mosaic tesserae", "Hierarchical scaling", "Symbolic color use"],
                "famous_works": ["Hagia Sophia mosaics", "Vladimir Mother of God", "Ravenna mosaics", "Christ Pantocrator"]
            },
            "Renaissance (Italian)": {
                "emoji": "🏛️",
                "period": "3000-30 BCE",
                "background": "Ancient Egyptian art served religious and political purposes, depicting gods, pharaohs, and the afterlife. The strict artistic conventions (profile view for faces, frontal view for torsos) lasted for millennia, demonstrating cultural continuity.",
                "importance": "Egyptian art provides insight into one of history's longest-lasting civilizations. Tomb paintings, sculptures, and hieroglyphics preserved knowledge of daily life, religious beliefs, and political structures for over 3,000 years.",
                "restoration": "Egyptian artifacts require climate control due to their age and the dry environment they're adapted to. Pigments derived from minerals need careful stabilization. Many works involve stone, papyrus, or plaster, each requiring specialized treatment.",
                "techniques": ["Hierarchical scale", "Composite view", "Register composition", "Symbolic color", "Relief carving"],
                "famous_works": ["Tutankhamun's mask", "Nefertiti bust", "Tomb of Nefertari", "Book of the Dead papyri"]
            },
            "Greek Classical Art": {
                "emoji": "🏛️",
                "period": "5th-4th Century BCE",
                "background": "Classical Greek art emphasized ideal beauty, proportion, and naturalism. Sculptors like Phidias and Praxiteles created works that embodied philosophical ideals of harmony and balance, influencing Western art for millennia.",
                "importance": "Greek classical art established standards of beauty and proportion that shaped Western civilization. The emphasis on the human form, mathematical ratios, and idealized naturalism continues to influence art, architecture, and aesthetics.",
                "restoration": "Ancient Greek sculptures often survive as Roman copies or fragments. Restoration involves careful cleaning of marble, bronze conservation, and ethical decisions about reconstruction. Missing pieces may be left unfilled to respect historical integrity.",
                "techniques": ["Contrapposto stance", "Golden ratio proportions", "Idealized naturalism", "Bronze hollow-casting", "Polychrome marble"],
                "famous_works": ["Parthenon sculptures", "Discobolus", "Venus de Milo", "Winged Victory"]
            },
            "Aboriginal Australian Art": {
                "emoji": "🪃",
                "period": "40,000+ years ago-Present",
                "background": "Aboriginal art is one of the world's oldest continuous art traditions, depicting Dreamtime stories, ancestral beings, and connection to land. Rock paintings, bark paintings, and dot paintings encode spiritual knowledge and cultural laws.",
                "importance": "Aboriginal art represents humanity's oldest living art tradition, preserving tens of thousands of years of cultural knowledge. The art is inseparable from spiritual beliefs, law, and connection to country (land).",
                "restoration": "Aboriginal art restoration requires consultation with traditional owners and respect for sacred content. Rock art conservation must consider environmental exposure. Contemporary works on canvas need protection from UV damage while preserving natural ochres.",
                "techniques": ["Dot painting", "X-ray art (showing internal organs)", "Natural ochre pigments", "Symbolic mapping", "Layered narratives"],
                "famous_works": ["Bradshaw paintings", "X-ray art (Kakadu)", "Papunya Tula movement", "Wandjina spirit figures"]
            }
        }
        
        # Display selected insight
        if insight_type in cultural_insights:
            insight = cultural_insights[insight_type]
            
            # Header card
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #8B4513 0%, #A0522D 100%); color: white; padding: 2rem; border-radius: 15px; text-align: center; margin-bottom: 2rem; box-shadow: 0 8px 25px rgba(0,0,0,0.2);">
                <div style="font-size: 4rem; margin-bottom: 1rem;">{insight['emoji']}</div>
                <h2 style="color: white; margin: 0; font-family: 'Playfair Display', serif; font-size: 2.5rem;">{insight_type}</h2>
                <p style="margin: 0.5rem 0 0 0; font-size: 1.3rem; opacity: 0.95;">📅 {insight['period']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Historical Background
            with st.expander("📚 Historical Background", expanded=True):
                st.markdown(f"""
                <div style="padding: 1rem; background: #FFFEF7; border-radius: 10px; border-left: 4px solid #8B4513;">
                    <p style="font-size: 1.1rem; line-height: 1.8; color: #333;">{insight['background']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Cultural Importance
            with st.expander("⭐ Why This Art is Culturally Important", expanded=True):
                st.markdown(f"""
                <div style="padding: 1rem; background: #FFF8E1; border-radius: 10px; border-left: 4px solid #D2691E;">
                    <p style="font-size: 1.1rem; line-height: 1.8; color: #333;">{insight['importance']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Restoration Rules
            with st.expander("🛠️ Typical Restoration Rules for This Period", expanded=True):
                st.markdown(f"""
                <div style="padding: 1rem; background: #E8F5E9; border-radius: 10px; border-left: 4px solid #228B22;">
                    <p style="font-size: 1.1rem; line-height: 1.8; color: #333;">{insight['restoration']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Key Techniques
            st.markdown("""
            <h3 style="color: #8B4513; font-family: 'Playfair Display', serif; margin-top: 2rem; font-size: 1.8rem;">
                🎨 Key Artistic Techniques
            </h3>
            """, unsafe_allow_html=True)
            
            cols = st.columns(2)
            for idx, technique in enumerate(insight['techniques']):
                with cols[idx % 2]:
                    st.markdown(f"""
                    <div style="background: white; padding: 1rem; border-radius: 10px; margin-bottom: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-left: 3px solid #CD853F;">
                        <p style="margin: 0; color: #8B4513; font-weight: bold;">✓ {technique}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Famous Works
            st.markdown("""
            <h3 style="color: #8B4513; font-family: 'Playfair Display', serif; margin-top: 2rem; font-size: 1.8rem;">
                🖼️ Famous Masterpieces
            </h3>
            """, unsafe_allow_html=True)
            
            for work in insight['famous_works']:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #FFF8DC 0%, #FAEBD7 100%); padding: 1rem; border-radius: 10px; margin-bottom: 0.8rem; border-left: 4px solid #8B4513;">
                    <p style="margin: 0; color: #333; font-size: 1.1rem;">🎨 <strong>{work}</strong></p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab4:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("""
        <h2 style="text-align: center; color: #8B4513; font-family: 'Playfair Display', serif; font-size: 2.5rem; margin-bottom: 2rem;">
            💰 Conservation Cost Calculator
        </h2>
        <p style="text-align: center; color: #666; font-size: 1.1rem; margin-bottom: 3rem;">
            Get accurate cost estimates for your art restoration project
        </p>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="display: flex; justify-content: center; margin: 2rem 0;">
            <div style="background: linear-gradient(135deg, #FFD700 0%, #FFA500 50%, #FF8C00 100%); 
                        padding: 2rem; border-radius: 50%; width: 140px; height: 140px; 
                        display: flex; align-items: center; justify-content: center;
                        box-shadow: 0 12px 40px rgba(255, 152, 0, 0.4);
                        animation: rotate 8s linear infinite;">
                <div style="font-size: 5rem;">💰</div>
            </div>
        </div>
        <style>
            @keyframes rotate {
                from { transform: rotate(0deg); }
                to { transform: rotate(360deg); }
            }
        </style>
        """, unsafe_allow_html=True)
        
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown('<div style="padding: 2rem; background: linear-gradient(135deg, #FFF8DC 0%, #FAEBD7 100%); border-radius: 15px; border-left: 5px solid #8B4513;">', unsafe_allow_html=True)
            st.markdown('<h3 style="color: #8B4513; margin-top: 0;">📏 Artwork Dimensions</h3>', unsafe_allow_html=True)
            
            width_cm = st.number_input("Width (cm)", min_value=1, max_value=500, value=50, key="width_input_calc")
            height_cm = st.number_input("Height (cm)", min_value=1, max_value=500, value=70, key="height_input_calc")
            artwork_area = (width_cm * height_cm) / 10000
            
            st.markdown(f'<p style="color: #666; font-size: 0.95rem; margin-top: 1rem;">📐 <strong>Total Area:</strong> {artwork_area:.2f} m²</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div style="padding: 2rem; background: linear-gradient(135deg, #FFF8DC 0%, #FAEBD7 100%); border-radius: 15px; border-left: 5px solid #8B4513; margin-top: 1.5rem;">', unsafe_allow_html=True)
            st.markdown('<h3 style="color: #8B4513; margin-top: 0;">🎨 Artwork Type</h3>', unsafe_allow_html=True)
            
            artwork_types = {
                "Oil Painting": {"base_rate": 150, "complexity": 1.2},
                "Watercolor/Paper": {"base_rate": 120, "complexity": 1.0},
                "Sculpture (Stone)": {"base_rate": 200, "complexity": 1.5},
                "Sculpture (Bronze)": {"base_rate": 250, "complexity": 1.6},
                "Textile/Tapestry": {"base_rate": 180, "complexity": 1.3},
                "Manuscript/Document": {"base_rate": 140, "complexity": 1.1},
                "Mural/Fresco": {"base_rate": 220, "complexity": 1.4},
                "Ceramic/Pottery": {"base_rate": 160, "complexity": 1.2}
            }
            
            selected_artwork = st.selectbox("Select artwork type:", list(artwork_types.keys()), key="artwork_type_calc")
            artwork_info = artwork_types[selected_artwork]
            st.markdown(f'<p style="color: #666; font-size: 0.9rem; margin-top: 1rem;">💵 Base Rate: ${artwork_info["base_rate"]}/m² | Complexity: {artwork_info["complexity"]}x</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_right:
            st.markdown('<div style="padding: 2rem; background: linear-gradient(135deg, #F0E68C 0%, #FFE4B5 100%); border-radius: 15px; border-left: 5px solid #D2691E;">', unsafe_allow_html=True)
            st.markdown('<h3 style="color: #8B4513; margin-top: 0;">🔍 Damage Severity</h3>', unsafe_allow_html=True)
            
            damage_levels = ["Minor (5-10% damage)", "Moderate (10-25% damage)", "Significant (25-50% damage)", "Severe (50-75% damage)", "Critical (75-100% damage)"]
            damage_multipliers = [1.0, 1.3, 1.6, 2.0, 2.5]
            damage_index = st.select_slider("Select severity level:", options=range(len(damage_levels)), value=1, format_func=lambda x: damage_levels[x], key="damage_severity_calc")
            damage_mult = damage_multipliers[damage_index]
            st.markdown(f'<p style="color: #666; font-size: 0.9rem; margin-top: 1rem;">⚠️ Cost Multiplier: {damage_mult}x</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div style="padding: 2rem; background: linear-gradient(135deg, #F0E68C 0%, #FFE4B5 100%); border-radius: 15px; border-left: 5px solid #D2691E; margin-top: 1.5rem;">', unsafe_allow_html=True)
            st.markdown('<h3 style="color: #8B4513; margin-top: 0;">⏰ Urgency Level</h3>', unsafe_allow_html=True)
            urgency_options = {"Standard (6-8 weeks)": 1.0, "Priority (3-4 weeks)": 1.3, "Emergency (1-2 weeks)": 1.6}
            selected_urgency = st.radio("Select urgency:", list(urgency_options.keys()), key="urgency_calc", horizontal=False)
            urgency_mult = urgency_options[selected_urgency]
            st.markdown(f'<p style="color: #666; font-size: 0.9rem; margin-top: 1rem;">📍 Timeline Multiplier: {urgency_mult}x</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div style="padding: 2rem; background: linear-gradient(135deg, #E6F3FF 0%, #E0F4FF 100%); border-radius: 15px; border-left: 5px solid #1976D2; margin-top: 1.5rem;">', unsafe_allow_html=True)
        st.markdown('<h3 style="color: #1976D2; margin-top: 0;">🛠️ Additional Services</h3>', unsafe_allow_html=True)
        services = {"Professional Photography & Documentation": 250, "UV/Infrared Analysis": 300, "Chemical Analysis & Testing": 400, "Custom Framing/Mounting": 350, "Climate-Controlled Storage (monthly)": 150, "Insurance & Certification": 200}
        selected_services = st.multiselect("Select additional services:", list(services.keys()), key="services_calc")
        services_cost = sum([services[s] for s in selected_services])
        st.markdown(f'<p style="color: #333; font-size: 0.95rem; margin-top: 1rem;">💰 <strong>Services Total:</strong> ${services_cost}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<hr style="border: 2px solid #D2691E; margin: 2rem 0;">', unsafe_allow_html=True)
        st.markdown('<h2 style="text-align: center; color: #8B4513; font-family: \'Playfair Display\', serif; font-size: 2.2rem; margin: 2rem 0;">💎 Cost Estimation Results</h2>', unsafe_allow_html=True)
        
        base_cost = artwork_info["base_rate"] * artwork_area * artwork_info["complexity"]
        damage_cost = base_cost * damage_mult
        labor_hours = (artwork_area * 20) * damage_mult
        labor_cost = labor_hours * 45
        materials_cost = base_cost * 0.3 * damage_mult
        total_before_urgency = damage_cost + labor_cost + materials_cost + services_cost
        total_cost = total_before_urgency * urgency_mult
        min_estimate = total_cost * 0.85
        max_estimate = total_cost * 1.15
        timeline_weeks = (6 + (damage_index * 1.5)) * urgency_mult
        
        col_res1, col_res2, col_res3 = st.columns(3)
        with col_res1:
            st.markdown(f'<div style="background: linear-gradient(135deg, #FFF8DC 0%, #FAEBD7 100%); padding: 2rem; border-radius: 15px; text-align: center; box-shadow: 0 6px 20px rgba(0,0,0,0.1); border-left: 5px solid #FFB90F;"><div style="font-size: 2.5rem; margin-bottom: 0.5rem;">💵</div><p style="color: #666; font-size: 0.9rem; margin: 0.5rem 0 0 0;">Estimated Cost Range</p><h3 style="color: #8B4513; margin: 0.8rem 0; font-family: \'Playfair Display\', serif;">${min_estimate:,.0f} - ${max_estimate:,.0f}</h3><p style="color: #999; font-size: 0.85rem; margin: 0;">Base: ${total_cost:,.0f}</p></div>', unsafe_allow_html=True)
        with col_res2:
            st.markdown(f'<div style="background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%); padding: 2rem; border-radius: 15px; text-align: center; box-shadow: 0 6px 20px rgba(0,0,0,0.1); border-left: 5px solid #4CAF50;"><div style="font-size: 2.5rem; margin-bottom: 0.5rem;">⏱️</div><p style="color: #666; font-size: 0.9rem; margin: 0.5rem 0 0 0;">Project Timeline</p><h3 style="color: #2E7D32; margin: 0.8rem 0; font-family: \'Playfair Display\', serif;">{timeline_weeks:.1f} weeks</h3><p style="color: #999; font-size: 0.85rem; margin: 0;">{int(timeline_weeks * 5)} working days</p></div>', unsafe_allow_html=True)
        with col_res3:
            st.markdown(f'<div style="background: linear-gradient(135deg, #F3E5F5 0%, #E1BEE7 100%); padding: 2rem; border-radius: 15px; text-align: center; box-shadow: 0 6px 20px rgba(0,0,0,0.1); border-left: 5px solid #9C27B0;"><div style="font-size: 2.5rem; margin-bottom: 0.5rem;">👨‍🔧</div><p style="color: #666; font-size: 0.9rem; margin: 0.5rem 0 0 0;">Labor Hours</p><h3 style="color: #6A1B9A; margin: 0.8rem 0; font-family: \'Playfair Display\', serif;">{labor_hours:.0f} hours</h3><p style="color: #999; font-size: 0.85rem; margin: 0;">${labor_cost:,.0f}</p></div>', unsafe_allow_html=True)
        
        st.markdown('<h3 style="color: #8B4513; margin-top: 2rem; font-family: \'Playfair Display\', serif;">📊 Detailed Cost Breakdown</h3>', unsafe_allow_html=True)
        breakdown_col1, breakdown_col2 = st.columns(2)
        with breakdown_col1:
            st.markdown(f'<div style="background: white; padding: 2rem; border-radius: 12px; border: 2px solid #D2B48C;"><h4 style="color: #8B4513; margin-top: 0;">💰 Cost Components</h4><div style="line-height: 2.2; color: #555; font-size: 0.95rem;"><p><strong>Restoration Work:</strong> ${damage_cost:,.0f}</p><p><strong>Labor Cost:</strong> ${labor_cost:,.0f}</p><p><strong>Materials:</strong> ${materials_cost:,.0f}</p><p><strong>Additional Services:</strong> ${services_cost:,.0f}</p><hr style="border: 1px solid #D2B48C; margin: 0.5rem 0;"><p style="font-size: 1.1rem; color: #8B4513;"><strong>Total Estimated Cost:</strong> ${total_cost:,.0f}</p></div></div>', unsafe_allow_html=True)
        with breakdown_col2:
            st.markdown(f'<div style="background: white; padding: 2rem; border-radius: 12px; border: 2px solid #D2B48C;"><h4 style="color: #8B4513; margin-top: 0;">📈 Cost Multipliers Applied</h4><div style="line-height: 2.2; color: #555; font-size: 0.95rem;"><p>🎨 <strong>Artwork Type:</strong> {artwork_info["complexity"]}x</p><p>🔍 <strong>Damage Severity:</strong> {damage_mult}x</p><p>⏰ <strong>Urgency Level:</strong> {urgency_mult}x</p><p>📐 <strong>Artwork Area:</strong> {artwork_area:.2f} m²</p><hr style="border: 1px solid #D2B48C; margin: 0.5rem 0;"><p style="font-size: 0.9rem; color: #666;">✅ Includes ±15% margin for contingencies</p></div></div>', unsafe_allow_html=True)
        
        st.markdown('<div style="background: #FFF9E6; padding: 2rem; border-radius: 12px; border-left: 5px solid #FF9800; margin-top: 2rem;"><p style="color: #8B4513; margin: 0; font-weight: bold;">📝 Important Note:</p><p style="color: #666; margin: 0.5rem 0 0 0; font-size: 0.95rem;">This calculator provides estimates based on standard conservation industry rates. Actual costs may vary based on artwork condition, accessibility, location, and specialist availability. Please consult with certified conservators for detailed project quotes.</p></div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# Results Page
elif st.session_state.page == 'results':
    st.markdown("""
    <div class="main-header">
        <h1 class="main-title">🎨 ArtRestorer AI</h1>
        <p class="subtitle">AI-Powered Smart Assistance for Art Restoration & Cultural Heritage Preservation</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h2 style="color: #8B4513; font-size: 2.5rem; margin-bottom: 0.5rem; font-family: 'Playfair Display', serif;">🎯 AI Restoration Analysis Complete</h2>
        <p style="color: #666; font-size: 1.1rem;">Comprehensive expert guidance generated for your artwork</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #8B4513 0%, #A0522D 100%); color: white; padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem;">
        <h3 style="margin: 0 0 0.5rem 0; color: white;">Analysis for: {st.session_state.user_data['name']}</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-top: 1rem;">
            <div><strong>📁 Project:</strong> {st.session_state.user_data['artwork_type']}</div>
            <div><strong>👤 Role:</strong> {st.session_state.user_data['role']}</div>
            <div><strong>🎯 Goal:</strong> {st.session_state.user_data['goal']}</div>
            <div><strong>📅 Date:</strong> {datetime.now().strftime('%B %d, %Y')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="result-box">', unsafe_allow_html=True)
    
    col_a, col_b = st.columns([3, 1])
    with col_a:
        st.markdown('<h3 style="margin: 0; font-size: 2.2rem;">📋 Detailed Analysis Report</h3>', unsafe_allow_html=True)
    with col_b:
        if st.download_button(
            label="📥 Download",
            data=f"""ArtRestorer AI - Restoration Analysis Report
═══════════════════════════════════════════════════════

PREPARED FOR: {st.session_state.user_data['name']}
ROLE: {st.session_state.user_data['role']}
ARTWORK TYPE: {st.session_state.user_data['artwork_type']}
PROJECT GOAL: {st.session_state.user_data['goal']}

DATE: {datetime.now().strftime('%B %d, %Y')}

═══════════════════════════════════════════════════════

{st.session_state.result_text}

═══════════════════════════════════════════════════════
Generated by ArtRestorer AI
Powered by Google Gemini AI
HeritaTech Solutions

This analysis is advisory only. Always consult certified conservators
for physical restoration work.
""",
            file_name=f"ArtRestorer_AI_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            key="download_report"
        ):
            st.success("✅ Report downloaded successfully!")
    
    st.markdown('<hr style="border: 2px solid #D2691E; margin: 1rem 0;">', unsafe_allow_html=True)
    
    # Format the result text with HTML for better presentation
    formatted_result = st.session_state.result_text.replace(
        "COMPREHENSIVE RESTORATION ANALYSIS",
        "🎨 <span style='font-size: 2rem; font-weight: bold; color: #8B4513;'>COMPREHENSIVE RESTORATION ANALYSIS</span>"
    )
    
    # Add styling to section headers
    formatted_result = formatted_result.replace("EXPERT RESTORATION GUIDANCE:", 
        "<br><h2 style='color: #8B4513; font-family: \"Playfair Display\", serif; margin-top: 2rem;'>👨‍🎨 EXPERT RESTORATION GUIDANCE</h2>")
    
    formatted_result = formatted_result.replace("1. HISTORICAL CONTEXT & SIGNIFICANCE",
        "<h3 style='color: #A0522D; margin-top: 2rem;'>📚 1. HISTORICAL CONTEXT & SIGNIFICANCE</h3>")
    formatted_result = formatted_result.replace("2. CONDITION ASSESSMENT",
        "<h3 style='color: #A0522D; margin-top: 2rem;'>🔍 2. CONDITION ASSESSMENT</h3>")
    formatted_result = formatted_result.replace("3. RESTORATION METHODOLOGY",
        "<h3 style='color: #A0522D; margin-top: 2rem;'>🛠️ 3. RESTORATION METHODOLOGY</h3>")
    formatted_result = formatted_result.replace("4. MATERIALS & TECHNIQUES",
        "<h3 style='color: #A0522D; margin-top: 2rem;'>🎨 4. MATERIALS & TECHNIQUES</h3>")
    formatted_result = formatted_result.replace("5. CULTURAL & HISTORICAL CONSIDERATIONS",
        "<h3 style='color: #A0522D; margin-top: 2rem;'>🏛️ 5. CULTURAL & HISTORICAL CONSIDERATIONS</h3>")
    formatted_result = formatted_result.replace("6. TECHNICAL SPECIFICATIONS",
        "<h3 style='color: #A0522D; margin-top: 2rem;'>⚙️ 6. TECHNICAL SPECIFICATIONS</h3>")
    formatted_result = formatted_result.replace("7. CONSERVATION CHALLENGES & SOLUTIONS",
        "<h3 style='color: #A0522D; margin-top: 2rem;'>💡 7. CONSERVATION CHALLENGES & SOLUTIONS</h3>")
    formatted_result = formatted_result.replace("8. PREVENTIVE CONSERVATION",
        "<h3 style='color: #A0522D; margin-top: 2rem;'>🛡️ 8. PREVENTIVE CONSERVATION</h3>")
    formatted_result = formatted_result.replace("9. ETHICAL CONSIDERATIONS",
        "<h3 style='color: #A0522D; margin-top: 2rem;'>⚖️ 9. ETHICAL CONSIDERATIONS</h3>")
    formatted_result = formatted_result.replace("10. DOCUMENTATION & REPORTING",
        "<h3 style='color: #A0522D; margin-top: 2rem;'>📝 10. DOCUMENTATION & REPORTING</h3>")
    
    formatted_result = formatted_result.replace("CONCLUSION:",
        "<h2 style='color: #8B4513; font-family: \"Playfair Display\", serif; margin-top: 2rem;'>✅ CONCLUSION</h2>")
    formatted_result = formatted_result.replace("IMPORTANT DISCLAIMER:",
        "<h3 style='color: #D2691E; margin-top: 2rem;'>⚠️ IMPORTANT DISCLAIMER</h3>")
    
    # Style subsections
    formatted_result = formatted_result.replace("a) DOCUMENTATION PHASE", "<strong style='color: #8B4513;'>📸 a) DOCUMENTATION PHASE</strong>")
    formatted_result = formatted_result.replace("b) STABILIZATION PHASE", "<strong style='color: #8B4513;'>🔧 b) STABILIZATION PHASE</strong>")
    formatted_result = formatted_result.replace("c) CLEANING PHASE", "<strong style='color: #8B4513;'>🧹 c) CLEANING PHASE</strong>")
    formatted_result = formatted_result.replace("d) RESTORATION PHASE", "<strong style='color: #8B4513;'>🎨 d) RESTORATION PHASE</strong>")
    
    formatted_result = formatted_result.replace("Challenge 1:", "<strong style='color: #CD853F;'>⚠️ Challenge 1:</strong>")
    formatted_result = formatted_result.replace("Challenge 2:", "<strong style='color: #CD853F;'>⚠️ Challenge 2:</strong>")
    formatted_result = formatted_result.replace("Challenge 3:", "<strong style='color: #CD853F;'>⚠️ Challenge 3:</strong>")
    formatted_result = formatted_result.replace("Challenge 4:", "<strong style='color: #CD853F;'>⚠️ Challenge 4:</strong>")
    
    formatted_result = formatted_result.replace("Solution:", "<strong style='color: #228B22;'>✓ Solution:</strong>")
    
    formatted_result = formatted_result.replace("Color Palette Recommendations:", "<strong style='color: #8B4513;'>🎨 Color Palette Recommendations:</strong>")
    formatted_result = formatted_result.replace("Application Techniques:", "<strong style='color: #8B4513;'>🖌️ Application Techniques:</strong>")
    formatted_result = formatted_result.replace("Environmental Controls:", "<strong style='color: #8B4513;'>🌡️ Environmental Controls:</strong>")
    formatted_result = formatted_result.replace("Handling & Display:", "<strong style='color: #8B4513;'>🖐️ Handling & Display:</strong>")
    
    # Add background to important sections
    formatted_result = formatted_result.replace("═══════════════════════════════════════════════════════",
        "<hr style='border: 2px solid #D2691E; margin: 2rem 0;'>")
    
    st.markdown(f'<div class="result-text" style="font-size: 1.05rem; line-height: 2;">{formatted_result}</div>', unsafe_allow_html=True)
    st.markdown('<hr style="border: 1px solid #D2691E; margin: 2rem 0;">', unsafe_allow_html=True)
    
    st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
    if st.button("🔄 Analyze Another Artwork", key="back_btn"):
        st.session_state.page = 'main'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Feedback Button Section - ONLY ON RESULTS PAGE
    st.markdown("""
    <div style="text-align: center; margin: 4rem 0 2rem 0; padding: 2rem;">
        <h2 style="font-family: 'Playfair Display', serif; color: #8B4513; font-size: 2.5rem; margin-bottom: 1rem;">💬 Share Your Experience</h2>
        <p style="color: #666; font-size: 1.2rem; margin-bottom: 2rem;">Your feedback helps us improve ArtRestorer AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    col_fb1, col_fb2, col_fb3 = st.columns([1, 1, 1])
    with col_fb2:
        if st.button("📝 Open Feedback Form", key="open_feedback_results", use_container_width=True):
            st.session_state.show_feedback_results = True
    
    # Feedback Form - Shows when button is clicked
    if 'show_feedback_results' not in st.session_state:
        st.session_state.show_feedback_results = False
    
    if st.session_state.show_feedback_results:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #FFF8DC 0%, #FAEBD7 100%); border-radius: 20px; padding: 3rem 2rem; margin: 2rem 0; box-shadow: 0 8px 30px rgba(0,0,0,0.15); border: 4px solid #8B4513; animation: slideDown 0.4s ease;">
            <h2 style="font-family: 'Playfair Display', serif; color: #8B4513; text-align: center; font-size: 2.8rem; margin-bottom: 1rem;">📝 We Value Your Feedback</h2>
            <p style="text-align: center; color: #666; font-size: 1.2rem; margin-bottom: 2rem;">Help us improve ArtRestorer AI by sharing your experience</p>
        </div>
        <style>
            @keyframes slideDown {
                from { opacity: 0; transform: translateY(-20px); }
                to { opacity: 1; transform: translateY(0); }
            }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown('<div style="background: white; border-radius: 15px; padding: 2.5rem; box-shadow: 0 6px 20px rgba(0,0,0,0.1); border-left: 6px solid #8B4513; max-width: 900px; margin: 0 auto 3rem auto;">', unsafe_allow_html=True)
        
        col_fb1, col_fb2 = st.columns(2)
        
        with col_fb1:
            feedback_name = st.text_input("👤 Your Name", key="feedback_name_results", placeholder="Enter your full name")
            feedback_email = st.text_input("📧 Email Address (Optional)", key="feedback_email_results", placeholder="your.email@example.com")
            feedback_rating = st.select_slider(
                "⭐ Overall Rating",
                options=["⭐ Poor", "⭐⭐ Fair", "⭐⭐⭐ Good", "⭐⭐⭐⭐ Very Good", "⭐⭐⭐⭐⭐ Excellent"],
                value="⭐⭐⭐ Good",
                key="feedback_rating_results"
            )
        
        with col_fb2:
            feedback_category = st.selectbox(
                "📌 Feedback Category",
                ["General Feedback", "Feature Request", "Bug Report", "Accuracy of Analysis", "User Experience", "Documentation", "Other"],
                key="feedback_category_results"
            )
            feedback_recommend = st.radio(
                "💡 Would you recommend ArtRestorer AI?",
                ["👍 Yes", "🤔 Maybe", "👎 No"],
                horizontal=True,
                key="feedback_recommend_results"
            )
        
        feedback_comments = st.text_area(
            "💬 Your Comments & Suggestions",
            placeholder="Share your thoughts, suggestions, or report any issues. We read every piece of feedback!",
            height=180,
            key="feedback_comments_results"
        )
        
        col_fb_btn1, col_fb_btn2, col_fb_btn3 = st.columns([1, 1, 1])
        with col_fb_btn1:
            if st.button("❌ Cancel", key="cancel_feedback_results", use_container_width=True):
                st.session_state.show_feedback_results = False
                st.rerun()
        with col_fb_btn2:
            if st.button("📤 Submit Feedback", key="submit_feedback_results", use_container_width=True):
                if feedback_name and feedback_comments:
                    st.success("✅ Thank you for your valuable feedback! Your input helps us improve ArtRestorer AI.")
                    st.balloons()
                    import time
                    time.sleep(2)
                    st.session_state.show_feedback_results = False
                    st.rerun()
                else:
                    st.error("⚠️ Please provide your name and comments before submitting.")
        
        st.markdown('</div>', unsafe_allow_html=True)