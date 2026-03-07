import streamlit as st
import requests
import os
from datetime import date, timedelta
import base64


# -----------------------------
# CONFIG
# -----------------------------

st.set_page_config(page_title="AI Car Rental", layout="wide")

BACKEND_URL = os.environ.get("BACKEND_URL")
if not BACKEND_URL:
    st.error("❌ BACKEND_URL missing in env")
    st.stop()


# -----------------------------
# GLOBAL STYLING
# -----------------------------

st.markdown("""
<style>

body{
background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);
color:white;
}

.block-container{
padding-top:2rem;
}

.hero{
text-align:center;
padding:120px 20px;
animation:fadeIn 1s ease-in-out;
}

.hero h1{
font-size:60px;
font-weight:800;
}

.hero p{
font-size:20px;
opacity:0.8;
}

.hero-btn{
padding:14px 30px;
font-size:18px;
border-radius:30px;
background:linear-gradient(45deg,#00c6ff,#0072ff);
border:none;
color:white;
cursor:pointer;
transition:0.3s;
}

.hero-btn:hover{
transform:scale(1.05);
}

.card{
background:rgba(255,255,255,0.08);
padding:30px;
border-radius:16px;
backdrop-filter:blur(10px);
transition:0.3s;
}

.card:hover{
transform:translateY(-5px);
}

@keyframes fadeIn{
from{opacity:0;transform:translateY(20px)}
to{opacity:1;transform:translateY(0)}
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
# LANDING PAGE
# -----------------------------

def landing_page():

    st.markdown("""
    <div class="hero">
        <h1>🚗 AI Powered Car Rental</h1>
        <p>Find the perfect car instantly with AI recommendations</p>
    </div>
    """, unsafe_allow_html=True)

    col1,col2,col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="card">
        <h3>🤖 AI Recommendations</h3>
        <p>Smart suggestions based on your preferences.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="card">
        <h3>⚡ Fast Booking</h3>
        <p>Book your car within seconds.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="card">
        <h3>🚘 Premium Fleet</h3>
        <p>Choose from the best brands.</p>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.write("")

    col1,col2,col3 = st.columns([1,2,1])

    with col2:

        if st.button("🔐 Login"):
            st.session_state["page"] = "login"
            st.rerun()

        if st.button("📝 Register"):
            st.session_state["page"] = "login"
            st.rerun()


# -----------------------------
# SIDEBAR
# -----------------------------

def render_sidebar():

    st.sidebar.markdown("### 🚗 AI Car Rental")

    st.sidebar.success(f"Welcome {st.session_state['user']['name']} 👋")

    st.sidebar.write("---")

    if st.sidebar.button("🎛 Preferences"):
        st.session_state["page"] = "preferences"
        st.rerun()

    if st.sidebar.button("📅 Book Car"):
        st.session_state["page"] = "book"
        st.rerun()

    st.sidebar.write("---")

    if st.sidebar.button("🚪 Logout"):
        st.session_state.clear()
        st.session_state["page"] = "home"
        st.rerun()


# -----------------------------
# LOGIN PAGE
# -----------------------------

def login_page():

    st.markdown('<div class="card">', unsafe_allow_html=True)

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

    st.markdown('</div>', unsafe_allow_html=True)


# -----------------------------
# PREFERENCES PAGE
# -----------------------------

def preferences_page():

    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.title("🎛 Choose Your Preferences")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(render_tile("assets/brand.jpeg"), unsafe_allow_html=True)
        st.session_state["filters"]["Brand"] = st.selectbox(
            "Brand",
            ["Toyota", "Honda", "Hyundai", "BMW"]
        )

    with col2:
        st.markdown(render_tile("assets/fuel.jpeg"), unsafe_allow_html=True)
        st.session_state["filters"]["Fuel_Type"] = st.selectbox(
            "Fuel Type",
            ["Petrol", "Diesel", "Electric"]
        )

    with col3:
        st.markdown(render_tile("assets/type.jpeg"), unsafe_allow_html=True)
        st.session_state["filters"]["Body_Type"] = st.selectbox(
            "Body Type",
            ["SUV", "Sedan", "Hatchback"]
        )

    with col4:
        st.markdown(render_tile("assets/transmission.jpeg"), unsafe_allow_html=True)
        st.session_state["filters"]["Transmission"] = st.selectbox(
            "Transmission",
            ["Manual", "Automatic"]
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

    st.markdown('</div>', unsafe_allow_html=True)


# -----------------------------
# BOOK PAGE
# -----------------------------

def book_page():

    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.title("🚗 Book Your Car")

    cars = safe_get(f"{BACKEND_URL}/api/cars")

    if not cars:
        st.error("No cars found")
        return

    dropdown = []
    rec_pairs = set()

    for car in st.session_state["recommended_cars"]:

        brand = car.get("Brand")
        model = car.get("Model")

        if not brand or not model:
            continue

        dropdown.append(f"{brand} {model} (For You)")
        rec_pairs.add((brand, model))

    for c in cars:

        brand = c.get("Brand") or c.get("brand")
        model = c.get("Model") or c.get("model")

        if (brand, model) not in rec_pairs:
            dropdown.append(f"{brand} {model}")

    chosen = st.selectbox("Select Car", dropdown)

    if "(For You)" in chosen:

        raw = chosen.replace(" (For You)", "")
        brand, model = raw.split(" ", 1)

        selcar = next(
            c for c in st.session_state["recommended_cars"]
            if c["Brand"] == brand and c["Model"] == model
        )

        price = 2000

    else:

        selcar = next(
            c for c in cars
            if f"{c.get('Brand') or c.get('brand')} {c.get('Model') or c.get('model')}" == chosen
        )

        price = selcar.get("price", 2000)

    st.session_state["selected_car"] = selcar

    col1, col2 = st.columns(2)

    with col1:
        pickup = st.date_input("Pickup Date", date.today())

    with col2:
        drop = st.date_input("Return Date", date.today() + timedelta(days=1))

    days = max((drop - pickup).days, 1)

    st.write(f"### Total Cost: ₹{days * price}")

    if st.button("Confirm Booking"):

        real_car = next(
            (
                c for c in cars
                if (c.get("Brand") or c.get("brand")) == (selcar.get("Brand") or selcar.get("brand"))
                and (c.get("Model") or c.get("model")) == (selcar.get("Model") or selcar.get("model"))
            ),
            None
        )

        if not real_car:
            st.error("Car not found in database")
            return

        r = safe_post(
            f"{BACKEND_URL}/api/book",
            {
                "user_id": str(st.session_state["user"]["_id"]),
                "car_id": str(real_car["_id"])
            }
        )

        if r and r.get("success"):
            st.success("Booking confirmed 🎉")

    st.markdown('</div>', unsafe_allow_html=True)


# -----------------------------
# ROUTING
# -----------------------------

if st.session_state["page"] == "home":

    landing_page()

elif st.session_state["page"] == "login":

    login_page()

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
