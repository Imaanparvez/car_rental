import streamlit as st
from pymongo import MongoClient

client = MongoClient(st.secrets["mongo_uri"])
db = client["car_rental"]

users_col = db["users"]
cars_col = db["cars"]
interactions_col = db["interactions"]
