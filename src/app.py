import streamlit as st
import pandas as pd
import requests
import sqlite3
import json
import streamlit.components.v1 as components
from datetime import timedelta

# ✅ 페이지 설정 (가로 확장 레이아웃 적용)
st.set_page_config(layout="wide")

# ✅ SQLite 데이터베이스 경로
DB_PATH = "C:/Users/pc/Python_Projects/prj_small_world/db/network_analysis.db"

# ✅ Streamlit UI 설정
st.title("📊 유저 네트워크 성장 과정 시각화")

# ✅ 데이터베이스 연결 및 유저 목록 가져오기
conn = sqlite3.connect(DB_PATH)
df_users = pd.read_sql_query("SELECT user_id, created_at FROM users ORDER BY created_at ASC", conn)
conn.close()

# ✅ 유저 선택 (드롭다운 리스트)
selected_user = st.selectbox("유저를 선택하세요:", df_users["user_id"].astype(str).tolist())

# ✅ 선택된 유저의 가입 날짜 가져오기
user_created_at = df_users[df_users["user_id"].astype(str) == selected_user]["created_at"].values
user_created_at = pd.to_datetime(user_created_at[0]).date() if len(user_created_at) > 0 else None

# ✅ 해당 유저의 친구 요청 데이터 조회
conn = sqlite3.connect(DB_PATH)
query_friend_requests = """
    SELECT requests_list FROM friend_requests_optimized WHERE user_id = ?
"""
df_requests = pd.read_sql_query(query_friend_requests, conn, params=(selected_user,))
conn.close()

# ✅ 선택된 유저의 친구 요청 기록이 있다면, 가입 이후부터 해당 날짜까지 범위 설정
if not df_requests.empty:
    df_requests["requests_list"] = df_requests["requests_list"].apply(json.loads)  # ✅ json.loads() 적용
    min_date = user_created_at  # 유저 가입 날짜
    max_date = df_requests["requests_list"].apply(
        lambda x: max([pd.to_datetime(req["created_at"]).date() for req in x], default=min_date)
    ).max()
else:
    min_date, max_date = user_created_at, user_created_at  # 유저 가입 날짜로 초기화

# ✅ 오류 방지: `min_date == max_date`일 경우, `max_date`를 +1일 추가
if min_date == max_date:
    max_date += timedelta(days=1)

# ✅ 네트워크 빌드 시간 선택 슬라이더
selected_date = st.slider("네트워크 빌드 시간 선택", min_value=min_date, max_value=max_date, value=min_date)

# ✅ 선택된 유저와 날짜 출력
st.markdown(f"✅ **선택된 유저:** {selected_user}")
st.markdown(f"📆 **가입 날짜:** {user_created_at}")

# ✅ Dash 서버에 데이터 요청
payload = {"selected_user": selected_user, "selected_date": str(selected_date)}
response = requests.post("http://127.0.0.1:8050/update_network", json=payload)

if response.status_code == 200:
    network_data = response.json()
    node_count = len([item for item in network_data if "source" not in item["data"]])
    edge_count = len([item for item in network_data if "source" in item["data"]])
    st.success(f"✅ **네트워크 업데이트 완료** (노드: {node_count}, 엣지: {edge_count})")
else:
    st.error("⚠️ **네트워크 업데이트 실패**")
    st.write(response.text)  # 🔍 오류 메시지 확인

# ✅ Dash 네트워크 시각화 불러오기 (유저 & 날짜 반영)
st.markdown("## 🌐 네트워크 시각화")
iframe_url = f"http://127.0.0.1:8050/dash/?user={selected_user}&date={selected_date}"
components.iframe(iframe_url, width=1500, height=900, scrolling=True)
