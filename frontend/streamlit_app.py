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
    st.session_state["page"] = "preferences"

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
    except Exception as e:
        st.error(str(e))
    st.error(f"Error: {r.text}")
    return None


def safe_get(url):
    try:
        r = requests.get(url, timeout=20)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        st.error(str(e))
    st.error(f"Error: {r.text}")
    return None


# ------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------
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
        st.session_state["page"] = "login"
        st.rerun()


# ------------------------------------------------------------
# LOGIN / SIGNUP PAGE
# ------------------------------------------------------------
def login_page():
    st.title("🔐 Login / Sign Up")

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            user = safe_post(f"{BACKEND_URL}/api/login",
                             {"email": email, "password": password})
            if user and "user" in user:
                st.session_state["user"] = user["user"]
                st.session_state["page"] = "preferences"
                st.rerun()
            st.error("Invalid Credentials")

    with tab2:
        name = st.text_input("Name")
        email = st.text_input("Email", key="signup_email")
        phone = st.text_input("Phone")
        password = st.text_input("Password", type="password", key="signup_pass")

        if st.button("Sign Up"):
            r = safe_post(f"{BACKEND_URL}/api/signup",
                          {"name": name, "email": email, "phone": phone, "password": password})
            if r and r.get("success"):
                st.success("Account created. Login Now!")
            else:
                st.error("Signup failed")


# ------------------------------------------------------------
# PREFERENCES PAGE (IMAGE TILE PAGE)
# ------------------------------------------------------------
def preferences_page():
    st.title("🎛 Choose Your Preferences")

    # CSS for clickable tiles
    st.markdown("""
        <style>
            .tile-img {
                width: 100%;
                height: 130px;
                border-radius: 15px;
                object-fit: cover;
                cursor: pointer;
                transition: 0.2s;
            }
            .tile-img:hover {
                transform: scale(1.06);
                opacity: 0.9;
            }
        </style>
    """, unsafe_allow_html=True)

    # Image tile function
    def tile(image_path, label, key, options):
        try:
            img64 = base64.b64encode(open(image_path, "rb").read()).decode()
        except:
            img64 = ""

        # Click image to open dropdown
        if st.button(" ", key=f"btn_{key}"):
            st.session_state[f"open_{key}"] = not st.session_state.get(f"open_{key}", False)

        st.markdown(
            f"<img src='data:image/jpeg;base64,{img64}' class='tile-img'>"
            f"<h5 style='text-align:center'>{label}</h5>",
            unsafe_allow_html=True
        )

        if st.session_state.get(f"open_{key}", False):
            st.session_state["filters"][key] = st.selectbox(
                f"Select {label}", options, key=f"sel_{key}"
            )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        tile("assets/brand.jpeg", "Brand", "Brand",
             ["Toyota", "Honda", "Hyundai", "BMW"])

    with col2:
        tile("assets/fuel.jpeg", "Fuel Type", "Fuel_Type",
             ["Petrol", "Diesel", "Electric"])

    with col3:
        tile("assets/type.jpeg", "Body Type", "Body_Type",
             ["SUV", "Sedan", "Hatchback"])

    with col4:
        tile("assets/transmission.jpeg", "Transmission", "Transmission",
             ["Manual", "Automatic"])

    st.write("---")

    if st.button("📌 Recommend"):
        payload = st.session_state["filters"].copy()
        payload["min_mileage"] = 10
        payload["max_engine_cc"] = 4000

        rec = safe_post(f"{BACKEND_URL}/recommend", payload)

        if rec:
            # Clean bad results
            st.session_state["recommended_cars"] = [
                car for car in rec if car.get("Brand") and car.get("Model")
            ]

            st.session_state["page"] = "book"
            st.rerun()


# ------------------------------------------------------------
# BOOK CAR PAGE
# ------------------------------------------------------------
def book_page():
    st.title("🚗 Book Your Car")

    cars = safe_get(f"{BACKEND_URL}/api/cars")
    if not cars:
        st.error("No cars found")
        return

    st.write("### 🎯 Select a Car")

    dropdown = []
    rec_pairs = set()

    # Recommended at top (NO divider)
    for car in st.session_state["recommended_cars"]:
        brand = car.get("Brand")
        model = car.get("Model")
        if not brand or not model:
            continue

        dropdown.append(f"{brand} {model} (For You)")
        rec_pairs.add((brand, model))

    # Then all cars
    for c in cars:
        if (c["brand"], c["model"]) not in rec_pairs:
            dropdown.append(f"{c['brand']} {c['model']}")

    default = 0

    if st.session_state["selected_car"]:
        sc = st.session_state["selected_car"]
        brand = sc.get("Brand")
        model = sc.get("Model")

        if brand and model:
            label = f"{brand} {model} (For You)"
            if label in dropdown:
                default = dropdown.index(label)

    chosen = st.selectbox("Select Car", dropdown, index=default)

    # Map selected car
    if "(For You)" in chosen:
        raw = chosen.replace(" (For You)", "")
        brand, model = raw.split(" ", 1)
        selcar = next(c for c in st.session_state["recommended_cars"]
                      if c["Brand"] == brand and c["Model"] == model)
        price = 2000
    else:
        selcar = next(c for c in cars if f"{c['brand']} {c['model']}" == chosen)
        price = selcar["price"]

    st.session_state["selected_car"] = selcar

    # Dates
    col1, col2 = st.columns(2)
    with col1:
        pickup = st.date_input("Pickup", date.today())
    with col2:
        drop = st.date_input("Return", date.today() + timedelta(days=1))

    days = max((drop - pickup).days, 1)
    total = days * price

    st.write(f"### 💰 Total Cost: ₹{total}")

    if st.button("Confirm Booking"):
        r = safe_post(
            f"{BACKEND_URL}/api/book",
            {
                "user_id": st.session_state["user"]["_id"],
                "car_id": selcar.get("_id", selcar.get("Car_ID"))
            }
        )
        if r and r.get("success"):
            st.success("Booking Confirmed 🎉")


# ------------------------------------------------------------
# ROUTER
# ------------------------------------------------------------
if st.session_state["user"] is None:
    login_page()
else:
    render_sidebar()

    if st.session_state["page"] == "preferences":
        preferences_page()
    elif st.session_state["page"] == "book":
        book_page()
    else:
        preferences_page()
