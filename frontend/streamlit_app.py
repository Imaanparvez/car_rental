import streamlit as st
import requests
from datetime import date, timedelta
import pandas as pd
import os

BACKEND_URL = "http://127.0.0.1:5000"

st.set_page_config(page_title="AI Car Rental", layout="wide")

# -----------------------------
# GLOBAL CSS
# -----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

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
border-radius:8px;
height:48px;
width:100%;
font-weight:600;
font-size:16px;
transition:all 0.3s ease;
border: none;
background-color: #2b2b2b;
color: white;
}

.stButton>button:hover{
transform:translateY(-2px);
box-shadow: 0 4px 12px rgba(0,0,0,0.15);
background-color: #000;
color: white;
}

.card{
background:white;
padding:24px;
border-radius:16px;
box-shadow:0 8px 24px rgba(0,0,0,0.06);
text-align:center;
margin-bottom:24px;
border: 1px solid #f0f0f0;
transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.card:hover{
transform:translateY(-5px);
box-shadow:0 12px 32px rgba(0,0,0,0.1);
}

.center-title{
text-align:center;
margin-top:40px;
margin-bottom:20px;
font-weight:700;
color:#111;
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

    # Hero Banner
    st.markdown("""
    <div style="
        position: relative;
        padding: 100px 40px;
        border-radius: 16px;
        text-align: center;
        color: white;
        margin-bottom: 40px;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    ">
        <div style="
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background-image: url('https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?auto=format&fit=crop&q=80');
            background-size: cover;
            background-position: center;
            z-index: 0;
        "></div>
        <div style="
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0,0,0,0.6);
            z-index: 1;
        "></div>
        <div style="position: relative; z-index: 2;">
            <h1 style="font-size: 3.5rem; font-weight: 800; margin-bottom: 20px;">Redefining Your Drive</h1>
            <p style="font-size: 1.2rem; color: #f0f0f0; margin-bottom: 40px; max-width: 600px; margin-left: auto; margin-right: auto;">
                Experience seamless, AI-powered car rentals. Discover the perfect vehicle tailormade for your journey with our advanced recommendation engine.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.session_state["user"] is None:
             btn_label = "Get Started Now 🚀"
        else:
             btn_label = "Explore Cars 🚗"
             
        if st.button(btn_label, type="primary"):
             if st.session_state["user"] is None:
                 st.session_state["page"] = "login"
             else:
                 st.session_state["page"] = "preferences"
             st.rerun()

    st.write("")
    st.write("")
    
    # Why Choose Us Section
    st.markdown("<h2 style='text-align: center; margin-bottom: 40px;'>Why Choose Premium AI Rentals?</h2>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        with st.container(border=True):
            st.markdown("<img src='https://images.unsplash.com/photo-1555215695-3004980ad54e?auto=format&fit=crop&q=80&w=400&h=250' style='width: 100%; height: 180px; object-fit: cover; border-radius: 8px 8px 0 0; margin-bottom: 15px;'>", unsafe_allow_html=True)
            st.markdown("<h3 style='text-align: center;'>Smart AI Matching</h3>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #666;'>Our recommendation model analyzes your preferences and past history to find a car tailored perfectly for you.</p>", unsafe_allow_html=True)
            
    with c2:
        with st.container(border=True):
            st.markdown("<img src='https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?auto=format&fit=crop&q=80&w=400&h=250' style='width: 100%; height: 180px; object-fit: cover; border-radius: 8px 8px 0 0; margin-bottom: 15px;'>", unsafe_allow_html=True)
            st.markdown("<h3 style='text-align: center;'>Premium Fleet</h3>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #666;'>We vet and maintain a vast selection of high-quality vehicles, from sporty hatchbacks to luxury SUVs.</p>", unsafe_allow_html=True)
            
    with c3:
        with st.container(border=True):
            st.markdown("<img src='https://images.unsplash.com/photo-1506015391300-4802dc74de2e?auto=format&fit=crop&q=80&w=400&h=250' style='width: 100%; height: 180px; object-fit: cover; border-radius: 8px 8px 0 0; margin-bottom: 15px;'>", unsafe_allow_html=True)
            st.markdown("<h3 style='text-align: center;'>Instant Booking</h3>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #666;'>No queues, no endless paperwork. Confirm your booking in seconds and get the car delivered to your location.</p>", unsafe_allow_html=True)

    st.write("")
    st.write("")
    st.divider()

    # Metrics Section
    m1, m2, m3 = st.columns(3)
    m1.metric(label="Cars Available", value="500+", delta="Growing daily")
    m2.metric(label="Active Users", value="10k+", delta="12% this month")
    m3.metric(label="Successful Trips", value="25k+", delta="High rated")
    
    st.write("")
    st.divider()

    # Footer
    st.markdown("""
    <div style="text-align: center; color: #888; font-size: 0.9rem; margin-top: 20px;">
        <p>© 2026 AI Premium Car Rentals. All rights reserved.</p>
        <p>Built with Streamlit & Machine Learning</p>
    </div>
    """, unsafe_allow_html=True)


# -----------------------------
# LOGIN PAGE
# -----------------------------
def login_page():

    st.markdown("<h1 style='text-align: center;'>🔐 Login / Sign Up</h1>", unsafe_allow_html=True)
    st.write("")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        with st.container(border=True):

            tab1, tab2 = st.tabs(["Login", "Sign Up"])

            with tab1:

                email = st.text_input("Email", key="login_email")
                password = st.text_input("Password", type="password", key="login_password")
                st.write("")

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
                        st.error("Invalid credentials")

            with tab2:

                name = st.text_input("Name", key="signup_name")
                email = st.text_input("Email", key="signup_email")
                phone = st.text_input("Phone", key="signup_phone")
                password = st.text_input("Password", type="password", key="signup_password")
                st.write("")

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
                        st.success("Account created successfully. Please login.")


# -----------------------------
# PREFERENCES PAGE
# -----------------------------
def preferences_page():

    st.markdown("<h1 style='text-align: center;'>🎛 Choose Your Preferences</h1>", unsafe_allow_html=True)
    st.write("")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        with st.container(border=True):

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
            st.write("")

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

    st.markdown("<h1 style='text-align: center; margin-bottom: 20px;'>🚗 Dashboard</h1>", unsafe_allow_html=True)

    cars = safe_get(f"{BACKEND_URL}/api/cars")

    with st.container(border=True):
        st.markdown("### 🔍 Search Cars")
        search = st.text_input("Search by brand or model", placeholder="e.g. Toyota, Honda")
        st.write("")

        if search:

            seen=set()

            for i,c in enumerate(cars):

                name=f"{c['Brand']} {c['Model']}".title()

                if search.lower() in name.lower():

                    if name not in seen:

                        seen.add(name)

                        with st.container(border=True):
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.markdown(f"#### {name}")
                                st.write(f"Fuel: {c.get('Fuel_Type')} | Body: {c.get('Body_Type')} | Engine: {c.get('Engine_CC')}cc")
                            with col2:
                                if st.button("View Car", key=f"search_{i}"):

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

            with st.container(border=True):

                st.markdown(f"<h3 style='text-align:center;'>{brand} {model}</h3>", unsafe_allow_html=True)
                st.write("")

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

    st.markdown('<h3 class="center-title">👥 Previous Users Also Viewed</h3>', unsafe_allow_html=True)

    cols = st.columns(3)

    for i,car in enumerate(st.session_state["cf_cars"]):

        brand = car["Brand"].title()
        model = car["Model"].title()

        with cols[i%3]:

            with st.container(border=True):

                st.markdown(f"<h3 style='text-align:center;'>{brand} {model}</h3>", unsafe_allow_html=True)
                st.write("")

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

    st.markdown('<h3 class="center-title">🕒 Your Booking History</h3>', unsafe_allow_html=True)
    
    user_id = st.session_state["user"].get("_id") if st.session_state.get("user") else None
    if user_id:
        history = safe_get(f"{BACKEND_URL}/api/user-bookings/{user_id}")
        if history and len(history) > 0:
            with st.container(border=True):
                for item in history:
                    st.markdown(f"**🚗 {item['car']}** — Booked {item['count']} time(s)")
        else:
            st.info("You don't have any past bookings yet.")


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

    st.markdown("<h1 style='text-align: center;'>💳 Payment Details</h1>", unsafe_allow_html=True)
    st.write("")

    col1, col2, col3 = st.columns([1, 4, 1])

    with col2:
        with st.container(border=True):

            c1, c2 = st.columns([1, 1])

            with c1:
                st.markdown(f"""
                <h3 style="margin-top:0;">{brand} {model}</h3>
                <p><strong>Year:</strong> {year}</p>
                <p><strong>Engine CC:</strong> {cc}</p>
                <p><strong>Mileage:</strong> {mileage}</p>
                """, unsafe_allow_html=True)

            with c2:
                pickup = st.date_input("Pickup Date", date.today())
                drop = st.date_input("Return Date", date.today()+timedelta(days=1))

                days = max((drop - pickup).days, 1)

                price_per_day = 800 + cc * 0.8
                total_price = days * price_per_day

                st.markdown(f"### Total: ₹{int(total_price)}")
                st.write(f"({days} days @ ₹{int(price_per_day)}/day)")

            st.write("")
            
            # -----------------------------
            # CONFIRM PAYMENT BUTTON
            # -----------------------------
            if st.button("Confirm Booking"):

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

    # Contact Us Hero Banner
    st.markdown("""
    <div style="
        position: relative;
        padding: 60px 40px;
        border-radius: 16px;
        text-align: center;
        color: white;
        margin-bottom: 40px;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    ">
        <div style="
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background-image: url('https://images.unsplash.com/photo-1596524430615-b46475ddff6e?auto=format&fit=crop&q=80');
            background-size: cover;
            background-position: center;
            z-index: 0;
        "></div>
        <div style="
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0,0,0,0.7);
            z-index: 1;
        "></div>
        <div style="position: relative; z-index: 2;">
            <h1 style="font-size: 3rem; font-weight: 800; margin-bottom: 10px;">📞 Get in Touch</h1>
            <p style="font-size: 1.2rem; color: #f0f0f0;">
                We are here to help you 24/7. Reach out to us for any inquiries or support.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("### Contact Information")
        st.write("Feel free to contact us directly using the information below.")
        
        with st.container(border=True):
            st.markdown("#### 📍 Location")
            st.markdown("<p style='color: #666; font-size: 16px;'>Srinagar, Kashmir</p>", unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("#### 📞 Phone")
            st.markdown("<p style='color: #666; font-size: 16px;'>+91 6005333097</p>", unsafe_allow_html=True)
            
        with st.container(border=True):
            st.markdown("#### 📧 Email")
            st.markdown("<p style='color: #666; font-size: 16px;'>support@aicarrental.com</p>", unsafe_allow_html=True)

    with col2:
        st.markdown("### Send us a Message")
        with st.container(border=True):
            name = st.text_input("Your Name")
            email = st.text_input("Your Email")
            message = st.text_area("Your Message", height=120)
            
            if st.button("Submit Message", type="primary"):
                if name and email and message:
                    st.success("✅ Thank you! Your message has been sent successfully.")
                else:
                    st.error("Please fill out all fields before submitting.")


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