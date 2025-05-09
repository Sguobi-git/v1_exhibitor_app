import streamlit as st
import base64
import os

# Page configuration
st.set_page_config(
    page_title="Expo Convention",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide Streamlit components and make truly full screen
hide_streamlit_style = """
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {
        padding-top: 0;
        padding-bottom: 0;
        max-width: 100%;
        width: 100%;
    }
    .main .block-container {
        margin: 0;
        max-width: 100%;
        padding-left: 0;
        padding-right: 0;
    }
    .stApp {
        margin: 0;
        padding: 0;
        width: 100vw;
        height: 100vh;
        overflow: hidden;
    }
    section.main {
        margin: 0;
        padding: 0;
        width: 100vw;
    }
    
    /* Button positioning */
    .stButton {
        display: flex;
        justify-content: center;
        align-items: center;
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        z-index: 999;
        width: auto;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: white;
        color: black;
        border: 2px solid black;
        padding: 15px 35px;
        font-size: 1.5rem;
        border-radius: 50px;
        cursor: pointer;
        transition: all 0.3s ease;
        font-weight: 500;
        text-transform: uppercase;
        font-family: 'Poppins', sans-serif;
    }
    
    .stButton > button:hover {
        background-color: #f0f0f0;
        transform: scale(1.1);
        box-shadow: 0 0 10px rgba(0,0,0,0.2);
    }
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Function to encode files to base64
def get_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# Encode video and logo
# video_base64 = get_base64("S:/Work (Souhail)/Archive/Exhibitor Version/expo-app/assets/intro_video.mp4")
video_base64 = get_base64("v0 Exhibitor app/assets/intro_video.mp4")
# logo_base64 = get_base64("S:/Work (Souhail)/Archive/Exhibitor Version/expo-app/assets/expo_blanco.png")
logo_base64 = get_base64("v0 Exhibitor app/assets/expo_blanco.png")

# Create a session state object if one doesn't exist
if 'navigate_to_home' not in st.session_state:
    st.session_state.navigate_to_home = False

# Create a function to set the state value
def set_navigate_to_home():
    st.session_state.navigate_to_home = True

# Check if we need to navigate to Home
if st.session_state.navigate_to_home:
    # Reset the state
    st.session_state.navigate_to_home = False
    # Use streamlit's native navigation
    st.switch_page("pages/Home.py")

# HTML with embedded video and top-left logo
html_code = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@500&display=swap');
body {{
    margin: 0;
    padding: 0;
    overflow: hidden;
    font-family: 'Poppins', sans-serif;
    width: 100vw;
    height: 100vh;
}}
.video-container {{
    position: absolute;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    overflow: hidden;
}}
video {{
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
}}
.top-left-container {{
    position: absolute;
    top: 30px;
    left: 30px;
    z-index: 20;
    text-align: left;
    color: white;
}}
.welcome-text {{
    font-size: 1.2rem;
    color: white;
    margin-bottom: 8px;
    letter-spacing: 2px;
}}
.logo {{
    width: 300px;
}}
</style>
<div class="video-container">
    <video autoplay loop muted playsinline>
        <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
        Your browser does not support the video tag.
    </video>
    <div class="top-left-container">
        <div class="welcome-text">POWERED BY</div>
        <img class="logo" src="data:image/png;base64,{logo_base64}" alt="Expo Logo"/>
    </div>
</div>
"""

# Display the HTML (video and logo)
st.components.v1.html(html_code, height=1000, scrolling=False)

# Add the centrally positioned button
# This button will be positioned by CSS
if st.button("Let's show off together", on_click=set_navigate_to_home, key="enter_button"):
    pass
