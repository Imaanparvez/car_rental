import streamlit as st
import requests
import os
from datetime import date, timedelta
import base64

BACKEND_URL = os.environ.get("BACKEND_URL")

if not BACKEND_URL:
    st.error("❌ BACKEND_URL missing")
    st.stop()

st.set_page_config(page_title="AI Car Rental", layout="wide")

# -----------------------------
# GLOBAL CSS (FOR FULLSCREEN HERO)
# -----------------------------
st.markdown("""
<style>

[data-testid="stAppViewContainer"]{
    padding:0;
}

.block-container{
    padding:0 !important;
    max-width:100% !important;
}

.hero{
    position:relative;
    width:100vw;
    height:100vh;
    margin-left:calc(-50vw + 50%);
    overflow:hidden;
}

.hero img{
    position:absolute;
    width:100%;
    height:100%;
    object-fit:cover;
}

.hero::after{
    content:"";
    position:absolute;
    inset:0;
    background:linear-gradient(
        rgba(0,0,0,0.6),
        rgba(0,0,0,0.3),
        rgba(0,0,0,0.6)
    );
}

@keyframes floatText{
    0%{transform:translateY(0)}
    50%{transform:translateY(-5px)}
    100%{transform:translateY(0)}
}

.top{
    position:absolute;
    top:6%;
    width:100%;
    text-align:center;
    color:white;
    z-index:5;
}

.top h1{
    font-size:36px;
    margin:0;
    text-shadow:0 5px 25px rgba(0,0,0,0.9);
    animation:floatText 4s ease-in-out infinite;
}

.top h3{
    font-size:20px;
    margin-top:6px;
    animation:floatText 4s ease-in-out infinite;
}

.top p{
    font-size:16px;
    margin-top:4px;
    animation:floatText 4s ease-in-out infinite;
}

.bottom{
    position:absolute;
    bottom:14%;
    width:100%;
    text-align:center;
    color:white;
    z-index:5;
}

.bottom p{
    font-size:18px;
    animation:floatText 4s ease-in-out infinite;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# SESSION STATE
# -----------------------------
if "user" not in st.session_state:
    st.session_state["user"] = None

if "page" not in st.session_state:
    st.session_state["page"] = "home"

if "filters" not in st.session_state:
    st.session_state["filters"] = {
        "Brand": None,
        "Fuel_Type": None,
        "Body_Type": None,
        "Transmission": None
    }

if "recommended_cars" not in st.session_state:
    st.session_state["recommended_cars"] = []

if "selected_car" not in st.session_state:
    st.session_state["selected_car"] = None


# -----------------------------
# API HELPERS
# -----------------------------
def safe_post(url, payload):
    try:
        r = requests.post(url, json=payload, timeout=20)
        if r.status_code == 200:
            return r.json()
        else:
            st.error(r.text)
    except Exception as e:
        st.error(str(e))
    return None


# -----------------------------
# HOME PAGE
# -----------------------------
def home_page():

    st.sidebar.title("Navigation")

    if st.sidebar.button("🔐 Login"):
        st.session_state["page"] = "login"
        st.rerun()

    if st.sidebar.button("📝 Sign Up"):
        st.session_state["page"] = "login"
        st.rerun()

    st.markdown("""
    <div class="hero">

    <img src="https://images.unsplash.com/photo-1503376780353-7e6692767b70">

    <div class="top">
        <h1>Your next drive starts here</h1>
        <h3>Choose • Book • Hit the road</h3>
        <p>Renting made simple</p>
    </div>

    <div class="bottom">
        <p>Smart • Reliable • Affordable</p>
        <p>Experience the future of cars</p>
    </div>

    </div>
    """, unsafe_allow_html=True)


# -----------------------------
# LOGIN PAGE
# -----------------------------
def login_page():

    st.title("🔐 Login / Sign Up")

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:

        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):

            user = safe_post(
                f"{BACKEND_URL}/api/login",
                {"email": email, "password": password}
            )

            if user and "user" in user:
                st.session_state["user"] = user["user"]
                st.session_state["page"] = "preferences"
                st.rerun()
            else:
                st.error("Invalid Credentials")

    with tab2:

        name = st.text_input("Name")
        email = st.text_input("Email", key="signup_email")
        phone = st.text_input("Phone")
        password = st.text_input("Password", type="password", key="signup_pass")

        if st.button("Sign Up"):

            r = safe_post(
                f"{BACKEND_URL}/api/signup",
                {
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "password": password
                }
            )

            if r and r.get("success"):
                st.success("Account created. Login Now!")
            else:
                st.error("Signup failed")


# -----------------------------
# ROUTING
# -----------------------------
if st.session_state["page"] == "home":
    home_page()

elif st.session_state["user"] is None:
    login_page()