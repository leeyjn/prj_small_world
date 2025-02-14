import streamlit as st
import requests
import pandas as pd
import json
import sqlite3

# ✅ 로컬 SQLite 데이터베이스 경로
DB_PATH = "C:/Users/pc/Python_Projects/prj_small_world/db/network_analysis.db"

# ✅ SQLite 연결 함수
def get_user_created_at(user_id):
    """유저의 가입 날짜(created_at) 가져오기"""
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT created_at FROM users WHERE user_id = ?
    """
    df = pd.read_sql_query(query, conn, params=(user_id,))
    conn.close()
    
    if df.empty:
        return None
    return df["created_at"].iloc[0]

def get_user_friend_requests(user_id):
    """유저의 친구 요청 데이터 가져오기"""
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT requests_list FROM friend_requests_optimized
        WHERE user_id = ?
    """
    df = pd.read_sql_query(query, conn, params=(user_id,))
    conn.close()

    if df.empty:
        return pd.DataFrame(columns=["send_user_id", "created_at"])
    
    df["requests_list"] = df["requests_list"].apply(json.loads)
    requests_expanded = []
    
    for _, row in df.iterrows():
        for req in row["requests_list"]:
            requests_expanded.append({
                "send_user_id": req["send_user_id"],
                "created_at": req["created_at"]
            })
    
    return pd.DataFrame(requests_expanded)

# ✅ Streamlit UI
st.title("📊 유저 네트워크 성장 과정 시각화")

# ✅ 유저 선택 드롭다운
conn = sqlite3.connect(DB_PATH)
query_users = """
    SELECT user_id FROM users ORDER BY created_at ASC
"""
df_users = pd.read_sql_query(query_users, conn)
conn.close()

selected_user = st.selectbox("유저를 선택하세요:", df_users["user_id"].astype(str))

# ✅ 선택된 유저의 가입 날짜 가져오기
user_created_at = get_user_created_at(selected_user)
if not user_created_at:
    st.error("🚨 해당 유저의 가입 날짜를 찾을 수 없습니다.")
    st.stop()

# ✅ 유저의 친구 요청 데이터 가져오기
df_requests = get_user_friend_requests(selected_user)
df_requests["created_at"] = pd.to_datetime(df_requests["created_at"])

# ✅ 슬라이딩 바의 범위 설정
min_date = pd.to_datetime(user_created_at)  # ✅ 유저의 가입 날짜를 최소값으로 설정
max_date = df_requests["created_at"].max() if not df_requests.empty else min_date  # ✅ 유저가 마지막으로 친구를 추가한 날짜

# ✅ 슬라이딩 바 추가
selected_date = st.slider(
    "네트워크 빌드 시간 선택", 
    min_value=min_date.date(), 
    max_value=max_date.date(), 
    value=min_date.date()
)

# ✅ 유저 정보 표시
st.markdown(f"✅ **선택된 유저:** {selected_user}")
st.markdown(f"📆 **가입 날짜:** {min_date.date()}")

# ✅ Dash 서버로 데이터 요청
response = requests.post(
    "http://localhost:8050/update_network",
    json={"selected_user": selected_user, "selected_date": str(selected_date)}
)

if response.status_code == 200:
    network_data = response.json()
    st.markdown(f"📊 **네트워크 노드 수:** {len([n for n in network_data if 'source' not in n['data']])}")
    st.markdown(f"🔗 **네트워크 엣지 수:** {len([e for e in network_data if 'source' in e['data']])}")
else:
    st.error("🚨 Dash 서버에서 데이터를 가져오는 데 실패했습니다.")

