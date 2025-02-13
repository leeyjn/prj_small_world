import streamlit as st
import sqlite3
import pandas as pd
import networkx as nx
import dash
from dash import dcc, html
import dash_cytoscape as cyto
from flask import Flask
import json
from datetime import datetime
import os

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

# ✅ 친구 요청 데이터 가져오기 (JSON 형태로 저장된 requests_list 파싱)
query_friend_requests = """
    SELECT user_id, requests_list
    FROM friend_requests_optimized
    WHERE user_id = ?
"""
df_requests = pd.read_sql_query(query_friend_requests, conn, params=(selected_user,))

# ✅ JSON 데이터를 DataFrame으로 변환
friend_requests = []
for _, row in df_requests.iterrows():
    user_id = row["user_id"]
    requests_list = json.loads(row["requests_list"]) if isinstance(row["requests_list"], str) else []
    
    for request in requests_list:
        friend_requests.append({
            "receive_user_id": user_id,
            "send_user_id": request["send_user_id"],
            "created_at": request["created_at"],
            "status": request["status"]
        })

df_requests_expanded = pd.DataFrame(friend_requests)

# ✅ 3️⃣ 유저별 슬라이딩 바의 최소/최대 날짜 계산
if not df_requests_expanded.empty:
    df_requests_expanded["created_at"] = pd.to_datetime(df_requests_expanded["created_at"], errors="coerce")
    min_date = df_requests_expanded["created_at"].min().to_pydatetime()  # 🔥 Timestamp -> datetime 변환
    max_date = df_requests_expanded["created_at"].max().to_pydatetime()  # 🔥 Timestamp -> datetime 변환
else:
    min_date = datetime.strptime(user_created_at, "%Y-%m-%d %H:%M:%S.%f").replace(microsecond=0)  # 🔥 datetime 변환 후 마이크로초 제거
    max_date = datetime.today()

# ✅ 4️⃣ 친구 추가 시각화 (유저별 동적 타임라인 슬라이더 적용)
selected_date = st.slider("네트워크 빌드 시간 선택", min_value=min_date, max_value=max_date, value=min_date)

# ✅ 5️⃣ 선택된 기간 내의 친구 요청 필터링
filtered_requests = df_requests_expanded[df_requests_expanded["created_at"] <= selected_date]

# ✅ 6️⃣ 네트워크 그래프 데이터 구성
G = nx.Graph()
G.add_node(int(selected_user), label=str(selected_user))  # 초기 노드

for _, row in filtered_requests.iterrows():
    G.add_node(row["send_user_id"], label=str(row["send_user_id"]))
    G.add_edge(int(selected_user), row["send_user_id"])

# ✅ Cytoscape 노드 & 엣지 변환
cyto_nodes = [{"data": {"id": str(n), "label": str(n)}} for n in G.nodes]
cyto_edges = [{"data": {"source": str(u), "target": str(v)}} for u, v in G.edges]

# ✅ Flask 앱 생성
server = Flask(__name__)
app = dash.Dash(__name__, server=server, routes_pathname_prefix="/dash/")

# ✅ Dash 레이아웃 설정
app.layout = html.Div([
    html.H3("📡 네트워크 성장 과정"),
    cyto.Cytoscape(
        id="cyto-graph",
        elements=cyto_nodes + cyto_edges,
        layout={"name": "cose"},
        style={"width": "100%", "height": "600px", "border": "1px solid black"},
        stylesheet=[
            {"selector": "node", "style": {"content": "data(label)", "text-valign": "center", "background-color": "#0084ff"}},
            {"selector": "edge", "style": {"line-color": "#9dbaea", "width": 2}},
        ]
    )
])

# ✅ Dash 앱을 Streamlit에서 iframe으로 표시
st.write("### 네트워크 성장 과정")
st.components.v1.iframe("http://localhost:8050/dash/", height=700)

# ✅ SQLite 연결 종료
conn.close()

# ✅ Dash 실행
if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
