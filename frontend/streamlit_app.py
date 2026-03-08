import streamlit as st
import requests
from datetime import date, timedelta
import pandas as pd
import os

BACKEND_URL = os.environ["BACKEND_URL"]

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
.block-container{padding-top:1rem;padding-left:2rem;padding-right:2rem;max-width:1400px;margin:auto;}

.hero{
position:relative;
width:100vw;
height:85vh;
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

.card{
background:white;
padding:20px;
border-radius:12px;
box-shadow:0 4px 10px rgba(0,0,0,0.1);
text-align:center;
margin-bottom:20px;
}

.center-title{
text-align:center;
margin-top:30px;
margin-bottom:10px;
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

if "cf_cars" not in st.session_state:
    st.session_state["cf_cars"] = []

if "selected_car" not in st.session_state:
    st.session_state["selected_car"] = None

if "booking_success" not in st.session_state:
    st.session_state["booking_success"] = False


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
# SIDEBAR
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

        if st.button("📞 Contact Us"):
            st.session_state["page"] = "contact"
            st.rerun()

        if st.button("🚪 Logout"):
            st.session_state["user"] = None
            st.session_state["recommended_cars"] = []
            st.session_state["cf_cars"] = []
            st.session_state["page"] = "home"
            st.rerun()


# -----------------------------
# HOME PAGE
# -----------------------------
def home_page():

    st.markdown("""
    <div class="hero">
    <img src="https://images.unsplash.com/photo-1503376780353-7e6692767b70">

    <div style="position:absolute;top:10%;width:100%;text-align:center;color:white;">
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
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login"):

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
        password = st.text_input("Password", type="password", key="signup_password")

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
                st.success("Account created")


# -----------------------------
# PREFERENCES PAGE
# -----------------------------
def preferences_page():

    st.title("🎛 Choose Your Preferences")

    brand = st.selectbox("Car Brand",
                         ["Select your choice","Kia","Honda","Toyota","BMW","Hyundai","Maruti"])

    fuel = st.selectbox("Fuel Type",
                        ["Select your choice","Petrol","Diesel","Electric"])

    body = st.selectbox("Body Type",
                        ["Select your choice","SUV","Sedan","Hatchback"])

    mileage = st.selectbox("Mileage Preference",
                           ["Select your choice","Any","Low","Medium","High"])

    engine = st.selectbox("Engine Power Preference",
                          ["Select your choice","Any","Low Power","Medium Power","High Power"])

    if st.button("📌 Recommend"):

        payload = {
            "user_id": st.session_state["user"]["_id"],
            "preferences":{
                "Brand":brand,
                "Fuel_Type":fuel,
                "Body_Type":body,
                "Mileage":mileage,
                "Engine_CC":engine
            }
        }

        rec = safe_post(f"{BACKEND_URL}/api/recommend", payload)

        if rec:

            st.session_state["recommended_cars"] = rec.get("cbf",[])
            st.session_state["cf_cars"] = rec.get("cf",[])

            st.session_state["page"] = "book"
            st.rerun()


# -----------------------------
# BOOK DASHBOARD
# -----------------------------
def book_page():

    st.title("🚗 Car Dashboard")

    cars = safe_get(f"{BACKEND_URL}/api/cars")

    st.subheader("🔍 Search Cars")

    search = st.text_input("Search by brand or model")

    if search:

        seen=set()

        for i,c in enumerate(cars):

            name=f"{c['Brand']} {c['Model']}".title()

            if search.lower() in name.lower():

                if name not in seen:

                    seen.add(name)

                    if st.button(f"{name} - View Car", key=f"search_{i}"):

                        car_id = c.get("_id") or c.get("Car_ID")

                        log_interaction(car_id,"search")
                        log_interaction(car_id,"view")

                        st.session_state["selected_car"]=c
                        st.session_state["page"]="payment"
                        st.rerun()

    st.divider()

    st.markdown('<h3 class="center-title">⭐ Recommended For You</h3>', unsafe_allow_html=True)

    cols = st.columns(3)

    for i,car in enumerate(st.session_state["recommended_cars"]):

        brand = car["Brand"].title()
        model = car["Model"].title()

        with cols[i%3]:

            st.markdown('<div class="card">', unsafe_allow_html=True)

            st.markdown(f"### {brand} {model}")

            if st.button("View Car", key=f"cbf_{i}"):

                real_car=None
                for c in cars:
                    if c["Brand"].lower()==car["Brand"].lower() and c["Model"].lower()==car["Model"].lower():
                        real_car=c
                        break

                if real_car:
                    car_id = real_car["_id"]
                    log_interaction(car_id,"view")
                    st.session_state["selected_car"]=real_car
                    st.session_state["page"]="payment"
                    st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<h3 class="center-title">👥 Previous Users Also Viewed</h3>', unsafe_allow_html=True)

    cols = st.columns(3)

    for i,car in enumerate(st.session_state["cf_cars"]):

        brand = car["Brand"].title()
        model = car["Model"].title()

        with cols[i%3]:

            st.markdown('<div class="card">', unsafe_allow_html=True)

            st.markdown(f"### {brand} {model}")

            if st.button("View Car", key=f"cf_{i}"):

                real_car=None
                for c in cars:
                    if c["Brand"].lower()==car["Brand"].lower() and c["Model"].lower()==car["Model"].lower():
                        real_car=c
                        break

                if real_car:
                    car_id = real_car["_id"]
                    log_interaction(car_id,"view")
                    st.session_state["selected_car"]=real_car
                    st.session_state["page"]="payment"
                    st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------
# PAYMENT PAGE
# -----------------------------
# -----------------------------
# PAYMENT PAGE
# -----------------------------
def payment_page():

    car = st.session_state["selected_car"]

    brand = car.get("Brand","").title()
    model = car.get("Model","").title()

    year = car.get("Year","")
    cc = car.get("Engine_CC",1500)
    mileage = car.get("Mileage","")

    st.title("💳 Payment")

    col1,col2 = st.columns([1,1])

    with col1:

        st.markdown(f"""
        ### {brand} {model}

        **Year:** {year}

        **Engine CC:** {cc}

        **Mileage:** {mileage}
        """)

    with col2:

        pickup = st.date_input("Pickup Date", date.today())
        drop = st.date_input("Return Date", date.today()+timedelta(days=1))

        days = max((drop - pickup).days, 1)

        price_per_day = 800 + cc * 0.8
        total_price = days * price_per_day

        st.markdown(f"### Total Price: ₹{int(total_price)}")

        # -----------------------------
        # CONFIRM PAYMENT BUTTON
        # -----------------------------
        if st.button("Confirm Payment"):

            car_id = car.get("_id") or car.get("Car_ID")

            try:

                response = requests.post(
                    f"{BACKEND_URL}/api/book",
                    json={
                        "user_id": st.session_state["user"]["_id"],
                        "car_id": car_id
                    }
                )

                data = response.json()

                if data.get("success"):

                    st.success("✅ Car booked successfully. It will be delivered to your location.")

                    st.session_state["booking_success"] = True
                    st.session_state["page"] = "confirmation"

                    st.rerun()

                else:
                    st.error("Booking failed")

            except Exception as e:
                st.error(f"Error: {e}")

# -----------------------------
# CONFIRMATION PAGE
# -----------------------------
def confirmation_page():

    car = st.session_state["selected_car"]

    brand = car.get("Brand","").title()
    model = car.get("Model","").title()

    st.markdown("<h1 style='text-align:center;'>🎉 Booking Confirmed</h1>", unsafe_allow_html=True)

    st.success(f"✅ Your {brand} {model} has been booked successfully.")
    st.info("🚚 The car will be delivered to your location.")

    col1,col2,col3 = st.columns([1,2,1])

    with col2:

        if st.button("Go to Dashboard"):

            st.session_state["page"] = "book"
            st.session_state["booking_success"] = False
            st.rerun()


# -----------------------------
# CONTACT PAGE
# -----------------------------
def contact_page():

    st.title("📞 Contact Us")

    st.write("Email: support@aicarrental.com")
    st.write("Phone: +91 9876543210")
    st.write("Location: Bangalore, India")


# -----------------------------
# ROUTING
# -----------------------------
if st.session_state["page"] == "home":
    home_page()

elif st.session_state["page"] == "login":
    login_page()

elif st.session_state["page"] == "preferences":
    preferences_page()

elif st.session_state["page"] == "book":
    book_page()

elif st.session_state["page"] == "payment":
    payment_page()

elif st.session_state["page"] == "confirmation":
    confirmation_page()

elif st.session_state["page"] == "contact":
    contact_page()