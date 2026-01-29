import streamlit as st
import requests
import os
from datetime import date, timedelta
import base64

# ------------------------------------------------------------
# BACKEND URL
# ------------------------------------------------------------
BACKEND_URL = os.environ.get("BACKEND_URL")
if not BACKEND_URL:
    st.error("❌ BACKEND_URL missing in env")
    st.stop()

# ------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------
st.set_page_config(page_title="AI Car Rental", layout="wide")

# ------------------------------------------------------------
# SESSION STATE
# ------------------------------------------------------------
if "user" not in st.session_state:
    st.session_state["user"] = None

if "page" not in st.session_state:
    st.session_state["page"] = "login"

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


# ------------------------------------------------------------
# SAFE REQUEST HELPERS
# ------------------------------------------------------------
def safe_post(url, payload):
    try:
        r = requests.post(url, json=payload, timeout=20)
        if r.status_code == 200:
            return r.json()
        st.error(f"❌ {r.status_code}: {r.text}")
    except Exception as e:
        st.error(str(e))
    return None


def safe_get(url):
    try:
        r = requests.get(url, timeout=20)
        if r.status_code == 200:
            return r.json()
        st.error(f"❌ {r.status_code}: {r.text}")
    except Exception as e:
        st.error(str(e))
    return None


# ------------------------------------------------------------
# LOGIN / SIGNUP PAGE
# ------------------------------------------------------------
def login_page():
    st.title("🔐 Login / Sign Up")

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    # LOGIN
    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            user = safe_post(f"{BACKEND_URL}/api/login",
                             {"email": email, "password": password})
            if user and "user" in user:
                st.session_state["user"] = user["user"]
                st.session_state["page"] = "book"
                st.rerun()
            else:
                st.error("Invalid credentials")

    # SIGNUP
    with tab2:
        name = st.text_input("Name")
        email = st.text_input("Email", key="sign_email")
        phone = st.text_input("Phone")
        password = st.text_input("Password", type="password", key="sign_pass")

        if st.button("Sign Up"):
            r = safe_post(f"{BACKEND_URL}/api/signup",
                          {"name": name, "email": email, "phone": phone, "password": password})

            if r and r.get("success"):
                st.success("Account created! Login now.")
            else:
                st.error("Signup failed.")


# ------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------
def render_sidebar():
    st.sidebar.success(f"Welcome {st.session_state['user']['name']} 👋")

    if st.sidebar.button("📅 Book Car"):
        st.session_state["page"] = "book"
        st.rerun()

    if st.sidebar.button("🚪 Logout"):
        st.session_state.clear()
        st.session_state["page"] = "login"
        st.rerun()


# ------------------------------------------------------------
# BOOK PAGE
# ------------------------------------------------------------
def book_page():
    st.title("🚗 Book a Car")
    st.write("### 🔍 Choose Your Preferences")

    # CSS for tile image clicking
    st.markdown("""
        <style>
            .click-img {
                width: 100%;
                height: 130px;
                border-radius: 12px;
                object-fit: cover;
                cursor: pointer;
                transition: 0.2s;
            }
            .click-img:hover {
                transform: scale(1.05);
                opacity: 0.85;
            }
        </style>
    """, unsafe_allow_html=True)

    # ---------- TILE FUNCTION ----------
    def image_tile(image_path, label, key, options):
        """Image tile that toggles dropdown on click."""

        img_b64 = ""
        try:
            img_b64 = base64.b64encode(open(image_path, "rb").read()).decode()
        except:
            pass

        # Clicking image → toggle dropdown
        if st.button(" ", key=f"btn_{key}"):
            st.session_state[f"open_{key}"] = not st.session_state.get(f"open_{key}", False)

        st.markdown(
            f"""
            <img src="data:image/jpeg;base64,{img_b64}" class="click-img">
            <h5 style="text-align:center;">{label}</h5>
            """,
            unsafe_allow_html=True,
        )

        # Dropdown appears if opened
        if st.session_state.get(f"open_{key}", False):
            choice = st.selectbox(f"Select {label}", options, key=f"sel_{key}")
            st.session_state["filters"][key] = choice

    # ---------- TILE GRID ----------
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        image_tile("assets/brand.jpeg", "Brand", "Brand",
                   ["Toyota", "Honda", "Hyundai", "BMW"])

    with c2:
        image_tile("assets/fuel.jpeg", "Fuel Type", "Fuel_Type",
                   ["Petrol", "Diesel", "Electric"])

    with c3:
        image_tile("assets/type.jpeg", "Body Type", "Body_Type",
                   ["SUV", "Sedan", "Hatchback"])

    with c4:
        image_tile("assets/transmission.jpeg", "Transmission", "Transmission",
                   ["Manual", "Automatic"])

    st.write("---")

    # ---------- RECOMMEND BUTTON ----------
    if st.button("📌 Recommend"):
        payload = st.session_state["filters"].copy()
        payload["min_mileage"] = 10
        payload["max_engine_cc"] = 4000

        rec = safe_post(f"{BACKEND_URL}/recommend", payload)

        if rec:
            cleaned = []
            for car in rec:
                if car.get("Brand") and car.get("Model"):
                    cleaned.append(car)

            st.session_state["recommended_cars"] = cleaned
            st.session_state["page"] = "book"
            st.rerun()

    # ---------- SELECT CAR ----------
    st.write("### 🎯 Select Your Car")

    cars = safe_get(f"{BACKEND_URL}/api/cars")
    if not cars:
        st.error("No cars found")
        return

    dropdown = []
    rec_pairs = set()

    # Recommended first
    for car in st.session_state["recommended_cars"]:
        brand = car.get("Brand")
        model = car.get("Model")
        if not brand or not model:
            continue

        label = f"{brand} {model} (For You)"
        dropdown.append(label)
        rec_pairs.add((brand, model))

    if dropdown:
        dropdown.append("────────── All Cars ──────────")

    # All cars
    for c in cars:
        if (c["brand"], c["model"]) not in rec_pairs:
            dropdown.append(f"{c['brand']} {c['model']}")

    default_index = 0
    if st.session_state["selected_car"]:
        sc = st.session_state["selected_car"]
        brand = sc.get("Brand")
        model = sc.get("Model")

        if brand and model:
            lbl = f"{brand} {model} (For You)"
            if lbl in dropdown:
                default_index = dropdown.index(lbl)

    chosen = st.selectbox("Select Car", dropdown, index=default_index)

    # map dropdown to car obj
    if "(For You)" in chosen:
        raw = chosen.replace(" (For You)", "")
        brand, model = raw.split(" ", 1)
        selcar = next(c for c in st.session_state["recommended_cars"]
                      if c["Brand"] == brand and c["Model"] == model)
        price = 2000
    else:
        selcar = next(c for c in cars
                      if f"{c['brand']} {c['model']}" == chosen)
        price = selcar["price"]

    st.session_state["selected_car"] = selcar

    # ---------- DATE PICK ----------
    col1, col2 = st.columns(2)
    with col1:
        pickup = st.date_input("Pickup Date", date.today())
    with col2:
        drop = st.date_input("Return Date", date.today() + timedelta(days=1))

    days = max((drop - pickup).days, 1)
    st.write(f"### 💰 Total Cost: ₹{days * price}")

    # ---------- CONFIRM BOOKING ----------
    if st.button("Confirm Booking"):
        result = safe_post(
            f"{BACKEND_URL}/api/book",
            {
                "user_id": st.session_state["user"]["_id"],
                "car_id": selcar.get("_id", selcar.get("Car_ID"))
            }
        )
        if result and result.get("success"):
            st.success("Booking confirmed! 🎉")


# ------------------------------------------------------------
# ROUTING
# ------------------------------------------------------------
if st.session_state["user"] is None:
    login_page()
else:
    render_sidebar()
    book_page()
