import streamlit as st
import requests
from datetime import date, timedelta
import base64

BACKEND_URL = os.environ.get("BACKEND_URL")

st.set_page_config(page_title="AI Car Rental", layout="wide")

# -----------------------------
# GLOBAL CSS
# -----------------------------
st.markdown("""
<style>

[data-testid="stHeader"]{background: transparent;}
#MainMenu{visibility:hidden;}
footer{visibility:hidden;}

[data-testid="stAppViewContainer"]{padding:0;}
.block-container{padding:0 !important;max-width:100% !important;}

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

if "recommended_cars" not in st.session_state:
    st.session_state["recommended_cars"] = []

# -----------------------------
# API HELPERS
# -----------------------------
def safe_post(url, payload):
    try:
        r = requests.post(url, json=payload)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None


def safe_get(url):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None


# -----------------------------
# ACTION LOGGER
# -----------------------------
def log_interaction(car_id, action):

    if st.session_state["user"] is None:
        return

    try:
        requests.post(
            f"{BACKEND_URL}/api/interact",
            json={
                "user_id": st.session_state["user"]["_id"],
                "car_id": car_id,
                "action": action
            }
        )
    except:
        pass


# -----------------------------
# IMAGE HELPER
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
        background:#111;">
        <img src="data:image/jpeg;base64,{img64}"
        style="width:100%;height:100%;object-fit:cover;">
    </div>
    """


# -----------------------------
# SIDEBAR NAVIGATION
# -----------------------------
with st.sidebar:

    st.markdown("## 🚗 AI Car Rental")

    if st.session_state["user"] is None:

        if st.button("🔐 Login"):
            st.session_state["page"] = "login"
            st.rerun()

        if st.button("📝 Sign Up"):
            st.session_state["page"] = "login"
            st.rerun()

    else:

        if st.button("🏠 Home"):
            st.session_state["page"] = "home"
            st.rerun()

        if st.button("🎛 Preferences"):
            st.session_state["page"] = "preferences"
            st.rerun()

        if st.button("🚗 Book Car"):
            st.session_state["page"] = "book"
            st.rerun()

        if st.button("🚪 Logout"):
            st.session_state["user"] = None
            st.session_state["recommended_cars"] = []
            st.session_state["page"] = "home"
            st.rerun()


# -----------------------------
# HOME PAGE
# -----------------------------
def home_page():

    st.markdown("""
    <div class="hero">
    <img src="https://images.unsplash.com/photo-1503376780353-7e6692767b70">

    <div style="position:absolute;top:6%;width:100%;text-align:center;color:white;">
        <h1>Your next drive starts here</h1>
        <h3>Choose • Book • Hit the road</h3>
        <p>Renting made simple</p>
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

        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login", key="login_button"):

            user = safe_post(
                f"{BACKEND_URL}/api/login",
                {"email": email, "password": password}
            )

            if user and "user" in user:
                st.session_state["user"] = user["user"]
                st.session_state["page"] = "preferences"
                st.rerun()

    with tab2:

        name = st.text_input("Name", key="signup_name")
        email = st.text_input("Email", key="signup_email")
        phone = st.text_input("Phone", key="signup_phone")
        password = st.text_input("Password", type="password", key="signup_pass")

        if st.button("Sign Up", key="signup_button"):

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
                st.success("Account created")


# -----------------------------
# PREFERENCES PAGE
# -----------------------------
def preferences_page():

    st.title("🎛 Choose Your Preferences")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(render_tile("assets/brand.jpeg"), unsafe_allow_html=True)

        brand = st.selectbox(
            "Car Brand",
            ["Select your choice","Kia","Honda","Toyota","BMW","Hyundai","Maruti"]
        )

    with col2:
        st.markdown(render_tile("assets/fuel.jpeg"), unsafe_allow_html=True)

        fuel = st.selectbox(
            "Fuel Type",
            ["Select your choice","Petrol","Diesel","Electric"]
        )

    with col3:
        st.markdown(render_tile("assets/type.jpeg"), unsafe_allow_html=True)

        body = st.selectbox(
            "Body Type",
            ["Select your choice","SUV","Sedan","Hatchback"]
        )

    col4, col5 = st.columns(2)

    with col4:
        mileage = st.selectbox(
            "Mileage Preference",
            ["Select your choice","Any","Low","Medium","High"]
        )

    with col5:
        engine = st.selectbox(
            "Engine Power Preference",
            ["Select your choice","Any","Low Power","Medium Power","High Power"]
        )

    if st.button("📌 Recommend"):

        payload = {
            "user_id": st.session_state["user"]["_id"],
            "Brand": brand,
            "Fuel_Type": fuel,
            "Body_Type": body,
            "Mileage": mileage,
            "Engine_CC": engine
        }

        rec = safe_post(f"{BACKEND_URL}/api/recommend", payload)

        if rec:
            st.session_state["recommended_cars"] = rec
            st.session_state["page"] = "book"
            st.rerun()


# -----------------------------
# BOOK PAGE
# -----------------------------
def book_page():

    st.title("🚗 Book Your Car")

    cars = safe_get(f"{BACKEND_URL}/api/cars")

    dropdown = []

    for car in st.session_state["recommended_cars"]:
        dropdown.append(f"{car['Brand']} {car['Model']} (For You)")

    for c in cars:
        dropdown.append(f"{c['Brand']} {c['Model']}")

    chosen = st.selectbox("Select Car", dropdown)

    chosen_clean = chosen.replace(" (For You)", "")

    brand, model = chosen_clean.split(" ",1)

    selcar = None

    for c in cars:
        if (
            c.get("Brand","").lower() == brand.lower()
            and
            c.get("Model","").lower() == model.lower()
        ):
            selcar = c
            break

    if selcar is None:
        st.error("Car not found")
        st.stop()

    # -----------------------------
    # CLICK ACTION
    # -----------------------------
    if "(For You)" in chosen:
        log_interaction(selcar["_id"], "click")

    # -----------------------------
    # VIEW ACTION
    # -----------------------------
    log_interaction(selcar["_id"], "view")

    price = selcar.get("price",2000)

    pickup = st.date_input("Pickup Date", date.today())
    drop = st.date_input("Return Date", date.today()+timedelta(days=1))

    days = max((drop - pickup).days, 1)

    st.write(f"### Total Cost: ₹{days*price}")

    if st.button("Confirm Booking"):

        # -----------------------------
        # BOOK ACTION
        # -----------------------------
        log_interaction(selcar["_id"], "book")

        r = safe_post(
            f"{BACKEND_URL}/api/book",
            {
                "user_id": st.session_state["user"]["_id"],
                "car_id": selcar["_id"]
            }
        )

        if r and r.get("success"):
            st.success("Booking confirmed 🎉")


# -----------------------------
# PAGE ROUTING
# -----------------------------
if st.session_state["page"] == "home":
    home_page()

elif st.session_state["page"] == "login":
    login_page()

elif st.session_state["page"] == "preferences":
    preferences_page()

elif st.session_state["page"] == "book":
    book_page()