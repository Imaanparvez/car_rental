from flask import Flask, render_template, request, redirect, session, url_for
from datetime import date, timedelta
from auth import login_user, register_user
from cars import get_all_cars
from interactions import log_booking_interaction
from seed_data import seed_cars
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "fallbacksecret")  # Needed for sessions


# --------------------------
# HOME PAGE
# --------------------------
@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")

    return render_template("home.html", user=session["user"])


# --------------------------
# LOGIN
# --------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = login_user(email, password)

        if user:
            session["user"] = user
            return redirect("/")
        else:
            return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")


# --------------------------
# SIGN UP
# --------------------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        password = request.form["password"]

        if register_user(name, email, phone, password):
            return redirect("/login")
        else:
            return render_template("signup.html", error="User already exists")

    return render_template("signup.html")


# --------------------------
# LOGOUT
# --------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# --------------------------
# CAR BOOKING PAGE
# --------------------------
@app.route("/book", methods=["GET", "POST"])
def book():
    if "user" not in session:
        return redirect("/login")

    cars = get_all_cars()

    if request.method == "POST":
        car_id = request.form["car_id"]

        log_booking_interaction(
            user_id=session["user"]["_id"],
            car_id=car_id
        )

        return render_template("book.html", cars=cars, success="Booking confirmed!")

    return render_template("book.html", cars=cars)


# --------------------------
# ADMIN SEED
# --------------------------
@app.route("/seed")
def seed():
    if "user" not in session or session["user"]["email"] != "imaanparvez1@gmail.com":
        return "Unauthorized", 403

    count = seed_cars()
    return f"Added {count} cars"


# --------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
