import streamlit as st
import requests
from data_loader import load_users, load_friend_requests
from ui_components import user_selector, date_slider

df_users = load_users()
selected_user = user_selector(df_users)

df_requests = load_friend_requests(selected_user)

if not df_requests.empty:
    min_date = df_requests["created_at"].min().date()
    max_date = df_requests["created_at"].max().date()
    selected_date = date_slider(min_date, max_date)

    requests.post("http://localhost:8050/dash/", json={"selected_user": selected_user, "selected_date": str(selected_date)})

st.write("### 네트워크 성장 과정")
st.components.v1.iframe("http://localhost:8050/dash/", height=700)
