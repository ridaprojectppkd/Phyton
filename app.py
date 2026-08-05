import streamlit as st
from sign_language import run_sign, stop_speech as stop_sign
from object_assistant import run_assistant, stop_speech as stop_object

# 🔥 MATIKAN MENU DEFAULT STREAMLIT
st.set_page_config(
    page_title="Smart AI Vision",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ❌ HIDE menu atas + footer
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ✅ SIDEBAR MENU CUSTOM
menu = st.sidebar.radio(
    "Menu",
    ["Home", "Object Detection", "Sign Language"]
)

# =========================
# HOME
# =========================
if menu == "Home":

    st.markdown("""
    <style>
    .hero {
        text-align: center;
        padding: 50px;
    }
    .hero h1 {
        font-size: 50px;
        color: #4CAF50;
    }
    .hero p {
        font-size: 20px;
        color: #555;
    }
    .card-container {
        display: flex;
        justify-content: center;
        gap: 30px;
        margin-top: 50px;
    }
    .card {
        background: white;
        padding: 30px;
        border-radius: 15px;
        width: 250px;
        text-align: center;
        box-shadow: 0px 4px 20px rgba(0,0,0,0.1);
        transition: 0.3s;
        cursor: pointer;
    }
    .card:hover {
        transform: scale(1.05);
    }
    .card a {
        text-decoration: none;
        color: black;
    }
    </style>

    <div class="hero">
        <h1>🚀 Smart AI Vision</h1>
        <p>Deteksi objek & bahasa isyarat dengan AI modern</p>
    </div>

    <div class="card-container">

        <div class="card">
            <a href="?page=object">
                <h3>👁 Object Detection</h3>
                <p>Deteksi objek secara real-time</p>
            </a>
        </div>

        <div class="card">
            <a href="?page=sign">
                <h3>🤟 Sign Language</h3>
                <p>Terjemahkan bahasa isyarat</p>
            </a>
        </div>

    </div>
    """, unsafe_allow_html=True)

    # 🔥 HANDLE NAVIGASI DARI CARD
    query = st.query_params

    if query.get("page") == "object":
        stop_sign()
        stop_object()
        run_assistant()

    elif query.get("page") == "sign":
        stop_object()
        stop_sign()
        run_sign()

# =========================
# OBJECT DETECTION
# =========================
elif menu == "Object Detection":
    stop_sign()
    stop_object()
    run_assistant()

# =========================
# SIGN LANGUAGE
# =========================
elif menu == "Sign Language":
    stop_object()
    stop_sign()
    run_sign()