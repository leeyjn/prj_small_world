import streamlit as st
import pandas as pd
import requests
import sqlite3

# ✅ SQLite 데이터베이스 경로
DB_PATH = "C:/Users/pc/Python_Projects/prj_small_world/db/network_analysis.db"

# ✅ Streamlit UI 설정
st.title("📊 유저 네트워크 성장 과정 시각화")

# ✅ 데이터베이스 연결 및 유저 목록 가져오기
conn = sqlite3.connect(DB_PATH)
df_users = pd.read_sql_query("SELECT user_id, created_at FROM users ORDER BY created_at ASC", conn)
conn.close()

# ✅ 유저 선택
selected_user = st.selectbox("유저를 선택하세요:", df_users["user_id"].astype(str).tolist())

# ✅ 선택된 유저의 가입 날짜 가져오기
user_created_at = df_users[df_users["user_id"].astype(str) == selected_user]["created_at"].values
if len(user_created_at) > 0:
    user_created_at = pd.to_datetime(user_created_at[0]).date()
else:
    user_created_at = None

# ✅ 친구 요청 데이터 로드
conn = sqlite3.connect(DB_PATH)
query_friend_requests = """
    SELECT requests_list FROM friend_requests_optimized WHERE user_id = ?
"""
df_requests = pd.read_sql_query(query_friend_requests, conn, params=(selected_user,))
conn.close()

if not df_requests.empty:
    df_requests["requests_list"] = df_requests["requests_list"].apply(lambda x: pd.DataFrame(eval(x)))
    min_date = df_requests["requests_list"].apply(lambda x: x["created_at"].min()).min()
    max_date = df_requests["requests_list"].apply(lambda x: x["created_at"].max()).max()
    min_date, max_date = pd.to_datetime(min_date).date(), pd.to_datetime(max_date).date()
else:
    min_date, max_date = user_created_at, user_created_at

# ✅ 네트워크 빌드 시간 선택 슬라이더
selected_date = st.slider("네트워크 빌드 시간 선택", min_value=min_date, max_value=max_date, value=min_date)

# ✅ 선택된 유저와 날짜 출력
st.markdown(f"✅ **선택된 유저:** {selected_user}")
st.markdown(f"📆 **가입 날짜:** {user_created_at}")

# ✅ Dash 서버에 데이터 요청
payload = {"selected_user": selected_user, "selected_date": str(selected_date)}
response = requests.post("http://localhost:8050/update_network", json=payload)

if response.status_code == 200:
    network_data = response.json()
    node_count = len([item for item in network_data if "source" not in item["data"]])
    edge_count = len([item for item in network_data if "source" in item["data"]])
else:
    network_data = []
    node_count, edge_count = 0, 0

st.markdown(f"📊 **네트워크 노드 수:** {node_count}")
st.markdown(f"🔗 **네트워크 엣지 수:** {edge_count}")
