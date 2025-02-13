import streamlit as st
import sqlite3
import pandas as pd
import networkx as nx
import dash_cytoscape as cyto
import json
from datetime import datetime
import os

# ✅ 환경 감지 (로컬 vs. 클라우드)
if "STREAMLIT_SERVER" in os.environ:
    DB_PATH = "/mount/src/prj_small_world/db/network_analysis.db"  # 클라우드 환경용
else:
    DB_PATH = "C:/Users/pc/Python_Projects/prj_small_world/db/network_analysis.db"  # 로컬 환경용

# ✅ SQLite 연결
conn = sqlite3.connect(DB_PATH, check_same_thread=False)  # ✅ Streamlit 실행 시 `check_same_thread=False` 필요!

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
min_date = datetime.strptime(user_created_at, "%Y-%m-%d")
max_date = datetime.today()

# ✅ 3️⃣ 친구 추가 시각화 (슬라이더)
selected_date = st.slider("네트워크 빌드 시간 선택", min_value=min_date, max_value=max_date, value=min_date)

# ✅ 4️⃣ 친구 요청 데이터 가져오기
query_friend_requests = """
    SELECT receive_user_id, send_user_id, created_at
    FROM friend_requests_optimized
    WHERE receive_user_id = ?
    ORDER BY created_at ASC
"""
df_requests = pd.read_sql_query(query_friend_requests, conn, params=(selected_user,))

# ✅ 5️⃣ 네트워크 그래프 데이터 구성
G = nx.Graph()
G.add_node(int(selected_user), label=str(selected_user))  # 초기 노드

# ✅ 시간 순서대로 친구 추가 (슬라이더에서 선택한 시간 이전의 요청만 반영)
for _, row in df_requests.iterrows():
    if datetime.strptime(row["created_at"], "%Y-%m-%d %H:%M:%S") <= selected_date:
        G.add_node(row["send_user_id"], label=str(row["send_user_id"]))
        G.add_edge(int(selected_user), row["send_user_id"])

# ✅ Cytoscape 노드 & 엣지 변환
cyto_nodes = [{"data": {"id": str(n), "label": str(n)}} for n in G.nodes]
cyto_edges = [{"data": {"source": str(u), "target": str(v)}} for u, v in G.edges]

# ✅ Cytoscape 네트워크 시각화
cyto_style = {
    "height": "600px",
    "width": "100%",
    "border": "1px solid lightgray"
}

st.write("### 네트워크 성장 과정")
cyto_graph = cyto.Cytoscape(
    id="cyto-graph",
    elements=cyto_nodes + cyto_edges,
    layout={"name": "cose"},
    style=cyto_style
)
st.write(cyto_graph)

# ✅ SQLite 연결 종료
conn.close()
