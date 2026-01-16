import streamlit as st
from pymongo import MongoClient

uri = st.secrets["mongo"]["mongo_uri"]

client = MongoClient(uri)
db = client["car_rental"]

users_col = db["users"]
cars_col = db["cars"]
interactions_col = db["interactions"]
