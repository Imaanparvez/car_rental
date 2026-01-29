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
# UTILITY: Load image as Base64
# ------------------------------------------------------------
def load_image_base64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return ""


# ------------------------------------------------------------
# CONSISTENT TILE RENDERER
# ------------------------------------------------------------
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

    # LOGIN
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
            else:
                st.error("Invalid Credentials")

    # SIGNUP
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
# PREFERENCES PAGE (Image Tiles)
# ------------------------------------------------------------
def preferences_page():
    st.title("🎛 Choose Your Preferences")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(render_tile("assets/brand.jpeg"), unsafe_allow_html=True)
        st.session_state["filters"]["Brand"] = st.selectbox(
            "Brand", ["Toyota", "Honda", "Hyundai", "BMW"], key="brand_dd"
        )

    with col2:
        st.markdown(render_tile("assets/fuel.jpeg"), unsafe_allow_html=True)
        st.session_state["filters"]["Fuel_Type"] = st.selectbox(
            "Fuel Type", ["Petrol", "Diesel", "Electric"], key="fuel_dd"
        )

    with col3:
        st.markdown(render_tile("assets/type.jpeg"), unsafe_allow_html=True)
        st.session_state["filters"]["Body_Type"] = st.selectbox(
            "Body Type", ["SUV", "Sedan", "Hatchback"], key="body_dd"
        )

    with col4:
        st.markdown(render_tile("assets/transmission.jpeg"), unsafe_allow_html=True)
        st.session_state["filters"]["Transmission"] = st.selectbox(
            "Transmission", ["Manual", "Automatic"], key="trans_dd"
        )

    st.write("---")

    if st.button("📌 Recommend"):
        f = st.session_state["filters"]
        missing = [key.replace("_", " ") for key, val in f.items() if val is None]

        if missing:
            missing_text = ", ".join(missing)
            st.warning(f"⚠ Please select {missing_text}")
            return

        payload = {
            "Brand": f["Brand"],
            "Fuel_Type": f["Fuel_Type"],
            "Body_Type": f["Body_Type"],
            "Transmission": f["Transmission"],
        }

        rec = safe_post(f"{BACKEND_URL}/recommend", payload)

        if rec:
            st.session_state["recommended_cars"] = [
                car for car in rec if car.get("Brand") and car.get("Model")
            ]
            st.session_state["page"] = "book"
            st.rerun()


# ------------------------------------------------------------
# BOOK CAR PAGE (unchanged)
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

    # Recommended first
    for car in st.session_state["recommended_cars"]:
        brand = car.get("Brand")
        model = car.get("Model")
        if not brand or not model:
            continue

        dropdown.append(f"{brand} {model} (For You)")
        rec_pairs.add((brand, model))

    # All other cars
    for c in cars:
        if (c["brand"], c["model"]) not in rec_pairs:
            dropdown.append(f"{c['brand']} {c['model']}")

    default = 0

    # Preserve selection
    if st.session_state["selected_car"]:
        sc = st.session_state["selected_car"]
        brand, model = sc.get("Brand"), sc.get("Model")
        if brand and model:
            lbl = f"{brand} {model} (For You)"
            if lbl in dropdown:
                default = dropdown.index(lbl)

    chosen = st.selectbox("Select Car", dropdown, index=default)

    # Map to car
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

    col1, col2 = st.columns(2)
    with col1:
        pickup = st.date_input("Pickup Date", date.today())
    with col2:
        drop = st.date_input("Return Date", date.today() + timedelta(days=1))

    days = max((drop - pickup).days, 1)

    st.write(f"### 💰 Total Cost: ₹{days * price}")

    if st.button("Confirm Booking"):
        r = safe_post(
            f"{BACKEND_URL}/api/book",
            {"user_id": st.session_state["user"]["_id"],
             "car_id": selcar.get("_id", selcar.get("Car_ID"))}
        )
        if r and r.get("success"):
            st.success("Booking confirmed 🎉")


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
