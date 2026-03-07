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

.block-container{
padding:0rem 0rem 0rem 0rem;
}

.main{
background:black;
}

/* HERO SECTION */

.hero-container{
position:fixed;
top:0;
left:0;
width:100vw;
height:100vh;
overflow:hidden;
}

.hero-container img{
width:100%;
height:100%;
object-fit:cover;
}

/* DARK OVERLAY */

.hero-overlay{
position:absolute;
top:0;
left:0;
width:100%;
height:100%;
background:linear-gradient(
to bottom,
rgba(0,0,0,0.55),
rgba(0,0,0,0.1),
rgba(0,0,0,0.65)
);
}

/* TOP TEXT */

.hero-top{
position:absolute;
top:80px;
width:100%;
text-align:center;
color:white;
}

.hero-title{
font-size:54px;
font-weight:700;
}

.hero-sub{
font-size:26px;
margin-top:10px;
}

/* BOTTOM TEXT */

.hero-bottom{
position:absolute;
bottom:80px;
width:100%;
text-align:center;
color:white;
}

.hero-tag{
font-size:30px;
font-weight:600;
}

.hero-caption{
font-size:20px;
margin-top:8px;
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

        <img src="assets/car_images/hero.jpg">

        <div class="hero-overlay"></div>

        <div class="hero-top">
            <div class="hero-title">Your next drive starts here</div>
            <div class="hero-sub">Choose • Book • Hit the road</div>
        </div>

        <div class="hero-bottom">
            <div class="hero-tag">AI Powered Car Rental System</div>
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
# PREFERENCES PAGE
# -----------------------------
def preferences_page():

    st.title("🎛 Choose Your Preferences")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.session_state["filters"]["Brand"] = st.selectbox(
            "Brand",
            ["Toyota", "Honda", "Hyundai", "BMW"],
        )

    with col2:
        st.session_state["filters"]["Fuel_Type"] = st.selectbox(
            "Fuel Type",
            ["Petrol", "Diesel", "Electric"],
        )

    with col3:
        st.session_state["filters"]["Body_Type"] = st.selectbox(
            "Body Type",
            ["SUV", "Sedan", "Hatchback"],
        )

    with col4:
        st.session_state["filters"]["Transmission"] = st.selectbox(
            "Transmission",
            ["Manual", "Automatic"],
        )

    st.write("---")

    if st.button("📌 Recommend"):

        f = st.session_state["filters"]

        payload = {
            "Brand": f["Brand"],
            "Fuel_Type": f["Fuel_Type"],
            "Body_Type": f["Body_Type"],
            "Transmission": f["Transmission"]
        }

        rec = safe_post(f"{BACKEND_URL}/recommend", payload)

        if rec:

            st.session_state["recommended_cars"] = [
                car for car in rec if car.get("Brand") and car.get("Model")
            ]

            st.session_state["page"] = "book"
            st.rerun()


# -----------------------------
# BOOK PAGE
# -----------------------------
def book_page():

    st.title("🚗 Book Your Car")

    cars = safe_get(f"{BACKEND_URL}/api/cars")

    if not cars:
        st.error("No cars found")
        return

    dropdown = []

    for c in cars:
        dropdown.append(f"{c.get('Brand')} {c.get('Model')}")

    chosen = st.selectbox("Select Car", dropdown)

    selcar = next(
        c for c in cars
        if f"{c.get('Brand')} {c.get('Model')}" == chosen
    )

    price = selcar.get("price", 2000)

    col1, col2 = st.columns(2)

    with col1:
        pickup = st.date_input("Pickup Date", date.today())

    with col2:
        drop = st.date_input("Return Date", date.today() + timedelta(days=1))

    days = max((drop - pickup).days, 1)

    st.write(f"### Total Cost: ₹{days * price}")

    if st.button("Confirm Booking"):

        r = safe_post(
            f"{BACKEND_URL}/api/book",
            {
                "user_id": str(st.session_state["user"]["_id"]),
                "car_id": str(selcar["_id"])
            }
        )

        if r and r.get("success"):
            st.success("Booking confirmed 🎉")


# -----------------------------
# ROUTING
# -----------------------------
if st.session_state["page"] == "home":
    home_page()

elif st.session_state["user"] is None:
    login_page()

else:

    render_sidebar()

    if st.session_state["page"] == "preferences":
        preferences_page()

    elif st.session_state["page"] == "book":
        book_page()

    else:
        preferences_page()
