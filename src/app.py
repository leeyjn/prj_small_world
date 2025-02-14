import streamlit as st
import subprocess
from data_loader import load_users, load_friend_requests
from network_builder import build_network
from ui_components import user_selector, date_slider
import requests

DASH_SERVER_CMD = ["python", "src/dash_server.py"]
try:
    subprocess.Popen(DASH_SERVER_CMD, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
except Exception as e:
    st.error(f"⚠️ Dash 서버 실행 실패: {e}")

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
