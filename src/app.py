import streamlit as st
import subprocess
from data_loader import load_users, load_friend_requests
from network_builder import build_network
from ui_components import user_selector, date_slider
import requests

# ✅ Dash 서버 실행
DASH_SERVER_CMD = ["python", "src/dash_server.py"]
try:
    subprocess.Popen(DASH_SERVER_CMD, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
except Exception as e:
    st.error(f"⚠️ Dash 서버 실행 실패: {e}")

# ✅ 유저 데이터 로드
df_users = load_users()
selected_user = user_selector(df_users)

# ✅ 유저별 데이터 로드
df_requests = load_friend_requests(selected_user)

# ✅ 슬라이딩 바 설정
min_date = df_requests["created_at"].min() if not df_requests.empty else None
max_date = df_requests["created_at"].max() if not df_requests.empty else None

if min_date and max_date:
    selected_date = date_slider(min_date, max_date)

    # ✅ Dash 서버에 유저 & 시간 정보 업데이트
    requests.post("http://localhost:8050/dash/", json={"selected_user": selected_user, "selected_date": str(selected_date)})

# ✅ Dash 네트워크 그래프 표시
st.write("### 네트워크 성장 과정")
st.components.v1.iframe("http://localhost:8050/dash/", height=700)
