import streamlit as st
import requests
import os
from datetime import date, timedelta
import base64

BACKEND_URL = os.environ.get("BACKEND_URL")
if not BACKEND_URL:
    st.error("❌ BACKEND_URL missing in env")
    st.stop()

st.set_page_config(page_title="AI Car Rental", layout="wide")

# -----------------------------
# GLOBAL STYLES
# -----------------------------
st.markdown("""
<style>

[data-testid="stAppViewContainer"]{
padding:0;
margin:0;
}

.main{
padding:0;
margin:0;
}

.hero-container{
position:relative;
height:100vh;
width:100vw;
overflow:hidden;
}

.hero-container img{
position:absolute;
top:0;
left:0;
width:100%;
height:100%;
object-fit:cover;
}

.hero-top{
position:absolute;
top:8%;
width:100%;
text-align:center;
color:white;
animation:fadeIn 1.2s ease-in-out;
}

.hero-bottom{
position:absolute;
bottom:8%;
width:100%;
text-align:center;
color:white;
animation:fadeIn 2s ease-in-out;
}

.hero-title{
font-size:56px;
font-weight:700;
}

.hero-sub{
font-size:26px;
margin-top:10px;
}

.hero-tag{
font-size:20px;
margin-top:8px;
}

.hero-caption{
font-size:22px;
margin-top:6px;
}

@keyframes fadeIn{
0%{opacity:0;transform:translateY(20px);}
100%{opacity:1;transform:translateY(0);}
}

.stButton>button{
border-radius:12px;
height:45px;
width:100%;
font-weight:600;
transition:0.3s;
}

.stButton>button:hover{
transform:scale(1.05);
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
            st.error(f"Error: {r.text}")
    except Exception as e:
        st.error(str(e))
    return None


def safe_get(url):
    try:
        r = requests.get(url, timeout=20)
        if r.status_code == 200:
            return r.json()
        else:
            st.error(f"Error: {r.text}")
    except Exception as e:
        st.error(str(e))
    return None


# -----------------------------
# IMAGE HELPERS
# -----------------------------
def load_image_base64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return ""


def render_tile(image_path):
    img64 = load_image_base64(image_path)
    return f"""
    <div style="
        width:180px;
        height:120px;
        border-radius:12px;
        overflow:hidden;
        display:flex;
        justify-content:center;
        align-items:center;
        background:#111;
    ">
        <img src="data:image/jpeg;base64,{img64}"
            style="
                width:100%;
                height:100%;
                object-fit:cover;
            "
        >
    </div>
    """


# -----------------------------
# HOME LANDING PAGE
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
    <div class="hero-container">

        <img src="https://images.unsplash.com/photo-1511919884226-fd3cad34687c?w=3840">

        <div class="hero-top">
            <div class="hero-title">Your next drive starts here</div>
            <div class="hero-sub">Choose • Book • Hit the road</div>
            <div class="hero-tag">Renting made simple</div>
        </div>

        <div class="hero-bottom">
            <div class="hero-caption"><h2>AI Powered Car Rental System</h2></div>
            <div class="hero-caption">Smart • Reliable • Affordable</div>
            <div class="hero-caption">Experience the future of cars</div>
        </div>

    </div>
    """, unsafe_allow_html=True)


# -----------------------------
# SIDEBAR AFTER LOGIN
# -----------------------------
def render_sidebar():

    st.sidebar.success(f"Welcome {st.session_state['user']['name']} 👋")

    if st.sidebar.button("🎛 Preferences"):
        st.session_state["page"] = "preferences"
        st.rerun()

    if st.sidebar.button("📅 Book Car"):
        st.session_state["page"] = "book"
        st.rerun()

    if st.sidebar.button("🚪 Logout"):
        st.session_state.clear()
        st.session_state["page"] = "home"
        st.rerun()


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

else:
    render_sidebar()
