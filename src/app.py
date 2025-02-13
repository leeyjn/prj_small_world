import streamlit as st
import sqlite3
import pandas as pd
import networkx as nx
import subprocess
import json
from datetime import datetime

# ✅ SQLite 데이터베이스 연결
DB_PATH = "C:/Users/pc/Python_Projects/prj_small_world/db/network_analysis.db"
conn = sqlite3.connect(DB_PATH)

# ✅ 1️⃣ 유저 목록 가져오기 (가입일 기준 정렬)
query_users = """
    SELECT user_id, friends_num, created_at
    FROM users
    ORDER BY created_at ASC
"""
df_users = pd.read_sql_query(query_users, conn)

# ✅ 2️⃣ Streamlit UI 구성
st.title("📊 유저 네트워크 성장 과정 시각화")

# ✅ 유저 선택 드롭다운 (가입일 순 정렬)
selected_user = st.selectbox("유저를 선택하세요:", df_users["user_id"].astype(str))

# ✅ 선택된 유저의 가입 날짜 가져오기
user_created_at = df_users[df_users["user_id"] == int(selected_user)]["created_at"].values[0]

# ✅ Flask/Dash 서버 실행 (이미 실행 중인지 확인 후 실행)
DASH_SERVER_CMD = ["python", "src/dash_server.py"]
try:
    subprocess.Popen(DASH_SERVER_CMD, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
except Exception as e:
    st.error(f"⚠️ Dash 서버 실행 실패: {e}")

# ✅ Streamlit에서 Dash 앱을 iframe으로 포함
st.write("### 네트워크 성장 과정")
st.components.v1.iframe("http://localhost:8050/dash/", height=700)

# ✅ SQLite 연결 종료
conn.close()
